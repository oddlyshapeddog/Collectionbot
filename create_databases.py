import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 
Base = declarative_base()
 
class User(Base):
    __tablename__ = 'user'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = Column(String, primary_key=True) 
    name = Column(String(40), nullable=False) #names can't be more than 32 characters on discord anyway
    startdate = Column(Date, nullable=False)
    level = Column(Integer, nullable=False)
    currency = Column(Integer, nullable=False)
    streak = Column(Integer, nullable=False)
    expiry = Column(Date, nullable=False)
    submitted = Column(Boolean, nullable=False)
    raffle = Column(Boolean, nullable=False)
    promptsadded = Column(Integer, nullable=False)
    totalsubmissions = Column(Integer, nullable=False)
    currentxp = Column(Integer, nullable=False)
    adores = Column(Integer, nullable=False)
    highscore = Column(Integer, nullable=False)
    decaywarning = Column(Boolean, nullable=False)
 
# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///TAPE_Database.db')
 
# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)