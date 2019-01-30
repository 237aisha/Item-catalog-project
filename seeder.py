# coding: utf-8
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, CategoryItem, User

engine = create_engine('sqlite:///catalogDatabase.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Category for Romantic
Category1 = Category(user_id=1, name=u"Romantic")

session.add(Category1)
session.commit()

CategoryItem1 = CategoryItem(user_id=1, name=u'About Time', 
  description=u"""Richard Curtis, England’s foremost rom-commer,
  here plays with the space-time continuum in the most engaging
  and quirky way he knows how. While Domhnall Gleeson and Rachel
  McAdams play off each other well,the love that’s celebrated
  here is more the bond between father and son, as Bill Nighy
  brings heartbreaking pathos to the tale.""",
                      category=Category1)

session.add(CategoryItem1)
session.commit()


CategoryItem2 = CategoryItem(user_id=1, name=u"Sliding Doors", 
       description=u"""Peter Howitt’s high concept romantic comedy
        might hinge on how much you’re wanting double the Gwyneth 
        Paltrow, but she still manages to make you root for her
         (and at no point tries to to sell you magic vagina eggs).
          She’s Helen, who catches a tube train – or doesn’t – 
          and the film follows the romantic misadventures across
           parallel storylines. It refuses to rely on the gimmick,
            and both Paltrow and John Hannah make respectably adorable leads."""
                     , category=Category1)

session.add(CategoryItem2)
session.commit()

# Category for Comedy
Category2 = Category(user_id=1, name=u"Comedy")

session.add(Category2)
session.commit()

CategoryItem1 = CategoryItem(user_id=1, name=u"Old School",
 description=u"""You’re my boy, Blue! Say what you
 will about the Frat Pack films that followed it, but "Old School"
 still gets a passing grade. Part of the one-two punch (the other being "Elf") 
 that made Will Ferrell a bona fide movie star, this reminder that you’re never
  too old to start a fraternity also brought us Luke Wilson and Vince Vaughn at 
  their best. Its hilarity is all the more impressive when considering other movies
  of its kind haven’t aged as well — we’re looking at you, "Wedding Crashers". """,
                      category=Category2)

session.add(CategoryItem1)
session.commit()


CategoryItem2 = CategoryItem(user_id=1, name=u"Best in Show", 
       description=u"""It doesn’t go up to 11, but Christopher
        Guest’s account of a barking-mad dog show is still the 
        finest mockumentary ever made about anything besides a 
        Stonehenge-obsessed rock band. Last year’s similar "Mascots" 
        was funny enough, but mostly served to remind viewers what a
         one-of-a-kind accomplishment “Best in Show” is — the line 
         between laughing with and at these characters may be thin 
         as Guest endears his ensemble to us even as he mocks them,
          but at least we never stop rooting for the doggos.""",
                     category=Category2)

session.add(CategoryItem2)
session.commit()


# Category for Action
Category3 = Category(user_id=1, name="Action")

session.add(Category3)
session.commit()

CategoryItem1 = CategoryItem(user_id=1, name=u"Die Hard",
 description=u"""Die Hard is a 1988 American action film directed
  by John McTiernan and written by Steven de Souza and Jeb Stuart.
   It is based on the 1979 novel Nothing Lasts Forever, by Roderick
    Thorp. Die Hard follows off-duty New York City Police Department
     officer John McClane as he takes on a group of highly organized
      wrongdoers led by Hans Gruber, who perform a caper in a Los Angeles
       skyscraper under the guise of a terrorist attack using hostages,
        including McClane's wife Holly, to keep the police at bay.""",
                      category=Category3)

session.add(CategoryItem1)
session.commit()


CategoryItem2 = CategoryItem(user_id=1, name=u"Terminator 2: Judgment Day", 
       description=u"""Terminator 2: Judgment Day is a 1991 American science
        fiction action thriller film written, produced and directed by
         James Cameron. The film stars Arnold Schwarzenegger, Linda Hamilton,
          Robert Patrick and Edward Furlong. It is the second installment of
           the Terminator franchise and the sequel to the 1984 film The Terminator.
           Terminator 2 follows Sarah Connor and her ten-year-old son John,
            who is protected by a less advanced Terminator who is also sent
             back in time, as they are pursued by a new, more advanced Terminator,
              the liquid metal, shapeshifting T-1000, sent back in time to take out
               John Connor and prevent him from becoming the leader of the human
                resistance."""
                     ,category=Category3)

session.add(CategoryItem2)
session.commit()

print "added menu items!"
