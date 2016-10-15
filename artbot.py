import discord
import logging
import datetime
import simplejson as json
import asyncio
import os
import sys

## sheets
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import zipfile

## modules


spreadsheet_schema = {"Discord Name":1,"Start Date":2,"Score":3,"Currency":4,"Streak":5,"Streak Expires":6}


### Art bot by Ciy 1.0
### Simple bot for Discord designed to manage image collection.

logging.basicConfig(level = logging.INFO)

botEmail =  ""
botPassword = ""
ServerSheet = ""

## global googlesheets setup
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('',scope)


gc = gspread.authorize(credentials)
sheet_link = gc.open(ServerSheet).sheet1

client = discord.Client()

@client.event
async def on_ready():
    print('Bot Online.')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.content.startswith('!hi') and message.author != message.author.server.me:
        await client.send_message(message.channel, "Why, hello there!")
    elif message.content.startswith('!submit') and message.author != message.author.server.me:
        try:
            curdate = datetime.date.today()
            potentialstreak = curdate + datetime.timedelta(days=7)
            today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
            streakdate = "{0}-{1}-{2}".format(potentialstreak.month, potentialstreak.day, potentialstreak.year)
            jsonstr = json.dumps(message.attachments[0])
            jsondict = json.loads(jsonstr)
            filepath = os.getcwd()+"/"+today

            url = jsondict['url']
            filename = jsondict['filename']
            gc = gspread.authorize(credentials)
            sheet_link = gc.open(ServerSheet).sheet1
            foundscore = False
            for sheetname in sheet_link.col_values(1):
                if sheetname == message.author.name:
                    foundname = True
                    foundnameindex = sheet_link.col_values(1).index(sheetname)+1
            if not foundname:
                await client.send_message(message.channel, "I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.")
            elif sheet_link.cell(foundnameindex, 7).value == "yes":
                await client.send_message(message.channel, "You seem to have submitted something today already!")
            else:
                if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.gif'):
                    os.system('wget {0} -P {1}'.format(url, filepath))
                    newscore =  int(sheet_link.cell(foundnameindex, 3).value) + 1
                    sheet_link.update_cell(foundnameindex, 3, newscore)
                    sheet_link.update_cell(foundnameindex, 7, "yes")
                    sheet_link.update_cell(foundnameindex, 6, streakdate)
                    await client.send_message(message.channel,"Submission Successful! Score updated!")
                else:
                    await client.send_message("Not a png, jpg, or gif file.")
        except:
            pass
    elif message.content.startswith('!linksubmit') and message.author != message.author.server.me:
        url = message.content.split(" ")
        curdate = datetime.date.today()
        potentialstreak = curdate + datetime.timedelta(days=7)
        today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
        streakdate = "{0}-{1}-{2}".format(potentialstreak.month, potentialstreak.day, potentialstreak.year)
        filepath = os.getcwd()+"/"+today

        gc = gspread.authorize(credentials)
        sheet_link = gc.open(ServerSheet).sheet1

        for sheetname in sheet_link.col_values(1):
            if sheetname == message.author.name:
                foundname = True
                foundnameindex = sheet_link.col_values(1).index(sheetname)+1
        if not foundname:
            await client.send_message(message.channel, "I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.")
        elif sheet_link.cell(foundnameindex, 7).value == "yes":
            await client.send_message(message.channel, "You seem to have submitted something today already!")
        else:
            if url[1].endswith('.png') or url[1].endswith('.jpg') or url[1].endswith('.gif'):
                os.system('wget {0} -P {1}'.format(url[1], filepath))
                newscore = int(sheet_link.cell(foundnameindex, 3).value)+1
                sheet_link.update_cell(foundnameindex, 3, newscore)
                sheet_link.update_cell(foundnameindex, 7, "yes")
                sheet_link.update_cell(foundnameindex, 6, streakdate)
                await client.send_message(message.channel, "Link Submission Successful! Score updated!")
            else:
                await client.send_message("Not a png, jpg, or gif file")

    elif message.content.startswith('!collect') and message.author != message.author.server.me:
        collecttime = message.content.split(" ")
        today = collecttime[1]
        #curdate = datetime.date.today()
        #today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
        zf = zipfile.ZipFile("%s.zip" %today, "w", zipfile.ZIP_DEFLATED)
        src = os.path.abspath(today)
        for dirname, subdirs, files in os.walk(src):
            for filename in files:
                abs_filepath = os.path.abspath(os.path.join(dirname, filename))
                arcname = abs_filepath[len(src)+1:]
                zf.write(abs_filepath, arcname)
        zf.close()
        await client.send_file(message.channel, os.getcwd()+"/"+today+".zip")

    elif message.content.startswith('!register') and message.author != message.author.server.me:
        gc = gspread.authorize(credentials)
        sheet_link = gc.open(ServerSheet).sheet1
        curdate = datetime.date.today()
        today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
        already_registered = False
        for sheetname in sheet_link.col_values(1):
            if sheetname == message.author.name:
                already_registered = True
            else:
                pass
        if not already_registered:
            sheet_link.append_row([message.author.name,today,0,0,0,0,"no"])
            await client.send_message(message.channel, "Successfully registered!")
        else:
            await client.send_message(message.channel, "You're already registered!")

    elif message.content.startswith('!help') and message.author != message.author.server.me:
        await client.send_message(message.channel,"Here's a quick little starter guide for all of you happy little artists wishing to participate.\n !register will add you to our spreadsheet where we keep track of every submission you make\n To submit content, drag and drop the file (.png, .gif, .jpg) into discord and add '!submit' as a comment to it.\n If you'd like to submit via internet link, make sure you right click the image and select 'copy image location' and submit that URL using the !linksubmit command ")
    elif message.content.startswith('!score') and message.author != message.author.server.me:
        gc = gspread.authorize(credentials)
        sheet_link = gc.open(ServerSheet).sheet1
        foundscore = False
        for sheetname in sheet_link.col_values(1):
            if sheetname == message.author.name:
                await client.send_message(message.channel,"You have {0} points".format(sheet_link.cell(sheet_link.col_values(1).index(sheetname)+1, 3).value))
                foundscore = True
        if not foundscore:
            await client.send_message(message.channel, "I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.")

client.run(botEmail, botPassword)
