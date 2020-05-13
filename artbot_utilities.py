import json
#SQLalchemy stuff
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
import discord
import time
import math
from datetime import date, timedelta, time, datetime
#declaration for User class is in here
from create_databases import Base, User, Contest, QuestsMembers, QuestsList

#Avoid using global variables here

def getDBUser(session, userID): #gets the database user based on the user's ID
	db_user = None #return none if we can't find a user
	try: #try to find user in database using id
		db_user = session.query(User).filter(User.id == userID).one()
	except sqlalchemy.orm.exc.NoResultFound:
		print('No user found, probably not registered')
	except sqlalchemy.orm.exc.MultipleResultsFound:
		print('Multiple users found, something is really broken!')
	return db_user #this value will be None or a valid user, make sure to check

def getDBContest(session, number): #gets the database user based on the user's ID
	db_contest = None
	try: #try to find user in database using id
		db_contest = session.query(Contest).filter(Contest.id == number).one()
	except sqlalchemy.orm.exc.NoResultFound:
		print('No contest found')
	except sqlalchemy.orm.exc.MultipleResultsFound:
		print('Multiple contests found, something is really broken!')
	return db_contest

def getDBQuestMember(session, number, quest): #gets the database user based on the user's ID and the quest number
	db_questmember = None
	try: #try to find user in database using id
		if quest == "all":
			db_questmember = session.query(QuestsMembers).filter(QuestsMembers.usrId == number)
		else:
			db_questmember = session.query(QuestsMembers).filter(QuestsMembers.usrId == number).filter(QuestsMembers.questId == quest).one()
	except sqlalchemy.orm.exc.NoResultFound:
		print('No user quest found, probably not registered')
	return db_questmember #may be multiple if we request all

def getDBQuestItem(session, number): #gets the database user based on the user's ID
	db_questitem = None
	try: #try to find user in database using id
		db_questitem = session.query(QuestsList).filter(QuestsList.questId == number).one()
	except sqlalchemy.orm.exc.NoResultFound:
		print('No quest item found')
	except sqlalchemy.orm.exc.MultipleResultsFound:
		print('Multiple items found, something is really broken!')
	return db_questitem

def getDBAutoQuests(session): #gets auto quests
	db_quests = session.query(QuestsList).filter(QuestsList.mode == "auto")
	return db_quests

def getDBManualQuests(session): #gets manual quests
	db_quests = session.query(QuestsList).filter(QuestsList.mode == "manual")
	return db_quests

def getDBResetQuests(session): #gets resetable quests
	db_quests = session.query(QuestsList).filter(QuestsList.reset == True)
	return db_quests

def isNumber(num):
	try:
		int(num)
		return True
	except ValueError:
		return False

async def confirmDecision(client, user):
	def check(msg):
		return msg.content.startswith('!') and user == msg.author
	confirm = await client.wait_for('message' ,timeout=60, check=check)
	if confirm.content.lower().startswith('!yes'):
		return True
	elif confirm.content.lower().startswith('!no'):
		return False

#redo this to work with -message-
async def confirmContest(client, user):
	def check(msg):
		return msg.content.startswith('!') and msg.author == user
	confirm = await client.wait_for('message' ,timeout=60,check=check)
	if confirm.content.lower().startswith('!'):
		parse = confirm.content.split("!")
		return parse[1]


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

async def buyitem(session, client,itemName, price, author, channel):
	boughtItem = False
	db_user = getDBUser(session, author.id)

	if (db_user != None):
		buyer_amount = db_user.currency
		if buyer_amount >= price:
			await channel.send( "```Python\n@{0}, you have {1} currency. \n```\n```Markdown\n# You're about to purchase a {2} for {3} currency. To confirm type !yes, to decline, type !no.\n```".format(author.name, db_user.currency, itemName, price))
			try:
				confirm = await confirmDecision(client, author)
				if confirm:
					new_buyer_balance = buyer_amount - price
					db_user.currency = new_buyer_balance
					session.commit()
					boughtItem = True
					await channel.send( "```diff\n+ {0} has been successfully purchased!\n```".format(itemName))
				else:
					await channel.send( "```Markdown\n# Transaction cancelled.\n```")
			except Exception as e:
				print("transaction with {0} timed out".format(author.name))
				print(e)
		else:
			await channel.send( "```Markdown\n- Not enough credits. {0} needed, you have {1}```".format(price, buyer_amount))
	else:
		await channel.send( "```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact an admin immediately.\n```")
	return boughtItem

async def checkQuests(session,config,usrId):

	#checks through all auto quests per user
	autoQuests = getDBAutoQuests(session)
	for x in autoQuests:
		await checkQuestCompletion(session,config, usrId,x.questId)


async def checkQuestCompletion(session,config, usrId,questId):

	db_quester = getDBQuestMember(session ,usrId,questId)
	db_questitem = getDBQuestItem(session ,questId)

	if(db_quester != None):

		if(db_quester.completed == False and db_quester.progress >= db_questitem.completion):
			await config.botChannel.send("<@{1}>, you have completed quest {0}!\n`{2}`".format(str(questId),usrId,db_questitem.description))
			await config.botChannel.send("`awarded {0} xp points!`".format(db_questitem.award))
			db_quester.completed = True
			db_user = session.query(User).filter(User.id == usrId).one()
			if(questId == 2):
				# raffle quest adds on 20 + current_streak_2
				await addXP(db_user,db_questitem.award + int(math.floor((db_user.streak)/2)))
			else:
				await addXP(db_user,db_questitem.award)

	else:

		print('quest for user not found')

	session.commit()
	

async def updateRoles(session, config,serv):
	#get all rows and put into memory
	for dbUser in session.query(User).all():
		streak = dbUser.streak
		member = False #default value
		#if the default value is retained (we didn't find a user)
		#then do nothing. This caused the old bug
		
		for person in serv.members:
			if str(dbUser.id) == str(person.id):
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
			otherRoles = [r for r in member.roles if r.name in config.streak_roles]
			#print(otherRoles)
			if(streakRank != None and streakRank in otherRoles):
				otherRoles.remove(streakRank)
			#print(otherRoles)
			#remove the roles they shouldn't have
			if(len(otherRoles) > 0):
				await member.remove_roles( *otherRoles)
			#add the correct role
			if(streakRank != None and streakRank not in member.roles):
				await member.add_roles(streakRank)
				print("updating roles for {0} with streak {1}".format(member, streak))
	print('Updating Roles Completed')


#This class stores the config information for the artbot.
#Keep this at bottom
class Config():
	live = False
	spreadsheet_schema = {}
	months = {}
	nonach_roles = []
	override_roles = []
	streak_roles= []
	eight_ball = []
	tapeGuild = ''
	botChannel = ''
	adminRole = ''
	adminRoleName = 'no-role'
	guildName = 'no-guild'
	botChannelName = 'no-channel'
	submitChannels = []
	adoreEmoji = 0
	adoreEmojiID = 0
	discordKey = ''
	
	def LoadFromFile(self, filename):
		data={}
		with open(filename) as json_file:  
			data = json.load(json_file)
		#read generic data
		self.spreadsheet_schema = data['all_config']['spreadsheet_schema']
		self.months = data['all_config']['months']
		self.nonach_roles = data['all_config']['nonach_roles']
		self.override_roles = data['all_config']['override_roles']
		self.streak_roles = data['all_config']['streak_roles']
		self.eight_ball = data['all_config']['eight_ball']
		#configure live or test data
		key = 'live_config' if self.live == True else 'test_config'
		self.adminRoleName = data[key]['adminRoleName']
		self.guildName = data[key]['guildName']
		self.botChannelName = data[key]['botChannelName']
		self.submitChannels = data[key]['submitChannels']
		self.adoreEmojiID = data[key]['adoreEmojiID']
		self.discordKey = data[key]['discordKey']
		
	def WriteToFile(self, filename):
		data = {}
		#generic config for both live and test
		data['all_config'] = {
			'spreadsheet_schema' : self.spreadsheet_schema,
			'months' : self.months,
			'nonach_roles' : self.nonach_roles,
			'override_roles' : self.override_roles,
			'streak_roles' : self.streak_roles,
			'eight_ball' : self.eight_ball
		}
		#data specific to live
		data['live_config'] = {
			'adminRoleName' : self.adminRoleName,
			'guildName' : self.guildName,
			'botChannelName' : self.botChannelName,
			'submitChannels' : self.submitChannels,
			'adoreEmojiID' : self.adoreEmojiID,
			'discordKey' : ' '
		}
		#data specific to test
		data['test_config'] = {
			'adminRoleName' : self.adminRoleName,
			'guildName' : self.guildName,
			'botChannelName' : self.botChannelName,
			'submitChannels' : self.submitChannels,
			'adoreEmojiID' : self.adoreEmojiID,
			'discordKey' : ' '
		}
		with open(filename, 'w') as outfile:  
			json.dump(data, outfile, indent=4)
			
