import discord
import logging
import datetime
import simplejson as json
import asyncio
import math
import os
import random
import sys
import pytz

#SQLalchemy stuff
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
from datetime import date, timedelta, time, datetime
#declaration for User class is in here
from create_databases import Base, User

#scheduling stuff
from pytz import utc
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import zipfile

##Schedluing for housekeeping
scheduler = AsyncIOScheduler(timezone=utc)

#Bind the data type to the engine and connect to our SQL database
engine = create_engine('sqlite:///TAPE_Database.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
#create session
session = DBSession() #session.commit() to store data, and session.rollback() to discard changes

spreadsheet_schema = {"Discord Name":1,"Start Date":2,"Level":3,"Currency":4,"Streak":5,"Streak Expires":6,"Submitted Today?":7,"Raffle Prompt Submitted":8,"Week Team":9,"Month Team":10,"Referred By":11,"Prompts Added":12,"Current XP":13}
months = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
streak_roles = ["0+ Streak","5+ Streak","10+ Streak","15+ Streak","20+ Streak","25+ Streak","30+ Streak","60+ Streak","90+ Streak","120+ Streak","150+ Streak","200+ Streak","250+ Streak","300+ Streak","Admins","Raffle","Community Admins","Type !help for info","@everyone","NSFW Artist", "Artists", "Head Admins"]
admins = ["Ciy","DShou","SilviaWindmane","Fluttair|Thunderbolt","Mal Winters","kawaiipony","aFluffyGuy","Skye","~ <3","Scruffasus","Whatsapokemon"]
eight_ball = ["It is certain.","It is decidedly so.","Without a doubt.","Yes, definitely.","You may rely on it.","As I see it, yes.","Most likely.","Outlook good.","Yes.","Signs point to yes.","Reply hazy try again.","Ask again later.","Better not tell you now.","Cannot predict now.","Concentrate and ask again.","Don't count on it.","My reply is no.","My sources say no.","Outlook not so good.","Very doubtful."]

channel_ids = {"class_1":"241060721994104833", "class_2":"236678008562384896"}
tapeServer = 'no server'
botChannel = 'no channel'

### Art bot by Whatsapokemon and Ciy 2.0
### Simple bot for Discord designed to manage image collection.

logging.basicConfig(level = logging.INFO)
botEmail =  ""
botPassword = ""

client = discord.Client()

@client.event
async def on_ready():
    global tapeServer
    global botChannel
    print('Bot Online.')
    print(client.user.name)
    print(client.user.id)
    print('------')
    #Store the server and the bot command channel
    for s in client.servers:
        #if s.name == 'WhatsaTestServer':
        if s.name == 'The Art Plaza Extravaganza':
            tapeServer = s
    for c in tapeServer.channels:
        if c.name == 'bot-channel':
        #if c.name == 'botspam':
            botChannel = c


@client.event
async def on_reaction_add(reaction, user):
    userToUpdate = reaction.message.author.id
    #if the submission is a proxy submission
    if(reaction.message.content.lower().startswith('!proxysubmit')):
        #Change attribution of proxy submits to the mentioned user
        userToUpdate = reaction.message.mentions[0].id
    try:
        if type(reaction.emoji) is discord.Emoji:
            if reaction.emoji.id == "284820985767788554" and user.id != userToUpdate and reaction.message.content.startswith("!submit"):
                print("reaction added " + user.name + " " + str(reaction.emoji))
                #find user in database using id
                db_user = session.query(User).filter(User.id == userToUpdate).one()
                #increase adores by 1
                db_user.adores = db_user.adores+1
                #commit session
                session.commit()
    except:
        print("Adding reaction broke for user " + userToUpdate)

@client.event
async def on_reaction_remove(reaction, user):
    userToUpdate = reaction.message.author.id
    #if the submission is a proxy submission
    if(reaction.message.content.lower().startswith('!proxysubmit')):
        #Change attribution of proxy submits to the mentioned user
        userToUpdate = reaction.message.mentions[0].id
    try:
        if type(reaction.emoji) is discord.Emoji:
            if reaction.emoji.id == "284820985767788554" and user.id != userToUpdate and reaction.message.content.startswith("!submit"):
                print("reaction removed " + user.name + " " + str(reaction.emoji))
                #find user in database using id
                db_user = session.query(User).filter(User.id == userToUpdate).one()
                #increase adores by 1
                db_user.adores = db_user.adores-1
                #commit session
                session.commit()
    except:
        print("Adding reaction broke for user " + userToUpdate)


@client.event
async def on_message(message):
    if message.content.lower() == "f" and message.author != message.author.server.me and message.channel.id == "279098440820981760":
        await client.send_message(message.channel, "```Markdown\n {0} has paid their respects.\n```".format(message.author))
    elif message.content.lower().startswith('!submit') and message.author != message.author.server.me:
        if "https://" in message.content.lower() or "http://" in message.content.lower():
            # do linksubmit
            await linkSubmit(message, message.author)
        else:
            try:
                #normal submit.
                await normalSubmit(message, message.author)
            except:
                pass
    elif message.content.lower().startswith('!register') and message.author != message.author.server.me:
        curdate = datetime.utcnow()
        today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
        already_registered = False
        #try to find user in database using id
        try:
            db_user = session.query(User).filter(User.id == message.author.id).one()
            already_registered = True
        except sqlalchemy.orm.exc.NoResultFound:
            print('No user found, this is fine, creating new user now.')
        except sqlalchemy.orm.exc.MultipleResultsFound:
            print('Multiple users found, something is really broken!')

        #add a new user if there's no registered user
        if not already_registered:
            #create new user object
            new_user = User(name=message.author.name, level=1, id=message.author.id, startdate=curdate, currency=0, streak=0, expiry=curdate, submitted=0, raffle=0, promptsadded=0, totalsubmissions=0, currentxp=0, adores=0)
            #add to session
            session.add(new_user)
            #give relevant roles
            serv = message.server
            for rank in serv.roles:
                if rank.name == "0+ Streak":
                    await client.add_roles(message.author, rank)
            for rank in serv.roles:
                if rank.name == "Artists":
                    await client.add_roles(message.author, rank)
            #commit session
            session.commit()
            await client.send_message(message.channel, "```diff\n+ Successfully registered!\n```")
        else:
            await client.send_message(message.channel, "```Markdown\n# You're already registered!\n```")

    elif message.content.lower().startswith('!help') and message.author != message.author.server.me:
        await client.send_message(message.channel,"```Markdown\n# Here's a quick little starter guide for all of you happy little artists wishing to participate.\n# !register will add you to our spreadsheet where we keep track of every submission you make\n# To submit content, drag and drop the file (.png, .gif, .jpg) into discord and add '!submit' as a comment to it.\n# If you'd like to submit via internet link, make sure you right click the image and select 'copy image location' and submit that URL using the !submit command.\n# The !timeleft command will let you know how much longer you have left to submit for the day!\n# To see your current scorecard, type !stats \n# To see your achievement status, type !ach\n# Having trouble figuring out what to draw? try !artblock for a prompt.\n# Want to add a prompt to our pool? use the !idea command to do that!\n``` \n ```diff\n - For those of our older artists, you may access the nsfw channels by typing !nsfwjoin and you can hide those channels by typing !nsfwleave. \n - When submitting nsfwcontent please use the r18 channels respectively!!\n```")
    elif message.content.lower().startswith('!stats') and message.author != message.author.server.me:
        foundscore = False
        #try to find user in database using id
        try:
            db_user = session.query(User).filter(User.id == message.author.id).one()
            foundscore = True
        except sqlalchemy.orm.exc.NoResultFound:
            print('No user found, probably not registered')
        except sqlalchemy.orm.exc.MultipleResultsFound:
            print('Multiple users found, something is really broken!')


        #if we found the user in our spreadsheet
        if foundscore == True:
            #then extract individual stats for simplicity
            user_name = db_user.name
            current_score = db_user.totalsubmissions
            current_xp = db_user.currentxp
            current_level = db_user.level
            currency_amount = db_user.currency
            current_streak = db_user.streak
            stats_embed = discord.Embed(title=message.author.name, description="Score Card", color=0x33cccc)
            stats_embed.set_thumbnail(url=message.author.avatar_url)
            stats_embed.add_field(name="Total Submissions", value=db_user.totalsubmissions,inline=True)
            stats_embed.add_field(name="Current Streak",value=db_user.streak,inline=True)
            stats_embed.add_field(name="Currency", value=db_user.currency,inline=True)

            #get the date of the expiry
            #Streak expires at 7am UTC on that day
            streak_expiration = db_user.expiry
            streak_expiration = datetime.combine(streak_expiration, time(7,0))
            #and get now in UTC
            now = datetime.utcnow()
            #then compare the difference between those times
            delta = streak_expiration - now
            #get time difference
            d_days = delta.days
            delta = delta.seconds
            d_sec = int(delta % 60)
            delta = delta - d_sec
            d_min = int((delta % 3600) / 60)
            delta = delta - (d_min*60)
            d_hour = int(delta / 3600)

            #streak_expiration_month = months[int(streak_expiration[1])]
            #streak_expiration_day = streak_expiration[0]
            #streak_expiration_year = streak_expiration[2]
            submitted_today =  'yes' if db_user.submitted == 1 else 'no'
            raffle_completed = 'yes' if db_user.raffle == 1 else 'no'
            adores = db_user.adores
            stats_embed.add_field(name="Adores",value="{0}".format(adores))
            ##build XP card here.
            #adores_card = "```http\nAdores - {0}\n```".format(adores)
            next_level_required_xp = current_level*10+50
            #xp_card = "```Markdown\n# Level: {0}   XP: {1}/{2}\n# ".format(current_level,current_xp,next_level_required_xp)
            percent = current_xp/next_level_required_xp
            expbar = ""
            blips = 20
            while percent > 0:
                expbar = expbar + '●'
                percent = percent - 0.05
                blips = blips - 1
            while blips > 0:
                expbar = expbar + '○'
                blips = blips - 1
            #xp_card = xp_card + '\n```'
            #name_card = "```Python\n@{0} - Score Card:\n```".format(user_name)
            stats_embed.add_field(name="Level: {0}    XP: {1}/{2}".format(db_user.level,db_user.currentxp,next_level_required_xp),value=expbar,inline=True)
            submit_status = ""
            raffle_status = ""
            stats_embed.add_field(name="Streaks Expires",value="{0} Days, {1} Hours, {2} Minutes, {3} Seconds.".format(d_days, d_hour, d_min, d_sec),inline=True)
            #stats_card = "```diff\n+ Total Submissions: {0}\n+ Currency: {1}\n+ Current Streak: {2}\n- Streak Expires: {3} {4}, {5}\n".format(current_score,currency_amount,current_streak,streak_expiration_month,streak_expiration_day,streak_expiration_year)
            #stats_card = "```diff\n+ Total Submissions: {0}\n+ Currency: {1}\n+ Current Streak: {2}\n- Streak Expires: {3} Days, {4} Hours, {5} Minutes, {6} Seconds\n".format(current_score,currency_amount,current_streak,d_days, d_hour, d_min, d_sec)
            if submitted_today == 'yes':
                submit_status = ":white_check_mark: You have submitted today"
            else:
                submit_status = ":red_circle: You have not submitted today."
            if raffle_completed == 'yes':
                raffle_status = ":white_check_mark: You have completed the raffle prompt this month."
            else:
                raffle_status =":red_circle: You have not completed the raffle prompt this month."
            #score_card = name_card + xp_card + adores_card + stats_card
            stats_embed.add_field(name="Submit Status",value=submit_status,inline=True)
            stats_embed.add_field(name="Raffle Status",value=raffle_status,inline=True)
            await client.send_message(message.channel, embed=stats_embed)
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
        now = datetime.utcnow()
        end = datetime(now.year, now.month, now.day, hour=7,minute=0,second=0,microsecond=0)
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
        await client.send_message(message.channel, "```Markdown\n# Updating Roles...\n```")
        await updateRoles(message.server)
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
        foundname = False
        serv = message.server
        #try to find user in database using id
        try:
            db_user = session.query(User).filter(User.id == message.author.id).one()
            foundname = True
        except sqlalchemy.orm.exc.NoResultFound:
            print('No user found, probably not registered')
        except sqlalchemy.orm.exc.MultipleResultsFound:
            print('Multiple users found, something is really broken!')

        if not foundname:
            await client.send_message(message.channel, "```diff\n- You need to be registered to suggest prompts.\n```")
        else:
            db_user.promptsadded = newpromptscore = db_user.promptsadded+1
            session.commit()
            await client.send_message(message.channel, "```diff\n+ Your prompt suggestion has been recorded!\n```")
            if newpromptscore == 20:
                for rank in serv.roles:
                    if rank.name == "Idea Machine":
                        await client.add_roles(message.author,rank)
                        await client.send_message(message.channel, "```Python\n @{0} Achievement Unlocked: Idea Machine\n```".format(message.author.name))
            fp = open('prompts.txt','a+')
            fp.write(message.content[6:]+'\n')
            fp.close()
    elif message.content.lower().startswith('!8ball') and message.author != message.author.server.me:
        if(True):
            await client.send_message(message.channel,'`{0} shakes their eight ball..`\n:8ball: `{1}`'.format(message.author.name, random.choice(eight_ball)))
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
        working_index = 0
        price = 100
        curdate = datetime.date.utcnow()
        potentialstreak = curdate + datetime.timedelta(days=30)
        today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
        streakdate = "{0}-{1}-{2}".format(potentialstreak.month, potentialstreak.day, potentialstreak.year)
        #try to find user in database using id
        foundname = False
        try:
            db_user = session.query(User).filter(User.id == message.author.id).one()
            foundname = True
        except sqlalchemy.orm.exc.NoResultFound:
            print('No user found, probably not registered')
        except sqlalchemy.orm.exc.MultipleResultsFound:
            print('Multiple users found, something is really broken!')

        if foundname:
            def check(msg):
                return msg.content.startswith('!')
            buyer_amount = db_user.currency
            if buyer_amount >= price:
                await client.send_message(message.channel, "```Python\n@{0}\n```\n```Markdown\n# You're about to purchase a 30 day vacation to protect your streak for 100 credits. (any new submissions will reset this to 7 days). To confirm and buy type !yes, to decline, type !no.\n```".format(message.author.name))
                confirm = await client.wait_for_message(author=message.author,check=check)
                if confirm.content.lower().startswith('!yes'):
                    new_buyer_balance = buyer_amount - price
                    db_user.currency = new_buyer_balance
                    db_user.expiry = potentialstreak
                    session.commit()
                    await client.send_message(message.channel, "```diff\n+ Vacation purchased, your streak now expires on {0} {1}, {2}. Bon Voyage!\n```".format(months[potentialstreak.month],potentialstreak.day,potentialstreak.year))
                elif confirm.content.lower().startswith('!no'):
                    await client.send_message(message.channel, "```Markdown\n# Transaction cancelled.\n```")
            else:
                await client.send_message(message.channel, "```Markdown\n- Not enough credits. {0} needed, you have {1}```".format(price, buyer_amount))
        else:
            await client.send_message(message.channel, "```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
    elif message.content.lower().startswith('!markraffle') and message.author.name in admins:
        try:
            receiver = message.mentions[0]
            db_user = session.query(User).filter(User.id == receiver.id).one()
            db_user.raffle = 1
            session.commit()
            await client.send_message(message.channel,"```diff\n+ Raffle submission marked for: {0}\n```".format(receiver.name))
        except:
            await client.send_message(message.channel,"```diff\n- Something went wrong.\n```")
            session.rollback()
    elif message.content.lower().startswith('!buy') and message.author != message.author.server.me:
        #under construction.
        parse = message.content.split(" ")
        item_name = parse[1].lower()
        price = 0
        foundname = False
        serv = message.server
        #try to find user in database using id
        try:
            db_user = session.query(User).filter(User.id == message.author.id).one()
            foundname = True
        except sqlalchemy.orm.exc.NoResultFound:
            print('No user found, probably not registered')
        except sqlalchemy.orm.exc.MultipleResultsFound:
            print('Multiple users found, something is really broken!')


        if not foundname:
            await client.send_message(message.channel,"```diff\n- You were not found in sheet, make sure to register before you use the shop.\n```")
        else:
            buyer_currency = db_user.currency
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
                db_user.currency = new_currency
                session.commit()
                await client.send_message(message.channel,"```diff\n+ Successfully payed {0} credits for {1}. Your total balance is now: {2}\n```".format(price,item_name,new_currency))
    elif message.content.lower().startswith("!undo") and (message.author.name in admins):
        userid = message.content.split(" ")
        #get user ID to roll back
        if(len(userid) >= 2):
            userid = userid[1]
        else:
            userid = "0"

        #try to find user in database using id
        foundname = False
        try:
            db_user = session.query(User).filter(User.id == userid).one()
            foundname = True
        except sqlalchemy.orm.exc.NoResultFound:
            print('No user found, probably not registered')
        except sqlalchemy.orm.exc.MultipleResultsFound:
            print('Multiple users found, something is really broken!')

        if(foundname):
            #update all the stats
            newscore = db_user.totalsubmissions-1
            newcurrency = db_user.currency-10
            current_streak = db_user.streak
            new_streak = current_streak-1
            current_xp = db_user.currentxp
            xp_lost = 20 + int(math.floor((current_streak)/2))
            current_level = db_user.level
            last_level_required_xp = (current_level-1)*10 + 50
            new_xp_total = current_xp - xp_lost
            #if we levelled up, increase level
            if new_xp_total < 0:
                current_level = current_level - 1
                new_xp_total = last_level_required_xp + new_xp_total
                db_user.level = current_level
                db_user.currentxp = new_xp_total
            #otherwise just increase exp
            else:
                db_user.currentxp = new_xp_total
            #write all new values to our cells
            db_user.totalsubmissions = newscore
            db_user.currency = newcurrency
            db_user.streak = new_streak
            db_user.submitted = 0
            #update the cells in the sheet
            session.commit()
            await client.send_message(message.channel,"```Markdown\n#Score reverted for user {0}\n```".format(userid))
    elif message.content.lower().startswith("!proxysubmit") and (message.author.name in admins):
        print('proxy submission - ' + str(len(message.mentions)))
        if (len(message.mentions)>0):
            userToUpdate = message.mentions[0]
            if "https://" in message.content.lower() or "http://" in message.content.lower():
                # do linksubmit
                await linkSubmit(message, userToUpdate)
            else:
                try:
                    #normal submit.
                    await normalSubmit(message, userToUpdate)
                except:
                    pass
    elif message.content.lower().startswith("!setstreak") and (message.author.name in admins):
        userid = message.content.split(" ")
        newstreak = 0
        #get user ID to roll back
        if(len(userid) >= 3):
            newstreak = int(userid[2])
            userid = userid[1]
        else:
            userid = "0"
        #try to find user in database using id
        foundname = False
        try:
            db_user = session.query(User).filter(User.id == userid).one()
            foundname = True
        except sqlalchemy.orm.exc.NoResultFound:
            print('No user found, probably not registered')
        except sqlalchemy.orm.exc.MultipleResultsFound:
            print('Multiple users found, something is really broken!')
        if(foundname):
            #set streak to the given streak
            db_user.streak = newstreak
            session.commit()
            await client.send_message(message.channel,"```Markdown\n#Streak set to {0} for user {1}\n```".format(newstreak,userid))
    elif message.content.lower().startswith("!quit") and (message.author.name in admins):
        await client.send_message(message.channel,"Shutting down BotRoss, bye byeee~")
        sys.exit(5)
    elif message.content.lower().startswith("!reset") and (message.author.name in admins):
        await client.send_message(message.channel,"Resetting BotRoss (assuming Ciy and Whatsa did their job right), bye byeee~")
        sys.exit()
    elif message.content.lower().startswith("!embedtest") and (message.author.name in admins):
        testembed.set_thumbnail(url=message.author.avatar_url)
        testembed.add_field(name="Test_Field",value="Ciy is a butt.",inline=True)
        await client.send_message(message.channel, embed=testembed)

async def updateRoles(serv):
    #get all rows and put into memory
    for curr_member in session.query(User).all():
        streak = curr_member.streak
        cur_member = False #default value
        #if the default value is retained (we didn't find a user)
        #then do nothing. This caused the old bug
        for person in serv.members:
            if curr_member.id == person.id:
                cur_member = person
        #if we found a member, update their roles
        if(cur_member != False):
            if streak >= 300:
                for rank in serv.roles:
                    if rank.name == "300+ Streak":
                        if(rank not in cur_member.roles):
                            await client.add_roles(cur_member,rank)
                            print("updating roles for {0} with streak {1}".format(cur_member, streak))
            elif streak >= 250 and streak < 300:
                for rank in serv.roles:
                    if rank.name == "250+ Streak":
                        if(rank not in cur_member.roles):
                            await client.add_roles(cur_member,rank)
                            print("updating roles for {0} with streak {1}".format(cur_member, streak))
            elif streak >= 200 and streak < 250:
                for rank in serv.roles:
                    if rank.name == "200+ Streak":
                        if(rank not in cur_member.roles):
                            await client.add_roles(cur_member,rank)
                            print("updating roles for {0} with streak {1}".format(cur_member, streak))
            elif streak >= 150 and streak < 200:
                for rank in serv.roles:
                    if rank.name == "150+ Streak":
                        if(rank not in cur_member.roles):
                            await client.add_roles(cur_member,rank)
                            print("updating roles for {0} with streak {1}".format(cur_member, streak))
            elif streak >= 120 and streak < 150:
                for rank in serv.roles:
                    if rank.name == "120+ Streak":
                        if(rank not in cur_member.roles):
                            await client.add_roles(cur_member,rank)
                            print("updating roles for {0} with streak {1}".format(cur_member, streak))
            elif streak >= 90 and streak < 120:
                for rank in serv.roles:
                    if rank.name == "90+ Streak":
                        if(rank not in cur_member.roles):
                            await client.add_roles(cur_member,rank)
                            print("updating roles for {0} with streak {1}".format(cur_member, streak))
            elif streak >= 60 and streak < 100:
                for rank in serv.roles:
                    if rank.name == "60+ Streak":
                        if(rank not in cur_member.roles):
                            await client.add_roles(cur_member,rank)
                            print("updating roles for {0} with streak {1}".format(cur_member, streak))
            elif streak >= 30 and streak < 60:
                for rank in serv.roles:
                    if rank.name == "30+ Streak":
                        if(rank not in cur_member.roles):
                            await client.add_roles(cur_member,rank)
                            print("updating roles for {0} with streak {1}".format(cur_member, streak))
            elif streak >= 25 and streak < 30:
                for rank in serv.roles:
                    if rank.name == "25+ Streak":
                        if(rank not in cur_member.roles):
                            await client.add_roles(cur_member,rank)
                            print("updating roles for {0} with streak {1}".format(cur_member, streak))
            elif streak >=20 and streak < 25:
                for rank in serv.roles:
                    if rank.name == "20+ Streak":
                        if(rank not in cur_member.roles):
                            await client.add_roles(cur_member,rank)
                            print("updating roles for {0} with streak {1}".format(cur_member, streak))
            elif streak >=15 and streak < 20:
                for rank in serv.roles:
                    if rank.name == "15+ Streak":
                        if(rank not in cur_member.roles):
                            await client.add_roles(cur_member,rank)
                            print("updating roles for {0} with streak {1}".format(cur_member, streak))
            elif streak >=10 and streak < 15:
                for rank in serv.roles:
                    if rank.name == "10+ Streak":
                        if(rank not in cur_member.roles):
                            await client.add_roles(cur_member,rank)
                            print("updating roles for {0} with streak {1}".format(cur_member, streak))
            elif streak >=5 and streak < 10:
                for rank in serv.roles:
                    if rank.name == "5+ Streak":
                        if(rank not in cur_member.roles):
                            await client.add_roles(cur_member,rank)
                            print("updating roles for {0} with streak {1}".format(cur_member, streak))

async def linkSubmit(message, userToUpdate):
    url = message.content.split(" ")
    print('link submitting for ' + str(userToUpdate.name))
    print(str(userToUpdate.name) + "'s url - " + url[1])
    print('link submitting for ' + str(userToUpdate.name))
    await handleSubmit(message, userToUpdate, url[1])

async def normalSubmit(message, userToUpdate):
    print('submitting for ' + str(userToUpdate.name))
    jsonstr = json.dumps(message.attachments[0])
    jsondict = json.loads(jsonstr)
    url = jsondict['url']
    print(str(userToUpdate.name) + "'s url - " + url)

    print('normal submitting for ' + str(userToUpdate.name))
    await handleSubmit(message, userToUpdate, url)




async def handleSubmit(message, userToUpdate, url):
    curdate = datetime.utcnow()
    potentialstreak = curdate + timedelta(days=8)
    today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
    streakdate = "{0}-{1}-{2}".format(potentialstreak.month, potentialstreak.day, potentialstreak.year)
    print('getting filepath to download for ' + str(userToUpdate.name))
    filepath = os.getcwd()+"/"+today

    #try to find user in database using id
    foundname = False
    try:
        db_user = session.query(User).filter(User.id == userToUpdate.id).one()
        foundname = True
        print('found user in database - ' + db_user.name)
    except sqlalchemy.orm.exc.NoResultFound:
        print('No user found, probably not registered')
    except sqlalchemy.orm.exc.MultipleResultsFound:
        print('Multiple users found, something is really broken!')
    #first find if we have  the user in our list

    if not foundname:
        await client.send_message(message.channel, "```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
    else:
        #db_user is our member object

        #check if already submitted
        if db_user.submitted == 1:
            print(str(userToUpdate.name) + ' already submitted')
            await client.send_message(message.channel, "```diff\n- You seem to have submitted something today already!\n```")
        #otherwise, do the submit
        else:
            if url.lower().endswith('.png') or url.lower().endswith('.jpg') or url.lower().endswith('.gif') or url.lower().endswith('.jpeg'):
                #if message.channel.id == channel_ids['class_2']:
                    #print('starting file download')
                    #os.system('wget {0} -P {1}'.format(url, filepath))
                    #print('finishing file download')
                #update all the stats
                newscore = db_user.totalsubmissions+1
                newcurrency = db_user.currency+10
                current_streak = db_user.streak
                new_streak = current_streak+1
                current_xp = db_user.currentxp
                xp_gained = 20 + int(math.floor(current_streak/2))
                current_level = db_user.level
                next_level_required_xp = current_level*10 + 50
                new_xp_total = current_xp + xp_gained
                #if we levelled up, increase level
                if new_xp_total >= next_level_required_xp:
                    current_level = current_level + 1
                    new_xp_total = new_xp_total - next_level_required_xp
                    db_user.level = str(current_level)
                    db_user.currentxp = str(new_xp_total)
                    await client.send_message(message.channel,"```Markdown\n# @{0} Level Up! You are now level {1}!\n```".format(userToUpdate.name,current_level))
                #otherwise just increase exp
                else:
                    db_user.currentxp = str(new_xp_total)
                #write all new values to our cells
                db_user.totalsubmissions = newscore
                db_user.currency = newcurrency
                db_user.streak = new_streak
                db_user.submitted = 1
                db_user.expiry = potentialstreak
                #and push all cells to the database
                session.commit()
                print("finishing updating " + db_user.name + "'s stats")
                await client.send_message(message.channel, "```diff\n+ @{0} Link Submission Successful! Score updated!\n+ {1}xp gained.```".format(userToUpdate.name,xp_gained))
                print("submit complete")
            else:
                await client.send_message(message.channel, "```diff\n- Not a png, jpg, or gif file```")

async def roletask():
    #Do a role update
    print("Performing Role Update")
    await client.send_message(botChannel, "```Markdown\n# Updating Roles Automatically...\n```")
    await updateRoles(tapeServer)
    await client.send_message(botChannel, "```diff\n+ Updating roles was a happy little success!\n```")

async def housekeeper():
    curdate = datetime.utcnow()
    today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)

    #get all rows and put into memory
    members = session.query(User).all()
    print("Housekeeping on " + str(len(members)) + " rows on " + today)

    for curr_member in members:
        # Update in batch
        #If we're past the streak
        if((curdate.date() - curr_member.expiry).days >= 0 and curr_member.streak > 0):
            pointReduce = pow(2,(curdate.date() - curr_member.expiry).days+1)
            #reduce streak by 2^(daysPastStreak+1), until streak is zero
            print("Removing {0} points from {1}'s streak".format(pointReduce,curr_member.name))
            curr_member.streak = max(curr_member.streak-pointReduce,0)
        #Set submitted to no
        curr_member.submitted = 0
    #commit all changes to the sheet at once
    session.commit()
    print("housekeeping finished")

#do role update every 3 hours
scheduler.add_job(roletask, 'cron', hour='1,4,7,10,13,16,19,21')
#run housekeeping at 7am UTC
scheduler.add_job(housekeeper, 'cron', hour=7)
scheduler.start()
client.run(botEmail, botPassword)
#client.run('')
