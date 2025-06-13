import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import math
import requests
import json
import roman
import csv
from mojang import API

# Discord bot token and hypixel api key
load_dotenv(dotenv_path="keys.env")
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
api_key = os.getenv("HYPIXEL_API_KEY")									# update every 3 days 

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# given data
mode_list = ['oa', 'uhc', 'sw', 'mw', 'blitz', 'op', 'classic', 'bow', 'ndb', 'combo', 'tnt', 'sumo', 'bridge', 'pkd', 'boxing', 'arena', 'all', 'kit'] # mode aliases
mode_db_list = ['oa', 'uhc', 'sw', 'mw', 'blitz', 'op', 'classic', 'bow', 'potion', 'combo', 'bowspleef', 'sumo', 'bridge', 'parkour_eight', 'boxing', 'duel_arena'] # mode database aliases
mode_names = ['Overall', 'UHC', 'SkyWars', 'MW', 'Blitz', 'OP', 'Classic', 'Bow', 'NoDebuff', 'Combo', 'TNT', 'Sumo', 'Bridge', 'Parkour', 'Boxing', 'Arena'] # clean mode names
div_list = ['ASCENDED', 'DIVINE', 'CELESTIAL', 'Godlike', 'Grandmaster', 'Legend', 'Master', 'Diamond', 'Gold', 'Iron', 'Rookie', 'None'] # divisions
div_req = [100000, 50000, 25000, 10000, 5000, 2000, 1000, 500, 250, 100, 50, 0] # requirements for each division title
div_step = [10000, 10000, 5000, 3000, 1000, 600, 200, 100, 50, 30, 10, 1] # requirements to go up a level within a division title



# Functions
def dataget(ign):														# Load player's Hypixel stats												# get player's uuid to avoid 5 min cooldown
	try:															
		response = requests.get(f"https://playerdb.co/api/player/minecraft/{ign}")
		uuid = response.json()["data"]["player"]["id"]
		url = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"
		res = requests.get(url)
		data = res.json()
	except KeyError:
		data = 'Failed to load data for this player.'
	return data
	
def mode_clean(mode):
	while mode not in mode_list:										# check that the mode is valid
		'''if mode == 'help':
			print('Available modes:')
			for i in mode_list:
				if i != 'all':
					print(f'{i},', end=' ')
				else:
					print('all.')
			mode = str(input('Mode: '))'''
		if mode == 'all':
			break
	if mode not in mode_list:
		print('Invalid mode.')
		print("Type 'help' to get the mode aliases.")
		mode = str(input('Mode: ')).lower()
		if mode != 'all':		
			mode_index = mode_list.index(mode)        					# convert the alias to the mode's full name
			mode_clean = mode_names[mode_index]
	return mode_clean

def get_rank(ign, data):
    try:
        data["player"]
    except KeyError:
        return (data)
    if "newPackageRank" in data["player"]:
        rank = (data["player"]["newPackageRank"]) # A player's rank (excluding MVP++) is stored under"rank" in "newPackageRank".
        if rank == 'MVP_PLUS':
            if "monthlyPackageRank" in data["player"]: # This category only exists for users who have bought MVP++ at least once
                mvp_plus_plus = (data["player"]["monthlyPackageRank"]) # MVP++ is stored separately under "monthlyPackageRank"
                if mvp_plus_plus == "NONE":
                    return ('[MVP+]')
                else:
                    return("[MVP++]")
            else:
                return("[MVP+]")
        elif rank == 'MVP':
            return ('[MVP]')
        elif rank == 'VIP_PLUS':
            return ('[VIP+]')
        elif rank == 'VIP':
            return ('[VIP]')
    else:
        return ('')
        
# Bot readiness confirmation
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')

# Bot commands
@bot.command(name='h')
async def h(ctx):
	await ctx.send(f"""
# **Help Menu** <:avatar:1382441832809500792>

- `!d <ign> <mode>` — Check wins and division title for a player in a specific duels mode.
  -> `!d Technoblade sw`

- `!d <ign> all` — Check wins and division titles across all duels modes.
  -> `!d Technoblade all`

- `!kit <ign> <kit>` — Check (ranked) kit wins in SkyWars duels.
  -> `!kit poki95 pyromancer`

Available modes: `oa`, `uhc`, `sw`, `mw`, `blitz`, `op`, `classic`, `bow`, `ndb`, `combo`, `tnt`, `sumo`, `bridge`, `pkd`, `boxing`, `arena`
Available kits: `pyromancer`, `magician`, `athlete`, `armorer`, `champion`, `scout`, `hound`, `cactus`, `enderman`, `knight`, `batguy`, `frog`, `guardian`,  

For any issues, contact **poki95** on Discord.
""")

@bot.command(name='d')
async def d(ctx, ign, mode):
	data = dataget(ign)
#	url = f"https://api.hypixel.net/player?key={api_key}&name={ign}"
#	res = requests.get(url)
#	data = res.json()
	error = False
	try:
		data["player"]
	except KeyError:
		if str(data) == "{'success': False, 'cause': 'You have already looked up this name recently'}":
			await ctx.send('You have already looked up this name recently. Try again in 5 minutes!')
			error = True
		else:
			await ctx.send('Unidentified error. Contact `poki95` on Discord. Thanks!')	
	if mode not in mode_list:
		await ctx.send(f'`{mode}` is not an available mode. Type `!h` for help.')
	elif error == False:
		if mode == 'all':
				displayname = data["player"]["displayname"]
				for mode_db in mode_db_list:
					if mode_db == 'oa':
						try:
							globals()[f'{mode_db}_wins'] = data["player"]["stats"]["Duels"]["wins"]
						except KeyError:  
							globals()[f'{mode_db}_wins'] = 0
					elif mode_db == 'uhc':
						try:
							globals()[f'{mode_db}_duel_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_duel_wins"]
						except KeyError:  
							globals()[f'{mode_db}_duel_wins'] = 0
						try:
							globals()[f'{mode_db}_doubles_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_doubles_wins"]
						except KeyError:
							globals()[f'{mode_db}_doubles_wins'] = 0
						try:	
							globals()[f'{mode_db}_four_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_four_wins"]
						except KeyError:
							globals()[f'{mode_db}_four_wins'] = 0
						try:
							globals()[f'{mode_db}_meetup_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_meetup_wins"]
						except KeyError:
							globals()[f'{mode_db}_meetup_wins'] = 0
						globals()[f'{mode_db}_wins'] = (
						globals()[f'{mode_db}_duel_wins']
						+ globals()[f'{mode_db}_doubles_wins']
						+ globals()[f'{mode_db}_four_wins']
						+ globals()[f'{mode_db}_meetup_wins'])
					elif mode_db in ['sw', 'mw', 'op']:
						try:
							globals()[f'{mode_db}_duel_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_duel_wins"]
						except KeyError:  
							globals()[f'{mode_db}_duel_wins'] = 0
						try:
							globals()[f'{mode_db}_doubles_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_doubles_wins"]
						except KeyError:
							globals()[f'{mode_db}_doubles_wins'] = 0
						globals()[f'{mode_db}_wins'] = (globals()[f'{mode_db}_duel_wins'] + globals()[f'{mode_db}_doubles_wins'])
					elif mode_db == 'bridge':
						try:
							globals()[f'{mode_db}_duel_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_duel_wins"]
						except KeyError:
							globals()[f'{mode_db}_duel_wins'] = 0
						try:
							globals()[f'{mode_db}_doubles_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_doubles_wins"]
						except KeyError:
							globals()[f'{mode_db}_doubles_wins'] = 0
						try:	
							globals()[f'{mode_db}_threes_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_threes_wins"]
						except KeyError:
							globals()[f'{mode_db}_threes_wins'] = 0
						try:	
							globals()[f'{mode_db}_four_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_four_wins"]
						except KeyError:
							globals()[f'{mode_db}_four_wins'] = 0
						try:	
							globals()[f'{mode_db}_2v2v2v2_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_2v2v2v2_wins"]
						except KeyError:
							globals()[f'{mode_db}_2v2v2v2_wins'] = 0
						try:	
							globals()[f'{mode_db}_3v3v3v3_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_3v3v3v3_wins"]
						except KeyError:
							globals()[f'{mode_db}_3v3v3v3_wins'] = 0
						try:	
							globals()[f'{mode_db}_capture_threes_wins'] = data["player"]["stats"]["Duels"]["capture_threes_wins"]
						except KeyError:
							globals()[f'{mode_db}_capture_threes_wins'] = 0
						globals()[f'{mode_db}_wins'] = (
						globals()[f'{mode_db}_duel_wins']
						+ globals()[f'{mode_db}_doubles_wins']
						+ globals()[f'{mode_db}_threes_wins']
						+ globals()[f'{mode_db}_four_wins']
						+ globals()[f'{mode_db}_2v2v2v2_wins']
						+ globals()[f'{mode_db}_3v3v3v3_wins']
						+ globals()[f'{mode_db}_capture_threes_wins'])
					elif mode_db in ['parkour_eight', 'duel_arena']:
						try:
							globals()[f'{mode_db}_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_wins"]
						except KeyError:
							globals()[f'{mode_db}_wins'] = 0
					else:	
						try:
							globals()[f'{mode_db}_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_duel_wins"]
						except KeyError:
							globals()[f'{mode_db}_wins'] = 0

					mode_index = mode_db_list.index(mode_db)        				# convert the database alias to the mode's full name
					mode_clean = mode_names[mode_index]
					#print(f'{mode_clean} wins: {globals()[f'{mode_db}_wins']}')	# print the wins for every mode
						
				for mode_db in mode_db_list:
					mode_index = mode_db_list.index(mode_db)        				# convert the database alias to the mode's full name
					mode_clean = mode_names[mode_index]
					if mode_db == 'oa':												# overall titles require 2x the wins compared to mode titles
						practical_wins = (globals()[f'{mode_db}_wins'])/2											# so divide practical wincount by 2
					else:
						practical_wins = globals()[f'{mode_db}_wins']				# use practical wincount 

					wincount = str(globals()[f'{mode_db}_wins'])[::-1]				# group digits by 3 for readability (e.g. 139,813)
					multiple_of_three = 1
					wincount_list = []
					for digit in wincount:
						wincount_list.append(digit)
						if multiple_of_three%3 == 0:
							wincount_list.append(',')
						multiple_of_three += 1
					wincount_list.reverse()
					if wincount_list[0] == ',':
						wincount_list.pop(0)
					wincount = ''
					for digit in wincount_list:
						wincount += digit

					div_number = 0
					for req in div_req:												# choose the right division + division number
						if practical_wins >= req:
							div = div_list[div_number]
							surplus = practical_wins - (req - div_step[div_number])
							div_num = math.floor(surplus/div_step[div_number])
							break
						div_number += 1
						
					if div_num > 50:												# make sure ASCENDED L is the maximum division
						div_num = 50	
					elif div == 'None':												# remove any division number when below Rookie
						div_num = 1
						
					if div_num != 1:												# show the division number when it's not 1
						div_num = roman.toRoman(div_num)
						if globals()[f'{mode_db}_wins'] == 1:
								globals()[f'message_{mode_db}'] = f'{wincount} win - {mode_clean} {div} {div_num}'		
						else:
								globals()[f'message_{mode_db}'] = f'{wincount} wins - {mode_clean} {div} {div_num} '
					else:															# hide the division number when it's 1
						if globals()[f'{mode_db}_wins'] == 1:													
								globals()[f'message_{mode_db}'] = f'{wincount} win - {mode_clean} {div}'			
						else:
								globals()[f'message_{mode_db}'] = f'{wincount} wins - {mode_clean} {div}'
				await ctx.send(f'''
{get_rank(ign, data)} {displayname}
{message_oa}
{message_uhc}
{message_sw}
{message_mw}
{message_blitz}
{message_op}
{message_classic}
{message_bow}
{message_potion}
{message_combo}
{message_bowspleef}
{message_sumo}
{message_bridge}
{message_parkour_eight}
{message_boxing}
{message_duel_arena}
''')
								
		#		try:
		#			capture_duel_wins = data["player"]["stats"]["Duels"]["capture_duel_wins"]
		#		except KeyError:
		#			capture_duel_wins = 0
		#		ghost_wins = (capture_duel_wins)
		#		await ctx.send(f'Ghost wins: {ghost_wins}')
		else:
			mode_index = mode_list.index(mode)
			mode_db = mode_db_list[mode_index]
			if mode_db == 'oa':
				try:
					globals()[f'{mode_db}_wins'] = data["player"]["stats"]["Duels"]["wins"]
				except KeyError:  
					globals()[f'{mode_db}_wins'] = 0
			elif mode_db == 'uhc':
				
				try:
					globals()[f'{mode_db}_duel_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_duel_wins"]
				except KeyError:  
					globals()[f'{mode_db}_duel_wins'] = 0
				try:
					globals()[f'{mode_db}_doubles_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_doubles_wins"]
				except KeyError:
					globals()[f'{mode_db}_doubles_wins'] = 0
				try:	
					globals()[f'{mode_db}_four_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_four_wins"]
				except KeyError:
					globals()[f'{mode_db}_four_wins'] = 0
				try:
					globals()[f'{mode_db}_meetup_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_meetup_wins"]
				except KeyError:
					globals()[f'{mode_db}_meetup_wins'] = 0
				globals()[f'{mode_db}_wins'] = (
				globals()[f'{mode_db}_duel_wins']
				+ globals()[f'{mode_db}_doubles_wins']
				+ globals()[f'{mode_db}_four_wins']
				+ globals()[f'{mode_db}_meetup_wins'])
			elif mode_db in ['sw', 'mw', 'op']:
				try:
					globals()[f'{mode_db}_duel_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_duel_wins"]
				except KeyError:  
					globals()[f'{mode_db}_duel_wins'] = 0
				try:
					globals()[f'{mode_db}_doubles_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_doubles_wins"]
				except KeyError:
					globals()[f'{mode_db}_doubles_wins'] = 0
				globals()[f'{mode_db}_wins'] = (globals()[f'{mode_db}_duel_wins'] + globals()[f'{mode_db}_doubles_wins'])
			elif mode_db == 'bridge':
				try:
					globals()[f'{mode_db}_duel_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_duel_wins"]
				except KeyError:
					globals()[f'{mode_db}_duel_wins'] = 0
				try:
					globals()[f'{mode_db}_doubles_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_doubles_wins"]
				except KeyError:
					globals()[f'{mode_db}_doubles_wins'] = 0
				try:	
					globals()[f'{mode_db}_threes_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_threes_wins"]
				except KeyError:
					globals()[f'{mode_db}_threes_wins'] = 0
				try:	
					globals()[f'{mode_db}_four_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_four_wins"]
				except KeyError:
					globals()[f'{mode_db}_four_wins'] = 0
				try:	
					globals()[f'{mode_db}_2v2v2v2_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_2v2v2v2_wins"]
				except KeyError:
					globals()[f'{mode_db}_2v2v2v2_wins'] = 0
				try:	
					globals()[f'{mode_db}_3v3v3v3_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_3v3v3v3_wins"]
				except KeyError:
					globals()[f'{mode_db}_3v3v3v3_wins'] = 0
				try:	
					globals()[f'{mode_db}_capture_threes_wins'] = data["player"]["stats"]["Duels"]["capture_threes_wins"]
				except KeyError:
					globals()[f'{mode_db}_capture_threes_wins'] = 0
				globals()[f'{mode_db}_wins'] = (
				globals()[f'{mode_db}_duel_wins']
				+ globals()[f'{mode_db}_doubles_wins']
				+ globals()[f'{mode_db}_threes_wins']
				+ globals()[f'{mode_db}_four_wins']
				+ globals()[f'{mode_db}_2v2v2v2_wins']
				+ globals()[f'{mode_db}_3v3v3v3_wins']
				+ globals()[f'{mode_db}_capture_threes_wins'])
			elif mode_db in ['parkour_eight', 'duel_arena']:
				try:
					globals()[f'{mode_db}_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_wins"]
				except KeyError:
					globals()[f'{mode_db}_wins'] = 0
			else:	
				try:
					globals()[f'{mode_db}_wins'] = data["player"]["stats"]["Duels"][f"{mode_db}_duel_wins"]
				except KeyError:
					globals()[f'{mode_db}_wins'] = 0
			# print(f'{globals()[f'{mode_db}_wins']}')
			
			mode_index = mode_db_list.index(mode_db)        				# convert the database alias to the mode's full name
			mode_clean = mode_names[mode_index]
			
			if mode_db == 'oa':													# overall titles require 2x the wins compared to mode titles
				practical_wins = (globals()[f'{mode_db}_wins'])/2				# so divide practical wincount by 2
			else:
				practical_wins = globals()[f'{mode_db}_wins']					# use practical wincount 

			wincount = str(globals()[f'{mode_db}_wins'])[::-1]					# group digits by 3 for readability (e.g. 139,813)
			multiple_of_three = 1
			wincount_list = []
			for digit in wincount:
				wincount_list.append(digit)
				if multiple_of_three%3 == 0:
					wincount_list.append(',')
				multiple_of_three += 1
			wincount_list.reverse()
			if wincount_list[0] == ',':
				wincount_list.pop(0)
			wincount = ''
			for digit in wincount_list:
				wincount += digit

			div_number = 0
			for req in div_req:													# choose the right division + division number
				if practical_wins >= req:
					div = div_list[div_number]
					surplus = practical_wins - (req - div_step[div_number])
					div_num = math.floor(surplus/div_step[div_number])
					break
				div_number += 1
				
			if div_num > 50:													# make sure ASCENDED L is the maximum division
				div_num = 50	
			elif div == 'None':													# remove any division number when below Rookie
				div_num = 1
				
			if div_num != 1:													# show the division number when it's not 1
				div_num = roman.toRoman(div_num)
				if globals()[f'{mode_db}_wins'] == 1:
						await ctx.send(f'{mode_clean} {div} {div_num} - {wincount} win')		
				else:
						await ctx.send(f'{mode_clean} {div} {div_num} - {wincount} wins')
			else:																# hide the division number when it's 1
				if globals()[f'{mode_db}_wins'] == 1:												
						await ctx.send(f'{mode_clean} {div} - {wincount} win')			
				else:
						await ctx.send(f'{mode_clean} {div} - {wincount} wins')

@bot.command(name='kit')
async def kit(ctx, ign, kit_user):
	data = dataget(ign)
#	url = f"https://api.hypixel.net/player?key={api_key}&name={ign}"
#	res = requests.get(url)
#	data = res.json()
	kit = kit_user.lower()
	error = False
	try:
		data["player"]
	except KeyError:
		if str(data) == "{'success': False, 'cause': 'You have already looked up this name recently'}":
			await ctx.send('You have already looked up this name recently. Try again in 5 minutes!')
		else:
			await ctx.send('Unidentified error. Contact `poki95` on Discord. Thanks!')
		error = True
	if error == False:
		displayname = data["player"]["displayname"]
		globals()[f'{kit}_wins'] = data["player"]["stats"]["Duels"][f"{kit}_kit_wins"]
		await ctx.send(f'{get_rank(ign, data)} {displayname} has {globals()[f'{kit}_wins']} {kit} wins.')

# Run the bot
bot.run(TOKEN)
