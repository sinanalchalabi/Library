#!/usr/bin/env python
""" This file is to dump random data to our Database for testing purposes"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Library, Base, Book, User

engine = create_engine('sqlite:///library.db')
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
User1 = User(name="Sinan AlChalabi", email="sinan.alchalabi@gmail.com",
             picture='https://lh3.googleusercontent.com/-Y9x1_kOJ2Zc\
             /AAAAAAAAAAI/AAAAAAAAAIU/iIv2FcqFGs0/s60-p-rw-no-il/photo.jpg')
session.add(User1)
session.commit()

# The Library Of Congress
library1 = Library(user_id=1, name="The Library Of Congress")

session.add(library1)
session.commit()


book1 = Book(user_id=1, name="Infamous",
             description="The true story of countess Erzsebet Bathory",
             author="Kimberly L Craft", category="History", library=library1)

session.add(book1)
session.commit()

book2 = Book(user_id=1, name="The shadow catcher",
             description="rratives from two different eras intertwine: \
             the fraught passion between turn-of-the-twentieth-century \
             icon Edward Curtis (1868-1952) and his muse-wife, \
             Clara; and a twenty-first-century journey of redemption.",
             author="Marianne Wiggins", category="Biography", library=library1)

session.add(book2)
session.commit()

book3 = Book(user_id=1, name="The Poesy Ring",
             description="It's 1830 in County Kerry, Ireland, and a gold ring is \
             thrown into the wind by a young woman on a black horse... ",
             author="Bob Graham", category="Children", library=library1)

session.add(book3)
session.commit()

book4 = Book(user_id=1, name="Twilight",
             description="When seventeen-year-old Bella leaves \
             Phoenix to live with her father in Forks, Washington, \
             she meets an exquisitely handsome boy at school \
             for whom she feels an overwhelming attraction and \
             who she comes to realize is not wholly human.",
             author="Stephenie Meyer;", category="Romance", library=library1)

session.add(book4)
session.commit()

book5 = Book(user_id=1, name="Chinese art",
             description="Guide to motifs and visual imagery",
             author="Patricia Bjaaland Welch",
             category="Art", library=library1)

session.add(book5)
session.commit()

# Bodleian Library
library2 = Library(user_id=1, name="Bodleian Library")

session.add(library2)
session.commit()


book1 = Book(user_id=1, name="The season",
             description="Showing no interest in the sumptuous balls, \
             lavish dinner parties, and country weekends enjoyed by \
             the rest of early nineteenth-century London society, \
             seventeen-year-old Lady Alexandra Stafford seeks adventure \
             as she investigates the puzzling murder of the Earl of \
             Blackmoor, father of devilishly handsome Gavin.",
             author="Sarah MacLean", category="Mystery", library=library2)

session.add(book1)
session.commit()

book2 = Book(user_id=1, name="A brief history of the world",
             description="This course provides a survey of the expanse of human \
             development and civilization across the globe. \
             It begins with the invention of agriculture in the Neolithic era \
             and ends with the urbanized, technologically \
             sophisticated world of the 21st century.",
             author="Peter N Stearns", category="History", library=library2)

session.add(book2)
session.commit()

book3 = Book(user_id=1, name="The magic pencil", description="",
             author="Karen E Dabney", category="Children", library=library2)

session.add(book3)
session.commit()

# Library of Alexandria
library3 = Library(user_id=1, name="Library of Alexandria")

session.add(library3)
session.commit()


book1 = Book(user_id=1, name="Milton Glaser posters",
             description="Milton Glaser has designed more than 500 posters.\
             Some, like his 1967 Bob Dylan poster for Columbia Records,\
             are icons;",
             author="Milton Glaser", category="Art", library=library3)

session.add(book1)
session.commit()

book2 = Book(user_id=1, name="Chinese Dumplings",
             description="As Matilda Campbell's story begins in 1638, \
             this high-spirited and intelligent nineteen-year-old Scot is \
             unwilling to accept society's rules and barriers \
             regarding gender and class",
             author="Sarah Chloe Burns", category="History", library=library3)

session.add(book2)
session.commit()

print "Libraries and Books has been added"
