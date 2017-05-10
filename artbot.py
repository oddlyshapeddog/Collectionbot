import discord
import logging
import datetime
import simplejson as json
import asyncio
import math
import os
import random
import sys

## sheets
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import zipfile

## modules


spreadsheet_schema = {"Discord Name":1,"Start Date":2,"Level":3,"Currency":4,"Streak":5,"Streak Expires":6,"Submitted Today?":7,"Raffle Prompt Submitted":8,"Week Team":9,"Month Team":10,"Referred By":11,"Prompts Added":12,"Current XP":13}
months = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
streak_roles = ["0+ Streak","5+ Streak","10+ Streak","15+ Streak","20+ Streak","25+ Streak","30+ Streak","60+ Streak","90+ Streak","120+ Streak","150+ Streak","200+ Streak","250+ Streak","300+ Streak","Admins","Raffle","Community Admins","Type !help for info","@everyone","NSFW Artist", "Artists", "Head Admins"]
admins = ["Ciy","DShou","SilviaWindmane","Fluttair|Thunderbolt","Mal Winters","kawaiipony","aFluffyGuy","Skye","~ <3","Scruffasus"]
eight_ball = ["It is certain.","It is decidedly so.","Without a doubt.","Yes, definitely.","You may rely on it.","As I see it, yes.","Most likely.","Outlook good.","Yes.","Signs point to yes.","Reply hazy try again.","Ask again later.","Better not tell you now.","Cannot predict now.","Concentrate and ask again.","Don't count on it.","My reply is no.","My sources say no.","Outlook not so good.","Very doubtful."]

channel_ids = {"class_1":"241060721994104833", "class_2":"236678008562384896"}

### Art bot by Ciy 1.5
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
async def on_reaction_add(reaction, user):
    print("reaction added")
    print(user.name)
    print(reaction.emoji)
    if reaction.emoji.id == "284820985767788554" and user.id != reaction.message.author.id:
        print("test add")
        sheet_link = gc.open(ServerSheet).sheet1
        submitter = reaction.message.author.id
        foundname = False
        foundnameindex = 0
        for sheetname in sheet_link.col_values(14):
            if sheetname == reaction.message.author.id:
                foundname = True
                foundnameindex = sheet_link.col_values(14).index(sheetname)+1
        if foundname:
            adorecount = int(sheet_link.cell(foundnameindex,15).value)
            adorecount = adorecount + 1
            sheet_link.update_cell(foundnameindex,15,adorecount)

@client.event
async def on_reaction_remove(reaction, user):
    print("reaction removed")
    print(user.name)
    print(reaction.emoji)
    if reaction.emoji.id == "284820985767788554" and user.id != reaction.message.author.id:
        print("test remove")
        gc = gspread.authorize(credentials)
        sheet_link = gc.open(ServerSheet).sheet1
        submitter = reaction.message.author.id
        foundname = False
        foundnameindex = 0
        for sheetname in sheet_link.col_values(14):
            if sheetname == reaction.message.author.id:
                foundname = True
                foundnameindex = sheet_link.col_values(14).index(sheetname)+1
        if foundname:
            adorecount = int(sheet_link.cell(foundnameindex,15).value)
            adorecount = adorecount - 1
            sheet_link.update_cell(foundnameindex,15,adorecount)


@client.event
async def on_message(message):
    if message.content.lower().startswith('f') and message.author != message.author.server.me:
        await client.send_message(message.channel, "```Markdown\n {0} has paid their respects.\n```".format(message.author))
    elif message.content.lower().startswith('!submit') and message.author != message.author.server.me:
        if "https://" in message.content.lower() or "http://" in message.content.lower():
            # do linksubmit
            url = message.content.split(" ")
            curdate = datetime.date.today()
            potentialstreak = curdate + datetime.timedelta(days=7)
            today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
            streakdate = "{0}-{1}-{2}".format(potentialstreak.month, potentialstreak.day, potentialstreak.year)
            filepath = os.getcwd()+"/"+today

            gc = gspread.authorize(credentials)
            sheet_link = gc.open(ServerSheet).sheet1

            for sheetname in sheet_link.col_values(14):
                if sheetname == message.author.id:
                    foundname = True
                    foundnameindex = sheet_link.col_values(14).index(sheetname)+1
            if not foundname:
                await client.send_message(message.channel, "```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
            elif sheet_link.cell(foundnameindex, 7).value == "yes":
                await client.send_message(message.channel, "```diff\n- You seem to have submitted something today already!\n```")
            else:
                if url[1].lower().endswith('.png') or url[1].lower().endswith('.jpg') or url[1].lower().endswith('.gif') or url[1].lower().endswith('.jpeg'):
                    if message.channel.id == channel_ids['class_2']:
                        os.system('wget {0} -P {1}'.format(url[1], filepath))
                    newscore = int(sheet_link.cell(foundnameindex, 12).value)+1
                    newcurrency = int(sheet_link.cell(foundnameindex, 4).value)+10
                    current_streak = int(sheet_link.cell(foundnameindex,5).value)
                    current_xp = int(sheet_link.cell(foundnameindex,13).value)
                    xp_gained = 20 + int(math.floor(current_streak/2))
                    current_level = int(sheet_link.cell(foundnameindex,3).value)
                    next_level_required_xp = current_level*10 + 50
                    new_xp_total = current_xp + xp_gained
                    if new_xp_total >= next_level_required_xp:
                        current_level = current_level + 1
                        new_xp_total = new_xp_total - next_level_required_xp
                        sheet_link.update_cell(foundnameindex,3,current_level)
                        sheet_link.update_cell(foundnameindex,13,new_xp_total)
                        await client.send_message(message.channel,"```Markdown\n# @{0} Level Up! You are now level {1}!\n```".format(message.author.name,current_level))
                    else:
                        sheet_link.update_cell(foundnameindex,13,new_xp_total)
                    sheet_link.update_cell(foundnameindex, 12, newscore)
                    sheet_link.update_cell(foundnameindex, 4, newcurrency)
                    sheet_link.update_cell(foundnameindex, 7, "yes")
                    sheet_link.update_cell(foundnameindex, 6, streakdate)
                    await client.send_message(message.channel, "```diff\n+ @{0} Link Submission Successful! Score updated!\n+ {1}xp gained.```".format(message.author.name,xp_gained))
                else:
                    await client.send_message("```diff\n- Not a png, jpg, or gif file\n```")
        else:
            try:
                #normal submit.
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
                for sheetname in sheet_link.col_values(14):
                    if sheetname == message.author.id:
                        foundname = True
                        foundnameindex = sheet_link.col_values(14).index(sheetname)+1
                if not foundname:
                    await client.send_message(message.channel, "```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
                elif sheet_link.cell(foundnameindex, 7).value == "yes":
                    await client.send_message(message.channel, "```diff\n- You seem to have submitted something today already.\n```")
                else:
                    if filename.lower().endswith('.png') or filename.lower().endswith('.jpg') or filename.lower().endswith('.gif') or filename.lower().endswith('.jpeg'):
                        if message.channel.id == channel_ids['class_2']:
                            os.system('wget {0} -P {1}'.format(url, filepath))
                        newscore =  int(sheet_link.cell(foundnameindex, 12).value) + 1
                        newcurrency = int(sheet_link.cell(foundnameindex, 4).value) + 10
                        current_streak = int(sheet_link.cell(foundnameindex,5).value)
                        current_xp = int(sheet_link.cell(foundnameindex,13).value)
                        xp_gained = 20 + int(math.floor(current_streak/2))
                        current_level = int(sheet_link.cell(foundnameindex,3).value)
                        next_level_required_xp = current_level*10 + 50
                        new_xp_total = current_xp + xp_gained
                        if new_xp_total >= next_level_required_xp:
                            current_level = current_level + 1
                            new_xp_total = new_xp_total - next_level_required_xp
                            sheet_link.update_cell(foundnameindex,3,current_level)
                            sheet_link.update_cell(foundnameindex,13,new_xp_total)
                            await client.send_message(message.channel,"```Markdown\n# @{0} Level Up! You are now level {1}!\n```".format(message.author,current_level))
                        else:
                            sheet_link.update_cell(foundnameindex,13,new_xp_total)
                        sheet_link.update_cell(foundnameindex, 12, newscore)
                        sheet_link.update_cell(foundnameindex, 4, newcurrency)
                        sheet_link.update_cell(foundnameindex, 7, "yes")
                        sheet_link.update_cell(foundnameindex, 6, streakdate)
                        await client.send_message(message.channel,"```diff\n+ #{0} Submission Successful! Score updated!\n+ {1}xp gained.```".format(message.author, xp_gained))
                    else:
                        await client.send_message("```diff\n- Not a png, jpg, or gif file.```")
            except:
                pass
    elif message.content.lower().startswith('!register') and message.author != message.author.server.me:
        gc = gspread.authorize(credentials)
        sheet_link = gc.open(ServerSheet).sheet1
        curdate = datetime.date.today()
        today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
        already_registered = False
        for sheetname in sheet_link.col_values(14):
            if sheetname == message.author.id:
                already_registered = True
            else:
                pass
        if not already_registered:
            sheet_link.append_row([message.author.name,today,1,0,0,0,"no","no","none","none",0,0,0,message.author.id,0])
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
        await client.send_message(message.channel,"```Markdown\n# Here's a quick little starter guide for all of you happy little artists wishing to participate.\n# !register will add you to our spreadsheet where we keep track of every submission you make\n# To submit content, drag and drop the file (.png, .gif, .jpg) into discord and add '!submit' as a comment to it.\n# If you'd like to submit via internet link, make sure you right click the image and select 'copy image location' and submit that URL using the !submit command.\n# The !timeleft command will let you know how much longer you have left to submit for the day!\n# To see your current scorecard, type !stats \n# To see your achievement status, type !ach\n# Having trouble figuring out what to draw? try !artblock for a prompt.\n# Want to add a prompt to our pool? use the !idea command to do that!\n``` \n ```diff\n - For those of our older artists, you may access the nsfw channels by typing !nsfwjoin and you can hide those channels by typing !nsfwleave. \n - When submitting nsfwcontent please use the r18 channels respectively!!\n```")
    elif message.content.lower().startswith('!stats') and message.author != message.author.server.me:
        gc = gspread.authorize(credentials)
        sheet_link = gc.open(ServerSheet).sheet1
        rownumber = 0
        foundscore = False
        try:
            rownumber = sheet_link.col_values(14).index(message.author.id)+1
            foundscore = True
        except:
            foundscore = False
#        for sheetname in sheet_link.col_values(1):
#            if sheetname == message.author.name:
#                rownumber = sheet_link.col_values(1).index(sheetname)+1
#                foundscore = True
        if foundscore == True:
            user_name = sheet_link.cell(rownumber, 1).value
            current_score = sheet_link.cell(rownumber, 12).value
            current_xp = int(sheet_link.cell(rownumber, 13).value)
            current_level = int(sheet_link.cell(rownumber, 3).value)
            currency_amount = sheet_link.cell(rownumber, 4).value
            current_streak = int(sheet_link.cell(rownumber, 5).value)
            streak_expiration = sheet_link.cell(rownumber, 6).value.split('-')
            streak_expiration_month = months[int(streak_expiration[0])]
            streak_expiration_day = streak_expiration[1]
            streak_expiration_year = streak_expiration[2]
            submitted_today = sheet_link.cell(rownumber, 7).value
            raffle_completed = sheet_link.cell(rownumber, 8).value
            adores = int(sheet_link.cell(rownumber,15).value)
            ##build XP card here.
            adores_card = "```http\nAdores - {0}\n```".format(adores)
            next_level_required_xp = current_level*10+50
            xp_card = "```Markdown\n# Level: {0}   XP: {1}/{2}\n# ".format(current_level,current_xp,next_level_required_xp)
            percent = current_xp/next_level_required_xp
            blips = 20
            while percent > 0:
                xp_card = xp_card + '●'
                percent = percent - 0.05
                blips = blips - 1
            while blips > 0:
                xp_card = xp_card + '○'
                blips = blips - 1
            xp_card = xp_card + '\n```'
            name_card = "```Python\n@{0} - Score Card:\n```".format(user_name)
            stats_card = "```diff\n+ Total Submissions: {0}\n+ Currency: {1}\n+ Current Streak: {2}\n- Streak Expires: {3} {4}, {5}\n".format(current_score,currency_amount,current_streak,streak_expiration_month,streak_expiration_day,streak_expiration_year)
            if submitted_today == 'yes':
                stats_card = stats_card +"+ You have submitted today.\n"
            else:
                stats_card = stats_card +"- You have not submitted today.\n"
            if raffle_completed == 'yes':
                stats_card = stats_card +"+ You have completed the raffle prompt this month.\n```"
            else:
                stats_card = stats_card +"- You have not completed the raffle prompt this month.\n```"
            score_card = name_card + xp_card + adores_card + stats_card
            await client.send_message(message.channel, score_card)
        else:
            await client.send_message(message.channel, "```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
    elif message.content.lower().startswith('!ach') and message.author != message.author.server.me:
        serv = message.server
        ach_card = "```Python\n @{0} - Achievements\n# Note: unlocked ones are in green and denoted with a '+'.\n```\n```diff\n".format(message.author.name)
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

    elif message.content.lower().startswith('!roleupdate') and (message.author.name in admins):
        gc = gspread.authorize(credentials)
        sheet_link = gc.open(ServerSheet).sheet1
        serv = message.server
        await client.send_message(message.channel, "```Markdown\n# Updating Roles...\n```")
        for id in sheet_link.col_values(14):
            try:
                streak = int(sheet_link.cell(sheet_link.col_values(1).index(id)+1,5).value)
            except:
                streak = -1
            for person in serv.members:
                if id == person.id:
                    cur_member = person
                    print("testing for {0}".format(cur_member))
            if streak >= 300:
                for rank in serv.roles:
                    if rank.name == "300+ Streak":
                        await client.add_roles(cur_member,rank)
            elif streak >= 250 and streak < 300:
                for rank in serv.roles:
                    if rank.name == "250+ Streak":
                        await client.add_roles(cur_member,rank)
            elif streak >= 200 and streak < 250:
                for rank in serv.roles:
                    if rank.name == "200+ Streak":
                        await client.add_roles(cur_member,rank)
            elif streak >= 150 and streak < 200:
                for rank in serv.roles:
                    if rank.name == "150+ Streak":
                        await client.add_roles(cur_member, rank)
            elif streak >= 120 and streak < 150:
                for rank in serv.roles:
                    if rank.name == "120+ Streak":
                        await client.add_roles(cur_member,rank)
            elif streak >= 90 and streak < 120:
                for rank in serv.roles:
                    if rank.name == "90+ Streak":
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
    elif message.content.lower().startswith('!artblock') and message.author != message.author.server.me:
        fp = open('prompts.txt', 'r+')
        await client.send_message(message.channel, "```Markdown\n# {0}\n```".format(random.choice(fp.readlines())))
        fp.close()
    elif message.content.lower().startswith('!idea') and message.author != message.author.server.me:
        gc = gspread.authorize(credentials)
        sheet_link = gc.open(ServerSheet).sheet1
        foundname = False
        serv = message.server
        for sheetname in sheet_link.col_values(14):
            if sheetname == message.author.id:
                foundname = True
                foundnameindex = sheet_link.col_values(14).index(sheetname)+1
        if not foundname:
            await client.send_message(message.channel, "```diff\n- You need to be registered to suggest prompts.\n```")
        else:
            newpromptscore = int(sheet_link.cell(foundnameindex,11).value) + 1
            await client.send_message(message.channel, "```diff\n+ Your prompt suggestion has been recorded!\n```")
            sheet_link.update_cell(foundnameindex,11,newpromptscore)
            if newpromptscore == 20:
                for rank in serv.roles:
                    if rank.name == "Idea Machine":
                        await client.add_roles(message.author,rank)
                        await client.send_message(message.channel, "```Python\n @{0} Achievement Unlocked: Idea Machine\n```".format(message.author.name))
            fp = open('prompts.txt','a+')
            fp.write(message.content[6:]+'\n')
            fp.close()
    elif message.content.lower().startswith('!8ball') and message.author != message.author.server.me:
        fp = open('unlocked8ball.txt', 'r+')
        if(True):
            await client.send_message(message.channel,'`{0} shakes their eight ball..`\n:8ball: `{1}`'.format(message.author.name, random.choice(eight_ball)))
        fp.close()
    elif message.content.lower().startswith('!roll') and message.author != message.author.server.me:
        dice = message.content.split(' ')[1]
        try:
            num_dice =  int(dice.split('d')[0])
            dice_value = int(dice.split('d')[1])
            rolls = []
            for i in range(0,num_dice):
                rolls.append(random.randint(1,dice_value))

            await client.send_message(message.channel, ":game_die: `Your rolls are: {0}`".format(rolls))
        except:
            await client.send_message(message.channel, "```diff\n- Invalid dice arguments\n```")
    elif message.content.lower().startswith('!award') and message.author.name in admins:
        #awards a command, such as 8ball, to a member.
        parse = message.content.split(" ")
        members_awarded = ""
        reward = parse[1]
        if reward == "8ball":
            fp = open('unlocked8ball.txt','a+')
            for receiver in message.mentions:
                fp.write(receiver.name+"\n")
                members_awarded = members_awarded +" "+receiver.name
            fp.close()
        await client.send_message(message.channel, "```Markdown\n# !{0} awarded to {1}```".format(reward, members_awarded))
    elif message.content.lower().startswith('!grant') and message.author.name in admins:
        #grants an achievement.
        parse = message.content.split("-")
        achievement_receivers = ""
        achievement_name = parse[1]
        serv = message.server
        for rank in serv.roles:
            if rank.name.lower() == achievement_name.lower():
                for person in message.mentions:
                    await client.add_roles(person, rank)
                    achievement_receivers = achievement_receivers + " " +person.name
        await client.send_message(message.channel, "```Markdown\n# {0} awarded to {1}\n```".format(achievement_name,achievement_receivers))
    elif message.content.lower().startswith('!vacation') and message.author != message.author.server.me:
        gc = gspread.authorize(credentials)
        sheet_link = gc.open(ServerSheet).sheet1
        working_index = 0
        price = 100
        curdate = datetime.date.today()
        potentialstreak = curdate + datetime.timedelta(days=30)
        today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
        streakdate = "{0}-{1}-{2}".format(potentialstreak.month, potentialstreak.day, potentialstreak.year)
        def check(msg):
            return msg.content.startswith('!')
        try:
            working_index = sheet_link.col_values(14).index(message.author.id)+1
            buyer_amount = int(sheet_link.cell(working_index,4).value)
            if buyer_amount >= price:
                await client.send_message(message.channel, "```Python\n@{0}\n```\n```Markdown\n# You're about to purchase a 30 day vacation to protect your streak for 100 credits. (any new submissions will reset this to 7 days). To confirm and buy type !yes, to decline, type !no.\n```".format(message.author.name))
                confirm = await client.wait_for_message(author=message.author,check=check)
                if confirm.content.lower().startswith('!yes'):
                    new_buyer_balance = buyer_amount - price
                    sheet_link.update_cell(working_index, 4, new_buyer_balance)
                    sheet_link.update_cell(working_index, 6, streakdate)
                    await client.send_message(message.channel, "```diff\n+ Vacation purchased, your streak now expires on {0} {1}, {2}. Bon Voyage!\n```".format(months[potentialstreak.month],potentialstreak.day,potentialstreak.year))
                elif confirm.content.lower().startswith('!no'):
                    await client.send_message(message.channel, "```Markdown\n# Transaction cancelled.\n```")
            else:
                await client.send_message(message.channel, "```Markdown\n- Not enough credits. {0} needed, you have {1}```".format())
        except:
            await client.send_message(message.channel, "```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
    elif message.content.lower().startswith('!markraffle') and message.author.name in admins:
        try:
            gc = gspread.authorize(credentials)
            receiver = message.mentions[0]
            sheet_link = gc.open(ServerSheet).sheet1
            working_row = sheet_link.col_values(14).index(receiver.id)+1
            sheet_link.update_cell(working_row,8,"yes")
            await client.send_message(message.channel,"```diff\n+ Raffle submission marked for: {0}\n```".format(receiver.name))
        except:
            await client.send_message(message.channel,"```diff\n- Something went wrong.\n```")
    elif message.content.lower().startswith('!buy') and message.author != message.author.server.me:
        #under construction.
        parse = message.content.split(" ")
        item_name = parse[1].lower()
        price = 0
        gc = gspread.authorize(credentials)
        sheet_link = gc.open(ServerSheet).sheet1
        foundname = False
        serv = message.server
        for sheetname in sheet_link.col_values(14):
            if sheetname == message.author.id:
                foundname = True
                foundnameindex = sheet_link.col_values(14).index(sheetname)+1
        if not foundname:
            await client.send_message(message.channel,"```diff\n- You were not found in sheet, make sure to register before you use the shop.\n```")
        else:
            buyer_currency = int(sheet_link.cell(foundnameindex,4).value)
            fp = open('shop.txt','r+')
            items_list = fp.readlines()
            for items in items_list:
                if items.lower().startswith(item_name):
                    price = int(items.split("-")[1])
            fp.close()
            if price > buyer_currency:
                await client.send_message(message.channel,"```diff\n- Not enough credits. {0} needed, you have {1}\n```".format(price,buyer_currency))
            else:
                new_currency = buyer_currency - price
                sheet_link.update_cell(foundnameindex,4,new_currency)
                await client.send_message(message.channel,"```diff\n+ Successfully payed {0} credits for {1}. Your total balance is now: {2}\n```".format(price,item_name,new_currency))


client.run(botEmail, botPassword)
