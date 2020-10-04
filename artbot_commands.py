import discord
import random
import datetime
import sys
import math
from artbot_utilities import *
import os
#from artbot import *
#Avoid using global variables here

async def handleCommands(session, config, client, message):
	if message.content.lower() == "f" and message.channel.id == "279098440820981760":
		await message.channel.send( "```Markdown\n {0} has paid their respects.\n```".format(message.author))
	elif message.content.lower().startswith('!submit'):
		if (message.channel.id in config.submitChannels or message.channel.name in config.submitChannels):
			#print(message.embeds[0].description)
			#print(message.embeds[0].thumbnail.url)
			#print(message.embeds[0].thumbnail.proxy_url)
			#print(message.embeds[0].provider)
			filetypes = config.allowed_submission_filetypes
			if(("https://" in message.content.lower() or "http://" in message.content.lower()) and (any(u in message.content.lower() for u in filetypes))):
				# do linksubmit
				print("link submission")
				await linkSubmit(session, config, message, message.author)
			elif (message.attachments != None and len(message.attachments) > 0):
				try:
					print("normal submission")
					#normal submit.
					await normalSubmit(session, config, message, message.author)
				except:
					pass
			
			else:
				await message.channel.send( "```diff\n- Invalid submission, need supported link or attachment```")
		else:
			await message.channel.send( "`Whoopsies, you can't submit in this channel!`")
	# elif message.content.lower().startswith('!register'):
	# 	curdate = datetime.utcnow()
	# 	today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
	# 	already_registered = False
	# 	#try to find user in database using id
	# 	db_user = getDBUser(session, message.author.id)
	# 	serv = message.guild
	# 	foundrole = discord.utils.find(lambda r: r.name == 'Artists', message.author.roles)
	# 	na = discord.utils.find(lambda r: r.name == 'New Artist', message.author.roles)

	# 	#add a new user if there's no registered user
	# 	if (db_user == None):
	# 		#create new user object
	# 		new_user = User(name=message.author.name, level=1, id=message.author.id, startdate=curdate, currency=0, streak=0, expiry=curdate, submitted=0, raffle=0, promptsadded=0, totalsubmissions=0, currentxp=0, adores=0, highscore=0, decaywarning=True)
	# 		#add to session
	# 		session.add(new_user)
	# 		#make user's quest board
	# 		db_quests = session.query(QuestsList)
	# 		for quest in db_quests:
	# 			new_quester = QuestsMembers(usrId = message.author.id, questId = quest.questId, name=message.author.name,completed = False, progress = 0)
	# 			session.add(new_quester)
	# 		#give relevant roles
	# 		for rank in serv.roles:
	# 			if rank.name == "0+ Streak":
	# 				await message.author.add_roles(rank)
	# 		for rank in serv.roles:
	# 			if rank.name == "New Artist":
	# 				await message.author.add_roles(rank)
	# 		#commit session
	# 		session.commit()
	# 		await message.channel.send( "```diff\n+ Successfully registered!\n```")
	# 	elif (db_user != None and foundrole == None and na == None):
	# 		aRole = discord.utils.find(lambda r: r.name == 'Artists', serv.roles)
	# 		await message.author.add_roles( aRole)
	# 		await message.channel.send( "```Markdown\n# You're registered, I'll give you your Artist role back!\n```")
	# 	else:
	# 		await message.channel.send( "```Markdown\n# You're already registered!\n```")

	elif message.content.lower().startswith('!help'):
		helpString = """```Markdown
# Here's a quick little starter guide for all of you happy little artists wishing to earn experience by submitting artwork.
# To submit content, drag and drop the file (.png, .gif, .jpg) into {0} and add '!submit' as a comment to it.
# If you'd like to submit via internet link, make sure you right click the image and select 'copy image location' and submit that URL using the !submit command.
# The !timeleft command will let you know how much longer you have left to submit for the day!
# To see your current scorecard, type !stats in the {1} channel
# To see your achievement status, type !ach
# To turn on or off the PM warning system about your streak use the command !streakwarning on or !streakwarning off.
```""".format(config.submitChannels[0], config.botChannel)
	# 	helpString = helpString . """```diff
	# - For those of our older artists, you may access the nsfw channels by typing !nsfwjoin and you can hide those channels by typing !nsfwleave. 
	# - When submitting nsfwcontent please use the r18 channels respectively!!
	# ```"""
		await message.channel.send( helpString)
	elif message.content.lower().startswith('!stats'):
		#try to find user in database using id
		db_user = getDBUser(session, message.author.id)

		#if we found the user in our spreadsheet
		if (db_user != None):

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
			stats_embed.add_field(name="Level: {0}	XP: {1}/{2}".format(db_user.level,db_user.currentxp,next_level_required_xp),value=expbar,inline=True)
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
			
			#quest check
			db_quester = getDBQuestMember(session,message.author.id,0)
			#update the stats quest
			#method to update a user based on id and quest
			if(db_quester != None):
				db_quester.progress = 1
				await checkSingleUserQuests(session,config,message.author.id,0)

		else:
			await message.channel.send("```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact a mod.\n```")
	elif message.content.lower().startswith('!ach'):
		serv = message.guild
		ach_card = "```Python\n @{0} - Achievements\n# Note: unlocked ones are in green and denoted with a 🏆.\n```\n```diff\n".format(message.author.name)
		for rank in serv.roles:
			if rank in message.author.roles and rank.name not in config.nonach_roles:
				ach_card = ach_card + '🏆 {0}\n'.format(rank.name)
			if rank not in message.author.roles and rank.name not in config.nonach_roles:
				ach_card = ach_card + '　 {0}\n'.format(rank.name)
		ach_card = ach_card + "```"
		await message.channel.send( ach_card)
	elif message.content.lower().startswith('!timeleft'):
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

	elif message.content.lower().startswith('!roleupdate') and (message.author.top_role >= config.adminRole):
		await message.channel.send( "```Markdown\n# Updating Roles...\n```")
		await updateRoles(session, config,message.guild)
		await message.channel.send( "```diff\n+ Updating roles was a happy little success!\n```")
	# elif message.content.lower().startswith('!nsfwjoin'):
	# 	serv = message.author.guild
	# 	for rank in serv.roles:
	# 		if rank.name == "NSFW Artist":
	# 			await message.author.add_roles(rank)
	# 			await message.channel.send( "```Markdown\nYou should now have access to the NSFW channels, Oh my!```")
	# elif message.content.lower().startswith('!nsfwleave'):
	# 	serv = message.author.guild
	# 	for rank in serv.roles:
	# 		if rank.name == "NSFW Artist":
	# 			await message.author.remove_roles( rank)
	# 			await message.channel.send( "```Markdown\nNSFW channels have been hidden.\n```")
	elif message.content.lower().startswith('!artblock'):
		fp = open('prompts.txt', 'r+',encoding="utf8")
		await message.channel.send( "```Markdown\n# {0}\n```".format(random.choice(fp.readlines())))
		fp.close()
	elif message.content.lower().startswith('!idea'):
		serv = message.guild

		# make sure the user is registered
		registerMessageAuthor(session, message)
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
	elif message.content.lower().startswith('!8ball'):
		if(True):
			await message.channel.send('`{0} shakes their eight ball..`\n:8ball: `{1}`'.format(message.author.name, random.choice(config.eight_ball)))
	elif message.content.lower().startswith('!roll'):
		dice = message.content.lower().split(' ')[1]
		try:
			num_dice =  int(dice.split('d')[0])
			dice_value = int(dice.split('d')[1])
			rolls = []
			for i in range(0,num_dice):
				rolls.append(random.randint(1,dice_value))

			await message.channel.send( ":game_die: `Your rolls are: {0}`".format(rolls))
		except:
			await message.channel.send( "```diff\n- Invalid dice arguments\n```")
	elif message.content.lower().startswith('!award') and message.author.top_role >= config.adminRole:
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
	elif message.content.lower().startswith('!grant') and message.author.top_role >= config.adminRole:
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
	elif message.content.lower().startswith('!ungrant') and message.author.top_role >= config.adminRole:
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
	elif message.content.lower().startswith('!vacation'):
		working_index = 0
		price = 100
		curdate = datetime.utcnow()
		potentialstreak = curdate + timedelta(days=30)
		today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
		streakdate = "{0}-{1}-{2}".format(potentialstreak.month, potentialstreak.day, potentialstreak.year)
		#try to find user in database using id
		db_user = getDBUser(session, message.author.id)

		if (db_user != None):
			buyer_amount = db_user.currency
			if buyer_amount >= price:
				await message.channel.send( "```Python\n@{0}\n```\n```Markdown\n# You're about to purchase a 30 day vacation to protect your streak for 100 credits. (any new submissions will reset this to 7 days). To confirm and buy type !yes, to decline, type !no.\n```".format(message.author.name))
				try:
					confirm = await confirmDecision(client, message.author)
					if confirm:
						new_buyer_balance = buyer_amount - price
						db_user.currency = new_buyer_balance
						db_user.expiry = potentialstreak
						session.commit()
						await message.channel.send( "```diff\n+ Vacation purchased, your streak now expires on {0} {1}, {2}. Bon Voyage!\n```".format(config.months[str(potentialstreak.month)],potentialstreak.day,potentialstreak.year))
					else:
						await message.channel.send( "```Markdown\n# Transaction cancelled.\n```")
				except Exception as e:
					print("transaction with {0} timed out".format(message.author.name))
			else:
				await message.channel.send( "```Markdown\n- Not enough credits. {0} needed, you have {1}```".format(price, buyer_amount))
		else:
			await message.channel.send( "```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact a mod.\n```")
	elif message.content.lower().startswith('!markraffle') and message.author.top_role >= config.adminRole:
		try:
			receiver = message.mentions[0]
			db_user = session.query(User).filter(User.id == receiver.id).one()
			db_user.raffle = 1
			session.commit()
			await message.channel.send("```diff\n+ Raffle submission marked for: {0}\n```".format(receiver.name))
		except:
			await message.channel.send("```diff\n- Something went wrong.\n```")
			session.rollback()
	elif message.content.lower().startswith('!unmarkraffle') and message.author.top_role >= config.adminRole:
		try:
			receiver = message.mentions[0]
			db_user = session.query(User).filter(User.id == receiver.id).one()
			db_user.raffle = 0
			session.commit()
			await message.channel.send("```diff\n+ Raffle submission unmarked for: {0}\n```".format(receiver.name))
		except:
			await message.channel.send("```diff\n- Something went wrong.\n```")
			session.rollback()
	elif message.content.lower().startswith('!buy'):
		#under construction.
		parse = message.content.split(" ")
		item_name = parse[1].lower()
		price = 0
		serv = message.guild

		# make sure the user is registered
		registerMessageAuthor(session, message)

		#try to find user in database using id
		db_user = getDBUser(session, message.author.id)

		buyer_currency = db_user.currency
		fp = open('shop.txt','r+')
		items_list = fp.readlines()
		price = None
		for items in items_list:
			if items.lower().startswith(item_name):
				price = int(items.split("-")[1])
		fp.close()
		if price == None:
			await message.channel.send("```diff\n- That item does not exist!```")
		elif price > buyer_currency:
			await message.channel.send("```diff\n- Not enough credits. {0} needed, you have {1}\n```".format(price,buyer_currency))
		else:
			purchase = await buyitem(session,client,"{0}".format(item_name), price, message.author, message.channel)
			if(purchase):
				await message.channel.send("```diff\n+ Successfully payed {0} credits for {1}. Your total balance is now: {2}\n```".format(price,item_name,db_user.currency))
			else:
				await message.channel.send("```diff\n+{0} was not purchased```".format(item_name))
	elif message.content.lower().startswith('!override'):
		override_string = message.content.split(" ")
		#get user ID to roll back
		if(len(override_string) >= 2):
			override_string = override_string[1]
			override_role = 0
			#try to find user in database using id
			db_user = getDBUser(session, message.author.id)
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
						purchase = await buyitem(session,client,"Role Override Streak ({0})".format(override_string), 100, message.author, message.channel)
						if(purchase):
							#remove old roles
							await message.author.remove_roles(*orRoles)
							#add new override to user
							await message.author.add_roles( role)
							await message.channel.send("```diff\n+You have successfully been granted the " + override_string + " Override role```")
					elif( int(override_string) > db_user.highscore):
						await message.channel.send("```diff\n-Your Streak high score is not high enough to use that override```")

	elif message.content.lower().startswith("!undo") and (message.author.top_role >= config.adminRole):
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
		db_user = getDBUser(session, userid)

		if(db_user != None):
			#update all the stats
			newscore = db_user.totalsubmissions-1
			newcurrency = db_user.currency-10
			current_streak = db_user.streak
			new_streak = current_streak-1
			current_xp = db_user.currentxp
			xp_gained = 10
			xp_lost = 10 + round(math.log2(current_streak-1)*2)
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
	elif message.content.lower().startswith("!proxysubmit") and (message.author.top_role >= config.adminRole):
		print('proxy submission - ' + str(len(message.mentions)))
		if (len(message.mentions)>0):
			userToUpdate = message.mentions[0]
			filetypes = [".gif",".jpg",".jpeg",".png"]
			if ("https://" in message.content.lower() or "http://" in message.content.lower()) and any(u in message.content.lower() for u in filetypes) :
				# do linksubmit
				await linkSubmit(session, config, message, userToUpdate)
			else:
				try:
					#normal submit.
					await normalSubmit(session, config, message, userToUpdate)
				except:
					pass
	elif message.content.lower().startswith("!setstreak") and (message.author.top_role >= config.adminRole):
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
		db_user = getDBUser(session, userid)

		if(db_user != None):
			#set streak to the given streak
			db_user.streak = newstreak
			session.commit()
			await message.channel.send("```Markdown\n#Streak set to {0} for user {1}\n```".format(newstreak,db_user.name))
	elif message.content.lower().startswith("!sethighscore") and (message.author.top_role >= config.adminRole):
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
		db_user = getDBUser(session, userid)

		if(db_user != None):
			#set streak to the given streak
			db_user.highscore = newhighscore
			session.commit()
			await message.channel.send("```Markdown\n#Streak high score set to {0} for user {1}\n```".format(newhighscore,db_user.name))
	elif message.content.lower().startswith("!resubmit") and (message.author.top_role >= config.adminRole):
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
		db_user = getDBUser(session, userid)

		if(db_user != None):
			#reset submission to false
			db_user.submitted = 0
			session.commit()
			await message.channel.send("```Markdown\n#Submission status reset to for user {0}\n```".format(db_user.name))
	elif message.content.lower() == "!quit" and (message.author.top_role >= config.adminRole):
		await message.channel.send("Shutting down BotRoss, bye byeee~")
		session.close()
		sys.exit(5)
	elif message.content.lower() == "!reset" and (message.author.top_role >= config.adminRole):
		await message.channel.send("Resetting BotRoss, bye byeee~")
		session.close()
		sys.exit()
	elif message.content.lower().startswith("!getraffle") and (message.author.top_role >= config.adminRole):
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
	elif message.content.lower().startswith("!resetraffle") and (message.author.top_role >= config.adminRole):
		await message.channel.send("This command will reset raffle marks for all members. Type !yes to confirm, or !no to cancel.")
		confirm = await confirmDecision(client, message.author)
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
						await resetQuestProgress(session, curr_member.id,2)
				#commit all changes to the sheet at once
				session.commit()
				print("raffle reset finished")
				await message.channel.send("Reset the raffle submissions for " + str(numRaffle) + " members")
			else:
				await message.channel.send("Cancelling raffle reset, phew.")
		except:
			print("Raffle Reset timed out")

	elif message.content.lower().startswith('!streakwarning'):
		# ensure the user is registered
		registerMessageAuthor(session, message)

		#find database user
		db_user = getDBUser(session, message.author.id)

		#on or off
		sp = message.content.split(" ")

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
				confirm = await confirmDecision(client, message.author)
				if(confirm): #if the user confirms update the database
					db_user.decaywarning = choice
					session.commit() #always commit the session after changes
					await message.channel.send("```diff\n+ PM warnings have been turned "+ choice_string + "\n```")
				else:
					await message.channel.send( "```Markdown\n# PM warnings are unchanged\n```")
			except:
				print("{0} warning mode unchanged".format(message.author.name))

	#admin command - give xp or take xp
	# new ex. !xp 300 @mentioned users
	# new ex. !xp -300 @mentioned users
	elif message.content.lower().startswith('!xp') and message.author.top_role >= config.adminRole:
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
	elif message.content.lower().startswith('!fullreset') and message.author.top_role >= config.adminRole:
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
	elif message.content.lower().startswith('!contest') and len(message.content.lower()) > 8  and message.author.top_role >= config.adminRole:

		#states, no contest(0), closed contest(1), open contest(2)
		# commands, no(0), close(1), open(2), extension (add a confirmation message here or)

		parse = message.content.split(" ")

		mode = parse[1]

		db_contest = getDBContest(session,0)

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
				confirm = await confirmContest(client, message.author)
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
				confirm = await confirmContest(client, message.author)
				await message.channel.send( "```Markdown\n#A new contest prompt has been added and opened which is {0}!\n```".format(str(confirm)))

				db_contest.prompt = confirm
				session.commit()

			else:
				await message.channel.send( "please type in off, closed, open, or extend!")


	#use to keep track of how long the contest is
	elif message.content.lower().startswith('!contest') and len(message.content.lower()) == 8:

		db_contest = getDBContest(session,0)

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
	elif message.content.lower().startswith('!runhouse') and message.author.top_role >= config.adminRole:
		await message.channel.send( "run housekeeping for testing\n")
		await housekeeper()

	elif message.content.lower().startswith('!create') and message.author.top_role >= config.adminRole:
		#Command for admins to create the quest table, and to update it when any new ones are added
		await message.channel.send( "```Markdown\n# Running quests list update\n```")
		await createQuestTable(session)
		await message.channel.send( "```diff\n+ Updated the questslist!\n```")

	elif message.content.lower().startswith('!updatequests') and message.author.top_role >= config.adminRole:
		#this method will be to fill in the quests for any user already signed up
		members = session.query(User).all()
		await message.channel.send( "```diff\n+ Please wait as every user has their quests updated...\n```")

		for curr_member in members:
			db_quests = session.query(QuestsList)
			db_questers = getDBQuestMember(session,curr_member.id,'all') #we can query the database for all the member's quests
			
			for quest in db_quests:
				if(next( (q for q in db_questers if q.questId==quest.questId), None) == None): #examine if the user already has the quest in the list
					new_quester = QuestsMembers(usrId = curr_member.id, questId = quest.questId, name=curr_member.name,completed = False, progress = 0)
					session.add(new_quester) #otherwise we add it

		await message.channel.send( "```diff\n+ Successfully updated your quests list!\n```")
		session.commit()

	elif message.content.lower().startswith('!resetlevels') and message.author.top_role >= config.adminRole:
		await message.channel.send("This command will reset levels and xp for all members. Type !yes to confirm, or !no to cancel.")
		confirm = await confirmDecision(client, message.author)
		if(confirm):
			members = session.query(User).all()
			await message.channel.send( "```Markdown\n# Reseting every users level and xp to 0\n```")
			for curr_member in members:
				curr_member.level = 0
				curr_member.currentxp = 0

			session.commit()
			await message.channel.send( "```Markdown\n# Reset successful!\n```")
		else:
			await message.channel.send("level reset cancelled")

	# elif message.content.lower().startswith('!resq') and message.author.top_role >= config.adminRole:
	#	 #test method to reset quests (abstract out resetting to its own method)
	#	 db_quests = session.query(QuestsList)
	#	 for quest in db_quests:
	#		 await resetQuestProgress(message.author.id,quest.questId)
	#		 session.commit()
	#	 #commit session
	#	 await message.channel.send("nothing")
	elif message.content.lower().startswith('!questreset') and message.author.top_role >= config.adminRole:

		db_quester = getDBQuestMember(session,message.author.id,0)
		db_user = getDBUser(session, message.author.id)
		parse = message.content.split(" ")
		db_quests = getDBResetQuests(session)
		markedQuest = None

		if(db_user == None):
			await message.channel.send("```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact a mod.\n```")
		elif(db_quester == None):
			await message.channel.send("```diff\n- I couldn't find your name on the quest board. Are you sure you're signed up? If you are, contact a mod.\n```")
		else:
			if(len(parse) > 1 and isNumber(parse[1])):
				questnum = int(parse[1])

				for quest in db_quests:
					if(quest.questId == int(questnum)):
						markedQuest = quest

				if(markedQuest != None):

					if(getDBQuestMember(session,message.author.id,questnum).completed == False):
						await message.channel.send("```diff\n- You have not completed this quest yet so you can't reset it!.\n```")
					elif(db_user.currency >= 500):

						await message.channel.send( "```Python\n@{0}\n```\n```Markdown\n# You're about to reset quest {0} for 500 currency, are you sure you want to do this?  Type !yes to confirm and !no to cancel\n```".format(questnum))
						try:
							confirm = await confirmDecision(client, message.author)
							if confirm:
								await message.channel.send( "```diff\n+ you have reset your status on quest {0}!\n```".format(questnum))
								await resetQuestProgress(session, db_user.id, questnum)
								db_user.currency = db_user.currency - 500
								session.commit()
							else:
								await message.channel.send( "```Markdown\n# Transaction cancelled.\n```")
						except:
							print("transaction with {0} timed out".format(message.author.name))

					else:
						await message.channel.send( "```diff\n- You do not have enough currency to reset the quest!\n```")
				else:
					await message.channel.send( "```diff\n- That is not a resetable quest!\n```")
			else:
				await message.channel.send( "```diff\n- Please enter in the questreset command with the number of a quest that can be reset!\n```")

	#add in extra part to limit to only a certain quest if specified, otherwise it sends all
	elif message.content.lower().startswith('!board'):
		db_quester = getDBQuestMember(session,message.author.id,0)
		db_user = getDBUser(session, message.author.id)
		parse = message.content.split(" ")

		if(db_user == None):
			await message.channel.send("```diff\n- I couldn't find your name in our spreadsheet. Are you sure you're registered? If you are, contact a mod.\n```")
		elif(db_quester == None):
			await message.channel.send("```diff\n- I couldn't find your name on the quest board. Are you sure you're signed up? If you are, contact a mod.\n```")
		else:

			if(len(parse) > 1 and isNumber(parse[1])):
				item = parse[1]
				user = discord.utils.get(client.get_all_members(), id=message.author.id)
				await message.channel.send( "```diff\n+ Please wait as we send you the quest progress data...\n```")
				embedQ = discord.Embed(color=0x85F7FF)
				db_questitem = getDBQuestItem(session,item)
				db_quester = getDBQuestMember(session,message.author.id,item)
				if(db_questitem != None):
					qName = "__**QUEST {0}**__".format(item)
					qTask = db_questitem.description
					qGoal = db_questitem.completion
					qProgress = "{0} out of {1}".format(db_quester.progress,qGoal)
					qStatusString = ':red_circle: You have not completed this quest' if db_quester.completed == False else ':white_check_mark: You have completed this quest!'

					embedQ.add_field(name=qName, value=qTask, inline=False)
					embedQ.add_field(name='XP Reward', value=db_questitem.award, inline=False)
					embedQ.add_field(name='Quest status', value=qStatusString, inline=False)
					embedQ.add_field(name='Your current progress', value=qProgress, inline=False)
					embedQ.add_field(name='Amount needed', value=qGoal, inline=False)
					await user.send(embed=embedQ)
					await message.channel.send( "```diff\n+ Your progress on quests  been sent!\n```")
				else:
					await message.channel.send( "```diff\n- Quest #{0} is not a valid quest, please refer back to the quest board for available quests!\n```".format(item))
			elif(len(parse) > 1 and str(parse[1]).lower() == "all"):
				# use split command to check for number and correspond that with a quest
				user = discord.utils.get(client.get_all_members(), id=message.author.id)
				db_quests = session.query(QuestsList)
				await message.channel.send( "```diff\n+ Please wait as we send you the quest progress data...\n```")

				for quests in db_quests:
					embedQ = discord.Embed(color=0x85F7FF)
					db_questitem = getDBQuestItem(session,quests.questId)
					db_quester = getDBQuestMember(session,message.author.id,quests.questId)
					qName = "__**QUEST {0}**__".format(quests.questId)
					qTask = db_questitem.description
					qGoal = db_questitem.completion
					qProgress = "{0} out of {1}".format(db_quester.progress,qGoal)
					qStatusString = ':red_circle: You have not completed this quest' if db_quester.completed == False else ':white_check_mark: You have completed this quest!'

					embedQ.add_field(name=qName, value=qTask, inline=False)
					embedQ.add_field(name='XP Reward', value=db_questitem.award, inline=False)
					embedQ.add_field(name='Quest status', value=qStatusString, inline=False)
					embedQ.add_field(name='Your current progress', value=qProgress, inline=False)
					embedQ.add_field(name='Amount needed', value=qGoal, inline=False)
					await user.send(embed=embedQ)

				await message.channel.send( "```diff\n+ Your progress on quests has been sent!\n```")
			else:
				db_quests = session.query(QuestsList)
				quest_card = "```Python\n @{0} - Quests\n# Note: Completed ones are in green and denoted with a '+'.\n```\n```diff\n".format(message.author.name)
				db_questers = getDBQuestMember(session,message.author.id,'all')
				for quest in db_quests:
					completed = next( (q for q in db_questers if q.questId==quest.questId), None).completed
					if(completed == True):
						quest_card = quest_card + '+ Quest {0}\n'.format(quest.questId)
					else:
						quest_card = quest_card + '# Quest {0}\n'.format(quest.questId)
				quest_card = quest_card + "```"

				await message.channel.send(quest_card)
	elif message.content.lower().startswith('!newartists') and message.author.top_role >= config.adminRole:
		#set users to New Artist if they have 0 total submits
		for user in message.guild.members:
			aRole = discord.utils.find(lambda r: r.name == 'Artists', user.roles)
			if(aRole):
				db_user = getDBUser(session, user.id)
				if(db_user):
					if(db_user.totalsubmissions < 1):
						print("replacing role for {0}".format(user.name))
						await user.remove_roles(aRole)
						await user.add_roles(discord.utils.find(lambda r: r.name == 'New Artist', message.guild.roles))				
	# elif message.content.lower().startswith('!battle') and message.channel == config.botChannel:

	# 	value = random.randint(1,20)

	# 	if(value == 1):
	# 		await message.channel.send( "The air is offended that you punched it, so it obliterates you.")
	# 	elif(value > 1 and value <= 5):
	# 		await message.channel.send( "You punch the air, the air judges you for it.")
	# 	elif(value > 5 and value <= 10):
	# 		await message.channel.send( "You punch the air, it is mildly inconvenienced by your show of violence.")
	# 	elif(value > 10 and value <= 18):
	# 		await message.channel.send( "You realize punching the air is not the solution, so you stab it instead.  Nothing happens.")
	# 	elif(value == 20 or value == 19):
	# 		await message.channel.send( "***NOBODY EXPECTS THE SPANISH INQUISITION!***")
	elif message.content.lower().startswith('!questaward') and message.author.top_role >= config.adminRole:
		#grants an achievement.
		parse = message.content.split("-")
		quest_receivers = ""
		markedQuest = None
		manQuests = getDBManualQuests(session)

		if(len(parse) < 2):
			await message.channel.send( "```Markdown\n# Incorrect!\n```")
		else:
			quest_id = parse[1]
			for quest in manQuests:
				if(quest.questId == int(quest_id)):
					markedQuest = quest

			if(markedQuest != None):
				print(quest.description)
				for person in message.mentions:
					db_quester = getDBQuestMember(session,person.id,quest_id)
					db_user = getDBUser(session, person.id)
					#if we found the user in our spreadsheet
					if(db_quester != None):
						db_questitem = getDBQuestItem(session,quest_id)
						db_quester.progress = 1
						db_user.currency = db_user.currency + db_questitem.award
						await checkSingleUserQuests(session, config,person.id,int(quest_id))
						await config.adminBotChannel.send("`Awarded {0} currency!`".format(db_questitem.award))
					else:
						await config.adminBotChannel.send("<@{0}>, does not have quest {1}! please check if the user is signed up for quests and if the admin selected the right quest".format(person.id,quest_id))

				await message.channel.send( "```Markdown\n# All quest entrants marked!\n```")
			else:
				await message.channel.send( "```Markdown\n# That quest is not avaialable for manual checking!\n```")


async def linkSubmit(session, config, message, userToUpdate):
	url = message.content.split(" ")
	print('link submitting for ' + str(userToUpdate.name) + " | url - " + url[1])
	#goes to quest or submit handlers
	await handleSubmit(session, config, message, userToUpdate, url[1])

async def normalSubmit(session, config, message, userToUpdate):
	print('submitting for ' + str(userToUpdate.name))
	url = message.attachments[0].url
	print(str(userToUpdate.name) + "'s url - " + url)

	print('normal submitting for ' + str(userToUpdate.name) + " | url - " + url)
	await handleSubmit(session, config, message, userToUpdate, url)


async def handleSubmit(session, config, message, userToUpdate, url):
	registerMessageAuthor(session, message)

	curdate = datetime.utcnow()
	potentialstreak = curdate + timedelta(days=7)
	today = "{0}-{1}-{2}".format(curdate.month, curdate.day, curdate.year)
	streakdate = "{0}-{1}-{2}".format(potentialstreak.month, potentialstreak.day, potentialstreak.year)
	#try to find user in database using id
	db_user = getDBUser(session, userToUpdate.id)
	#first find if we have  the user in our list

	#db_user is our member object

	#check if already submitted
	if db_user.submitted == 1:
		print(str(userToUpdate.name) + ' already submitted')
		await message.channel.send( "```diff\n- You seem to have submitted something today already!\n```")
	#otherwise, do the submit
	else:
		#update the submit quest
		db_quester = getDBQuestMember(session,message.author.id,1)
		if(db_quester != None):
			db_quester.progress = 1
			await checkSingleUserQuests(session,config,message.author.id,1)

		#update all the stats
		newscore = db_user.totalsubmissions+1
		newcurrency = db_user.currency+10
		current_streak = db_user.streak
		new_streak = current_streak+1
		current_xp = db_user.currentxp
		xp_gained = 10
		if(current_streak > 0):
			xp_gained = xp_gained + round(math.log2(current_streak)*2)
		current_level = db_user.level
		next_level_required_xp = current_level*10 + 50
		new_xp_total = current_xp + xp_gained
		#if we levelled up, increase level
		while new_xp_total >= next_level_required_xp:
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
		#print("finishing updating " + db_user.name + "'s stats")
		await message.channel.send( "```diff\n+ @{0} Submission Successful! Score updated!\n+ {1}xp gained.```".format(userToUpdate.name,xp_gained))
		#finally, add an adore to the submission
		await message.add_reaction( config.adoreEmoji)
		#print("submit complete")
		#check if we can make the a new artist a full artist
		aRole = discord.utils.find(lambda r: r.name == 'Artists', userToUpdate.roles)
		if(aRole == None):
			na = discord.utils.find(lambda r: r.name == 'New Artist', userToUpdate.roles)
			if(na):
				await userToUpdate.remove_roles(na)
				await userToUpdate.add_roles(discord.utils.find(lambda r: r.name == 'Artists', message.guild.roles))


async def createQuestTable(session):

	#tutorials

	#stats tutorial
	if(getDBQuestItem(session,0) == None):
		new_quest = QuestsList(questId = 0, description = "Use the !stats command once", completion = 1, award = 20, mode = "none",reset = False)
		session.add(new_quest)
	#submit tutorial
	if(getDBQuestItem(session,1) == None):
		new_quest = QuestsList(questId = 1, description = "Successfully submit a piece to a submission channel", completion = 1, award = 20, mode = "none",reset = False)
		session.add(new_quest)

	#raffle

	#Submit a raffle piece
	if(getDBQuestItem(session,2) == None):
		new_quest = QuestsList(questId = 2, description = "Successfully enter in a raffle piece for the monthly rafle", completion = 1, award = 20, mode = "auto",reset = False)
		session.add(new_quest)
	#have 5 overall submits
	if(getDBQuestItem(session,3) == None):
		new_quest = QuestsList(questId = 3, description = "Submit 5 pieces of art overall to the submission channels", completion = 5, award = 20, mode = "auto",reset = False)
		session.add(new_quest)
	#have 10 overall submits
	if(getDBQuestItem(session,4) == None):
		new_quest = QuestsList(questId = 4, description = "Submit 10 pieces of art overall to the submission channels", completion = 10, award = 40, mode = "auto",reset = False)
		session.add(new_quest)
	#have 20 overall submits
	if(getDBQuestItem(session,5) == None):
		new_quest = QuestsList(questId = 5, description = "Submit 20 pieces of art overall to the submission channels", completion = 20, award = 80, mode = "auto",reset = False)
		session.add(new_quest)
	#have 50 overall submits
	if(getDBQuestItem(session,6) == None):
		new_quest = QuestsList(questId = 6, description = "Submit 50 pieces of art overall to the submission channels", completion = 50, award = 160, mode = "auto",reset = False)
		session.add(new_quest)
	#have 100 overall submits
	if(getDBQuestItem(session,7) == None):
		new_quest = QuestsList(questId = 7, description = "Submit 100 pieces of art overall to the submission channels", completion = 100, award = 320, mode = "auto",reset = False)
		session.add(new_quest)
	#have 200 overall submits
	if(getDBQuestItem(session,8) == None):
		new_quest = QuestsList(questId = 8, description = "Submit 200 pieces of art overall to the submission channels", completion = 200, award = 640, mode = "auto",reset = False)
		session.add(new_quest)
	#have 300 overall submits
	if(getDBQuestItem(session,9) == None):
		new_quest = QuestsList(questId = 9, description = "Submit 300 pieces of art overall to the submission channels", completion = 300, award = 1280, mode = "auto",reset = False)
		session.add(new_quest)

	#streaks

	#attain a 5+streak highscore
	if(getDBQuestItem(session,10) == None):
		new_quest = QuestsList(questId = 10, description = "Attain a streak highscore of 5", completion = 5, award = 20, mode = "auto",reset = False)
		session.add(new_quest)
	#attain a 10+streak highscore
	if(getDBQuestItem(session,11) == None):
		new_quest = QuestsList(questId = 11, description = "Attain a streak highscore of 10", completion = 10, award = 40, mode = "auto",reset = False)
		session.add(new_quest)
	#attain a 15+streak highscore
	if(getDBQuestItem(session,12) == None):
		new_quest = QuestsList(questId = 12, description = "Attain a streak highscore of 15", completion = 15, award = 60, mode = "auto",reset = False)
		session.add(new_quest)
	#attain a 20+streak highscore
	if(getDBQuestItem(session,13) == None):
		new_quest = QuestsList(questId = 13, description = "Attain a streak highscore of 20", completion = 20, award = 80, mode = "auto",reset = False)
		session.add(new_quest)
	#attain a 25+streak highscore
	if(getDBQuestItem(session,14) == None):
		new_quest = QuestsList(questId = 14, description = "Attain a streak highscore of 25", completion = 25, award = 110, mode = "auto",reset = False)
		session.add(new_quest)
	#attain a 30+streak highscore
	if(getDBQuestItem(session,15) == None):
		new_quest = QuestsList(questId = 15, description = "Attain a streak highscore of 30", completion = 30, award = 140, mode = "auto",reset = False)
		session.add(new_quest)
	#attain a 60+streak highscore
	if(getDBQuestItem(session,16) == None):
		new_quest = QuestsList(questId = 16, description = "Attain a streak highscore of 60", completion = 60, award = 160, mode = "auto",reset = False)
		session.add(new_quest)
	#attain a 90+streak highscore
	if(getDBQuestItem(session,17) == None):
		new_quest = QuestsList(questId = 17, description = "Attain a streak highscore of 90", completion = 90, award = 200, mode = "auto",reset = False)
		session.add(new_quest)
	#attain a 120+streak highscore
	if(getDBQuestItem(session,18) == None):
		new_quest = QuestsList(questId = 18, description = "Attain a streak highscore of 120", completion = 120, award = 320, mode = "auto",reset = False)
		session.add(new_quest)
	#attain a 150+streak highscore
	if(getDBQuestItem(session,19) == None):
		new_quest = QuestsList(questId = 19, description = "Attain a streak highscore of 150", completion = 150, award = 450, mode = "auto",reset = False)
		session.add(new_quest)
	#attain a 200+streak highscore
	if(getDBQuestItem(session,20) == None):
		new_quest = QuestsList(questId = 20, description = "Attain a streak highscore of 200", completion = 200, award = 640, mode = "auto",reset = False)
		session.add(new_quest)
	#attain a 250+streak highscore
	if(getDBQuestItem(session,21) == None):
		new_quest = QuestsList(questId = 21, description = "Attain a streak highscore of 250", completion = 250, award = 900, mode = "auto",reset = False)
		session.add(new_quest)
	#attain a 300+streak highscore
	if(getDBQuestItem(session,22) == None):
		new_quest = QuestsList(questId = 22, description = "Attain a streak highscore of 300", completion = 300, award = 1280, mode = "auto",reset = False)
		session.add(new_quest)

	#time based quests (submitting daily for x time)
	if(getDBQuestItem(session,23) == None):
		new_quest = QuestsList(questId = 23, description = "Submit daily for 7 days", completion = 7, award = 100, mode = "auto",reset = True)
		session.add(new_quest)
	if(getDBQuestItem(session,24) == None):
		new_quest = QuestsList(questId = 24, description = "Submit daily for 30 days", completion = 30, award = 400, mode = "auto",reset = True)
		session.add(new_quest)
	if(getDBQuestItem(session,25) == None):
		new_quest = QuestsList(questId = 25, description = "Submit daily for 100 days", completion = 100, award = 1200, mode = "auto",reset = True)
		session.add(new_quest)
	if(getDBQuestItem(session,26) == None):
		new_quest = QuestsList(questId = 26, description = "Submit daily for 200 days", completion = 200, award = 2500, mode = "auto",reset = True)
		session.add(new_quest)
	if(getDBQuestItem(session,27) == None):
		new_quest = QuestsList(questId = 27, description = "Submit daily for 365 days", completion = 365, award = 4000, mode = "auto",reset = True)
		session.add(new_quest)

	#quests that will be marked by admins as they cannot be tracked by the admins
	#easy,medium,and hard mode quests have set rewards for their tiers
	#extra money can be gained from these quests

	if(getDBQuestItem(session,28) == None):
		new_quest = QuestsList(questId = 28, description = "Submit a drawing that has a hat in it", completion = 1, award = 20, mode = "manual",reset = False)
		session.add(new_quest)
	if(getDBQuestItem(session,29) == None):
		new_quest = QuestsList(questId = 29, description = "Submit a drawing of a character in armor", completion = 1, award = 80, mode = "manual",reset = False)
		session.add(new_quest)
	if(getDBQuestItem(session,30) == None):
		new_quest = QuestsList(questId = 30, description = "Submit a refsheet of a character in a questing outfit that includes: 1 full body shot (with or without clothes), 1 shot of their outfit, 1 shot of their weapon", completion = 1, award = 200, mode = "manual",reset = False)
		session.add(new_quest)

	session.commit()

async def resetQuestProgress(session, usrId,questId):

	db_quester = getDBQuestMember(session,usrId,questId)
	if(db_quester != None):
		db_quester.completed = 0
		db_quester.progress = 0
		session.commit()
