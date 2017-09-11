import schedule
import time
import simplejson as json
import datetime

#SQLalchemy stuff
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
from datetime import date, timedelta
#declaration for User class is in here
from create_databases import Base, User

## housekeeper helper script for bot ross

#Bind the data type to the engine and connect to our SQL database
engine = create_engine('sqlite:///TAPE_Database.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
#create session
session = DBSession() #session.commit() to store data, and session.rollback() to discard changes

def housekeeper():
    curdate = datetime.date.today()
    today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
    
    
    #get all rows and put into memory
    members = session.query(User).all()
    print("Housekeeping on " + str(len(members)) + " rows on " + today)
    
    for curr_member in members:
        # Update in batch
        #if submitted is yes
        #else if streak ends today
        if((curdate - curr_member.expiry).days == 0):
            #set streak to 0
            print("setting {0}'s streak to 0".format(curr_member.name))
            curr_member.streak = 0
        #Set submitted to no
        curr_member.submitted = 0
    #commit all changes to the sheet at once
    session.commit()
    print("housekeeping finished")



schedule.every().day.at("23:55").do(housekeeper)

while True:
    schedule.run_pending()
    time.sleep(1)
