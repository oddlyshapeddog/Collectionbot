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
            today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
            jsonstr = json.dumps(message.attachments[0])
            jsondict = json.loads(jsonstr)
            filepath = os.getcwd()+"/"+today

            url = jsondict['url']
            filename = jsondict['filename']
            if filename.endswith('.png') or filename.endswith('.jpg'):
                os.system('wget {0} -P {1}'.format(url, filepath))
                await client.send_message(message.channel,"Submission Successful!")
            else:
                await client.send_message("Not a png or jpg file.")
        except:
            pass


    elif message.content.startswith('!collect') and message.author != message.author.server.me:
        curdate = datetime.date.today()
        today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
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
        temp_link = gc.open(ServerSheet).sheet1
        curdate = datetime.date.today()
        today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
        already_registered = False
        for sheetname in sheet_link.col_values(1):
            if sheetname == message.author.name:
                already_registered = True
            else:
                pass
        if not already_registered:
            temp_link.append_row([message.author.name,today,0,0,0,0])
            await client.send_message(message.channel, "Successfully registered!")
        else:
            await client.send_message(message.channel, "You're already registered!")


client.run(botEmail, botPassword)
