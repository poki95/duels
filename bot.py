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
stats_file = 'stats.json'

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# given data
mode_list = ['oa', 'uhc', 'sw', 'mw', 'blitz', 'op', 'classic', 'bow', 'ndb', 'combo', 'tnt', 'sumo', 'bridge', 'pkd', 'boxing', 'arena', 'all'] # mode aliases
mode_db_list = ['oa', 'uhc', 'sw', 'mw', 'blitz', 'op', 'classic', 'bow', 'potion', 'combo', 'bowspleef', 'sumo', 'bridge', 'parkour_eight', 'boxing', 'duel_arena'] # mode database aliases
mode_names = ['Overall', 'UHC', 'SkyWars', 'MW', 'Blitz', 'OP', 'Classic', 'Bow', 'NoDebuff', 'Combo', 'TNT', 'Sumo', 'Bridge', 'Parkour', 'Boxing', 'Arena'] # clean mode names
div_list = ['ASCENDED', 'DIVINE', 'CELESTIAL', 'Godlike', 'Grandmaster', 'Legend', 'Master', 'Diamond', 'Gold', 'Iron', 'Rookie', 'None'] # divisions
div_req = [100000, 50000, 25000, 10000, 5000, 2000, 1000, 500, 250, 100, 50, 0] # requirements for each division title
div_step = [10000, 10000, 5000, 3000, 1000, 600, 200, 100, 50, 30, 10, 1] # requirements to go up a level within a division title
ranked_kits = ['default', 'scout', 'magician', 'armorer', 'champion', 'bowman', 'athlete', 'blacksmith', 'healer', 'pyromancer', 'hound', 'paladin']
kits = [
    "pyromancer", "magician", "athlete", "armorer", "champion", "scout", "hound", "paladin", "bowman",
    "healer", "cactus", "enderman", "knight", "batguy", "frog", "pharaoh", "pro",
    "ecologist", "grenade", "cannoneer", "golem", "hunter", "farmer", "disco", "slime", "enderchest",
    "guardian", "snowman", "enchanter", "warlock", "zookeeper", "pig rider", "nether lord", "fisherman",
    "troll", "energix", "salmon", "end lord",
    "sloth", "armorsmith", "jester", "princess",
    "fishmonger", "rookie", "archeologist", "engineer", "pyro", "fallen angel"
]
uhc_submodes = ['uhc_duel_wins', 'uhc_doubles_wins', 'uhc_four_wins', 'uhc_meetup_wins']
bridge_submodes = ['bridge_duel_wins', 'bridge_doubles_wins', 'bridge_threes_wins', 'bridge_four_wins', 'bridge_2v2v2v2_wins', 'bridge_3v3v3v3_wins', 'capture_threes_wins']
	
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

def format_number(n):
    return f'{n:,}'

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
                    return ('[MVP+] ')
                else:
                    return("[MVP++] ")
            else:
                return("[MVP+] ")
        elif rank == 'MVP':
            return ('[MVP] ')
        elif rank == 'VIP_PLUS':
            return ('[VIP+] ')
        elif rank == 'VIP':
            return ('[VIP] ')
    else:
        return str()

def get_division_info(wins, is_oa=False):
        practical_wins = wins / 2 if is_oa else wins
        for i, req in enumerate(div_req):
            if practical_wins >= req:
                div = div_list[i]
                div_num = math.floor((practical_wins - (req - div_step[i])) / div_step[i])
                break
        else:
            div = 'None'
            div_num = 1
        div_num = min(div_num, 50)
        return div, div_num

def load_stats():
    if not os.path.exists(stats_file):
        return {}
    with open(stats_file, "r") as f:
        return json.load(f)

def save_stats(data):
    with open(stats_file, "w") as f:
        json.dump(data, f, indent=4)


# Bot readiness confirmation
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('Pong! 🏓')
    
@bot.listen("stats")
async def stats(ctx):
	stats = load_stats()
	stats += 1
	save_usage(stats)

    
# Bot commands
@bot.command(name='h')
async def h(ctx):
	await ctx.send(f"""
# **Help Menu** <:avatar:1382441832809500792>

- `!d <ign>` — Check wins and division title for a player in all duels modes.
  -> `!d Monk_Eez`

- `!d <ign> <mode>` — Check wins and division title for a player in a specific duels mode.
  -> `!d Kuruxo parkour`

- `!kit <ign>` — Check all kits wins in SkyWars duels.
  -> `!kit LucaStevo`

- `!kit <ign> <kit>` — Check kit wins in MegaWalls, SkyWars and Blitz Duels.
  -> `!kit poki95 pyromancer`

- `!mkw <ign>` - Check best player's kit's wins.
   -> `!mkw mutton38`

Available modes: `oa`, `uhc`, `sw`, `mw`, `blitz`, `op`, `classic`, `bow`, `ndb`, `combo`, `tnt`, `sumo`, `bridge`, `pkd`, `boxing`, `arena`
Available kits: All sw, bw and blitzd kits.

For any issues, contact **poki95** on Discord.
""")

@bot.command(name='d')
async def d(ctx, ign, mode='all'):
	data = dataget(ign)
	
	error = False
	if "player" not in data:
		if str(data) == "{'success': False, 'cause': 'Invalid API key'}":
			await ctx.send("Invalid API key... Contact `poki95` on Discord. (hypixel won't give me a developer key bruh)")
			error = True
		else:
			await ctx.send('Unidentified error. Contact `poki95` on Discord. Thanks!')
		return

	if mode.lower() not in mode_list:
		await ctx.send(f'`{mode}` is not an available mode. Type `!h` for help.')
		return

	displayname = data["player"]["displayname"]
	duels_data = data["player"].get("stats", {}).get("Duels", {})
	mode_db = mode if mode == 'all' else mode_db_list[mode_list.index(mode.lower())]
	
	def get_mode_wins(mode_db):
		try:
			if mode_db == 'oa':
				return duels_data.get("wins", 0)
			elif mode_db == 'uhc':
				return sum(duels_data.get(submode, 0) for submode in uhc_submodes)
			elif mode_db == 'bridge':
				return sum(duels_data.get(submode, 0) for submode in bridge_submodes)
			elif mode_db in ['sw', 'mw', 'op']:
				return duels_data.get(f'{mode_db}_duel_wins', 0) + duels_data.get(f'{mode_db}_doubles_wins', 0)
			elif mode_db in ['parkour_eight', 'duel_arena']:
				return duels_data.get(f'{mode_db}_wins', 0)
			else:
				return duels_data.get(f'{mode_db}_duel_wins', 0)
		except KeyError:
			return 0

	
	wins = {}
	messages = {}
	
	modes = mode_db_list if mode == 'all' else [mode_db_list[mode_list.index(mode)]]
	
	for mode_db in modes:
		win_count = get_mode_wins(mode_db)
		wins[mode_db] = win_count
		
		is_oa = (mode_db == 'oa')
		div, div_num = get_division_info(win_count, is_oa)	
		division = f'{div} {roman.toRoman(div_num)}' if div_num != 1 and div != "None" else div
		
		win_s = "win" if win_count == 1 else "wins"
		mode_clean = mode_names[mode_db_list.index(mode_db)]
		messages[mode_db] = f"{format_number(win_count)} {mode_clean} {win_s} - {mode_clean} {division}"
        
	if mode == 'all':
		response = f"\n{get_rank(ign, data)}{displayname}\n" + "\n".join(messages[m] for m in mode_db_list)
		await ctx.send(response)
	else:
		await ctx.send(messages[modes[0]])
		
@bot.command(name='kit')
async def kit(ctx, ign, *, kit_user='all'):
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
		if kit == 'ranked':
			kit_wins_list = []
			for ranked_kit in ranked_kits:
				try:
					wins = data["player"]["stats"]["Duels"].get(f"{ranked_kit}_kit_wins", 0)
				except KeyError:
					wins = 0
				win_word = "win" if wins == 1 else "wins"
				kit_wins_list.append((wins, f"{wins} {ranked_kit} {win_word}"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			try:
				sw_duel_wins = data["player"]["stats"]["Duels"]["sw_duel_wins"]
				sw_doubles_wins = data["player"]["stats"]["Duels"]["sw_doubles_wins"]
				sw_wins = sw_duel_wins + sw_doubles_wins
			except KeyError:
				sw_wins = 0
			message_lines = [f'{get_rank(ign, data)}{displayname} has {sw_wins} SkyWars Duels wins.']
			message_lines.extend(msg for _, msg in sorted_kits)
			await ctx.send('\n'.join(message_lines))
		elif kit == 'all':
			kit_wins_list = []
			for swd_kit in kits:
				try:
					wins = data["player"]["stats"]["Duels"].get(f"{swd_kit}_kit_wins", 0)
				except KeyError:
					wins = 0
				if wins > 0:  # Only include kits with at least one win
					win_s = "win" if wins == 1 else "wins"
					kit_wins_list.append((wins, f"{wins} {swd_kit} {win_s}"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			try:
				sw_duel_wins = data["player"]["stats"]["Duels"]["sw_duel_wins"]
				sw_doubles_wins = data["player"]["stats"]["Duels"]["sw_doubles_wins"]
				sw_wins = sw_duel_wins + sw_doubles_wins
			except KeyError:
				sw_wins = 0
			message_lines = [f'{get_rank(ign, data)}{displayname} has {sw_wins} SkyWars Duels wins.']
			message_lines.extend(msg for _, msg in sorted_kits)
			await ctx.send('\n'.join(message_lines))
		else:
			globals()[f'{kit}_wins'] = data["player"]["stats"]["Duels"][f"{kit}_kit_wins"]
			await ctx.send(f'{get_rank(ign, data)}{displayname} has {globals()[f'{kit}_wins']} {kit} wins.')

@bot.command(name='wlb')
async def wlb(ctx):
	url = f"https://api.hypixel.net/leaderboards?key={api_key}"
	res = requests.get(url)
	data = res.json()
	duels_lb_data = data.get('leaderboards', {}).get('DUELS', {})
	weekly_lb_data = duels_lb_data[0].get('leaders', [])
	messages = {}
	pos = 0
	for uuid in weekly_lb_data[:10]:
		url = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"
		res = requests.get(url)
		data = res.json()
		displayname = data["player"]["displayname"]
		pos += 1
		messages[uuid] = f"{pos}. {get_rank(displayname, data)}{displayname}"
	response = f'Duels Weekly:\n' + "\n".join(messages[m] for m in weekly_lb_data[:10])
	await ctx.send(response)

@bot.command(name='mlb')
async def mlb(ctx):
	url = f"https://api.hypixel.net/leaderboards?key={api_key}"
	res = requests.get(url)
	data = res.json()
	duels_lb_data = data.get('leaderboards', {}).get('DUELS', {})
	monthly_lb_data = duels_lb_data[1].get('leaders', [])
	messages = {}
	pos = 0
	for uuid in monthly_lb_data[:10]:
		url = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"
		res = requests.get(url)
		data = res.json()
		displayname = data["player"]["displayname"]
		pos += 1
		messages[uuid] = f"{pos}. {get_rank(displayname, data)}{displayname}"
	response = f'Duels Monthly:\n' + "\n".join(messages[m] for m in monthly_lb_data[:10])
	await ctx.send(response)
	
@bot.command(name='mkw')
async def mkw(ctx, ign):
	data = dataget(ign)
	displayname = data["player"]["displayname"]
	try:
		duels_data = data["player"]["stats"]["Duels"]
	except (KeyError, TypeError):
		await ctx.send('Error message ;)')

	max_wins = 0
	best_kit = None

	for swd_kit in kits:
		kit_wins = duels_data.get(f"{swd_kit}_kit_wins", 0)
		if kit_wins > max_wins:
			max_wins = kit_wins
			best_kit = swd_kit
	sw_wins = duels_data.get(f'sw_duel_wins', 0) + duels_data.get(f'sw_doubles_wins', 0)
	percentage = round((max_wins/sw_wins)*100, 2)
	await ctx.send(f"{get_rank(displayname, data)}{displayname}{displayname}'s best kit is {best_kit.capitalize()}, with {max_wins} wins. ({percentage}%)")

# Run the bot
bot.run(TOKEN)
