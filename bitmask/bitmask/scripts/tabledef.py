# -*- coding: utf-8 -*-

import sys
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URI = 'postgresql://bitmask:password@localhost/bitmask'

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(SQLALCHEMY_DATABASE_URI)


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(30), unique=True)
    password = Column(String(255))

    def __repr__(self):
        return '<User %r>' % self.username


class MPK(Base):
    __tablename__ = "mpk"

    id = Column(Integer, primary_key=True)
    depth = Column(Integer, server_default="0")
    title = Column(String(30))
    url = Column(String(10), unique=True)
    mpk = Column(String(255))
    username = Column(String(255))

    def __repr__(self):
        return '<MPK %r>' % self.mpk

engine = db_connect()  # Connect to database
Base.metadata.create_all(engine)  # Create models
