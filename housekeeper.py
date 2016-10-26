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
    for sheetname in sheet_link.col_values(1):
        workingrow = sheet_link.col_values(1).index(sheetname)+1
        if sheet_link.cell(workingrow,7).value == "yes":
            newstreakscore = int(sheet_link.cell(workingrow,5).value)+1
            sheet_link.update_cell(workingrow, 5, newstreakscore)
        elif sheet_link.cell(workingrow,6).value == today:
            sheet_link.update_cell(workingrow,5,0)
        if sheet_link.cell(workingrow, 7).value != "Submitted Today?":
            sheet_link.update_cell(workingrow, 7, "no")



schedule.every().day.at("23:55").do(housekeeper)

while True:
    schedule.run_pending()
    time.sleep(1)
