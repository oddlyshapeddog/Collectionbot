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
            today = "{0}-{1}".format(date.month, date.year)
            jsonstr = json.dumps(message.attachments[0])
            jsondict = json.loads(jsonstr)
            filepath = os.getcwd()+today

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
        today = "{0}-{1}".format(date.month, date.year)

        for item in os.listdir(os.getcwd()+today):
            with ZipFile(today+".zip", 'w') as comp:
                comp.write(item)
        ZipFile.close()
        await client.send_file(message.channel, os.getcwd()+today+".zip")


client.run(botEmail, botPassword)
