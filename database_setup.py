#!/usr/bin/env python
""" This file is to build the required database for this project """
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

# Buliding Users Table
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'email': email.id,
        }

# Buliding Libraries Table
class Library(Base):
    __tablename__ = 'library'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }

# Buliding Books Tables
class Book(Base):
    __tablename__ = 'book'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    author = Column(String(80))
    category = Column(String(80))
    library_id = Column(Integer, ForeignKey('library.id'))
    library = relationship(Library)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'author': self.author,
            'category': self.category,
            'LibraryName': self.library.name,
            'LibraryID': self.library.id,
        }


engine = create_engine('sqlite:///library.db')


Base.metadata.create_all(engine)
