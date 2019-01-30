from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItem, User

from flask import session as login_session
import random
import string

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///catalogDatabase.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase +
                    string.digits) for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        login_session['credentials'] = credentials.to_json()
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
                      json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        print "this is the status " + result['status']
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    gdisconnect()
    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    # del login_session['access_token']
    flash("You have successfully been logged out.")
    return redirect(url_for('BrowseCatalog'))


@app.route('/')
@app.route('/catalog')
def BrowseCatalog():
    catalog = session.query(Category).all()
    items = session.query(CategoryItem).order_by(
                                             CategoryItem.id.desc()).limit(10)
    if 'username' not in login_session:
        return render_template('publiccatalog.html',
                               catalog=catalog, items=items)
    else:
        return render_template('catalog.html', catalog=catalog, items=items)


@app.route('/catalog/<category_name>/items')
def BrowseCategory(category_name):
    catalog = session.query(Category).all()
    items = session.query(CategoryItem).filter_by(category_name=category_name)
    return render_template('categories.html', catalog=catalog, items=items,
                           category_name=category_name)


@app.route('/catalog/<category_name>/<item_name>')
def BrowseCategoryItem(category_name, item_name):
    item = session.query(CategoryItem).filter_by(name=item_name).one()
    if 'username' not in login_session:
        return render_template('publicitems.html', item=item)
    else:
        return render_template('menu.html', item=item)


@app.route('/catalog/additem', methods=['GET', 'POST'])
def AddItem():
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        newitem = CategoryItem(name=request.form['name'],
                               user_id=login_session['user_id'],
                               description=request.form['description'],
                               category_name=request.form['categoryName'])
        session.add(newitem)
        flash('New Item %s Successfully Created' % newitem.name)
        session.commit()
        return redirect(url_for('BrowseCatalog'))
    else:
        catalog = session.query(Category).all()
        return render_template('AddItem.html', catalog=catalog)


@app.route('/catalog/<item_name>/edit', methods=['GET', 'POST'])
def EditItem(item_name):
    if 'username' not in login_session:
        return redirect('/login')
    editeditem = session.query(CategoryItem).filter_by(name=item_name).one()
    editCategory = session.query(Category).filter_by(
        name=editeditem.category_name).one()
    if request.method == 'POST':
        if request.form['name']:
            editeditem.name = request.form['name']
        if request.form['description']:
            editeditem.description = request.form['description']
        if request.form['categoryName']:
            editeditem.category_name = request.form['categoryName']
        session.add(editeditem)
        session.commit()
        flash('Item Successfully Edited %s' % editeditem.name)
        return redirect(url_for('BrowseCategory',
                                category_name=editCategory.name))
    else:
        catalog = session.query(Category).all()
        return render_template('edititem.html',
                               catalog=catalog, item=editeditem)


@app.route('/catalog/<item_name>/delete', methods=['GET', 'POST'])
def DeleteItem(item_name):
    if 'username' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(CategoryItem).filter_by(name=item_name).one()
    deleteCategory = session.query(
                     Category).filter_by(name=itemToDelete.category_name).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('%s Successfully Deleted' % itemToDelete.name)
        return redirect(
            url_for('BrowseCategory', category_name=deleteCategory.name))
    else:
        Catalog = session.query(Category).all()
        return render_template(
            'Deleteitem.html', Catalog=Catalog, item=item_name)


# JSON APIs to view Catalog Information
@app.route('/catalog/catalog.json')
def CatalogJSON():
    items = session.query(CategoryItem).order_by(CategoryItem.id.desc())
    return jsonify(Catalog_Items=[i.serialize for i in items])


@app.route('/catalog/<category_name>/item/<int:item_id>/JSON')
def itemJSON(category_name, item_id):
    item = session.query(CategoryItem).filter_by(id=item_id).one()
    return jsonify(Item=item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
