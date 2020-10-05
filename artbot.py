import discord
import logging
import datetime
import simplejson as json
import asyncio
import math
import random
import sys, traceback
import pytz
from os import environ
from artbot_utilities import *
from artbot_commands import *
from artbot_tests import *
import threading

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
config.live = False # Use this flag to change between live and test config
if environ.get('LIVE') is not None:
	config.live = True
config.LoadFromFile('config.json')

### Art bot by Whatsapokemon and MarshBreeze 2.0
### Simple bot for Discord designed to manage image collection.

logging.basicConfig(level = logging.ERROR)

client = discord.Client(fetch_offline_members=True, heartbeat_timeout=90.0)

SEPARATOR = '--------'

@client.event
async def on_ready():
	global config
	print('Bot Online. using {0} configuration'.format('LIVE' if config.live else 'TEST'))
	print('Bot name: {0}'.format(client.user.name))
	print('Bot client ID: {0}'.format(client.user.id))
	print(SEPARATOR)

	try:
		#Store the server and the bot command channel
		config.tapeGuild = discord.utils.find(lambda s: s.name == config.guildName, client.guilds)
		if (not config.tapeGuild):
			raise Exception('Discord server not found: {0}'.format(config.guildName))
		print("active server set to " + config.tapeGuild.name)

		config.botChannel = discord.utils.find(lambda c: c.id == config.botChannelName or c.name == config.botChannelName, config.tapeGuild.channels)
		if (not config.botChannel):
			raise Exception('Channel not found: {0}'.format(config.botChannelName))
		print("bot channel set to " + config.botChannel.name)
		#admin role, admin actions require at least this role (or any with higher priority)
		config.adminRole = discord.utils.find(lambda r: r.name == config.adminRoleName, config.tapeGuild.roles)
		if (not config.adminRole):
			raise Exception('Role not found: {0}'.format(config.adminRoleName))
		print("admin role set to " + config.adminRole.name)
		config.adoreEmoji = discord.utils.find(lambda e: e.id == config.adoreEmoji or e.name == config.adoreEmoji, config.tapeGuild.emojis)
		if (not config.adoreEmoji):
			raise Exception('Emoji not found: {0}'.format(config.adoreEmoji))
		print("adore emoji set to " + config.adoreEmoji.name)
		config.adminChannel = discord.utils.find(lambda c: c.id == config.adminChannelName or c.name == config.adminChannelName, config.tapeGuild.channels)
		if (not config.adminChannel):
			raise Exception('Channel not found: {0}'.format(adminChannelName))
		print("admin channel set to " + config.adminChannel.name)
		print(SEPARATOR)
	except Exception as e:
		print('Bot initialization error:', e)
		sys.exit(1)

	try:
		await config.adminChannel.send(config.on_join_message)
	except Exception as e:
		print('Unable to post to #{0}'.format(config.adminChannelName), e)
		sys.exit(1)


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
	await config.adminChannel.send( "```Markdown\n# Updating Roles Automatically...\n```")
	await updateRoles(session, config,config.tapeGuild)
	await config.adminChannel.send( "```diff\n+ Updating roles was a happy little success!\n```")

def housekeeper_start():
	thread = threading.Thread(target=housekeeper_create_loop)
	thread.start()
	
def housekeeper_create_loop():
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	
	engine = create_engine('sqlite:///TAPE_Database.db')
	Base.metadata.bind = engine
	DBSession = sessionmaker(bind=engine)
	#create new database session
	new_session = DBSession()
	loop.run_until_complete(housekeeper(new_session))

async def housekeeper(session):
	db_contest = getDBContest(session,0)
	curdate = datetime.utcnow()
	today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
	
	#get all rows and put into memory
	members = session.query(User).all()
	print("Housekeeping on " + str(len(members)) + " rows on " + today)
	print("Doing quest completions")
	
	##if False:
	for curr_member in members:
		member_quests = getDBQuestMember(session, curr_member.id, "all")
		#print('Checking quest completion for {0}'.format(curr_member.name))
		
		if member_quests.count() > 0:
			for quest in member_quests:
				# raffle check
				if(quest.questId == 2):
					if(quest.completed == False and curr_member.raffle == True):
						quest.progress = 1
				# submit x amount of pieces quests
				# 3-9
				if (quest.questId >= 3 and quest.questId <= 9):
					if(quest.completed == False):
						quest.progress = curr_member.totalsubmissions
				# attain x amount of streak score
				# 10-22
				if (quest.questId >= 10 and quest.questId <= 22):
					if(quest.completed == False):
						quest.progress = curr_member.highscore
				# update dailies here (23-27) 
				if (quest.questId >= 23 and quest.questId <= 27):
					if(quest.completed == False):
						if(quest.progress == 0 and curr_member.submitted == True):
							quest.progress = 1
						elif(quest.progress > 0 and curr_member.submitted == True):
							quest.progress = quest.progress + 1
						elif(quest.progress > 0 and curr_member.submitted == False):
							quest.progress = 0
	
	print("Doing submitted status reset")
	#reset all member's submitted status
	stmt = update(User).values(submitted=0)
	session.execute(stmt)
	session.commit()

	print("Contest block")
	if(db_contest != None):
		if(db_contest.mode == 2):
			days_left = (db_contest.end - curdate.date()).days
			# days_left = 0
			#contest has return to a closed state, manually change to a no contest state
			if(days_left == 0):
				db_contest.prompt = "The contest is closed, please wait until further announcements."
				db_contest.mode = 1

	#commit all changes to the sheet at once
	session.commit()
	print("housekeeping finished")

async def decayFunction():
	members = session.query(User).all()
	curdate = datetime.utcnow()
	today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
	
	print("Decay")
	warn_count = 0;
	decay_count = 0;
	for curr_member in members:
		#print('housekeeping member {0}'.format(curr_member.name))
		# Update in batch
		#set user in beginning if its needed to PM a user
		user = discord.utils.get(client.get_all_members(), id=int(curr_member.id))
		if(user != None):
			#check for warning until streak decay begins
			days_left = (curr_member.expiry - curdate.date()).days
			if(curr_member.decaywarning == True and curr_member.streak > 0):
				if(days_left == 3):
					try:
						warn_count=warn_count+1
						await user.send("You have 3 days until your streak begins to expire!\nIf you want to disable these warning messages then enter the command streakwarning off in #{0}".format(config.botChannelName))
					except:
						print('couldn\'t send 3day message to ' + curr_member.name)
				elif(days_left == 1):
					try:
						warn_count=warn_count+1
						await user.send("You have 1 day until your streak begins to expire!\nIf you want to disable these warning messages then enter the command streakwarning off in #{0}".format(config.botChannelName))
					except:
						print('couldn\'t send 1day message to ' + curr_member.name)
		#else:
			#print('User no longer visible to bot, must be gone')

		#If we're past the streak
		if((curdate.date() - curr_member.expiry).days >= 0 and curr_member.streak > 0):
			pointReduce = pow(2,(curdate.date() - curr_member.expiry).days+1)
			#reduce streak by 2^(daysPastStreak+1), until streak is zero
			#print("Removing {0} points from {1}'s streak".format(pointReduce,curr_member.name))
			curr_member.streak = max(curr_member.streak-pointReduce,0)
			#give a pm to warn about streak decay if member has left warnings on
			if(curr_member.decaywarning == True and user != None):
				decay_count=decay_count+1
				await user.send("Your streak has decayed by {0} points! Your streak is now {1}.\nIf you want to disable these warning messages then enter the command streakwarning off in #{2}".format(str(pointReduce),str(curr_member.streak), config.botChannelName))
				
	print("warned " + str(warn_count) + " and told " + str(decay_count) + " about decay")
	session.commit() #commit decay changes to database

async def questCompleteFunction():
	members = session.query(User).all()
	print("Checking quests for all members")
	
	await checkAllUsersQuests(session, config)
	print("Finished checking quests")
	
async def raffle_notification():
	#warn admins that the raffle has ended.
	mentionString = config.adminRole.mention
	await config.adminChannel.send( "{}\n```It's the start of the new month, don't forget the raffle!```".format(mentionString))

if environ.get('DISCORD_KEY') is not None:
	discordKey = environ.get('DISCORD_KEY')
else:
	discordKey = config.discordKey 
if (not discordKey):
	raise Exception('Your config.txt file is missing a discord key; get one here: https://discord.com/developers/applications/')

#do role update every 3 hours
scheduler.add_job(roletask, 'cron', hour='2,5,8,11,14,17,20,22')
#run housekeeping at 7am UTC
scheduler.add_job(housekeeper_start, 'cron', hour=7, minute=0) #hour=7:00
#warn users about their decay
scheduler.add_job(decayFunction, 'cron', hour=7, minute=2) #hour=7:02
scheduler.add_job(questCompleteFunction, 'cron', hour=7, minute=4) #hour=7:04
scheduler.add_job(raffle_notification, 'cron', day=1, hour=7, minute=15) #hour=7:15
scheduler.start()

try:
	client.run(discordKey) #Runs live or not live depending on flag set at top of file
except discord.errors.HTTPException as httpException:
	print ("Discord HTTP exception: {}".format(httpException))
except discord.errors.LoginFailure as httpException:
	print ("Discord login failure: {} Make sure your DISCORD_KEY environment variable is set to a valid Discord key.".format(httpException))
except:
	print ("Unexpected Discord error: {}".format(sys.exc_info()[0]))