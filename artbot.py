import discord
import logging
import datetime
import simplejson as json
import asyncio
import os
import sys

import zipfile

## modules


### Art bot by Ciy 1.0
### Simple bot for Discord designed to manage image collection.

logging.basicConfig(level = logging.INFO)

botEmail =  ""
botPassword = ""
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
                arcname = absname[len(src)+1:]
                zf.write(abs_filepath, arcname)
        zf.close()
        await client.send_file(message.channel, os.getcwd()+"/"+today+".zip")


client.run(botEmail, botPassword)
