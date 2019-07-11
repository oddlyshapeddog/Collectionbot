import discord
import sys, traceback
import asyncio
from artbot_utilities import *
from artbot_commands import *
import concurrent.futures
#from artbot import on_reaction_remove

#SQLalchemy stuff
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update
import time
from datetime import date, timedelta, time, datetime
#declaration for User class is in here
from create_databases import Base, User, Contest, QuestsMembers, QuestsList

testServer = 244805504235339777
testChannel = 386395766505340939

async def testCommands(session, config, client, message, live):
	if(live): return #We don't want to do this on a live server

	message = await config.botChannel.send( "TEST MESSAGE")
	message.content = "!REGISTER"
	
	
	#REGISTER
	try:
		await handleCommands(session, config, client, message)
		print("!REGISTER FUNCTION PASSED")
	except Exception as e: 
		print("ERROR IN !REGISTER COMMAND")
		print(e); traceback.print_exc(file=sys.stdout)
	#STATS
	message.content = "!STATS"
	try: 
		await handleCommands(session, config, client, message)
		print("!STATS FUNCTION PASSED")
	except Exception as e: 
		print("ERROR IN !STATS COMMAND")
		print(e); traceback.print_exc(file=sys.stdout)
	#SUBMIT
	message.content = "!SUBMIT https://i.imgur.com/lEyDOyL.png"
	try: 
		await handleCommands(session, config, client, message)
		print("!SUBMIT FUNCTION PASSED")
	except Exception as e: 
		print("ERROR IN !SUBMIT COMMAND")
		print(e); traceback.print_exc(file=sys.stdout)
	#TESTING ADORES
	try:
		reaction, user = await client.wait_for('reaction_add', timeout=5.0, check=lambda reaction, user: reaction.emoji.id == config.adoreEmoji.id)
		me = session.query(User).filter(User.id == config.tapeGuild.me.id).one()
		message=reaction.message
		if(me.adores > 0): print("!ADD ADORE FUNCTION PASSED")
		else: raise Exception("ERROR IN ADD ADORES COMMAND")
		await message.reactions[0].remove(config.tapeGuild.me)
		await asyncio.sleep(2)
		if(me.adores == 0): print("!REMOVE ADORE FUNCTION PASSED")
		else: raise Exception("ERROR IN REMOVE ADORES COMMAND")
	except Exception as e: 
		print(e); traceback.print_exc(file=sys.stdout)
	#ACH
	message.content = "!ACH"
	try: 
		await handleCommands(session, config, client, message)
	except Exception as e: 
		print("ERROR IN !ACH COMMAND")
		print(e); traceback.print_exc(file=sys.stdout)
	#TIMELEFT
	message.content = "!TIMELEFT"
	try: 
		await handleCommands(session, config, client, message)
	except Exception as e: 
		print("ERROR IN !TIMELEFT COMMAND")
		print(e); traceback.print_exc(file=sys.stdout)
	#NSFWJOIN
	message.content = "!NSFWJOIN"
	try: 
		await handleCommands(session, config, client, message)
		#do we have the NSFW role?
		role = discord.utils.get(config.tapeGuild.me.roles, name="NSFW Artist")
		if(role == None): raise Exception("ERROR IN !NSFWJOIN COMMAND")
		else: print("!NSFWJOIN FUNCTION PASSED")
	except Exception as e: 
		print("ERROR IN !NSFWJOIN COMMAND")
		print(e); traceback.print_exc(file=sys.stdout)
	#NSFWLEAVE
	message.content = "!NSFWLEAVE"
	try: 
		await handleCommands(session, config, client, message)
		#do we have the NSFW role?
		role = discord.utils.get(config.tapeGuild.me.roles, name="NSFW Artist")
		if(role != None): raise Exception("ERROR IN !NSFWLEAVE COMMAND")
		else: print("!NSFWLEAVE FUNCTION PASSED")
	except Exception as e: 
		print("ERROR IN !NSFWLEAVE COMMAND")
		print(e); traceback.print_exc(file=sys.stdout)
	#IDEA
	message.content = "!IDEA A LARGE BUTT"
	try: 
		await handleCommands(session, config, client, message)
		print("!IDEA FUNCTION PASSED")
	except Exception as e: 
		print("ERROR IN !IDEA COMMAND")
		print(e); traceback.print_exc(file=sys.stdout)
	#ARTBLOCK
	message.content = "!ARTBLOCK"
	try: 
		await handleCommands(session, config, client, message)
		print("!ARTBLOCK FUNCTION PASSED")
	except Exception as e: 
		print("ERROR IN !ARTBLOCK COMMAND")
		print(e); traceback.print_exc(file=sys.stdout)
	#8BALL
	message.content = "!8BALL"
	try: 
		await handleCommands(session, config, client, message)
		print("!8BALL FUNCTION PASSED")
	except Exception as e: 
		print("ERROR IN !8BALL COMMAND")
		print(e); traceback.print_exc(file=sys.stdout)
	#ROLL
	message.content = "!ROLL 1D20"
	try: 
		await handleCommands(session, config, client, message)
		print("!ROLL FUNCTION PASSED")
	except Exception as e: 
		print("ERROR IN !ROLL COMMAND")
		print(e); traceback.print_exc(file=sys.stdout)
	#VACATION
	message.content = "!VACATION"
	try: 
		#Give self enough currency
		me = session.query(User).filter(User.id == config.tapeGuild.me.id).one()
		me.currency = 10000
		session.commit()
		#send the !vacation command and the !yes response in two async threads
		loop = asyncio.get_event_loop()
		t1 = loop.create_task(sendCommand(session, config, client, message))
		t2 = loop.create_task(sendYes(config))
		await t1
		await t2
		asyncio.sleep(3)
		if(me.currency >= 10000): raise Exception()
		else: print("!VACATION FUNCTION PASSED")
	except Exception as e: 
		print("ERROR IN !VACATION COMMAND")
		print(e); traceback.print_exc(file=sys.stdout)
	#VACATION
	message.content = "!BUY MYSTERY"
	try: 
		#Give self enough currency
		me = session.query(User).filter(User.id == config.tapeGuild.me.id).one()
		me.currency = 10000
		session.commit()
		#send the !buy command and the !yes response in two async threads
		loop = asyncio.get_event_loop()
		t1 = loop.create_task(sendCommand(session, config, client, message))
		t2 = loop.create_task(sendYes(config))
		await t1
		await t2
		asyncio.sleep(3)
		if(me.currency >= 10000): raise Exception()
		else: print("!BUY FUNCTION PASSED")
	except Exception as e: 
		print("ERROR IN !BUY COMMAND")
		print(e); traceback.print_exc(file=sys.stdout)
	#VACATION
	message.content = "!OVERRIDE 10"
	try: 
		#Give self enough currency
		me = session.query(User).filter(User.id == config.tapeGuild.me.id).one()
		me.streak = 300
		me.highscore = 300
		session.commit()
		#send the !override command and the !yes response in two async threads
		loop = asyncio.get_event_loop()
		t1 = loop.create_task(sendCommand(session, config, client, message))
		t2 = loop.create_task(sendYes(config))
		await t1
		await t2
		asyncio.sleep(3)
		if(discord.utils.get(config.tapeGuild.me.roles, name="Override (10+)") == None): raise Exception()
		else: print("!OVERRIDE FUNCTION PASSED")
	except Exception as e: 
		print("ERROR IN !OVERRIDE COMMAND")
		print(e); traceback.print_exc(file=sys.stdout)
	#STREAKWARNING
	try: 
		me = session.query(User).filter(User.id == config.tapeGuild.me.id).one()
		message.content = "!STREAKWARNING"
		await handleCommands(session, config, client, message)
		message.content = "!STREAKWARNING OFF"
		#send the !streakwarning command and the !yes response in two async threads
		loop = asyncio.get_event_loop()
		t1 = loop.create_task(sendCommand(session, config, client, message))
		t2 = loop.create_task(sendYes(config))
		await t1
		await t2
		asyncio.sleep(3)
		if(me.decaywarning != False): raise Exception("Streakwarning didn't turn off")
		message.content = "!STREAKWARNING ON"
		#send the !streakwarning command and the !yes response in two async threads
		loop = asyncio.get_event_loop()
		t1 = loop.create_task(sendCommand(session, config, client, message))
		t2 = loop.create_task(sendYes(config))
		await t1
		await t2
		asyncio.sleep(3)
		if(me.decaywarning != True): raise Exception("Streakwarning didn't turn on")
		
		print("!STREAKWARNING FUNCTION PASSED")
	except Exception as e: 
		print("ERROR IN !STREAKWARNING COMMAND")
		print(e); traceback.print_exc(file=sys.stdout)
	#BOARD
	message.content = "!BOARD"
	try: 
		await handleCommands(session, config, client, message)
		print("!BOARD FUNCTION PASSED")
	except Exception as e: 
		print("ERROR IN !BOARD COMMAND")
		print(e); traceback.print_exc(file=sys.stdout)
	
		
	#REMOVE SELF FROM DATABASE
	session.query(User).filter(User.id == config.tapeGuild.me.id).delete()
	session.query(QuestsMembers).filter(QuestsMembers.usrId == config.tapeGuild.me.id).delete()
	#db_me = getDBUser(session, config.tapeGuild.me.id)
	#my_quests = getDBQuestMember(session, config.tapeGuild.me.id, 'all')
	#session.delete().where()
	#session.delete(db_me)
	session.commit()
	print("TESTS COMPLETED")

	
async def sendCommand(session, config, client, message):
	await handleCommands(session, config, client, message)

async def sendYes(config):
	await asyncio.sleep(2)
	await config.botChannel.send( "!YES")