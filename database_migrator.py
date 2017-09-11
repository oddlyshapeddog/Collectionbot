import schedule
import time
import simplejson as json
import datetime

#google sheets setup
import gspread
from oauth2client.service_account import ServiceAccountCredentials
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('creds.json',scope)
ServerSheet = "Art Plaza Extravaganza"
gc = gspread.authorize(credentials)
sheet_link = gc.open(ServerSheet).sheet1

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

curdate = datetime.date.today()
today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)

#count rows
rowCount = sheet_link.row_count
print("Migrating " + str(rowCount) + " users on " + today)
#get all rows and put into memory
cell_list = sheet_link.range(1,1,rowCount, 15)


#update our saved version of the data
for cellIndex in range(1,rowCount):
    rowIndex = cellIndex*15
    joinstring = cell_list[rowIndex+1].value
    joinstring = joinstring.split('-')
    joindate = datetime.date(int(joinstring[2]), int(joinstring[0]), int(joinstring[1]))
    expirestring = cell_list[rowIndex+5].value
    expirestring = expirestring.split('-')
    expiredate = datetime.date(int(expirestring[2]), int(expirestring[0]), int(expirestring[1]))
    #create a new User object for us to use
    new_user = User(name=cell_list[rowIndex].value, level=int(cell_list[rowIndex+2].value), id=cell_list[rowIndex+13].value, startdate=joindate, currency=cell_list[rowIndex+3].value, streak=cell_list[rowIndex+4].value, expiry=expiredate, submitted=0 if cell_list[rowIndex+6].value=='no' else 1, raffle=0 if cell_list[rowIndex+7].value=='no' else 1, promptsadded=cell_list[rowIndex+10].value, totalsubmissions=cell_list[rowIndex+11].value, currentxp=cell_list[rowIndex+12].value, adores=cell_list[rowIndex+14].value)
    
    #check if user is in database
    #try to find user in database using id
    already_registered = False
    try:
        db_user = session.query(User).filter(User.id == new_user.id).one()
        already_registered = True
    except sqlalchemy.orm.exc.NoResultFound:
        print('No user found, this is fine, Migrating {0}.'.format(new_user.name))
    except sqlalchemy.orm.exc.MultipleResultsFound:
        print('Multiple users found, something is really broken!')
        raise Exception('Multiple Users Error')
        
    if(already_registered == False):
        session.add(new_user)
        session.commit()
    
    

print("Migration finished")