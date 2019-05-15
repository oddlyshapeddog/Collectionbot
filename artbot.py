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
from sqlalchemy import update
import time
from datetime import date, timedelta, time, datetime
#declaration for User class is in here
from create_databases import Base, User, Contest, QuestsMembers, QuestsList

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

#total number of quests
quest_amount = 28

spreadsheet_schema = {"Discord Name":1,"Start Date":2,"Level":3,"Currency":4,"Streak":5,"Streak Expires":6,"Submitted Today?":7,"Raffle Prompt Submitted":8,"Week Team":9,"Month Team":10,"Referred By":11,"Prompts Added":12,"Current XP":13}
months = {1:"January",2:"February",3:"March",4:"April",5:"May",6:"June",7:"July",8:"August",9:"September",10:"October",11:"November",12:"December"}
nonach_roles = ["0+ Streak","5+ Streak","10+ Streak","15+ Streak","20+ Streak","25+ Streak","30+ Streak","60+ Streak","90+ Streak","120+ Streak","150+ Streak","200+ Streak","250+ Streak","300+ Streak","Admins","Raffle","Community Admins","Type !help for info","@everyone","NSFW Artist", "Artists", "Head Admins", "999+ Streak", "2000+ Streak", "Override (5+)", "Override (10+)", "Override (15+)", "Override (20+)", "Override (25+)", "Override (30+)", "Override (60+)", "Override (90+)", "Override (120+)", "Override (150+)", "Override (200+)", "Override (250+)", "Override (300+)"]
override_roles = ["Override (5+)", "Override (10+)", "Override (15+)", "Override (20+)", "Override (25+)", "Override (30+)", "Override (60+)", "Override (90+)", "Override (120+)", "Override (150+)", "Override (200+)", "Override (250+)", "Override (300+)"]
streak_roles = ["0+ Streak","5+ Streak","10+ Streak","15+ Streak","20+ Streak","25+ Streak","30+ Streak","60+ Streak","90+ Streak","120+ Streak","150+ Streak","200+ Streak","250+ Streak","300+ Streak", "999+ Streak", "2000+ Streak"]
eight_ball = ["It is certain.","It is decidedly so.","Without a doubt.","Yes, definitely.","You may rely on it.","As I see it, yes.","Most likely.","Outlook good.","Yes.","Signs point to yes.","Reply hazy try again.","Ask again later.","Better not tell you now.","Cannot predict now.","Concentrate and ask again.","Don't count on it.","My reply is no.","My sources say no.","Outlook not so good.","Very doubtful."]

channel_ids = {"class_1":241060721994104833, "class_2":236678008562384896}
tapeGuild = 'no server'
botChannel = 'no channel'
adminRole = 'no role'

### Art bot by Whatsapokemon and Ciy 2.0
### Simple bot for Discord designed to manage image collection.

logging.basicConfig(level = logging.INFO)

client = discord.Client()

###LIVE/DEBUG SETTINGS####
live = False
if(live):
    guildName = 'The Art Plaza Extravaganza'
    botChannelName = 'bot-channel'
    submitChannels = [236678008562384896, 302915168801783810, 241060721994104833, 313945720447303680]
    adoreEmoji = 284820985767788554
    adminRole = "Admins"
else:
    guildName = 'Marsh Palace'
    botChannelName = 'bot-testing'
    submitChannels = [271516310314156042,284618270659575818,386395766505340939,317414355501187072]
    adoreEmoji = 538580881225285652
    adminRole = "Admins"
##########################


@client.event
async def on_ready():
    global tapeGuild
    global botChannel
    global adminRole
    global adoreEmoji
    print('Bot Online.')
    print(client.user.name)
    print(client.user.id)
    print('------')
    #Store the server and the bot command channel
    tapeGuild = discord.utils.find(lambda s: s.name == guildName, client.guilds)
    print("active server set to " + tapeGuild.name)
    botChannel = discord.utils.find(lambda c: c.name == botChannelName, tapeGuild.channels)
    print("bot channel set to " + botChannel.name)
    #admin role, admin actions require at least this role (or any with higher priority)
    adminRole = discord.utils.find(lambda r: r.name == adminRole, tapeGuild.roles)
    print("admin role set to " + adminRole.name)
    adoreEmoji = discord.utils.find(lambda e: e.id == adoreEmoji, tapeGuild.emojis)
    print("adore emoji set to " + adoreEmoji.name)

@client.event
async def on_reaction_add(reaction, user):
    userToUpdate = reaction.message.author.id
    #if the submission is a proxy submission
    if(reaction.message.content.lower().startswith('!proxysubmit')):
        #Change attribution of proxy submits to the mentioned user
        userToUpdate = reaction.message.mentions[0].id
    try:
        if type(reaction.emoji) is discord.Emoji:
            if reaction.emoji.id == adoreEmoji.id and user.id != userToUpdate and (reaction.message.content.startswith("!submit") or reaction.message.content.startswith("!proxysubmit")):
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
            if reaction.emoji.id == adoreEmoji.id and user.id != userToUpdate and (reaction.message.content.startswith("!submit") or reaction.message.content.startswith("!proxysubmit")):
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
    if message.content.lower() == "f" and message.author != message.author.guild.me and message.channel.id == "279098440820981760":
        await message.channel.send( "```Markdown\n {0} has paid their respects.\n```".format(message.author))
    elif message.content.lower().startswith('!submit') and message.author != message.author.guild.me:
        if (message.channel.id in submitChannels):
            filetypes = [".gif",".jpg",".jpeg",".png"]
            if ("https://" in message.content.lower() or "http://" in message.content.lower()) and any(u in message.content.lower() for u in filetypes) :
                # do linksubmit
                await linkSubmit(message, message.author)
            else:
                try:
                    #normal submit.
                    await normalSubmit(message, message.author)
                except:
                    pass
        else:
            await message.channel.send( "`Whoopsies, you can't submit in this channel!`")
    elif message.content.lower().startswith('!register') and message.author != message.author.guild.me:
        curdate = datetime.utcnow()
        today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
        already_registered = False
        #try to find user in database using id
        db_user = getDBUser(message.author.id)
        serv = message.guild
        foundrole = discord.utils.find(lambda r: r.name == 'Artists', message.author.roles)

        #add a new user if there's no registered user
        if (db_user == None):
            #create new user object
            new_user = User(name=message.author.name, level=1, id=message.author.id, startdate=curdate, currency=0, streak=0, expiry=curdate, submitted=0, raffle=0, promptsadded=0, totalsubmissions=0, currentxp=0, adores=0, highscore=0, decaywarning=True)
            #add to session
            session.add(new_user)
            #give relevant roles
            for rank in serv.roles:
                if rank.name == "0+ Streak":
                    await message.author.add_roles(rank)
            for rank in serv.roles:
                if rank.name == "Artists":
                    await message.author.add_roles(rank)
            #commit session
            session.commit()
            await message.channel.send( "```diff\n+ Successfully registered!\n```")
        elif (db_user != None and foundrole == None):
            for rank in serv.roles:
                if rank.name == "Artists":
                    await message.author.add_roles( rank)
            await message.channel.send( "```Markdown\n# You're registered, I'll give you your Artist role back!\n```")
        else:
            await message.channel.send( "```Markdown\n# You're already registered!\n```")

    elif message.content.lower().startswith('!help') and message.author != message.author.guild.me:
        helpString = """```Markdown
# Here's a quick little starter guide for all of you happy little artists wishing to participate.
# !register will add you to our spreadsheet where we keep track of every submission you make
# To submit content, drag and drop the file (.png, .gif, .jpg) into discord and add '!submit' as a comment to it.
# If you'd like to submit via internet link, make sure you right click the image and select 'copy image location' and submit that URL using the !submit command.
# The !timeleft command will let you know how much longer you have left to submit for the day!
# To see your current scorecard, type !stats 
# To see your achievement status, type !ach
# Override your role colour using !override [Role Number], or !override none to clear an active override.
# To turn on or off the PM warning system about your streak use the command !streakwarning on or !streakwarning off.
```
```diff
- For those of our older artists, you may access the nsfw channels by typing !nsfwjoin and you can hide those channels by typing !nsfwleave. 
- When submitting nsfwcontent please use the r18 channels respectively!!
```"""
        await message.channel.send( helpString)
    elif message.content.lower().startswith('!stats') and message.channel == botChannel and message.author != message.author.guild.me:
        #try to find user in database using id
        db_user = getDBUser(message.author.id)

        #quest check
        db_quester = getDBQuestMember(message.author.id,0)

        #if we found the user in our spreadsheet
        if (db_user != None):
            #update the stats quest
            #method to update a user based on id and quest
            if(db_quester != None):
                db_quester.progress = 1
                await checkQuestCompletion(message.author.id,0)

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
            stats_embed.add_field(name="Streak High Score",value=db_user.highscore,inline=True)
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
            await message.channel.send(embed=stats_embed)
        else:
            await message.channel.send("```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
    elif message.content.lower().startswith('!ach') and message.author != message.author.guild.me:
        serv = message.guild
        ach_card = "```Python\n @{0} - Achievements\n# Note: unlocked ones are in green and denoted with a '+'.\n```\n```diff\n".format(message.author.name)
        for rank in serv.roles:
            if rank in message.author.roles and rank.name not in nonach_roles:
                ach_card = ach_card + '+ {0}\n'.format(rank.name)
            if rank not in message.author.roles and rank.name not in nonach_roles:
                ach_card = ach_card + '# {0}\n'.format(rank.name)
        ach_card = ach_card + "```"
        await message.channel.send( ach_card)
    elif message.content.lower().startswith('!timeleft') and message.author != message.author.guild.me:
        now = datetime.utcnow()
        end = datetime(now.year, now.month, now.day, hour=7,minute=0,second=0,microsecond=0)
        difference = end - now
        seconds_to_work = difference.seconds
        difference_hours = math.floor(seconds_to_work / 3600)
        seconds_to_work = seconds_to_work - 3600*difference_hours
        difference_minutes = math.floor(seconds_to_work / 60)
        seconds_to_work = seconds_to_work - 60*difference_minutes
        if difference_hours < 5:
            await message.channel.send( '```diff\n- {0} hours, {1} minutes, and {2} seconds left to submit for today!\n```'.format(difference_hours,difference_minutes,seconds_to_work))
        else:
            await message.channel.send( '```diff\n+ {0} hours, {1} minutes, and {2} seconds left to submit for today!\n```'.format(difference_hours,difference_minutes,seconds_to_work))

    elif message.content.lower().startswith('!roleupdate') and (message.author.top_role >= adminRole):
        await message.channel.send( "```Markdown\n# Updating Roles...\n```")
        await updateRoles(message.guild)
        await message.channel.send( "```diff\n+ Updating roles was a happy little success!\n```")
    elif message.content.lower().startswith('!nsfwjoin') and message.author != message.author.guild.me:
        serv = message.author.guild
        for rank in serv.roles:
            if rank.name == "NSFW Artist":
                await message.author.add_roles(rank)
                await message.channel.send( "```Markdown\nYou should now have access to the NSFW channels, Oh my!```")
    elif message.content.lower().startswith('!nsfwleave') and message.author != message.author.guild.me:
        serv = message.author.guild
        for rank in serv.roles:
            if rank.name == "NSFW Artist":
                await message.author.remove_roles( rank)
                await message.channel.send( "```Markdown\nNSFW channels have been hidden.\n```")
    elif message.content.lower().startswith('!artblock') and message.author != message.author.guild.me:
        fp = open('prompts.txt', 'r+')
        await message.channel.send( "```Markdown\n# {0}\n```".format(random.choice(fp.readlines())))
        fp.close()
    elif message.content.lower().startswith('!idea') and message.author != message.author.guild.me:
        serv = message.guild
        #try to find user in database using id
        db_user = getDBUser(message.author.id)

        if (db_user == None):
            await message.channel.send( "```diff\n- You need to be registered to suggest prompts.\n```")
        else:
            db_user.promptsadded = newpromptscore = db_user.promptsadded+1
            session.commit()
            await message.channel.send( "```diff\n+ Your prompt suggestion has been recorded!\n```")
            if newpromptscore == 20:
                for rank in serv.roles:
                    if rank.name == "Idea Machine":
                        await message.author.add_roles(rank)
                        await message.channel.send( "```Python\n @{0} Achievement Unlocked: Idea Machine\n```".format(message.author.name))
            fp = open('prompts.txt','a+')
            fp.write(message.content[6:]+'\n')
            fp.close()
    elif message.content.lower().startswith('!8ball') and message.author != message.author.guild.me:
        if(True):
            await message.channel.send('`{0} shakes their eight ball..`\n:8ball: `{1}`'.format(message.author.name, random.choice(eight_ball)))
    elif message.content.lower().startswith('!roll') and message.author != message.author.guild.me:
        dice = message.content.split(' ')[1]
        try:
            num_dice =  int(dice.split('d')[0])
            dice_value = int(dice.split('d')[1])
            rolls = []
            for i in range(0,num_dice):
                rolls.append(random.randint(1,dice_value))

            await message.channel.send( ":game_die: `Your rolls are: {0}`".format(rolls))
        except:
            await message.channel.send( "```diff\n- Invalid dice arguments\n```")
    elif message.content.lower().startswith('!award') and message.author.top_role >= adminRole:
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
        await message.channel.send( "```Markdown\n# !{0} awarded to {1}```".format(reward, members_awarded))
    elif message.content.lower().startswith('!grant') and message.author.top_role >= adminRole:
        #grants an achievement.
        parse = message.content.split("-")
        achievement_receivers = ""
        achievement_name = parse[1]
        serv = message.guild
        for rank in serv.roles:
            if rank.name.lower() == achievement_name.lower():
                for person in message.mentions:
                    await person.add_roles(rank)
                    achievement_receivers = achievement_receivers + " " +person.name
        await message.channel.send( "```Markdown\n# {0} awarded to {1}\n```".format(achievement_name,achievement_receivers))
    elif message.content.lower().startswith('!ungrant') and message.author.top_role >= adminRole:
        #grants an achievement.
        parse = message.content.split("-")
        achievement_receivers = ""
        achievement_name = parse[1]
        serv = message.guild
        for rank in serv.roles:
            if rank.name.lower() == achievement_name.lower():
                for person in message.mentions:
                    await person.remove_roles( rank)
                    achievement_receivers = achievement_receivers + " " +person.name
        await message.channel.send( "```Markdown\n# {0} removed from {1}\n```".format(achievement_name,achievement_receivers))
    elif message.content.lower().startswith('!vacation') and message.author != message.author.guild.me:
        working_index = 0
        price = 100
        curdate = datetime.utcnow()
        potentialstreak = curdate + timedelta(days=30)
        today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
        streakdate = "{0}-{1}-{2}".format(potentialstreak.month, potentialstreak.day, potentialstreak.year)
        #try to find user in database using id
        db_user = getDBUser(message.author.id)

        if (db_user != None):
            buyer_amount = db_user.currency
            if buyer_amount >= price:
                await message.channel.send( "```Python\n@{0}\n```\n```Markdown\n# You're about to purchase a 30 day vacation to protect your streak for 100 credits. (any new submissions will reset this to 7 days). To confirm and buy type !yes, to decline, type !no.\n```".format(message.author.name))
                try:
                    confirm = await confirmDecision(message.author)
                    if confirm:
                        new_buyer_balance = buyer_amount - price
                        db_user.currency = new_buyer_balance
                        db_user.expiry = potentialstreak
                        session.commit()
                        await message.channel.send( "```diff\n+ Vacation purchased, your streak now expires on {0} {1}, {2}. Bon Voyage!\n```".format(months[potentialstreak.month],potentialstreak.day,potentialstreak.year))
                    else:
                        await message.channel.send( "```Markdown\n# Transaction cancelled.\n```")
                except:
                    print("transaction with {0} timed out".format(message.author.name))
            else:
                await message.channel.send( "```Markdown\n- Not enough credits. {0} needed, you have {1}```".format(price, buyer_amount))
        else:
            await message.channel.send( "```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
    elif message.content.lower().startswith('!markraffle') and message.author.top_role >= adminRole:
        try:
            receiver = message.mentions[0]
            db_user = session.query(User).filter(User.id == receiver.id).one()
            db_user.raffle = 1
            session.commit()
            await message.channel.send("```diff\n+ Raffle submission marked for: {0}\n```".format(receiver.name))
        except:
            await message.channel.send("```diff\n- Something went wrong.\n```")
            session.rollback()
    elif message.content.lower().startswith('!unmarkraffle') and message.author.top_role >= adminRole:
        try:
            receiver = message.mentions[0]
            db_user = session.query(User).filter(User.id == receiver.id).one()
            db_user.raffle = 0
            session.commit()
            await message.channel.send("```diff\n+ Raffle submission unmarked for: {0}\n```".format(receiver.name))
        except:
            await message.channel.send("```diff\n- Something went wrong.\n```")
            session.rollback()
    elif message.content.lower().startswith('!buy') and message.author != message.author.guild.me:
        #under construction.
        parse = message.content.split(" ")
        item_name = parse[1].lower()
        price = 0
        serv = message.guild
        #try to find user in database using id
        db_user = getDBUser(message.author.id)

        if (db_user == None):
            await message.channel.send("```diff\n- You were not found in sheet, make sure to register before you use the shop.\n```")
        else:
            buyer_currency = db_user.currency
            fp = open('shop.txt','r+')
            items_list = fp.readlines()
            for items in items_list:
                if items.lower().startswith(item_name):
                    price = int(items.split("-")[1])
            fp.close()
            if price > buyer_currency:
                await message.channel.send("```diff\n- Not enough credits. {0} needed, you have {1}\n```".format(price,buyer_currency))
            else:
                new_currency = buyer_currency - price
                db_user.currency = new_currency
                session.commit()
                await message.channel.send("```diff\n+ Successfully payed {0} credits for {1}. Your total balance is now: {2}\n```".format(price,item_name,new_currency))
    elif message.content.lower().startswith('!override'):
        override_string = message.content.split(" ")
        #get user ID to roll back
        if(len(override_string) >= 2):
            override_string = override_string[1]
            override_role = 0
            #try to find user in database using id
            db_user = getDBUser(message.author.id)
            if(db_user != None):
                #get override role
                roleName = ""
                if(override_string in ["5","10","15","20","25","30","60","90","120","150","200","250","300"]):
                    roleName = "Override (" + override_string + "+)"


                role = discord.utils.get(message.guild.roles, name=roleName)
                if(override_string.lower() == "none" or role != None):
                    #get override roles to remove
                    orRoles = [r for r in message.author.roles if r.name.startswith("Override")]

                    if(override_string.lower() == "none"):
                        #remove old roles
                        await message.author.remove_roles( *orRoles)
                        await message.channel.send("```diff\n+Your Override has successfully been removed```")
                    #check if high score allows it
                    elif( int(override_string) <= db_user.highscore):
                        #Now do the purchase code
                        purchase = await buyitem("Role Override Streak ({0})".format(override_string), 100, message.author, message.channel)
                        if(purchase):
                            #remove old roles
                            print(orRoles)
                            await message.author.remove_roles(*orRoles)
                            #add new override to user
                            print(role)
                            await message.author.add_roles( role)
                            await message.channel.send("```diff\n+You have successfully been granted the " + override_string + " Override role```")
                    elif( int(override_string) > db_user.highscore):
                        await message.channel.send("```diff\n-Your Streak high score is not high enough to use that override```")

    elif message.content.lower().startswith("!undo") and (message.author.top_role >= adminRole):
        userid = message.content.split(" ")
        #get user ID to roll back
        if (len(message.mentions)>0):
            userid = message.mentions[0].id
        else:
            if(len(userid) >= 2):
                userid = userid[1]
            else:
                userid = "0"

        #try to find user in database using id
        db_user = getDBUser(userid)

        if(db_user != None):
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
            await message.channel.send("```Markdown\n#Score reverted for user {0}\n```".format(db_user.name))
    elif message.content.lower().startswith("!proxysubmit") and (message.author.top_role >= adminRole):
        print('proxy submission - ' + str(len(message.mentions)))
        if (len(message.mentions)>0):
            userToUpdate = message.mentions[0]
            filetypes = [".gif",".jpg",".jpeg",".png"]
            if ("https://" in message.content.lower() or "http://" in message.content.lower()) and any(u in message.content.lower() for u in filetypes) :
                # do linksubmit
                await linkSubmit(message, userToUpdate)
            else:
                try:
                    #normal submit.
                    await normalSubmit(message, userToUpdate)
                except:
                    pass
    elif message.content.lower().startswith("!setstreak") and (message.author.top_role >= adminRole):
        userid = message.content.split(" ")
        newstreak = 0
        #get user ID to roll back
        if (len(message.mentions)>0):
            newstreak = int(userid[2])
            userid = message.mentions[0].id
        else:
            if(len(userid) >= 3):
                newstreak = int(userid[2])
                userid = userid[1]
            else:
                userid = "0"
        #try to find user in database using id
        db_user = getDBUser(userid)

        if(db_user != None):
            #set streak to the given streak
            db_user.streak = newstreak
            session.commit()
            await message.channel.send("```Markdown\n#Streak set to {0} for user {1}\n```".format(newstreak,db_user.name))
    elif message.content.lower().startswith("!sethighscore") and (message.author.top_role >= adminRole):
        userid = message.content.split(" ")
        newhighscore = 0
        #get user ID to roll back
        if (len(message.mentions)>0):
            print(userid)
            newhighscore = int(userid[2])
            userid = message.mentions[0].id
        else:
            if(len(userid) >= 3):
                newhighscore = int(userid[2])
                userid = userid[1]
            else:
                userid = "0"
        #try to find user in database using id
        db_user = getDBUser(userid)

        if(db_user != None):
            #set streak to the given streak
            db_user.highscore = newhighscore
            session.commit()
            await message.channel.send("```Markdown\n#Streak high score set to {0} for user {1}\n```".format(newhighscore,db_user.name))
    elif message.content.lower().startswith("!resubmit") and (message.author.top_role >= adminRole):
        userid = message.content.split(" ")
        #get user ID to roll back
        if (len(message.mentions)>0):
            print(userid)
            userid = message.mentions[0].id
        else:
            if(len(userid) >= 2):
                userid = userid[1]
            else:
                userid = "0"
        #try to find user in database using id
        db_user = getDBUser(userid)

        if(db_user != None):
            #reset submission to false
            db_user.submitted = 0
            session.commit()
            await message.channel.send("```Markdown\n#Submission status reset to for user {0}\n```".format(db_user.name))
    elif message.content.lower() == "!quit" and (message.author.top_role >= adminRole):
        await message.channel.send("Shutting down BotRoss, bye byeee~")
        sys.exit(5)
    elif message.content.lower() == "!reset" and (message.author.top_role >= adminRole):
        await message.channel.send("Resetting BotRoss (assuming Ciy and Whatsa did their job right), bye byeee~")
        sys.exit()
    elif message.content.lower().startswith("!embedtest") and (message.author.top_role >= adminRole):
        testembed.set_thumbnail(url=message.author.avatar_url)
        testembed.add_field(name="Test_Field",value="Ciy is a butt.",inline=True)
        await message.channel.send( embed=testembed)
    elif message.content.lower().startswith("!getraffle") and (message.author.top_role >= adminRole):
        raffleString = "Raffle Submissions!\n==================="
        members = session.query(User).all()
        currRollNum = 0
        numRaffle = 0
        for curr_member in members:
            if(curr_member.raffle == 1 and curr_member.streak >= 5):
                tickets = 0
                #get number of tickets for the person
                if(curr_member.streak >= 120):
                    tickets = 30
                elif(curr_member.streak >= 90):
                    tickets = 25
                elif(curr_member.streak >= 60):
                    tickets = 20
                elif(curr_member.streak >= 30):
                    tickets = 15
                elif(curr_member.streak >= 25):
                    tickets = 10
                elif(curr_member.streak >= 20):
                    tickets = 8
                elif(curr_member.streak >= 15):
                    tickets = 6
                elif(curr_member.streak >= 10):
                    tickets = 5
                elif(curr_member.streak >= 5):
                    tickets = 1
                #add the user to our raffle
                numRaffle = numRaffle+1
                raffleString=raffleString + "\n**{2}-{3}** = {0}, streak={1}".format(curr_member.name, str(curr_member.streak), str(currRollNum+1), str(currRollNum+tickets))
                #add tickets to pile
                currRollNum = currRollNum + tickets
        await message.channel.send( raffleString)
        await message.channel.send( "`{0} people marked for the raffle - Roll a 1d{1}`".format(str(numRaffle),str(currRollNum)))
    elif message.content.lower().startswith("!resetraffle") and (message.author.top_role >= adminRole):
        await message.channel.send("This command will reset raffle marks for all members. Type !yes to confirm, or !no to cancel.")
        confirm = await confirmDecision(message.author)
        try:
            if(confirm):
                #Reset the raffle submissions for every user
                members = session.query(User).all()
                numRaffle = 0
                print("Resetting raffle on " + str(len(members)) + " members")
                for curr_member in members:
                    #reset raffle to no
                    if(curr_member.raffle == 1):
                        numRaffle = numRaffle+1
                        curr_member.raffle = 0
                #commit all changes to the sheet at once
                session.commit()
                print("raffle reset finished")
                await message.channel.send("Reset the raffle submissions for " + str(numRaffle) + " members")
            else:
                await message.channel.send("Cancelling raffle reset, phew.")
        except:
            print("Raffle Reset timed out")

    elif message.content.lower().startswith('!streakwarning') and message.author != message.author.guild.me:
        #find database user
        db_user = getDBUser(message.author.id)

        #on or off
        sp = message.content.split(" ")

        if(db_user != None):
            choice = True
            if(len(sp) > 1):
                if(sp[1].lower() == "on"): #command to turn on
                    choice = True
                elif(sp[1].lower() == "off"): #command to turn off
                    choice = False
                else:
                    await message.channel.send( "```Markdown\n# Command has been entered incorrectly, please use !streakwarning on or !streakwarning off\n```")
                    return #exit the method
            else: #Just show whether it's on or off
                status_string = "ON" if db_user.decaywarning == True else "OFF"
                await message.channel.send( "```Markdown\n# PM warnings are currently turned " + status_string + ". Use !streakwarning on or !streakwarning off to change.\n```")
                return #exit the method

            curr_mode = db_user.decaywarning
            choice_string = "ON" if choice == True else "OFF"
            if(choice == curr_mode):
                #just tell the user if we're not changing the status
                await message.channel.send( "```Markdown\n# PM warnings are already " + choice_string + "\n```")
            else: #otherwise ask the user for confirmation
                await message.channel.send( "```Python\n@{0}\n```\n```Markdown\n# You're about to you're about to turn ".format(message.author.name) + choice_string + " PM warnings for your streak, to confirm this change type !yes, to decline, type !no.\n```")
                try:
                    confirm = await confirmDecision(message.author)
                    if(confirm): #if the user confirms update the database
                        db_user.decaywarning = choice
                        session.commit() #always commit the session after changes
                        await message.channel.send("```diff\n+ PM warnings have been turned "+ choice_string + "\n```")
                    else:
                        await message.channel.send( "```Markdown\n# PM warnings are unchanged\n```")
                except:
                    print("{0} warning mode unchanged".format(message.author.name))
        else:
            await message.channel.send( "```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")

    #admin command - give xp or take xp
    # new ex. !xp 300 @mentioned users
    # new ex. !xp -300 @mentioned users
    elif message.content.lower().startswith('!xp') and message.author.top_role >= adminRole:
        parse = message.content.split(" ")
        xp_receivers = ""
        if(len(parse) > 2):

            if(isNumber(parse[1])):
                xp_amount = abs(int(parse[1]))
            else:
                await message.channel.send( "```Markdown\n# Not a valid number\n```")
                return

            #give xp to a user
            if(int(parse[1]) >= 0):
                for person in message.mentions:

                    db_user = session.query(User).filter(User.id == person.id).one()
                    await addXP(db_user,xp_amount)
                    xp_receivers = xp_receivers + " " + person.name
                    await message.channel.send("```Markdown\n# @{0} Level Up! You are now level {1}!\n```".format(person.name,db_user.level))

                session.commit()
                await message.channel.send( "```Markdown\n# {0} experience points given to{1}\n```".format(xp_amount,xp_receivers))

            #remove xp from a user
            elif(int(parse[1]) < 0):
                for person in message.mentions:

                    db_user = session.query(User).filter(User.id == person.id).one()
                    await subXP(db_user,xp_amount)
                    xp_receivers = xp_receivers + " " + person.name
                    await message.channel.send("```Markdown\n# @{0} You are now level {1}!\n```".format(person.name,db_user.level))

                session.commit()
                await message.channel.send( "```Markdown\n# {0} experience points taken from{1}\n```".format(xp_amount,xp_receivers))

            else:
                await message.channel.send( "```Markdown\n# please enter in add/sub\n```")

        else:
            await message.channel.send( "```Markdown\n# please enter in the command as !xp add/sub (amount of xp) (mentions of users)\n```")

    #admin command
    #fully reset use stats
    elif message.content.lower().startswith('!fullreset') and message.author.top_role >= adminRole:
        try:
            receiver = message.mentions[0]
            db_user = session.query(User).filter(User.id == receiver.id).one()
            db_user.level = 1
            db_user.currency = 0
            db_user.streak = 0
            db_user.highscore = 0
            db_user.adores = 0
            db_user.current_xp = 0
            db_user.raffle = False
            db_user.submitted = False
            db_user.questdecay = 0
            session.commit()
            await message.channel.send("```Markdown\n#{0} stats have been fully reset\n```".format(receiver.name))
        except:
            await message.channel.send("```Markdown\n#Something went wrong.\n```")
            session.rollback()


    # add in extension
    elif message.content.lower().startswith('!contest') and len(message.content.lower()) > 8  and message.author.top_role >= adminRole:

        #states, no contest(0), closed contest(1), open contest(2)
        # commands, no(0), close(1), open(2), extension (add a confirmation message here or)

        parse = message.content.split(" ")

        mode = parse[1]

        db_contest = getDBContest(0)

        if(db_contest == None):

            #default to no contest
            new_contest = Contest(id = 0, mode = 0, prompt="No contest is currently running!", end=datetime.utcnow())
            session.add(new_contest)
            await message.channel.send( "new contest table added")
            session.commit()

        else:
            #run other checks here

            #contest off - this mode does not need any housechecks
            if(mode.lower() == "off"):
                await message.channel.send( "Turning off the contest")
                db_contest.prompt = "No contest is being run right now."
                db_contest.mode = 0
                session.commit()
            #contest closed - this mode does not need any house checks, but yes for other admin actions
            elif(mode.lower() == "close"):
                await message.channel.send( "Closing the contest")
                db_contest.prompt = "The contest is closed, please wait until further announcements."
                db_contest.mode = 1
                session.commit()
            #contest open - this mode will need house checks
            elif(mode.lower() == "open"):
                #change date to much shorterfor testing later
                await message.channel.send( "```Markdown\n#Please enter in the prompt as !<insert prompt here>\n```")
                confirm = await confirmContest(message.author)
                await message.channel.send( "```Markdown\n#A new contest prompt has been added and opened which is {0}!\n```".format(str(confirm)))

                curdate = datetime.utcnow()
                endDate = curdate + timedelta(days=7)
                await message.channel.send( "Opening the contest")
                db_contest.prompt = confirm
                db_contest.mode = 2
                db_contest.end = endDate
                session.commit()
            #extend date of a contest if its open or closed
            elif(mode.lower() == "extend" and (db_contest.mode == 2 or db_contest.mode == 1)):

                endDate = db_contest.end + timedelta(days = 3)
                db_contest.end = endDate
                db_contest.mode = 2
                session.commit()
                await message.channel.send( "Contest has been extended by 3 days")

            #can only edit the prompt of an open contest
            elif(mode.lower() == "edit" and db_contest.mode == 2):

                await message.channel.send( "```Markdown\n#Please enter in the prompt as !<insert prompt here>\n```")
                confirm = await confirmContest(message.author)
                await message.channel.send( "```Markdown\n#A new contest prompt has been added and opened which is {0}!\n```".format(str(confirm)))

                db_contest.prompt = confirm
                session.commit()

            else:
                await message.channel.send( "please type in off, closed, open, or extend!")


    #use to keep track of how long the contest is
    elif message.content.lower().startswith('!contest') and len(message.content.lower()) == 8 and message.author != message.author.guild.me:

        db_contest = getDBContest(0)

        if (db_contest != None):
            streak_expiration = db_contest.end
            streak_expiration = datetime.combine(streak_expiration, time(2,0))
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
            await message.channel.send( "```Markdown\n#\"{0}\"\n```".format(db_contest.prompt))
            if(db_contest.mode == 2):
                await message.channel.send( "`The contest will run for {0} Days, {1} Hours, {2} Minutes, {3} Seconds`".format(d_days, d_hour, d_min, d_sec))
        else:
            await message.channel.send( "```Markdown\n#There is no contest data!\n```")

    #testing method
    elif message.content.lower().startswith('!runhouse') and message.author != message.author.guild.me and message.author.top_role >= adminRole:
        await message.channel.send( "run housekeeping for testing\n")
        await housekeeper()

    elif message.content.lower().startswith('!questing') and message.author != message.author.guild.me:
        #creates table for that user's quests
        db_user = getDBUser(message.author.id)
        db_quester = getDBQuestMember(message.author.id,0)
        if(db_user == None):
            await message.channel.send("```diff\n- I couldn't find your name in our spreadsheet. Please register as an artist with the !register command first before you can quest!\n```")
        elif(db_quester == None):
            for x in range(quest_amount):
                new_quester = QuestsMembers(usrId = message.author.id, questId = x, name=message.author.name,completed = False, progress = 0)
                session.add(new_quester)
            session.commit()
            await message.channel.send( "```diff\n+ Successfully signed up for quests!\n```")
        else:
            await message.channel.send( "```Markdown\n# You're already signed up for quests!\n```")

    elif message.content.lower().startswith('!updatequest') and message.author != message.author.guild.me:
        #user updates their own quest list when the main quests have been updated
        db_user = getDBUser(message.author.id)
        db_quester = getDBQuestMember(message.author.id,0)
        if(db_user == None):
            await message.channel.send("```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
        elif(db_quester == None):
            await message.channel.send("```diff\n- I couldn't find your name on the quest board. Are you sure you're signed up? If you are, contact an admin immediately.\n```")
        else:
            await message.channel.send( "```diff\n+ Please wait as we update your personal quests list...\n```")
            for x in range(quest_amount):
                db_quester = getDBQuestMember(message.author.id,x)
                if(db_quester == None):
                    new_quester = QuestsMembers(usrId = message.author.id, questId = x, name=message.author.name,completed = False, progress = 0)
                    session.add(new_quester)

            await message.channel.send( "```diff\n+ Successfully updated your quests list!\n```")
            session.commit()

    elif message.content.lower().startswith('!create') and message.author != message.author.guild.me and message.author.top_role >= adminRole:
        #Command for admins to create the quest table, and to update it when any new ones are added
        await message.channel.send( "```Markdown\n# Running quests list update\n```")
        await createQuestTable()
        await message.channel.send( "```diff\n+ Updated the questslist!\n```")

    elif message.content.lower().startswith('!resq') and message.author != message.author.guild.me and message.author.top_role >= adminRole:
        #test method to reset quests (abstract out resetting to its own method)
        for x in range(quest_amount):
            db_quester = getDBQuestMember(message.author.id,x)
            db_quester.completed = 0
            db_quester.progress = 0
            session.commit()
        #commit session
        await message.channel.send("nothing")

    #add in extra part to limit to only a certain quest if specified, otherwise it sends all
    elif message.content.lower().startswith('!board') and message.author != message.author.guild.me:
        db_quester = getDBQuestMember(message.author.id,0)
        db_user = getDBUser(message.author.id)
        parse = message.content.split(" ")

        if(db_user == None):
            await message.channel.send("```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
        elif(db_quester == None):
            await message.channel.send("```diff\n- I couldn't find your name on the quest board. Are you sure you're signed up? If you are, contact an admin immediately.\n```")
        else:

            if(len(parse) > 1 and isNumber(parse[1])):
                item = parse[1]
                user = discord.utils.get(client.get_all_members(), id=message.author.id)
                await message.channel.send( "```diff\n+ Please wait as we send you the quest progress data...\n```")
                embedQ = discord.Embed(color=0xFF85FF)
                db_questitem = getDBQuestItem(item)
                db_quester = getDBQuestMember(message.author.id,item)
                if(db_questitem != None):
                    qName = "__**QUEST {0}**__".format(item)
                    qTask = db_questitem.description
                    qProgress = db_quester.progress
                    qGoal = db_questitem.completion
                    embedQ.add_field(name=qName, value=qTask, inline=False)
                    embedQ.add_field(name='Your current progress', value=qProgress, inline=False)
                    embedQ.add_field(name='Amount needed', value=qGoal, inline=False)
                    await user.send(embed=embedQ)
                    await message.channel.send( "```diff\n+ Your progress on quests hass been sent!\n```")
                else:
                    await message.channel.send( "```diff\n+ Quest #{0} is not a valid quest, please refer back to the quest board for available quests!\n```".format(item))
            elif(len(parse) > 1 and str(parse[1]).lower() == "all"):
                # use split command to check for number and correspond that with a quest
                user = discord.utils.get(client.get_all_members(), id=message.author.id)
                await message.channel.send( "```diff\n+ Please wait as we send you the quest progress data...\n```")
                for x in range(quest_amount):
                    embedQ = discord.Embed(color=0xFF85FF)
                    db_questitem = getDBQuestItem(x)
                    db_quester = getDBQuestMember(message.author.id,x)
                    qName = "__**QUEST {0}**__".format(x)
                    qTask = db_questitem.description
                    qProgress = db_quester.progress
                    qGoal = db_questitem.completion
                    embedQ.add_field(name=qName, value=qTask, inline=False)
                    embedQ.add_field(name='Your current progress', value=qProgress, inline=False)
                    embedQ.add_field(name='Amount needed', value=qGoal, inline=False)
                    await user.send(embed=embedQ)
                await message.channel.send( "```diff\n+ Your progress on quests hass been sent!\n```")
            else:
                await message.channel.send( "```diff\n+ Please enter in the board command with the number of a quest or \"all\"!\n```")

async def updateRoles(serv):
    #get all rows and put into memory
    for dbUser in session.query(User).all():
        streak = dbUser.streak
        member = False #default value
        #if the default value is retained (we didn't find a user)
        #then do nothing. This caused the old bug
        for person in serv.members:
            if dbUser.id == person.id:
                member = person
        #if we found a member,
        if(member != False):
            #identify the role they should have
            streakRank = None
            if streak >= 2000:
                streakRank = discord.utils.get(serv.roles, name="2000+ Streak")
            elif streak >= 999:
                streakRank = discord.utils.get(serv.roles, name="999+ Streak")
            elif streak >= 300:
                streakRank = discord.utils.get(serv.roles, name="300+ Streak")
            elif streak >= 250:
                streakRank = discord.utils.get(serv.roles, name="250+ Streak")
            elif streak >= 200:
                streakRank = discord.utils.get(serv.roles, name="200+ Streak")
            elif streak >= 150:
                streakRank = discord.utils.get(serv.roles, name="150+ Streak")
            elif streak >= 120:
                streakRank = discord.utils.get(serv.roles, name="120+ Streak")
            elif streak >= 90:
                streakRank = discord.utils.get(serv.roles, name="90+ Streak")
            elif streak >= 60:
                streakRank = discord.utils.get(serv.roles, name="60+ Streak")
            elif streak >= 30:
                streakRank = discord.utils.get(serv.roles, name="30+ Streak")
            elif streak >= 25:
                streakRank = discord.utils.get(serv.roles, name="25+ Streak")
            elif streak >= 20:
                streakRank = discord.utils.get(serv.roles, name="20+ Streak")
            elif streak >= 15:
                streakRank = discord.utils.get(serv.roles, name="15+ Streak")
            elif streak >= 10:
                streakRank = discord.utils.get(serv.roles, name="10+ Streak")
            elif streak >= 5:
                streakRank = discord.utils.get(serv.roles, name="5+ Streak")

            #identify roles they should not have
            otherRoles = [r for r in member.roles if r.name in streak_roles]
            print(otherRoles)
            if(streakRank != None and streakRank in otherRoles):
                otherRoles.remove(streakRank)
            print(otherRoles)
            #remove the roles they shouldn't have
            if(len(otherRoles) > 0):
                await member.remove_roles( *otherRoles)
            #add the correct role
            if(streakRank != None and streakRank not in member.roles):
                await member.add_roles(streakRank)
                print("updating roles for {0} with streak {1}".format(member, streak))

async def linkSubmit(message, userToUpdate):
    url = message.content.split(" ")
    print('link submitting for ' + str(userToUpdate.name))
    print(str(userToUpdate.name) + "'s url - " + url[1])
    print('link submitting for ' + str(userToUpdate.name))
    #goes to quest or submit handlers
    await handleSubmit(message, userToUpdate, url[1])

async def normalSubmit(message, userToUpdate):
    print('submitting for ' + str(userToUpdate.name))
    #jsonstr = json.dumps(message.attachments[0])
    #jsondict = json.loads(jsonstr)
    #url = jsondict['url']
    url = message.attachments[0].url
    print(str(userToUpdate.name) + "'s url - " + url)

    print('normal submitting for ' + str(userToUpdate.name))
    await handleSubmit(message, userToUpdate, url)


async def handleSubmit(message, userToUpdate, url):
    curdate = datetime.utcnow()
    potentialstreak = curdate + timedelta(days=7)
    today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
    streakdate = "{0}-{1}-{2}".format(potentialstreak.month, potentialstreak.day, potentialstreak.year)
    print('getting filepath to download for ' + str(userToUpdate.name))
    filepath = os.getcwd()+"/"+today
    print('boob')
    #try to find user in database using id
    db_user = getDBUser(userToUpdate.id)
    print('boop')
    #first find if we have  the user in our list

    if (db_user == None):
        await message.channel.send( "```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
    else:
        #db_user is our member object

        #check if already submitted
        if db_user.submitted == 1:
            print(str(userToUpdate.name) + ' already submitted')
            await message.channel.send( "```diff\n- You seem to have submitted something today already!\n```")
        #otherwise, do the submit
        else:
            print('I am here')
            if url.lower().endswith('.png') or url.lower().endswith('.jpg') or url.lower().endswith('.gif') or url.lower().endswith('.jpeg'):
                #if message.channel.id == channel_ids['class_2']:
                #print('starting file download')
                #os.system('wget {0} -P {1}'.format(url, filepath))
                #print('finishing file download')

                #update the submit quest
                db_quester = getDBQuestMember(message.author.id,1)
                if(db_quester != None):
                    db_quester.progress = 1
                    await checkQuestCompletion(message.author.id,1)

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
                    await message.channel.send("```Markdown\n# @{0} Level Up! You are now level {1}!\n```".format(userToUpdate.name,current_level))
                #otherwise just increase exp
                else:
                    db_user.currentxp = str(new_xp_total)
                #update high score if it's higher
                if new_streak > db_user.highscore:
                    db_user.highscore = new_streak
                #write all new values to our cells
                db_user.totalsubmissions = newscore
                db_user.currency = newcurrency
                db_user.streak = new_streak
                db_user.submitted = 1
                db_user.expiry = potentialstreak
                #and push all cells to the database
                session.commit()
                print("finishing updating " + db_user.name + "'s stats")
                await message.channel.send( "```diff\n+ @{0} Submission Successful! Score updated!\n+ {1}xp gained.```".format(userToUpdate.name,xp_gained))
                #finally, add an adore to the submission
                await message.add_reaction( adoreEmoji)
                print("submit complete")
            else:
                await message.channel.send( "```diff\n- Not a png, jpg, or gif file```")

async def roletask():
    #Do a role update
    print("Performing Role Update")
    await botChannel.send( "```Markdown\n# Updating Roles Automatically...\n```")
    await updateRoles(tapeGuild)
    await botChannel.send( "```diff\n+ Updating roles was a happy little success!\n```")

async def housekeeper():
    db_contest = getDBContest(0)
    curdate = datetime.utcnow()
    today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)

    #get all rows and put into memory
    members = session.query(User).all()
    print("Housekeeping on " + str(len(members)) + " rows on " + today)

    if(db_contest != None):
        if(db_contest.mode == 2):
            days_left = (db_contest.end - curdate.date()).days
            # days_left = 0
            #contest has return to a closed state, manually change to a no contest state
            if(days_left == 0):
                db_contest.prompt = "The contest is closed, please wait until further announcements."
                db_contest.mode = 1


    for curr_member in members:
        print('housekeeping member {0}'.format(curr_member.name))
        # Update in batch
        #set user in beginning if its needed to PM a user
        user = discord.utils.get(client.get_all_members(), id=int(curr_member.id))
        if(user != None):
            #check for warning until streak decay begins
            days_left = (curr_member.expiry - curdate.date()).days
            if(curr_member.decaywarning == True and curr_member.streak > 0):
                if(days_left == 3):
                    try:
                        await user.send("You have 3 days until your streak begins to expire!\nIf you want to disable these warning messages then enter the command streakwarning off in the #bot-channel")
                    except:
                        print('couldn\'t send 3day message')
                elif(days_left == 1):
                    try:
                        await user.send("You have 1 day until your streak begins to expire!\nIf you want to disable these warning messages then enter the command streakwarning off in the #bot-channel")
                    except:
                        print('couldn\'t send 1day message')
        else:
            print('User no longer visible to bot, must be gone')

        #If we're past the streak
        if((curdate.date() - curr_member.expiry).days >= 0 and curr_member.streak > 0):

            pointReduce = pow(2,(curdate.date() - curr_member.expiry).days+1)
            #reduce streak by 2^(daysPastStreak+1), until streak is zero
            print("Removing {0} points from {1}'s streak".format(pointReduce,curr_member.name))
            curr_member.streak = max(curr_member.streak-pointReduce,0)
            #give a pm to warn about streak decay if member has left warnings on
            if(curr_member.decaywarning == True and user != None):
                try:
                    await user.send("Your streak has decayed by {0} points! Your streak is now {1}.\nIf you want to disable these warning messages then enter the command streakwarning off in the #bot-channel".format(str(pointReduce),str(curr_member.streak)))
                except:
                    print('couldn\'t  send decay message')

        # raffle check
        dbQuester = getDBQuestMember(curr_member.id,2)
        if(dbQuester != None and dbQuester.completed == False and curr_member.raffle == True):
            dbQuester.progress = 1

        # submit x amount of pieces quests
        # 3-9
        for x in range(3,10):
            dbQuester = getDBQuestMember(curr_member.id,x)
            if(dbQuester != None and dbQuester.completed == False):
                dbQuester.progress = curr_member.totalsubmissions

        # attain x amount of streak score
        # 10-22
        for x in range(10,23):
            dbQuester = getDBQuestMember(curr_member.id,x)
            if(dbQuester != None and dbQuester.completed == False):
                dbQuester.progress = curr_member.highscore

        # update dailies here (23-27)
        for x in range(23,28):
            dbQuester = getDBQuestMember(curr_member.id,x)
            if(dbQuester != None and dbQuester.completed == False):
                if(dbQuester.progress == 0 and curr_member.submitted == True):
                    dbQuester.progress = 1
                    print(1)
                elif(dbQuester.progress > 0 and curr_member.submitted == True):
                    dbQuester.progress = dbQuester.progress + 1
                    print(2)
                elif(dbQuester.progress > 0 and curr_member.submitted == False):
                    dbQuester.progress = 0
                else:
                    print("FAILURE TO CHECK PROPERLY")

        #Checks for quest completion here
        await checkQuests(curr_member.id)

    #commit all changes to the sheet at once
    #reset all member's submitted status
    stmt = update(User).values(submitted=0)
    session.execute(stmt)
    session.commit()
    print("housekeeping finished")

async def confirmDecision(user):
    def check(msg):
        return msg.content.startswith('!') and user == msg.author
    confirm = await client.wait_for('message' ,timeout=180, check=check)
    if confirm.content.lower().startswith('!yes'):
        return True
    elif confirm.content.lower().startswith('!no'):
        return False

#redo this to work with -message-
async def confirmContest(user):
    def check(msg):
        return msg.content.startswith('!') and msg.author == user
    confirm = await client.wait_for('message' ,timeout=180,check=check)
    if confirm.content.lower().startswith('!'):
        parse = confirm.content.split("!")
        return parse[1]

async def buyitem(itemName, price, author, channel):
    boughtItem = False
    db_user = getDBUser(author.id)

    if (db_user != None):
        buyer_amount = db_user.currency
        if buyer_amount >= price:
            await channel.send( "```Python\n@{0}, you have {1} currency. \n```\n```Markdown\n# You're about to purchase a {2} for {3} currency. To confirm type !yes, to decline, type !no.\n```".format(author.name, db_user.currency, itemName, price))
            try:
                confirm = await confirmDecision(author)
                if confirm:
                    new_buyer_balance = buyer_amount - price
                    db_user.currency = new_buyer_balance
                    session.commit()
                    boughtItem = True
                    await channel.send( "```diff\n+ {0} has been successfully purchased!\n```".format(itemName))
                else:
                    await channel.send( "```Markdown\n# Transaction cancelled.\n```")
            except:
                print("transaction with {0} timed out".format(author.name))
        else:
            await channel.send( "```Markdown\n- Not enough credits. {0} needed, you have {1}```".format(price, buyer_amount))
    else:
        await channel.send( "```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
    return boughtItem

#add in xp, accounts for levels
async def addXP(user,xp_amount):
    current_xp = user.currentxp
    xp_gained = xp_amount
    current_level = user.level
    next_level_required_xp = current_level*10 + 50
    new_xp_total = current_xp + xp_gained

    #while loop to get all the levels needed
    while new_xp_total >= next_level_required_xp:
        current_level = current_level + 1
        new_xp_total = new_xp_total - next_level_required_xp
        user.level = str(current_level)
        user.currentxp = str(new_xp_total)
        next_level_required_xp = current_level*10 + 50

    user.level = str(current_level)
    user.currentxp = str(new_xp_total)

#take away xp, accounts for levels
async def subXP(user,xp_amount):
    current_xp = user.currentxp
    xp_taken = xp_amount
    current_level = user.level
    next_level_required_xp = (current_level-1)*10 + 50
    new_xp_total = current_xp - xp_taken

    #while loop to take all the levels needed
    while new_xp_total < 0:
        current_level = current_level - 1

        if(current_level < 1):
            current_level = 1
            new_xp_total = 0
            break

        new_xp_total = new_xp_total + next_level_required_xp
        user.level = str(current_level)
        user.currentxp = str(new_xp_total)
        next_level_required_xp = (current_level-1)*10 + 50

    user.level = str(current_level)
    user.currentxp = str(new_xp_total)

async def createQuestTable():

    #tutorials

    #stats tutorial
    if(getDBQuestItem(0) == None):
        new_quest = QuestsList(questId = 0, description = "Use the !stats command once", completion = 1, award = 50)
        session.add(new_quest)
    #submit tutorial
    if(getDBQuestItem(1) == None):
        new_quest = QuestsList(questId = 1, description = "Successfully submit a piece to a submission channel", completion = 1, award = 50)
        session.add(new_quest)

    #raffle

    #Submit a raffle piece
    if(getDBQuestItem(2) == None):
        new_quest = QuestsList(questId = 2, description = "Successfully enter in a raffle piece for the monthly rafle", completion = 1, award = 50)
        session.add(new_quest)
    #have 5 overall submit
    if(getDBQuestItem(3) == None):
        new_quest = QuestsList(questId = 3, description = "Submit 5 pieces of art overall to the submission channels", completion = 5, award = 100)
        session.add(new_quest)
    #have 10 overall submits
    if(getDBQuestItem(4) == None):
        new_quest = QuestsList(questId = 4, description = "Submit 10 pieces of art overall to the submission channels", completion = 10, award = 500)
        session.add(new_quest)
    #have 20 overall submits
    if(getDBQuestItem(5) == None):
        new_quest = QuestsList(questId = 5, description = "Submit 20 pieces of art overall to the submission channels", completion = 20, award = 500)
        session.add(new_quest)
    #have 50 overall submits
    if(getDBQuestItem(6) == None):
        new_quest = QuestsList(questId = 6, description = "Submit 50 pieces of art overall to the submission channels", completion = 50, award = 500)
        session.add(new_quest)
    #have 100 overall submits
    if(getDBQuestItem(7) == None):
        new_quest = QuestsList(questId = 7, description = "Submit 100 pieces of art overall to the submission channels", completion = 100, award = 500)
        session.add(new_quest)
    #have 200 overall submits
    if(getDBQuestItem(8) == None):
        new_quest = QuestsList(questId = 8, description = "Submit 200 pieces of art overall to the submission channels", completion = 200, award = 500)
        session.add(new_quest)
    #have 300 overall submits
    if(getDBQuestItem(9) == None):
        new_quest = QuestsList(questId = 9, description = "Submit 300 pieces of art overall to the submission channels", completion = 300, award = 500)
        session.add(new_quest)

    #streaks

    #attain a 5+streak highscore
    if(getDBQuestItem(10) == None):
        new_quest = QuestsList(questId = 10, description = "Attain a streak highscore of 5", completion = 5, award = 100)
        session.add(new_quest)
    #attain a 10+streak highscore
    if(getDBQuestItem(11) == None):
        new_quest = QuestsList(questId = 11, description = "Attain a streak highscore of 10", completion = 10, award = 100)
        session.add(new_quest)
    #attain a 15+streak highscore
    if(getDBQuestItem(12) == None):
        new_quest = QuestsList(questId = 12, description = "Attain a streak highscore of 15", completion = 15, award = 100)
        session.add(new_quest)
    #attain a 20+streak highscore
    if(getDBQuestItem(13) == None):
        new_quest = QuestsList(questId = 13, description = "Attain a streak highscore of 20", completion = 20, award = 100)
        session.add(new_quest)
    #attain a 25+streak highscore
    if(getDBQuestItem(14) == None):
        new_quest = QuestsList(questId = 14, description = "Attain a streak highscore of 25", completion = 25, award = 100)
        session.add(new_quest)
    #attain a 30+streak highscore
    if(getDBQuestItem(15) == None):
        new_quest = QuestsList(questId = 15, description = "Attain a streak highscore of 30", completion = 30, award = 100)
        session.add(new_quest)
    #attain a 60+streak highscore
    if(getDBQuestItem(16) == None):
        new_quest = QuestsList(questId = 16, description = "Attain a streak highscore of 60", completion = 60, award = 100)
        session.add(new_quest)
    #attain a 90+streak highscore
    if(getDBQuestItem(17) == None):
        new_quest = QuestsList(questId = 17, description = "Attain a streak highscore of 90", completion = 90, award = 100)
        session.add(new_quest)
    #attain a 120+streak highscore
    if(getDBQuestItem(18) == None):
        new_quest = QuestsList(questId = 18, description = "Attain a streak highscore of 120", completion = 120, award = 100)
        session.add(new_quest)
    #attain a 150+streak highscore
    if(getDBQuestItem(19) == None):
        new_quest = QuestsList(questId = 19, description = "Attain a streak highscore of 150", completion = 150, award = 100)
        session.add(new_quest)
    #attain a 200+streak highscore
    if(getDBQuestItem(20) == None):
        new_quest = QuestsList(questId = 20, description = "Attain a streak highscore of 200", completion = 200, award = 100)
        session.add(new_quest)
    #attain a 250+streak highscore
    if(getDBQuestItem(21) == None):
        new_quest = QuestsList(questId = 21, description = "Attain a streak highscore of 250", completion = 250, award = 100)
        session.add(new_quest)
    #attain a 300+streak highscore
    if(getDBQuestItem(22) == None):
        new_quest = QuestsList(questId = 22, description = "Attain a streak highscore of 300", completion = 300, award = 100)
        session.add(new_quest)

    #time based quests (submitting daily for x time)
    if(getDBQuestItem(23) == None):
        new_quest = QuestsList(questId = 23, description = "Submit daily for 7 days", completion = 7, award = 100)
        session.add(new_quest)
    if(getDBQuestItem(24) == None):
        new_quest = QuestsList(questId = 24, description = "Submit daily for 30 days", completion = 30, award = 100)
        session.add(new_quest)
    if(getDBQuestItem(25) == None):
        new_quest = QuestsList(questId = 25, description = "Submit daily for 100 days", completion = 100, award = 100)
        session.add(new_quest)
    if(getDBQuestItem(26) == None):
        new_quest = QuestsList(questId = 26, description = "Submit daily for 200 days", completion = 200, award = 100)
        session.add(new_quest)
    if(getDBQuestItem(27) == None):
        new_quest = QuestsList(questId = 27, description = "Submit daily for 365 days", completion = 365, award = 100)
        session.add(new_quest)
    session.commit()

async def checkQuests(usrId):

    #checks through all quests per user
    for x in range(quest_amount):
        await checkQuestCompletion(usrId,x)


async def resetQuestProgress(usrId,questId):

    db_quester = getDBQuestMember(usrId,questId)
    if(db_quester != None):
        db_quester.completed = 0
        db_quester.progress = 0
        session.commit()

async def checkQuestCompletion(usrId,questId):

    db_quester = getDBQuestMember(usrId,questId)
    db_questitem = getDBQuestItem(questId)

    if(db_quester != None):

        if(db_quester.completed == False and db_quester.progress >= db_questitem.completion):
            await botChannel.send("<@{1}>, you have completed quest {0}!\n`{2}`".format(str(questId),usrId,db_questitem.description))
            db_quester.completed = True
            db_user = session.query(User).filter(User.id == usrId).one()
            await addXP(db_user,db_questitem.award)

    else:

        print('quest for user not found')

    session.commit()



def getDBUser(userID): #gets the database user based on the user's ID
    db_user = None #return none if we can't find a user
    try: #try to find user in database using id
        db_user = session.query(User).filter(User.id == userID).one()
    except sqlalchemy.orm.exc.NoResultFound:
        print('No user found, probably not registered')
    except sqlalchemy.orm.exc.MultipleResultsFound:
        print('Multiple users found, something is really broken!')
    return db_user #this value will be None or a valid user, make sure to check

def getDBContest(number): #gets the database user based on the user's ID
    db_contest = None
    try: #try to find user in database using id
        db_contest = session.query(Contest).filter(Contest.id == number).one()
    except sqlalchemy.orm.exc.NoResultFound:
        print('No user found, probably not registered')
    except sqlalchemy.orm.exc.MultipleResultsFound:
        print('Multiple users found, something is really broken!')
    return db_contest

def getDBQuestMember(number,quest): #gets the database user based on the user's ID and the quest number
    db_questmember = None
    try: #try to find user in database using id
        db_questmember = session.query(QuestsMembers).filter(QuestsMembers.usrId == number).filter(QuestsMembers.questId == quest).one()
    except sqlalchemy.orm.exc.NoResultFound:
        print('No user found, probably not registered')
    except sqlalchemy.orm.exc.MultipleResultsFound:
        print('Multiple users found, something is really broken!')
    return db_questmember

def getDBQuestItem(number): #gets the database user based on the user's ID
    db_questitem = None
    try: #try to find user in database using id
        db_questitem = session.query(QuestsList).filter(QuestsList.questId == number).one()
    except sqlalchemy.orm.exc.NoResultFound:
        print('No user found, probably not registered')
    except sqlalchemy.orm.exc.MultipleResultsFound:
        print('Multiple users found, something is really broken!')
    return db_questitem

def isNumber(num):
    try:
        int(num)
        return True
    except ValueError:
        return False

#do role update every 3 hours
scheduler.add_job(roletask, 'cron', hour='1,4,7,10,13,16,19,21')
#run housekeeping at 7am UTC
scheduler.add_job(housekeeper, 'cron', hour=7)
scheduler.start()
if(live):
    client.run('') #botross account
else:
    client.run('NTc2MjE4Mjk0MDUxMTQzNzAw.XNTYiQ.dBB--rLXp56FIVPrFySoUAjVs2A') #marsh test account
