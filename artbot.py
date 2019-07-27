import discord
import logging
import datetime
import simplejson as json
import asyncio
import math
import random
import sys, traceback
import pytz
from artbot_utilities import *
from artbot_commands import *
from artbot_tests import *

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

config = Config()
config.live = True #Use this flag to change between live and test config

config.LoadFromFile('config.txt')

### Art bot by Whatsapokemon and MarshBreeze 2.0
### Simple bot for Discord designed to manage image collection.

logging.basicConfig(level = logging.ERROR)

client = discord.Client()

@client.event
async def on_ready():
	global config
	print('Bot Online. using {0} configuration'.format('LIVE' if config.live else 'TEST'))
	print(client.user.name)
	print(client.user.id)
	print('------')
	#Store the server and the bot command channel
	config.tapeGuild = discord.utils.find(lambda s: s.name == config.guildName, client.guilds)
	print("active server set to " + config.tapeGuild.name)
	config.botChannel = discord.utils.find(lambda c: c.name == config.botChannelName, config.tapeGuild.channels)
	print("bot channel set to " + config.botChannel.name)
	#admin role, admin actions require at least this role (or any with higher priority)
	config.adminRole = discord.utils.find(lambda r: r.name == config.adminRoleName, config.tapeGuild.roles)
	print("admin role set to " + config.adminRole.name)
	config.adoreEmoji = discord.utils.find(lambda e: e.id == config.adoreEmojiID, config.tapeGuild.emojis)
	print("adore emoji set to " + config.adoreEmoji.name)

@client.event
async def on_reaction_add(reaction, user):
	userToUpdate = reaction.message.author.id
	#if the submission is a proxy submission
	if(reaction.message.content.lower().startswith('!proxysubmit')):
		#Change attribution of proxy submits to the mentioned user
		userToUpdate = reaction.message.mentions[0].id
	try:
		if type(reaction.emoji) is discord.Emoji:
			if ((user.id != userToUpdate and reaction.emoji.id == config.adoreEmoji.id and (reaction.message.content.startswith("!submit") or reaction.message.content.startswith("!proxysubmit"))) or
				(user.id == reaction.message.guild.me.id and reaction.emoji.id == config.adoreEmoji.id and reaction.message.content.startswith("TEST MESSAGE"))):
				print("reaction added " + user.name + " " + str(reaction.emoji))
				#find user in database using id
				db_user = getDBUser(session, userToUpdate)
				#increase adores by 1
				db_user.adores = db_user.adores+1
				#commit session
				session.commit()
	except:
		print("Adding reaction broke for user " + str(userToUpdate))
		traceback.print_exc(file=sys.stdout)

@client.event
async def on_reaction_remove(reaction, user):
	userToUpdate = reaction.message.author.id
	#if the submission is a proxy submission
	if(reaction.message.content.lower().startswith('!proxysubmit')):
		#Change attribution of proxy submits to the mentioned user
		userToUpdate = reaction.message.mentions[0].id
	try:
		if type(reaction.emoji) is discord.Emoji:
			if ((user.id != userToUpdate and reaction.emoji.id == config.adoreEmoji.id and (reaction.message.content.startswith("!submit") or reaction.message.content.startswith("!proxysubmit"))) or
				(user.id == reaction.message.guild.me.id and reaction.emoji.id == config.adoreEmoji.id and reaction.message.content.startswith("TEST MESSAGE"))):
				print("reaction removed " + user.name + " " + str(reaction.emoji))
				#find user in database using id
				db_user = getDBUser(session, userToUpdate)
				#increase adores by 1
				db_user.adores = db_user.adores-1
				#commit session
				session.commit()
	except:
		print("Adding reaction broke for user " + str(userToUpdate))
		traceback.print_exc(file=sys.stdout)


@client.event
async def on_message(message):
	if message.content.lower() == "+test":
		await testCommands(session, config, client, message)
	else:
		await handleCommands(session, config, client, message)



async def roletask():
	#Do a role update
	print("Performing Role Update")
	await config.botChannel.send( "```Markdown\n# Updating Roles Automatically...\n```")
	await updateRoles(session, config,config.tapeGuild)
	await config.botChannel.send( "```diff\n+ Updating roles was a happy little success!\n```")

async def housekeeper():
	db_contest = getDBContest(session,0)
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
		dbQuester = getDBQuestMember(session, curr_member.id,2)
		if(dbQuester != None and dbQuester.completed == False and curr_member.raffle == True):
			dbQuester.progress = 1

		# submit x amount of pieces quests
		# 3-9
		for x in range(3,10):
			dbQuester = getDBQuestMember(session ,curr_member.id,x)
			if(dbQuester != None and dbQuester.completed == False):
				dbQuester.progress = curr_member.totalsubmissions

		# attain x amount of streak score
		# 10-22
		for x in range(10,23):
			dbQuester = getDBQuestMember(session,curr_member.id,x)
			if(dbQuester != None and dbQuester.completed == False):
				dbQuester.progress = curr_member.highscore

		# update dailies here (23-27)
		for x in range(23,28):
			dbQuester = getDBQuestMember(session,curr_member.id,x)
			if(dbQuester != None and dbQuester.completed == False):
				if(dbQuester.progress == 0 and curr_member.submitted == True):
					dbQuester.progress = 1
				elif(dbQuester.progress > 0 and curr_member.submitted == True):
					dbQuester.progress = dbQuester.progress + 1
				elif(dbQuester.progress > 0 and curr_member.submitted == False):
					dbQuester.progress = 0

		#Checks for quest completion here
		await checkQuests(session,config,curr_member.id)

	#commit all changes to the sheet at once
	#reset all member's submitted status
	stmt = update(User).values(submitted=0)
	session.execute(stmt)
	session.commit()
	print("housekeeping finished")


#do role update every 3 hours
scheduler.add_job(roletask, 'cron', hour='1,4,7,10,13,16,19,21')
#run housekeeping at 7am UTC
scheduler.add_job(housekeeper, 'cron', hour=7) #hour=7
scheduler.start()
client.run(config.discordKey) #Runs live or not live depending on flag set at top of file
