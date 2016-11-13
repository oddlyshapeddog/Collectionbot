import discord
import logging
import datetime
import simplejson as json
import asyncio
import math
import os
import sys

## sheets
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import zipfile

## modules


spreadsheet_schema = {"Discord Name":1,"Start Date":2,"Score":3,"Currency":4,"Streak":5,"Streak Expires":6,"Submitted Today?":7,"Raffle Submission?":8}
months = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
streak_roles = ["0+ Streak","5+ Streak","10+ Streak","15+ Streak","20+ Streak","25+ Streak","30+ Streak","60+ Streak","100+ Streak","Admins","Community Admins","Type !help for info","@everyone","NSFW Artist", "Artists"]


### Art bot by Ciy 1.3.1
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
    if message.content.lower().startswith('!hi') and message.author != message.author.server.me:
        await client.send_message(message.channel, "```Markdown\nWhy, hello there!\n```")
    elif message.content.lower().startswith('!submit') and message.author != message.author.server.me:
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
                await client.send_message(message.channel, "```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
            elif sheet_link.cell(foundnameindex, 7).value == "yes":
                await client.send_message(message.channel, "```diff\n- You seem to have submitted something today already.\n```")
            else:
                if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.gif') or url[1].endswith('.PNG') or url[1].endswith('.JPG') or url[1].endswith('.GIF'):
                    os.system('wget {0} -P {1}'.format(url, filepath))
                    newscore =  int(sheet_link.cell(foundnameindex, 3).value) + 1
                    newcurrency = int(sheet_link.cell(foundnameindex, 4).value) + 10
                    sheet_link.update_cell(foundnameindex, 3, newscore)
                    sheet_link.update_cell(foundnameindex, 4, newcurrency)
                    sheet_link.update_cell(foundnameindex, 7, "yes")
                    sheet_link.update_cell(foundnameindex, 6, streakdate)
                    await client.send_message(message.channel,"```diff\n+ Submission Successful! Score updated!\n```")
                else:
                    await client.send_message("```diff\n- Not a png, jpg, or gif file.```")
        except:
            pass
    elif message.content.lower().startswith('!linksubmit') and message.author != message.author.server.me:
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
            await client.send_message(message.channel, "```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
        elif sheet_link.cell(foundnameindex, 7).value == "yes":
            await client.send_message(message.channel, "```diff\n- You seem to have submitted something today already!\n```")
        else:
            if url[1].endswith('.png') or url[1].endswith('.jpg') or url[1].endswith('.gif') or url[1].endswith('.PNG') or url[1].endswith('.JPG') or url[1].endswith('.GIF'):
                os.system('wget {0} -P {1}'.format(url[1], filepath))
                newscore = int(sheet_link.cell(foundnameindex, 3).value)+1
                newcurrency = int(sheet_link.cell(foundnameindex, 4).value)+10
                sheet_link.update_cell(foundnameindex, 3, newscore)
                sheet_link.update_cell(foundnameindex, 4, newcurrency)
                sheet_link.update_cell(foundnameindex, 7, "yes")
                sheet_link.update_cell(foundnameindex, 6, streakdate)
                await client.send_message(message.channel, "```diff\n+ Link Submission Successful! Score updated!\n```")
            else:
                await client.send_message("```diff\n- Not a png, jpg, or gif file\n```")

    elif message.content.lower().startswith('!collect') and message.author != message.author.server.me:
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

    elif message.content.lower().startswith('!register') and message.author != message.author.server.me:
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
            sheet_link.append_row([message.author.name,today,0,0,0,0,"no","no"])
            serv = message.server
            for rank in serv.roles:
                if rank.name == "0+ Streak":
                    await client.add_roles(message.author, rank)
            for rank in serv.roles:
                if rank.name == "Artists":
                    await client.add_roles(message.author, rank)
            await client.send_message(message.channel, "```diff\n+ Successfully registered!\n```")
        else:
            await client.send_message(message.channel, "```Markdown\n# You're already registered!\n```")

    elif message.content.lower().startswith('!help') and message.author != message.author.server.me:
        await client.send_message(message.channel,"```Markdown\n# Here's a quick little starter guide for all of you happy little artists wishing to participate.\n# !register will add you to our spreadsheet where we keep track of every submission you make\n# To submit content, drag and drop the file (.png, .gif, .jpg) into discord and add '!submit' as a comment to it.\n# If you'd like to submit via internet link, make sure you right click the image and select 'copy image location' and submit that URL using the !linksubmit command\n# The !timeleft command will let you know how much longer you have left to submit for the day!\n# To see your current scorecard, type !stats \n# To see your achievement status, type !ach\n``` \n ```diff\n - For those of our older artists, you may access the nsfw channels by typing !nsfwjoin and you can hide those channels by typing !nsfwleave. \n - When submitting nsfwcontent please use !nsfwsubmit and !nsfwlinksubmit respectively!!\n```")
    elif message.content.lower().startswith('!stats') and message.author != message.author.server.me:
        gc = gspread.authorize(credentials)
        sheet_link = gc.open(ServerSheet).sheet1
        rownumber = 0
        foundscore = False
        for sheetname in sheet_link.col_values(1):
            if sheetname == message.author.name:
                rownumber = sheet_link.col_values(1).index(sheetname)+1
                foundscore = True
        if foundscore == True:
            user_name = sheet_link.cell(rownumber, 1).value
            current_score = sheet_link.cell(rownumber, 3).value
            currency_amount = sheet_link.cell(rownumber, 4).value
            current_streak = sheet_link.cell(rownumber, 5).value
            streak_expiration = sheet_link.cell(rownumber, 6).value.split('-')
            streak_expiration_month = months[int(streak_expiration[0])]
            streak_expiration_day = streak_expiration[1]
            streak_expiration_year = streak_expiration[2]
            submitted_today = sheet_link.cell(rownumber, 7).value
            raffle_completed = sheet_link.cell(rownumber, 8).value
            stats_card = "```Python\n @{0} - Score Card:\n```\n```diff\n+ Current Score: {1}\n+ Currency: {2}\n+ Current Streak: {3}\n- Streak Expires: {4} {5}, {6}\n".format(user_name,current_score,currency_amount,current_streak,streak_expiration_month,streak_expiration_day,streak_expiration_year)
            if submitted_today == 'yes':
                stats_card = stats_card +"+ You have submitted today.\n"
            else:
                stats_card = stats_card +"- You have not submitted today.\n"
            if raffle_completed == 'yes':
                stats_card = stats_card +"+ You have completed the raffle prompt this month.\n```"
            else:
                stats_card = stats_card +"- You have not completed the raffle prompt this month.\n```"
            await client.send_message(message.channel, stats_card)
        else:
            await client.send_message(message.channel, "```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
    elif message.content.lower().startswith('!ach') and message.author != message.author.server.me:
        serv = message.server
        ach_card = "```Python\n @{0} - Achievements\n# Note: unlocked ones are in green.\n```\n```diff\n".format(message.author.name)
        for rank in serv.roles:
            if rank in message.author.roles and rank.name not in streak_roles:
                ach_card = ach_card + '+ {0}\n'.format(rank.name)
            if rank not in message.author.roles and rank.name not in streak_roles:
                ach_card = ach_card + '# {0}\n'.format(rank.name)
        ach_card = ach_card + "```"
        await client.send_message(message.channel, ach_card)
    elif message.content.lower().startswith('!timeleft') and message.author != message.author.server.me:
        now = datetime.datetime.now()
        end = datetime.datetime(now.year, now.month, now.day, hour=23,minute=55,second=0,microsecond=0)
        difference = end - now
        seconds_to_work = difference.seconds
        difference_hours = math.floor(seconds_to_work / 3600)
        seconds_to_work = seconds_to_work - 3600*difference_hours
        difference_minutes = math.floor(seconds_to_work / 60)
        seconds_to_work = seconds_to_work - 60*difference_minutes
        if difference_hours < 5:
            await client.send_message(message.channel, '```diff\n- {0} hours, {1} minutes, and {2} seconds left to submit for today!\n```'.format(difference_hours,difference_minutes,seconds_to_work))
        else:
            await client.send_message(message.channel, '```diff\n+ {0} hours, {1} minutes, and {2} seconds left to submit for today!\n```'.format(difference_hours,difference_minutes,seconds_to_work))

    elif message.content.lower().startswith('!roleupdate') and (message.author.name == 'Ciy' or message.author.name == 'DShou' or message.author.name == 'SilviaWindmane'):
        gc = gspread.authorize(credentials)
        sheet_link = gc.open(ServerSheet).sheet1
        serv = message.server
        await client.send_message(message.channel, "```Markdown\n#Updating Roles...\n```")
        for sheetname in sheet_link.col_values(1):
            try:
                streak = int(sheet_link.cell(sheet_link.col_values(1).index(sheetname)+1,5).value)
            except:
                streak = -1
            for person in serv.members:
                if sheetname == person.name:
                    cur_member = person
                    print("testing for {0}".format(cur_member))
            if streak >= 100:
                for rank in serv.roles:
                    if rank.name == "100+ Streak":
                        await client.add_roles(cur_member,rank)
            elif streak >= 60 and streak < 100:
                for rank in serv.roles:
                    if rank.name == "60+ Streak":
                        await client.add_roles(cur_member,rank)
            elif streak >= 30 and streak < 60:
                for rank in serv.roles:
                    if rank.name == "30+ Streak":
                        await client.add_roles(cur_member,rank)
            elif streak >= 25 and streak < 30:
                for rank in serv.roles:
                    if rank.name == "25+ Streak":
                        await client.add_roles(cur_member,rank)
            elif streak >=20 and streak < 25:
                for rank in serv.roles:
                    if rank.name == "20+ Streak":
                        await client.add_roles(cur_member,rank)
            elif streak >=15 and streak < 20:
                for rank in serv.roles:
                    if rank.name == "15+ Streak":
                        await client.add_roles(cur_member,rank)
            elif streak >=10 and streak < 15:
                for rank in serv.roles:
                    if rank.name == "10+ Streak":
                        await client.add_roles(cur_member,rank)
            elif streak >=5 and streak < 10:
                for rank in serv.roles:
                    if rank.name == "5+ Streak":
                        await client.add_roles(cur_member,rank)
        await client.send_message(message.channel, "```diff\n+ Updating roles was a happy little success!\n```")
    elif message.content.lower().startswith('!nsfwjoin') and message.author != message.author.server.me:
        serv = message.author.server
        for rank in serv.roles:
            if rank.name == "NSFW Artist":
                await client.add_roles(message.author,rank)
                await client.send_message(message.channel, "```Markdown\nYou should now have access to the NSFW channels, Oh my!```")
    elif message.content.lower().startswith('!nsfwleave') and message.author != message.author.server.me:
        serv = message.author.server
        for rank in serv.roles:
            if rank.name == "NSFW Artist":
                await client.remove_roles(message.author, rank)
                await client.send_message(message.channel, "```Markdown\nNSFW channels have been hidden.\n```")
    elif message.content.lower().startswith('!nsfwlinksubmit') and message.author != message.author.server.me:
        url = message.content.split(" ")
        curdate = datetime.date.today()
        potentialstreak = curdate + datetime.timedelta(days=7)
        today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
        streakdate = "{0}-{1}-{2}".format(potentialstreak.month, potentialstreak.day, potentialstreak.year)
        filepath = os.getcwd()+"/"+today

        gc = gspread.authorize(credentials)
        sheet_link = gc.open(ServerSheet).sheet1

        foundname = False
        for sheetname in sheet_link.col_values(1):
            if sheetname == message.author.name:
                foundname = True
                foundnameindex = sheet_link.col_values(1).index(sheetname)+1
        if not foundname:
            await client.send_message(message.channel, "```diff\n - I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
        elif sheet_link.cell(foundnameindex, 7).value == "yes":
            await client.send_message(message.channel, "```diff\n - You seem to have submitted something today already!\n```")
        else:
            if url[1].endswith('.png') or url[1].endswith('.jpg') or url[1].endswith('.gif') or url[1].endswith('.PNG') or url[1].endswith('.JPG') or url[1].endswith('.GIF'):
                newscore = int(sheet_link.cell(foundnameindex, 3).value)+1
                newcurrency = int(sheet_link.cell(foundnameindex, 4).value)+10
                sheet_link.update_cell(foundnameindex, 3, newscore)
                sheet_link.update_cell(foundnameindex, 4, newcurrency)
                sheet_link.update_cell(foundnameindex, 7, "yes")
                sheet_link.update_cell(foundnameindex, 6, streakdate)
                await client.send_message(message.channel, "```diff\n+Link Submission Successful! Score updated!\n```")
            else:
                await client.send_message("```diff\n- Not a png, jpg, or gif file\n```")
    elif message.content.lower().startswith('!nsfwsubmit') and message.author != message.author.server.me:
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
            foundname = False
            for sheetname in sheet_link.col_values(1):
                if sheetname == message.author.name:
                    foundname = True
                    foundnameindex = sheet_link.col_values(1).index(sheetname)+1
            if not foundname:
                await client.send_message(message.channel, "```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
            elif sheet_link.cell(foundnameindex, 7).value == "yes":
                await client.send_message(message.channel, "```diff\n- You seem to have submitted something today already!\n```")
            else:
                if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.gif') or url[1].endswith('.PNG') or url[1].endswith('.JPG') or url[1].endswith('.GIF'):
                    newscore =  int(sheet_link.cell(foundnameindex, 3).value) + 1
                    newcurrency = int(sheet_link.cell(foundnameindex, 4).value) + 10
                    sheet_link.update_cell(foundnameindex, 3, newscore)
                    sheet_link.update_cell(foundnameindex, 4, newcurrency)
                    sheet_link.update_cell(foundnameindex, 7, "yes")
                    sheet_link.update_cell(foundnameindex, 6, streakdate)
                    await client.send_message(message.channel,"```diff\n+ Submission Successful! Score updated!\n```")
                else:
                    await client.send_message("```diff\n- Not a png, jpg, or gif file.\n```")
        except:
            pass

client.run(botEmail, botPassword)
