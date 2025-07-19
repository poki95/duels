import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import math
import requests
import json
import roman
import csv
import time
import random
import asyncio
from re import sub
from mojang import API

# Discord bot token and hypixel api key
load_dotenv(dotenv_path="keys.env")
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
api_key = os.getenv("HYPIXEL_API_KEY")									# update every 3 days
dev_api_key = os.getenv("DEV_HYPIXEL_API_KEY")
stats_file = 'stats.json'

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# given data
mode_list = ['oa', 'uhc', 'sw', 'mw', 'blitz', 'op', 'classic', 'bow', 'ndb', 'combo', 'tnt', 'sumo', 'bridge', 'pkd', 'boxing', 'arena', 'all'] # mode aliases
mode_db_list = ['all_modes', 'uhc', 'sw', 'mw', 'blitz', 'op', 'classic', 'bow', 'potion', 'combo', 'bowspleef', 'sumo', 'bridge', 'parkour_eight', 'boxing', 'duel_arena'] # mode database aliases
mode_db_list_long = ['all_modes', 'uhc', 'skywars', 'megawalls', 'blitz', 'op', 'classic', 'bow', 'potion', 'combo', 'tnt_games', 'sumo', 'bridge', 'parkour', 'boxing', 'duel_arena']
mode_names = ['', 'UHC', 'SkyWars', 'MW', 'Blitz', 'OP', 'Classic', 'Bow', 'NoDebuff', 'Combo', 'TNT', 'Sumo', 'Bridge', 'Parkour', 'Boxing', 'Arena'] # clean mode names
div_list = ['ASCENDED', 'DIVINE', 'CELESTIAL', 'Godlike', 'Grandmaster', 'Legend', 'Master', 'Diamond', 'Gold', 'Iron', 'Rookie', 'None'] # divisions
div_req = [100000, 50000, 25000, 10000, 5000, 2000, 1000, 500, 250, 100, 50, 0] # requirements for each division title
div_step = [10000, 10000, 5000, 3000, 1000, 600, 200, 100, 50, 30, 10, 1] # requirements to go up a level within a division title
kits_sw = [
    "default", "scout", "magician", "armorer", "champion", "bowman", "athlete",
    "blacksmith", "healer", "pyromancer", "hound", "paladin", "armorsmith",
    "baseball player", "cannoneer", "ecologist", "enchanter", "enderman",
    "guardian", "hunter", "knight", "pharaoh", "pro", "snowman", "speleologist",
    "batguy", "disco", "energix", "cactus", "archeologist", "warlock", "frog",
    "grenade", "engineer", "pig rider", "salmon", "slime", "jester", "zookeeper",
    "sloth", "enderchest", "farmer", "fisherman", "princess", "pyro", "troll", "rookie",
	"fallen angel", "thundermeister", "end lord", "fishmonger", "nether lord",
    "monster trainer", "skeletor", "pyromaniac"
]
kits_blitz = [
    "horsetamer", "ranger", "archer", "astronaut", "troll", "meatmaster", "reaper", "shark",
    "reddragon", "golem", "jockey", "viking", "speleologist", "donkeytamer", "toxicologist",
    "rogue", "warlock", "slimeyslime", "shadow knight", "baker", "knight", "pigman", "guardian",
    "hype train", "warrior", "blaze", "wolftamer", "tim", "fisherman", "phoenix", "paladin",
    "milkman", "snowman", "farmer", "florist", "necromancer", "scout", "hunter", "diver",
    "armorer", "creepertamer", "arachnologist"
]
kits_mw = [
    'arcanist', 'cow', 'dreadlord', 'golem', 'herobrine', 'pigman', 'zombie',
    'angel', 'shark', 'pirate', 'werewolf', 'phoenix', 'squid', 'moleman',
    'shaman', 'hunter', 'creeper', 'automaton', 'enderman', 'blaze',
    'assassin', 'snowman', 'renegade', 'dragon', 'spider', 'sheep', 'skeleton'
]
kits = kits_sw + kits_blitz + kits_mw + ['top10', 'all']
kit_options = kits + ['sw', 'mw', 'blitz', 'top10', 'all']
uhc_submodes_ = ['uhc_duel_', 'uhc_doubles_', 'uhc_four_', 'uhc_meetup_']
bridge_submodes_ = ['bridge_duel_', 'bridge_doubles_', 'bridge_threes_', 'bridge_four_', 'bridge_2v2v2v2_', 'bridge_3v3v3v3_', 'capture_threes_']
min_wins_per_hour = [40, 75, 25, 80, 80, 100, 70, 20, 60, 80, 100, 20, 10, 20, 60]
max_wins_per_hour = [70, 85, 40, 100, 100, 150, 130, 40, 90, 110, 150, 30, 20, 30, 60]
gph = [70, 85, 40, 95, 85, 150, 120, 40, 75, 80, 160, 30, 12, 30, 60]
prefix_icons_db = ['STAR', 'FANCY_STAR', 'POINTY_STAR', 'SUN', 'BIOHAZARD', 'FLOWER', 'YIN_AND_YANG', 'SNOWMAN', 'HEART', 'GG', 'SMILEY', 'DIV_RANKING', '']
prefix_icons = ['✫', '✯', '✵', '☀', '☣', '❀', '☯', '☃', '❤', '**GG**', '^_^', '**#???**', '']
swd_lifetime = ['poki95', 'Monk_Eez', 'MartySnoozeman', 'Lucastevo', 'D3pTTT', 'Scary_J', 'nobuh', 'mutton38', 'ImHomoAf', '1337ALBY']

# Functions
def dataget(ign):														# Load player's Hypixel stats
	try:															
		response = requests.get(f"https://playerdb.co/api/player/minecraft/{ign}")
		uuid = response.json()["data"]["player"]["id"]
		url = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"
		res = requests.get(url)
		data = res.json()
	except KeyError:
		data = 'Failed to load data for this player.'
	return data
	
def get_duels_data(data):
	duels_data = data["player"].get("stats", {}).get("Duels", {})
	return duels_data

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

def statusget(ign):
	try:															
		response = requests.get(f"https://playerdb.co/api/player/minecraft/{ign}")
		uuid = response.json()["data"]["player"]["id"]
		url = f"https://api.hypixel.net/status?key={api_key}&uuid={uuid}"
		res = requests.get(url)
		status = res.json()
	except KeyError:
		status = 'Failed to load status for this player.'
	return status	

def get_recentgames(ign):
	try:															
		response = requests.get(f"https://playerdb.co/api/player/minecraft/{ign}")
		uuid = response.json()["data"]["player"]["id"]
		url = f"https://api.hypixel.net/recentgames?key={api_key}&uuid={uuid}"
		res = requests.get(url)
		recentgames = res.json()
	except KeyError:
		recentgames = 'Failed to load recent games for this player.'
	return recentgames

def get_mode_stat(mode_db, type, duels_data):
	if mode_db == 'all_modes':
		return duels_data.get(type, 0)
	elif mode_db == 'uhc':
		amount = 0
		for submode in uhc_submodes_:
			submode += type
			amount += duels_data.get(submode, 0)
		return amount
	elif mode_db == 'bridge':
		if type == 'kills' or type == 'deaths':
			amount = duels_data.get(f'bridge_{type}', 0)
		else:
			amount = 0
			for submode in bridge_submodes_:
				submode += type
				amount += duels_data.get(submode, 0)
		return amount
	elif mode_db in ['sw', 'mw', 'op']:
		return duels_data.get(f'{mode_db}_duel_{type}', 0) + duels_data.get(f'{mode_db}_doubles_{type}', 0)
	elif mode_db in ['parkour_eight', 'duel_arena']:
		return duels_data.get(f'{mode_db}_{type}', 0)
	else:
		return duels_data.get(f'{mode_db}_duel_{type}', 0)

def get_kit_wins(mode_db, kit, duels_data):
	wins = duels_data.get(f"{mode_db}_duel_{kit}_kit_wins", 0) + duels_data.get(f"{mode_db}_doubles_{kit}_kit_wins", 0)
	return wins

def stalk(ign):
	status = statusget(ign)
	session = status.get("session", {})
	game = session.get('gameType')
	mode = session.get('mode')
	map = session.get('map', False)
	return game, mode, map

def ign_based_on_discord_user(display_name, user_name):
	ign = display_name
	data = dataget(ign)
	if data == 'Failed to load data for this player.':
		ign = user_name
	return ign

def log(command, server, user):
	return f'{command} used in {server} by {user}'

def get_duels_stats(mode_db, duels_data):
	win_count = get_mode_stat(mode_db, 'wins', duels_data)
	win_s = "win" if win_count == 1 else "wins"
	loss_count = get_mode_stat(mode_db, 'losses', duels_data)
	loss_es = "loss" if loss_count == 1 else "losses"
	kill_count = get_mode_stat(mode_db, 'kills', duels_data)
	kill_s = "kill" if kill_count == 1 else "kills"
	death_count = get_mode_stat(mode_db, 'deaths', duels_data)
	death_s = "death" if death_count == 1 else "deaths"
	return win_count, win_s, loss_count, loss_es, kill_count, kill_s, death_count, death_s

def get_displayname(ign):
	return requests.get(f"https://playerdb.co/api/player/minecraft/{ign}").json()["data"]["player"]["username"]

# Bot readiness confirmation
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')

# Bot commands
@bot.command(name='ping')
async def ping(ctx, amount=1):
	for a in range(amount):
		await ctx.reply(f'Pong! 🏓')
    
@bot.command(name='h')
async def h(ctx):
	await ctx.send(f"""
# **Poki's Stats Checker** <:avatar:1382441832809500792>

- `!d <ign>` — Check wins, division title and estimated playtime for a player in all duels modes.
  -> `!d MCreeperWL`

- `!d <ign> <mode>` — Check wins, division title and estimated playtime for a player in a specific duels mode.
  -> `!d Sothey boxing`

- `!kit <ign>` — Check all player's kits' wins in a specific mode.
  -> `!kit Kronosaurus`

- `!kit <ign> <kit> <mode>` — Check player's kit's wins in MegaWalls, SkyWars or Blitz Duels.
  -> `!kit poki95 pyromancer sw`

- `!s <ign>` — Check player's status.
  -> `!s poki95`

- `!uuid <ign>` — Check player's UUID.
  -> `!uuid poki95`

- `!tlb <weekly/monthly>` - Check current Overall Weekly/Monthly duels leaderboard.
  -> `!tlb monthly`
	
For any issues, contact **`poki95`** on Discord.
""")
	print(f'!h used in {ctx.guild.name} by {ctx.author.name}')

@bot.command(name='d')
async def d(ctx, ign=None, mode='all'):
	if ign == None:
		ign = ign_based_on_discord_user(ctx.author.display_name, ctx.author.name)
			
	if ign.lower() in mode_list:
		mode = ign
		ign = ctx.author.display_name
		data = dataget(ign)
		if data == 'Failed to load data for this player.':
			ign = ctx.author.name
			
	data = dataget(ign)

	if "player" not in data:
		if str(data) == "{'success': False, 'cause': 'Invalid API key'}":
			api_key = os.getenv("HYPIXEL_API_KEY")	
		else:
			await ctx.send('Invalid IGN.')
		return

	if mode.lower() not in mode_list:
		await ctx.send(f'`{mode}` is not an available mode. Type `!h` for help.')
		return

	displayname = get_displayname(ign)

	if displayname.count('_') >= 2:
		displayname = f'`{displayname}`'

	duels_data = get_duels_data(data)
	
	equipped_icon = prefix_icons[prefix_icons_db.index(duels_data.get("equipped_prefix_icon", ''))]
	equipped_color = duels_data.get("equipped_prefix_color", '')
	equipped_title = duels_data.get("active_cosmetictitle", '')
	if equipped_title != '':
		equipped_icon = prefix_icons[prefix_icons_db.index(duels_data.get("equipped_prefix_icon", 'STAR'))]
	else:
		equipped_icon = ''
	
	current_title = ''
	wins = {}
	messages = {}
	
	modes = mode_db_list # if mode == 'all' else [mode_db_list[mode_list.index(mode)]]
	wins_list = []
	overall_playtime = 0
	for mode_db in modes:
		win_count, win_s, loss_count, loss_es, kill_count, kill_s, death_count, death_s = get_duels_stats(mode_db, duels_data)
		is_oa = (mode_db == 'oa')
		div, div_num = get_division_info(win_count, is_oa)	
		division = f'{div} {roman.toRoman(div_num)}' if div_num != 1 and div != "None" else div

		if ign.lower() == 'allsharkboy' and mode_db == 'bow':
			playtime = 100
		else:
			playtime = round((win_count + loss_count)/gph[mode_db_list.index(mode_db)-1], 1)

		mode_clean = mode_names[mode_db_list.index(mode_db)]
		if mode_db != 'all_modes':			
			overall_playtime += playtime
			if mode_db_list_long[mode_db_list.index(mode_db)] in equipped_title:
				current_title = f'{equipped_icon} {mode_clean} {oa_division if mode_db == 'all_modes' else division}'
			wins_list.append((win_count, f"{format_number(win_count)} {mode_clean} {win_s} - {mode_clean} {division} (~{playtime}h)"))

		else:
			overall_win_count = get_mode_stat(mode_db, 'wins', duels_data)
			div, div_num = get_division_info(win_count, True)	
			oa_division = f'{div} {roman.toRoman(div_num)}' if div_num != 1 and div != "None" else div
			win_s = "win" if win_count == 1 else "wins"
			mode_clean = mode_names[mode_db_list.index(mode_db)]
			if 'all_modes' in equipped_title:
				current_title = f'{equipped_icon} {mode_clean} {oa_division if mode_db == 'all_modes' else division}'
	sorted_modes = sorted(wins_list, key=lambda x: x[0], reverse=True)
	if displayname in swd_lifetime:
		if equipped_icon == '**#???**' and 'SkyWwaars' in current_title:
			current_title = current_title.replace('**#???**', f"**#{str(swd_lifetime.index(displayname)+1)}**")
		if displayname == 'poki95':
			current_title = '**#1** SkyWars ASCENDED II'
	if mode == 'all':
		message_lines = [f"{sub(' +', ' ', current_title)} {get_rank(ign, data)}{displayname}\n{format_number(overall_win_count)} Overall {win_s} - {oa_division} (~{round(overall_playtime)}h)"]
		message_lines.extend(msg for _, msg in sorted_modes)
		await ctx.send('\n'.join(message_lines))
	else:
		mode_db = mode if mode == 'all' else mode_db_list[mode_list.index(mode.lower())]
		win_count, win_s, loss_count, loss_es, kill_count, kill_s, death_count, death_s = get_duels_stats(mode_db, duels_data)
		is_oa = (mode_db == 'oa')
		div, div_num = get_division_info(win_count, is_oa)	
		division = f'{div} {roman.toRoman(div_num)}' if div_num != 1 and div != "None" else div
		mode_clean = mode_names[mode_db_list.index(mode_db)]
		playtime = round((win_count + loss_count)/gph[mode_db_list.index(mode_db)-1], 1)
		WLR = round(win_count/loss_count, 2) if loss_count != 0 else win_count
		KDR = round(kill_count/death_count, 2) if death_count != 0 else kill_count
		if mode in ['pkd', 'tnt', 'boxing']:
			message = sub(' +', ' ', f"""✫ {mode_clean} {oa_division if mode == 'oa' else division} {get_rank(ign, data)}{displayname} (~{playtime}h)
			{format_number(win_count)} {win_s} - {format_number(loss_count)} {loss_es} - {WLR} WLR""")			
		else:
			message = sub(' +', ' ', f"""✫ {mode_clean} {oa_division if mode == 'oa' else division} {get_rank(ign, data)}{displayname} (~{playtime if mode != 'oa' else overall_playtime}h)
			{format_number(win_count)} {win_s} - {format_number(loss_count)} {loss_es} - {WLR} WLR
			{format_number(kill_count)} {kill_s} - {format_number(death_count)} {death_s} - {KDR} KDR""")
		await ctx.send(message)
	print(log(ctx.message.content, ctx.guild.name, ctx.author.name))
	# print(f'!d {ign} {mode} used in {ctx.guild.name} by {ctx.author.name}')
	
@bot.command(name='kit')
async def kit(ctx, ign=None, mode='sw', kit='top10'):
	if ign == None:
		ign = ign_based_on_discord_user(ctx.author.display_name, ctx.author.name)
	elif ign.lower() in kits:
		kit = ign.lower()
		ign = ctx.author.display_name
		data = dataget(ign)
		if data == 'Failed to load data for this player.':
			ign = ctx.author.name
	elif ign.lower() in ['sw', 'blitz', 'mw']:
		mode = ign
		ign = ctx.author.display_name
		data = dataget(ign)
		if data == 'Failed to load data for this player.':
			ign = ctx.author.name

	data = dataget(ign)

	if data == 'Failed to load data for this player.':
		await ctx.send('Invalid IGN.')
		return

	if mode.lower() not in kit_options:
		await ctx.send(f'`{mode}` is not an available option. Type `!h` for help.')
		return
	if kit.lower() not in kit_options:
		await ctx.send(f'``{kit}` is not an available option. Type `!h` for help.')
		return		
	if mode.lower() in kits:
		if kit.lower() in ['sw', 'blitz', 'mw']:
			kit, mode = mode, kit
		else:
			kit, mode = mode, 'sw'

	displayname = get_displayname(ign)
	duels_data = get_duels_data(data)

	if mode.lower() == 'sw':
		sw_wins = get_mode_stat('sw', 'wins', duels_data)
		message_lines_sw = [f"{get_rank(ign, data)}{displayname} has {sw_wins} SkyWars Duels wins."]
		if kit.lower() == 'top10':
			kit_wins_list = []
			for swd_kit in kits_sw:
				wins = get_kit_wins('sw', swd_kit, duels_data)
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					percentage = round((wins/sw_wins)*100, 2) if sw_wins > 0 else 0.0
					kit_wins_list.append((wins, f"{wins} {swd_kit.capitalize()} {win_s} ({percentage}%)"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_sw.extend(msg for _, msg in sorted_kits[:10])
			remaining = sorted_kits[10:]
			if remaining:
				remaining_wins = sum(w for w, _ in remaining)
				remaining_percentage = round((remaining_wins/sw_wins)*100, 2) if sw_wins > 0 else 0.0
				win_s = "win" if remaining_wins == 1 else "wins"
				message_lines_sw.append(f"+ {remaining_wins} {win_s} with other kits ({remaining_percentage}%)")
			await ctx.send('\n'.join(message_lines_sw))
		elif kit == 'all':
			kit_wins_list = []
			for swd_kit in kits:
				wins = get_kit_wins('sw', swd_kit, duels_data)
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					kit_wins_list.append((wins, f"{wins} {swd_kit.capitalize()} {win_s}"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_sw.extend(msg for _, msg in sorted_kits)
			await ctx.send('\n'.join(message_lines_sw))
		else:
			wins = get_kit_wins('sw', kit, duels_data)
			win_s = "win" if wins == 1 else "wins"
			percentage = round((wins/sw_wins)*100, 2) if sw_wins > 0 else 0.0
			message = f'{get_rank(ign, data)}{displayname} has {wins} {kit.capitalize()} {win_s}. ({percentage}%)'
			await ctx.send(message)	
	elif mode.lower() == 'blitz':
		blitz_wins = get_mode_stat('blitz', 'wins', duels_data)
		message_lines_blitz = [f"{get_rank(ign, data)}{displayname} has {blitz_wins} Blitz Duels wins."] 
		if kit.lower() == 'top10':
			kit_wins_list = []
			for blitz_kit in kits_blitz:
				wins = get_kit_wins('blitz', blitz_kit, duels_data)
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					percentage = round((wins/blitz_wins)*100, 2) if blitz_wins > 0 else 0.0
					kit_wins_list.append((wins, f"{wins} {blitz_kit.capitalize()} {win_s} ({percentage}%)"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_blitz.extend(msg for _, msg in sorted_kits[:10])
			remaining = sorted_kits[10:]
			if remaining:
				remaining_wins = sum(w for w, _ in remaining)
				remaining_percentage = round((remaining_wins/blitz_wins)*100, 2) if blitz_wins > 0 else 0.0
				win_s = "win" if remaining_wins == 1 else "wins" 
				message_lines_blitz.append(f"+ {remaining_wins} {win_s} with other kits ({remaining_percentage}%)")
			await ctx.send('\n'.join(message_lines_blitz))
		elif kit.lower() == 'all':
			kit_wins_list = []
			for blitz_kit in kits_blitz:
				wins = get_kit_wins('blitz', blitz_kit, duels_data)
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					kit_wins_list.append((wins, f"{wins} {blitz_kit.capitalize()} {win_s}"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_blitz.extend(msg for _, msg in sorted_kits)
			await ctx.send('\n'.join(message_lines_blitz))
		else:
			for kit in kits_blitz:
					wins = get_kit_wins('blitz', kit, duels_data)
					win_s = "win" if wins == 1 else "wins"
					message = f"{get_rank(ign, data)}{displayname} has {wins} {kit.capitalize} {win_s}."
	elif mode.lower() == 'mw':
		mw_wins = get_mode_stat('mw', 'wins', duels_data)
		message_lines_mw = [f"{get_rank(ign, data)}{displayname} has {mw_wins} MegaWalls Duels wins."] 
		if kit.lower() == 'top10':
			kit_wins_list = []
			for mw_kit in kits_mw:
				wins = get_kit_wins('mw', mw_kit, duels_data)
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					percentage = round((wins/mw_wins)*100, 2) if mw_wins > 0 else 0.0
					kit_wins_list.append((wins, f"{wins} {mw_kit.capitalize()} {win_s} ({percentage}%)"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_mw.extend(msg for _, msg in sorted_kits[:10])
			remaining = sorted_kits[10:]
			if remaining:
				remaining_wins = sum(w for w, _ in remaining)
				remaining_percentage = round((remaining_wins/mw_wins)*100, 2) if mw_wins > 0 else 0.0
				win_s = "win" if remaining_wins == 1 else "wins" 
				message_lines_mw.append(f"+ {remaining_wins} {win_s} with other kits ({remaining_percentage}%)")
			await ctx.send('\n'.join(message_lines_mw))
		elif kit.lower() == 'all':
			kit_wins_list = []
			for mw_kit in kits_mw:
				wins = get_kit_wins('mw', mw_kit, duels_data)
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					kit_wins_list.append((wins, f"{wins} {mw_kit.capitalize()} {win_s}"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_mw.extend(msg for _, msg in sorted_kits)
			await ctx.send('\n'.join(message_lines_mw))
		else:
			for kit in kits_mw:
					wins = get_kit_wins('mw', kit, duels_data)
					win_s = "win" if wins == 1 else "wins"
					message = f"{get_rank(ign, data)}{displayname} has {wins} {kit.capitalize} {win_s}."

	else:
		wins = get_kit_wins(mode, kit, duels_data)
		win_s = "win" if wins == 1 else "wins"
		message = f"{get_rank(ign, data)}{displayname} has {wins} {kit.capitalize()} {win_s}."
		await ctx.send(message)
	print(log(ctx.message.content, ctx.guild.name, ctx.author.name))
	# print(f'!kit {ign} {mode} {kit} used in {ctx.guild.name} by {ctx.author.name}')

@bot.command(name='s')
async def s(ctx, ign=None):
	if ign == None:
		ign = ign_based_on_discord_user(ctx.author.display_name, ctx.author.name)
	status = statusget(ign)
	session = status.get("session", {})
	displayname = get_displayname(ign)
	if session.get("online"):
		game = session.get('gameType')
		mode = session.get('mode')
		map = session.get('map', False)
		message = f"{displayname}\nGame: {game}\nMode: {mode}\nMap: {map if map != False else mode}"
		await ctx.send(message)
	else:
		recent_games_data = get_recentgames(ign)["games"]
		if len(recent_games_data) != 0:
			messages_list = []
			for id in range(len(recent_games_data)):
				recentgames = get_recentgames(ign)["games"][id]
				start_time = round(recentgames.get('date', 'N/A')/1000)
				stop_time = round(recentgames.get('ended', 'N/A')/1000)
				game = recentgames.get('gameType')
				mode = recentgames.get('mode')
				map = recentgames.get('map', False)
				messages_list.append(f"{displayname}\nStarted: <t:{start_time}:T>\nEnded: <t:{stop_time}:T>\nGame: {game}\nMode: {mode}\nMap: {map if map != False else mode}")
			await ctx.send(f'{displayname} is (appearing) offline.\nRecent games:\n{'\n\n'.join(messages_list)}')
		else:
			await ctx.send(f'{displayname} is (appearing) offline. Recent games unavailable.')
		# print(recentgames)
	print(log(ctx.message.content, ctx.guild.name, ctx.author.name))	
	# print(f'!s {ign} used in {ctx.guild.name} by {ctx.author.name}')

@bot.command(name='tlb')
async def tlb(ctx, frequency='weekly'):
	url = f"https://api.hypixel.net/leaderboards?key={api_key}"
	res = requests.get(url)
	data = res.json()
	duels_lb_data = data.get('leaderboards', {}).get('DUELS', {})
	messages = {}
	pos = 0

	if frequency.lower() == 'weekly':
		weekly_lb_data = duels_lb_data[0].get('leaders', [])
		for uuid in weekly_lb_data[:10]:
			url = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"
			res = requests.get(url)
			data = res.json()
			displayname = data["player"]["displayname"]
			pos += 1
			messages[uuid] = f"{pos}. {get_rank(displayname, data)}{displayname}"
		response = f'Duels Weekly:\n' + "\n".join(messages[m] for m in weekly_lb_data[:10])
		await ctx.send(response)

	elif frequency.lower() == 'monthly':
		monthly_lb_data = duels_lb_data[1].get('leaders', [])
		for uuid in monthly_lb_data[:10]:
			url = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"
			res = requests.get(url)
			data = res.json()
			displayname = data["player"]["displayname"]
			pos += 1
			messages[uuid] = f"{pos}. {get_rank(displayname, data)}{displayname}"
	response = f'Duels Monthly:\n' + "\n".join(messages[m] for m in monthly_lb_data[:10])
	await ctx.send(response)

	print(log(ctx.message.content, ctx.guild.name, ctx.author.name))

@bot.command(name='uuid')
async def uuid(ctx, ign=None):
	if ign == None:
		ign = ign_based_on_discord_user(ctx.author.display_name, ctx.author.name)
	displayname = get_displayname(ign)
	uuid = requests.get(f"https://playerdb.co/api/player/minecraft/{ign}").json()["data"]["player"]["id"]
	await ctx.send(f"{displayname}'s UUID: `{uuid}`")

@bot.command(name='kits')
async def uuid(ctx, *, args=''):
	await ctx.send(f'Did you mean `!kit {args}`, {ctx.author.display_name}?')

@bot.command(name='dodge')
async def dodge(ctx, ign1, amount=7, ign2='poki95'):
	if str(ctx.channel) == 'dodging' and ctx.user.name == 'poki95':
		list1 = []
		list2 = []
		user_id = ctx.author.id
		x = 0
		while x < int(amount):
			game1, mode1, map1 = stalk(ign1)
			game2, mode2, map2 = stalk(ign2)
			message1 = f"{mode1} on {map1 if map1 != False else game1}"
			list1.append(message1)
			message2 = f"{mode2} on {map2 if map2 != False else game2}"
			list2.append(message2)
			await ctx.send(f'{ign1}: {message1}\n{ign2}: {message2}\nIterations remaining: {amount-x}/{amount}')
			if message1 == message2:
				if message1 != list1[(len(list1))-2] or message2 != list2[(len(list2))-2]:
					await ctx.send(f'DODGE! {ctx.author.mention}')
			x += 1
			await asyncio.sleep(random.randint(7, 10))
	else:
		await ctx.send(f'Private command.')
	print(log(ctx.message.content, ctx.guild.name, ctx.author.name))	
	print(f'Succesfully stalked {ign1} for {int(amount)} iterations')

@bot.command(name='test')
async def test(ctx, *, input):
	if ctx.author.name == 'poki95':
		test_commands_list = [f"{line.strip()}" for line in input.strip().split(',')]
		for test_command in test_commands_list:
			await ctx.send(test_command)
			await asyncio.sleep(5)
	print(log(ctx.message.content, ctx.guild.name, ctx.author.name))

@bot.command(name='session')
async def session(ctx, ign='poki95'):
	if str(ctx.channel) == 'tracking' and ctx.user.name == 'poki95':
		data = dataget(ign)
		duels_data = get_duels_data(data)
		user_id = ctx.author.id
		start_wins = get_mode_stat('all_modes', 'wins', duels_data)
		start_losses = get_mode_stat('all_modes', 'losses', duels_data)
		await ctx.send(f'current wins: {start_wins}')
		while True:
			await asyncio.sleep(300)
			data = dataget(ign)
			duels_data = get_duels_data(data)
			wins = get_mode_stat('all_modes', 'wins', duels_data)
			losses = get_mode_stat('all_modes', 'losses', duels_data)
			if losses == start_losses:
				WLR = (wins - start_wins)
			else:
				WLR = (wins - start_wins)/(losses - start_losses)
			await ctx.reply(f'{wins - start_wins} wins\n{losses - start_losses} losses\n{round(WLR, 2)} WLR')
				
	else:
		await ctx.send(f'Private command.')

@bot.command(name='check')
async def check(ctx, ign='None', type='wins', mode='all_modes'):
	data = dataget(ign)
	duels_data = get_duels_data(data)
	stat = get_mode_stat(mode, type, duels_data)
	await ctx.send(f'{ign} has {stat} {type} in {mode}')
	print(log(ctx.message.content, ctx.guild.name, ctx.author.name))

'''@bot.command(name='stop')
async def stop(ctx):
	if ctx.author.name in ['poki95', 'awesomeduy']:
		user_id = ctx.author.id
		if running_tasks[user_id]:
			running_tasks[user_id]
			await ctx.reply(f"Succesfully stopped {ctx.author.name}'s running task.")
		else:
			await ctx.reply(f"No tasks to be stopped for {ctx.author.name}.")'''


# Run the bot 
bot.run(TOKEN)
