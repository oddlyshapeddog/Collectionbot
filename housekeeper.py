import schedule
import time
import simplejson as json
import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials

## global googlesheets setup
## housekeeper helper script for


scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('',scope)
ServerSheet = ""


def housekeeper():
	curdate = datetime.date.today()
	today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
	gc = gspread.authorize(credentials)
	sheet_link = gc.open(ServerSheet).sheet1
	#count rows
	rowCount = sheet_link.row_count
	print("Housekeeping on " + str(rowCount) + " rows on " + today)
	#get all rows and put into memory
	cell_list = sheet_link.range(1,1,rowCount, 7)
	#update our saved version of the data
	for cellIndex in range(1,rowCount):
		# Update in batch
		#if submitted is yes
		rowIndex = cellIndex*7
		if(cell_list[rowIndex+6].value == "yes"):
			#update streak score by one
			newstreakscore = int(cell_list[rowIndex+4].value)+1
			cell_list[rowIndex+4].value = str(newstreakscore)
		#else if streak ends today
		elif(cell_list[rowIndex+5].value == today):
			#set streak to 0
			cell_list[rowIndex+4].value = "0"
		#Set submitted to no
		if(cell_list[rowIndex+6].value != "Submitted Today?"):
			cell_list[rowIndex+6].value = "no"
	#commit all changes to the sheet at once
	sheet_link.update_cells(cell_list)
	print("housekeeping finished")



schedule.every().day.at("23:55").do(housekeeper)

while True:
    schedule.run_pending()
    time.sleep(1)
