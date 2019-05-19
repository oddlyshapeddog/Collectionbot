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



class Contest(Base):
    __tablename__ = 'contest'

    #have status be an INTEGER for the 3 states, prompt can stay the same, don't need extra commands yet, focus on the time
    id = Column(Integer, primary_key=True)
    mode = Column(Integer, nullable=False)
    prompt = Column(String(100), nullable=False)
    end = Column(Date, nullable=False) #days parameter to keep track of when it ends

#when registering use the register command to add the user to this table too
class QuestsMembers(Base):
    __tablename__ = 'questsmembers'

    # #this is the id of a user and the rest of the columns will be for quests they completed
    usrId = Column(Integer, primary_key=True)
    questId = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)
    #marks if this user has completed the quest
    completed = Column(Boolean, nullable = False)
    #a user's progress on a quest
    progress = Column(Integer, nullable=False)



class QuestsList(Base):
    __tablename__ = 'questslists'

    # #this is the id of a user and the rest of the columns will be for quests they completed
    questId = Column(Integer, primary_key=True)
    description = Column(String(100), nullable=False)
    #the amount that needs to be done to complete a quest
    completion = Column(Integer, nullable=False)
    #amount of xp to be awarded for completing a quest
    award = Column(Integer, nullable=False)
    #auto if is check by the bot, manual if checked by an admin
    mode = Column(String(10), nullable=False)
    #quest that can be reset by the users
    reset = Column(Boolean,nullable=False)


# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///TAPE_Database.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
