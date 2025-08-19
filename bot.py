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
import sqlite3
from re import sub
from mojang import API
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# Discord bot token and hypixel api key
load_dotenv(dotenv_path="keys.env")
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
temp_api_key = os.getenv("HYPIXEL_API_KEY")									# update every 3 days
dev_api_key = os.getenv("DEV_HYPIXEL_API_KEY")

# Ensure a working Hypixel API key is being used
api_key = temp_api_key




# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# SQLite database setup
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS linked_users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	discord_name TEXT NOT NULL UNIQUE,
	discord_id INTEGER NOT NULL UNIQUE,
	mc_uuid TEXT NOT NULL UNIQUE,
	timestamp INTEGER NOT NULL
	)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS players (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	mc_uuid TEXT NOT NULL UNIQUE,
	rank TEXT,
	mc_ign TEXT NOT NULL,
	nwl INTEGER NOT NULL,
	guild TEXT,
	timestamp INTEGER NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS modes (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	mode_alias TEXT NOT NULL UNIQUE,
	mode_db TEXT NOT NULL,
	mode_clean TEXT,
	mode_desc TEXT
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS players_stats (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	mc_uuid TEXT NOT NULL,
	mode_id INTEGER NOT NULL,
	wins INTEGER,
	losses INTEGER,
	rounds INTEGER,
	kills INTEGER,
	deaths INTEGER,
	cws INTEGER,
	bws INTEGER,
	timestamp INTEGER NOT NULL,
	UNIQUE(mc_uuid, mode_id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS kits (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	mode TEXT NOT NULL,
	kit TEXT NOT NULL
)
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS players_kits_stats (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	mc_uuid TEXT NOT NULL,
	kit_id INTEGER NOT NULL,
	wins INTEGER,
	timestamp INTEGER NOT NULL,
	UNIQUE(mc_uuid, kit_id)
)
''')
conn.commit()


# Given data
mode_list = ['oa', 'uhc', 'sw', 'mw', 'blitz', 'op', 'classic', 'bow', 'ndb', 'combo', 'tnt', 'sumo', 'bridge', 'pkd', 'boxing', 'arena', 'spleef', 'quake', 'bw', 'all'] # mode aliases
mode_db_list = ['all_modes', 'uhc', 'sw', 'mw', 'blitz', 'op', 'classic', 'bow', 'potion', 'combo', 'bowspleef', 'sumo', 'bridge', 'parkour_eight', 'boxing', 'duel_arena', 'spleef', 'quake', 'bedwars'] # mode database aliases
mode_db_list_long = ['all_modes', 'uhc', 'skywars', 'megawalls', 'blitz', 'op', 'classic', 'bow', 'potion', 'combo', 'tnt_games', 'sumo', 'bridge', 'parkour', 'boxing', 'duel_arena', 'spleef', 'quake', 'bedwars']
mode_names = ['', 'UHC', 'SkyWars', 'MW', 'Blitz', 'OP', 'Classic', 'Bow', 'NoDebuff', 'Combo', 'TNT', 'Sumo', 'Bridge', 'Parkour', 'Boxing', 'Arena', 'Spleef', 'Quakecraft', 'BedWars'] # clean mode names
div_list = ['ASCENDED', 'DIVINE', 'CELESTIAL', 'Godlike', 'Grandmaster', 'Legend', 'Master', 'Diamond', 'Gold', 'Iron', 'Rookie', 'None'] # divisions
div_req = [100000, 50000, 25000, 10000, 5000, 2000, 1000, 500, 250, 100, 50, 0] # requirements for each division title
div_step = [10000, 10000, 5000, 3000, 1000, 600, 200, 100, 50, 30, 10, 1] # requirements to go up a level within a division title
kits_sw = [
    "default", "scout", "magician", "armorer", "champion", "bowman", "athlete", # 7
    "blacksmith", "healer", "pyromancer", "hound", "paladin", "armorsmith", # 6 
    "baseball player", "cannoneer", "ecologist", "enchanter", "enderman", # 5
    "guardian", "hunter", "knight", "pharaoh", "pro", "snowman", "speleologist", # 7
    "batguy", "disco", "energix", "cactus", "archeologist", "warlock", "frog", # 7 
    "grenade", "engineer", "pig rider", "salmon", "slime", "jester", "zookeeper", # 7
    "sloth", "enderchest", "farmer", "fisherman", "princess", "pyro", "troll", "rookie", # 8
 	"fallen angel", "thundermeister", "end lord", "fishmonger", "nether lord", # 5
    "monster trainer", "skeletor", "pyromaniac", 'golem', 'cryomancer', 'hellhound', # 6
	'witch', 'chronobreaker' # 2
] # total -> 60 i think
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
bridge_submodes_ = ['bridge_duel_', 'bridge_doubles_', 'bridge_threes_', 'bridge_four_', 'bridge_2v2v2v2_', 'bridge_3v3v3v3_', 'capture_threes_', 'capture_duel_']
# min_wins_per_hour = [40, 75, 25, 80, 80, 100, 70, 20, 60, 80, 100, 20, 10, 20, 60]
# max_wins_per_hour = [70, 85, 40, 100, 100, 150, 130, 40, 90, 110, 150, 30, 20, 30, 60]
gph = [70, 85, 40, 95, 85, 150, 120, 40, 75, 80, 160, 30, 12, 30, 60, 100, 90, 35]
duels_gph = [20, 40, 50, 60, 30, 100, 85, 30, 30, 12, 120, 8, 12, 25, 60, 90, 90, 15]
prefix_icons_db = [
	'sigma', 'root', 'delta', 'walls', 'strike', 'excited', 'reminiscence', 'arrow', 'deny', 'repeated', 'layered', 'arena', 'speed', 'platforms', 'rhythm', 'confused', 'beam', 'final', # Iron (18)
	'podium', 'fish', 'fallen_crest', 'regretting_this', 'smiley', 'heart', 'pointy_star', 'yin_and_yang', 'sun', 'fancy_star', 'snowman', 'biohazard', 'weight', 'flower', 'gg', 'smile_spam', 'reference', 'bill', # Grandmaster (18)
	'#???', 'bear', 'same_great_taste', 'wither', 'lucky', 'victory', 'uninterested', 'piercing_look', 'alchemist', 'bliss', 'innocent', # ASCENDED (OA: CELESTIAL) (11)
	'fists', 'flipper', "don't_punch", 'boxer', 'ghost', "don't_blink", 'Hypnotized' # ASCENDED (7)
	'star', '' # Special (2)
]
prefix_icons = [
	'Σ', '√', 'δ', '÷', '⚡', '!!', '≈', '➜', '∅', '²', '≡', 'Θ', '»', '...', '♫♪', '??', '--', '☠️', # 18
	'π', '><>', '☬', 'uwu', '^_^', '❤', '✵', '☯', '☀', '✯', '☃', '☣', 'B==B', '❀', 'GG', ':)))))', '{T}', '[($)]', # 18
	'#???', 'wowow', 'ಠ_ಠ', '[._.]', '|(◕◡◕)/', '༼つ◕_◕༽つ', '(T_T)', '|>-<|', '<∅_∅>', '(*_b*)', '{0ww0}', # 11
	'w(ಠ_ಠw)', '(`ಠ_ಠ)`≡T_T', '(*wb*)', "o=('_'Q)", '⚡(-w-⚡)', '-»[*_*]', '[@~@]' # 7
	'✫', '' # 2
]

swd_lifetime = ['poki95', 'Monk_Eez', 'MartySnoozeman', 'Lucastevo', 'D3pTTT', 'Scary_J', 'nobuh', 'mutton38', 'ImHomoAf', 'KissMyL']
# Functions

def dataget(ign):
	global api_key														# Load player's Hypixel stats
	try:															
		response = requests.get(f"https://playerdb.co/api/player/minecraft/{ign}")
		uuid = response.json()["data"]["player"]["id"]
		url = f"https://api.hypixel.net/player?key={api_key}&uuid={uuid}"
		res = requests.get(url)
		data = res.json()
	except KeyError:
		data = None	
	return data

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

def recentgamesget(ign):
	try:															
		response = requests.get(f"https://playerdb.co/api/player/minecraft/{ign}")
		uuid = response.json()["data"]["player"]["id"]
		url = f"https://api.hypixel.net/recentgames?key={api_key}&uuid={uuid}"
		res = requests.get(url)
		recentgames = res.json()
	except KeyError:
		recentgames = 'Failed to load recent games for this player.'
	return recentgames

def guildget(given, entry):
	if entry == 'player':
		try:															
			response = requests.get(f"https://playerdb.co/api/player/minecraft/{given}")
			uuid = response.json()["data"]["player"]["id"]
			url = f"https://api.hypixel.net/guild?key={api_key}&player={uuid}"
			res = requests.get(url)
			guild = res.json()
		except KeyError:
			guild = 'Failed to load guild for this player.'
		return guild	
	elif entry == 'guild':
		try:
			url = f"https://api.hypixel.net/guild?key={api_key}&name={given}"
			res = requests.get(url)
			guild = res.json()
		except KeyError:
			guild = 'Failed to load guild for this guild. :p'
		return guild	

def playerdbget(ign):
	try:
		playerdb = requests.get(f"https://playerdb.co/api/player/minecraft/{ign}").json()["data"]["player"]
	except KeyError:
		playerdb = None
	return playerdb

def get_duels_data(data):
	duels_data = data["player"].get("stats", {}).get("Duels", {})
	return duels_data

def getlb(mode):
	return mode

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

def get_nwl(ign, data):
	exp = data["player"]["networkExp"]
	nwl = round(math.sqrt(exp/1250 + 12.25) - 2.5, 2)
	return nwl

def get_guild(ign, guild_data):
	if guild_data["guild"] != None:
		guild = guild_data["guild"].get("name", None)
		return guild
	else:
		return None

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
	elif mode_db in ['sw', 'mw', 'op', 'classic']:
		return duels_data.get(f'{mode_db}_duel_{type}', 0) + duels_data.get(f'{mode_db}_doubles_{type}', 0)
	elif mode_db in ['parkour_eight', 'duel_arena']:
		return duels_data.get(f'{mode_db}_{type}', 0)
	elif mode_db == 'bedwars':
		if type == 'wins':
			return duels_data.get(f'{type}_bedwars', 0)
		else:
			return duels_data.get(f'bedwars_two_one_duels_rush_{type}', 0) + duels_data.get(f'bedwars_two_one_duels_{type}', 0)
	else:
		return duels_data.get(f'{mode_db}_duel_{type}', 0)

def get_winstreaks(mode_db, duels_data):
	if mode_db == 'all_modes':
		mode = 'overall'
	elif mode_db == 'duel_arena':
		mode = 'arena'
	else:
		mode = mode_db_list_long[mode_db_list.index(mode_db)]
	cws, bws = duels_data.get(f'current_{mode}_winstreak', 0), duels_data.get(f'best_{mode}_winstreak', 0)
	return cws, bws

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
	if data == None:
		ign = user_name
	return ign

def get_duels_stats(mode_db, duels_data):
	win_count = get_mode_stat(mode_db, 'wins', duels_data)
	win_s = "win" if win_count == 1 else "wins"
	loss_count = get_mode_stat(mode_db, 'losses', duels_data)
	loss_es = "loss" if loss_count == 1 else "losses"
	kill_count = get_mode_stat(mode_db, 'kills', duels_data)
	kill_s = "kill" if kill_count == 1 else "kills"
	death_count = get_mode_stat(mode_db, 'deaths', duels_data)
	death_s = "death" if death_count == 1 else "deaths"
	games_played = get_mode_stat(mode_db, 'rounds_played', duels_data)
	cws, bws = get_winstreaks(mode_db, duels_data)
	return win_count, win_s, loss_count, loss_es, games_played, kill_count, kill_s, death_count, death_s, cws, bws

def get_bw_submodes_stats(duels_data):
	return duels_data.get(f'bedwars_two_one_duels_wins', 0), duels_data.get(f'bedwars_two_one_duels_rush_wins', 0), duels_data.get(f'bedwars_two_one_duels_losses', 0), duels_data.get(f'bedwars_two_one_duels_rush_losses', 0)

def get_uuid(ign, playerdb_data):
	return playerdb_data["id"]

def get_displayname(ign, playerdb_data):
	if "username" in playerdb_data:
		return playerdb_data["username"]
	elif "displayname" in playerdb_data:
		return playerdb_data["displayname"]
	else:
		return 'Unable to get displayname.'

def link_to(discord_name, discord_id, uuid, playerdb_data):
	ign = get_displayname(uuid, playerdb_data)
	timestamp = round(time.mktime(time.localtime()))
	try:
		cursor.execute(
			"INSERT INTO linked_users (discord_name, discord_id, mc_uuid, timestamp) VALUES (?, ?, ?, ?)",
			(discord_name, discord_id, uuid, timestamp)
		)
		conn.commit()
		return (f"Linked user {discord_name} (ID: {discord_id})\n-> {ign} (UUID: `{uuid}`)")
	except Exception as e:
		if str(e) == 'UNIQUE constraint failed: linked_users.mc_uuid':
			return f'{ign} has already been linked.'
		elif str(e) == 'UNIQUE constraint failed: linked_users.discord_id':
			return f'{discord_name} is already linked.'
		else:
			return f'Failed: {e}'

def already_linked(discord_id):
	try:
		cursor.execute(f"SELECT mc_uuid FROM linked_users WHERE discord_id = {discord_id}")
		uuid = cursor.fetchone()[0]
		playerdb_data = playerdbget(uuid)
		user = get_displayname(uuid, playerdb_data)
		return f"User already linked to `{user}`."
	except Exception as e:
		if str(e) == "'NoneType' object is not subscriptable":
			return f"User not currently linked. Use `!link <ign>` to link."
		else:
			return e

def unlink_from(discord_id):
	try:
		cursor.execute(f'''
			SELECT mc_uuid
			FROM linked_users
			WHERE discord_id = {discord_id}
		''')
		uuid = cursor.fetchone()[0]
		cursor.execute(f'''
			DELETE FROM linked_users
			WHERE discord_id = {discord_id}
		''')
		conn.commit()
		return f"Unlinked user from `{uuid}`"
	except Exception as e:
		if str(e) == "'NoneType' object is not subscriptable":
			return f"User not currently linked."
		else:
			raise e

def ign_not_given(discord_id, display_name, user_name):
	try:
		cursor.execute(f"SELECT mc_uuid FROM linked_users WHERE discord_id = {discord_id}")
		uuid = cursor.fetchone()[0]
		playerdb_data = playerdbget(uuid)
		ign = get_displayname(str(uuid), playerdb_data)
		return ign
	except Exception as e:
		if str(e) == "'NoneType' object is not subscriptable":
			ign = ign_based_on_discord_user(display_name, user_name)
			return ign
		else:
			raise e

def add_player(uuid, data, playerdb_data):
	mc_ign = get_displayname(uuid, playerdb_data)
	guild_data = guildget(mc_ign, 'player')
	rank = get_rank(mc_ign, data)
	nwl = get_nwl(mc_ign, data)
	guild = get_guild(mc_ign, guild_data)
	timestamp = round(time.mktime(time.localtime()))
	try:
		cursor.execute(
			"INSERT INTO players (mc_uuid, rank, mc_ign, nwl, guild, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
			(uuid, rank, mc_ign, nwl, guild, timestamp)
		)
		conn.commit()
		print(f"Added {mc_ign} ({uuid}) to the players table")
	except Exception as e:
		if str(e) == 'UNIQUE constraint failed: players.mc_uuid':
			cursor.execute(f'''
				UPDATE players
				SET
					rank = ?,
					mc_ign = ?,
					nwl = ?,
					guild = ?,
					timestamp = ?
				WHERE mc_uuid = ?
			''', (rank, mc_ign, nwl, guild, timestamp, uuid))
			conn.commit()
		else:
			print(f'Add player failed. Reason: {e}')

def update_mode_stats(uuid, mode_db, wins, losses, rounds_played, kills, deaths, cws, bws):
	if mode_db not in mode_db_list:
		print(f"Invalid mode: '{mode_db}'")
		return
	mode_id = mode_db_list.index(mode_db) + 1
	mode_alias = mode_list[mode_db_list.index(mode_db)]
	timestamp = round(time.mktime(time.localtime()))
	try:
		cursor.execute(
			"INSERT INTO players_stats (mc_uuid, mode_id, wins, losses, rounds, kills, deaths, cws, bws, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
			(uuid, mode_id, wins, losses, rounds_played, kills, deaths, cws, bws, timestamp)
		)
		conn.commit()
	except Exception as e:
		if str(e) == 'UNIQUE constraint failed: players_stats.mc_uuid, players_stats.mode_id':
			cursor.execute(f'''
			UPDATE players_stats
			SET
				wins = ?,
				losses = ?,
				rounds = ?,
				kills = ?,
				deaths = ?,
				cws = ?,
				bws = ?,
				timestamp = ?
			WHERE mode_id = ? AND mc_uuid = ?
			''', (wins, losses, rounds_played, kills, deaths, cws, bws, timestamp, mode_id, uuid))
			conn.commit()
		else:
			print(f'Update mode stats failed. Reason: {e}')

def update_kit_stats(uuid, kit, kit_wins, mode):
	if kit not in kits:
		print(f"Invalid kit: '{kit}'")
		return
	try:
		cursor.execute("SELECT id FROM kits WHERE kit = ? AND mode = ?", (kit, mode))
		result = cursor.fetchone()
		# print(result)
		if result is None:
			return "Kit doesn't exist for the specified mode."
		kit_id = result[0]
	except Exception as e:
		return f"Error in selecting kit id: {e}" 
	# kit_id = kits.index(kit) + 1
	timestamp = round(time.mktime(time.localtime()))
	try:
		cursor.execute(
			"INSERT INTO players_kits_stats (mc_uuid, kit_id, wins, timestamp) VALUES (?, ?, ?, ?)",
			(uuid, kit_id, kit_wins, timestamp)
		)
		conn.commit()
	except Exception as e:
		if str(e) == 'UNIQUE constraint failed: players_kits_stats.mc_uuid, players_kits_stats.kit_id':
			cursor.execute(f'''
			UPDATE players_kits_stats
			SET
				wins = ?,
				timestamp = ?
			WHERE kit_id = ? AND mc_uuid = ?
			''', (kit_wins, timestamp, kit_id, uuid))
			conn.commit()
		else:
			print(f'Update kit stats failed. Reason: {e}')	

def get_all_players_with_kit_wins(kit, mode):
	try:
		cursor.execute("SELECT id FROM kits WHERE kit = ? AND mode = ?", (kit, mode))
		result = cursor.fetchone()
		# print(result)
		if result is None:
			return "Kit doesn't exist for the specified mode."
		kit_id = result[0]
	except Exception as e:
		return f"Error in selecting kit id: {e}" 
	try:
		cursor.execute(f"SELECT mc_uuid, wins FROM players_kits_stats WHERE kit_id = ?", (kit_id,))
		result = cursor.fetchall()
		# print(f"Fetched results: {result}")
		list = []
		for info in result:
			uuid = info[0]
			wins = info[1]
			cursor.execute(f"SELECT mc_ign FROM players WHERE mc_uuid = ?", (uuid,))
			user = cursor.fetchone()[0]
			list.append((wins, f"{user}: {wins} {kit.capitalize()} wins"))
		return list
	except Exception as e:
		raise e
		return f"error in selecting mc uuid: {e}" 
	
def add_all_players_stats(uuid_or_ign, info):
	try:
		playerdb_data = playerdbget(info)
		if uuid_or_ign == 'ign':
			uuid = get_uuid(info, playerdb_data)
		else:
			ign = get_displayname(info, playerdb_data)
			uuid = get_uuid(info, playerdb_data)
		data = dataget(info)
		add_player(uuid, data, playerdb_data)
		duels_data = get_duels_data(data)
		modes = mode_db_list 
		for mode_db in modes:
			win_count, win_s, loss_count, loss_es, games_played, kill_count, kill_s, death_count, death_s, cws, bws = get_duels_stats(mode_db, duels_data)
			update_mode_stats(uuid, mode_db, win_count, loss_count, games_played, kill_count, death_count, cws, bws) # UPDATE MODE STATS IN DB
		for kit in kits_sw:
			wins = get_kit_wins('sw', kit, duels_data)
			update_kit_stats(uuid, kit, wins, 'sw')				
		for kit in kits_blitz:
			wins = get_kit_wins('blitz', kit, duels_data)
			update_kit_stats(uuid, kit, wins, 'blitz')	
		for kit in kits_mw:
			wins = get_kit_wins('mw', kit, duels_data)
			update_kit_stats(uuid, kit, wins, 'mw')	
		time.sleep(5)
		return (f"{ign} has been added.")
	except Exception as e:
		return (f"Error adding {info}: {e}")		


# Is bot ready?
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
	
# Logging setup
commands_logs = 'commands_logs.json'
if not os.path.exists(commands_logs):
    with open(commands_logs, "w") as f:
        json.dump([], f)

@bot.event
async def on_message(message):
	if len(message.content) > 0:
		if str(message.content)[0] == '!':
			the_time = time.strftime("%X %x", time.localtime())
			if message.author.bot:
				await bot.process_commands(message)
				command_log = f"[{the_time}] [Bot Triggered] {message.author.name} in {message.author.guild}: {message.content}"
			else:
				await bot.process_commands(message)
				command_log = f"[{the_time}] [User Triggered] {message.author.name} in {message.author.guild}: {message.content}"
			with open(commands_logs, "r+") as f:
				data = json.load(f)
				data.append(command_log)
				f.seek(0)
				json.dump(data, f, indent=4)	


# Ignore invalid commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

# Bot commands
@bot.command(name='ping')
async def ping(ctx, amount=1):
	for a in range(amount):
		await ctx.reply(f'Pong! 🏓\n<t:{round(time.mktime(time.localtime()))}:T>')

@bot.command(name='h')
async def h(ctx, argument=None):
	if argument == None:
		await ctx.send(f"""
	# **Poki's Stats Checker** <:avatar:1382441832809500792>

	## Available commands:

	- !d -> Duels Stats (!h duels)
	- !kit -> Kit Stats (!h kit)
	- !s -> Player Status (!h status)
	- !tlb -> Current Leaderboards (!h lb)
	- !link -> Link Account (!h link)
		
		
	For any issues, contact **`poki95`** on Discord.
	""")
	elif argument in ['d', 'duel', 'duels']:
		await ctx.send(f"""
	Check a player's wins, division title, and estimated playtime.

	### !d <ign> -> Shows stats for all Duels modes.
			-> !d MCreeperWL

	### !d <ign> <mode> -> Shows more specific stats for a specific mode.
			-> !d Sothey boxing
			
	For any issues, contact **`poki95`** on Discord.
	""")
	elif argument in ['k', 'kit', 'kits']:
		await ctx.send(f"""
	Check a player's kit wins for a specific mode.

	### !kit <ign> <mode> -> Shows all kit wins for a specific mode.
			-> !kit sockatoo

	### !d <ign> <mode> <kit> -> Shows kit wins for a specific mode.
			-> !kit poki95 pyromancer
			
	For any issues, contact **`poki95`** on Discord.
	""")
	elif argument in ['s', 'status']:
		await ctx.send(f"""
	Check a player's Status on Hypixel.

	### !s <ign> -> Shows the player's status and recent games.
			-> !s mutton38
		
	For any issues, contact **`poki95`** on Discord.
	""")
	elif argument in ['lb', 'leaderboard']:
		await ctx.send(f"""
	Check various leaderboards on Hypixel.

	### !tlb <weekly/monthly> -> Shows the current Weekly/Monthly Duels Leaderboard.
			-> !tlb weekly

	### !klb <kit> <mode> -> Shows the unofficial leaderboard for given kit!

		
	For any issues, contact **`poki95`** on Discord.
	""")
	elif argument in ['link', 'unlink']:
		await ctx.send(f"""
	Link your Discord account to your Minecraft account for easier stats checking.

	### !link <ign> -> Links your Discord account to your Minecraft account.
			-> !link {ctx.author.name}

	### !unlink -> Unlinks your Discord account to your Minecraft account.
			-> !unlink
		
	For any issues, contact **`poki95`** on Discord.
	""")
	elif argument in ['u', 'update']:
		if ctx.author.name == 'poki95':
			await ctx.send('''
			# New update dropped!

	## New command

	- `!klb` -> Check Kit Leaderboards!
	## Existing commands changes

	- `!d` -> Updated icons and modes for the Duels Update 1.5

	Feedback is more than welcome! Contact `poki95` on Discord.
		
		
			''')
		else:
			await ctx.send("Unauthorized.")

@bot.command(name='d')
async def d(ctx, ign=None, mode='all'):
	if ign == None:
		ign = ign_not_given(ctx.author.id, ctx.author.display_name, ctx.author.name)
			
	if ign.lower() in mode_list:
		mode = ign
		ign = ign_not_given(ctx.author.id, ctx.author.display_name, ctx.author.name)
			
	data = dataget(ign)

	if data == None:
		await ctx.send('Invalid IGN.')
		return

	if mode.lower() not in mode_list:
		await ctx.send(f'`{mode}` is not an available mode. Type `!h` for help.')
		return
	
	playerdb_data = playerdbget(ign)
	displayname = get_displayname(ign, playerdb_data)
	uuid = get_uuid(ign, playerdb_data)

	add_player(uuid, data, playerdb_data)
	
	if displayname.count('_') >= 2 and displayname.count('__') != 1:
		displayname = f'`{displayname}`'

	duels_data = get_duels_data(data)
	
	equipped_icon = prefix_icons[prefix_icons_db.index(duels_data.get("active_prefix_icon", '').replace("prefix_icon_", ''))]
	equipped_color = duels_data.get("active_prefix_scheme", '')
	equipped_title = duels_data.get("active_title", '')
	if equipped_title != '':
		equipped_icon = prefix_icons[prefix_icons_db.index(duels_data.get("active_prefix_icon", 'prefix_icon_star').replace("prefix_icon_", ''))]
	else:
		equipped_icon = ''
	
	current_title = ''
	wins = {}
	messages = {}
	
	modes = mode_db_list # if mode == 'all' else [mode_db_list[mode_list.index(mode)]]
	wins_list = []
	overall_playtime = 0
	for mode_db in modes:
		win_count, win_s, loss_count, loss_es, games_played, kill_count, kill_s, death_count, death_s, cws, bws = get_duels_stats(mode_db, duels_data)

		is_oa = (mode_db == 'oa') 
		div, div_num = get_division_info(win_count, is_oa)	
		division = f'{div} {roman.toRoman(div_num)}' if div_num != 1 and div != "None" else div
		random_q_playtime = (win_count + loss_count)/gph[mode_db_list.index(mode_db)-1]
		ghost_games_playtime = (games_played - win_count - loss_count)/duels_gph[mode_db_list.index(mode_db)-1]
		playtime = round(random_q_playtime + ghost_games_playtime, 1)

		update_mode_stats(uuid, mode_db, win_count, loss_count, games_played, kill_count, death_count, cws, bws) # UPDATE MODE STATS IN DB
		mode_clean = mode_names[mode_db_list.index(mode_db)]
		if mode_db != 'all_modes':			
			overall_playtime += playtime
			if mode_db_list_long[mode_db_list.index(mode_db)] in equipped_title:
				current_title = f'{equipped_icon} {mode_clean} {oa_division if mode_db == 'all_modes' else division}'
			if mode_db == 'bedwars':
				normal_win_count, rush_win_count, normal_loss_count, rush_loss_count = get_bw_submodes_stats(duels_data)
				normal_playtime = (normal_win_count + normal_loss_count)/20
				rush_playtime = (rush_win_count + rush_loss_count)/40
				random_q_playtime = normal_playtime + rush_playtime				
				wins_list.append((win_count, f"{format_number(win_count)} {mode_clean} {win_s} - {mode_clean} {division} (~{playtime}h)"))
			elif mode_db == 'duel_arena':
				div, div_num = get_division_info(kill_count, False)	
				division = f'{div} {roman.toRoman(div_num)}' if div_num != 1 and div != "None" else div
				playtime = round(games_played/65, 1)
				wins_list.append((kill_count, f"{format_number(kill_count)} {mode_clean} {kill_s} - {mode_clean} {division} (~{playtime}h)"))
			else:
				wins_list.append((win_count, f"{format_number(win_count)} {mode_clean} {win_s} - {mode_clean} {division} (~{playtime}h)"))

		else:
			overall_win_count = get_mode_stat(mode_db, 'wins', duels_data)
			div, div_num = get_division_info(win_count, True)	
			oa_division = f'{div} {roman.toRoman(div_num)}' if div_num != 1 and div != "None" else div
			mode_clean = mode_names[mode_db_list.index(mode_db)]
			if 'all_modes' in equipped_title:
				current_title = f'{equipped_icon} {mode_clean} {oa_division if mode_db == 'all_modes' else division}'
	sorted_modes = sorted(wins_list, key=lambda x: x[0], reverse=True)
	if displayname in swd_lifetime:
		if equipped_icon == '#???' and 'SkyWars' in current_title:
			current_title = current_title.replace('#???', f"#{str(swd_lifetime.index(displayname)+1)}")
	#		if displayname == 'poki95':
	#			current_title = '#1 SkyWars ASCENDED II'
		
	if mode == 'all':	
		if overall_win_count >= 100000:
			current_title = '**' + current_title + '**'	
		message_lines = [f"{sub(' +', ' ', current_title)} {get_rank(ign, data)}{displayname}\n{format_number(overall_win_count)} Overall {win_s} - {oa_division} (~{round(overall_playtime)}h)"]
		message_lines.extend(msg for _, msg in sorted_modes)
		await ctx.send('\n'.join(message_lines))

	else:
		mode_db = mode_db_list[mode_list.index(mode.lower())]
		win_count, win_s, loss_count, loss_es, games_played, kill_count, kill_s, death_count, death_s, cws, bws = get_duels_stats(mode_db, duels_data)

		update_mode_stats(uuid, mode_db, win_count, loss_count, games_played, kill_count, death_count, cws, bws) # UPDATE MODE STATS IN DB
		
		is_oa = (mode_db == 'oa')
		div, div_num = get_division_info(win_count, is_oa)	
		division = f'{div} {roman.toRoman(div_num)}' if div_num != 1 and div != "None" else div
		mode_clean = mode_names[mode_db_list.index(mode_db)]
		random_q_playtime = (win_count + loss_count)/gph[mode_db_list.index(mode_db)-1]
		ghost_games = games_played - (win_count + loss_count)
		ghost_games_playtime = (ghost_games)/duels_gph[mode_db_list.index(mode_db)-1]
		playtime = round(random_q_playtime + ghost_games_playtime, 1)
		WLR = round(win_count/loss_count, 2) if loss_count != 0 else win_count
		KDR = round(kill_count/death_count, 2) if death_count != 0 else kill_count
		if mode in ['pkd', 'tnt', 'boxing', 'spleef']:
			message = sub(' +', ' ', f"""✫ {mode_clean} {oa_division if mode == 'oa' else division} {get_rank(ign, data)}{displayname} (~{playtime}h)
			{format_number(win_count)} {win_s} - {format_number(loss_count)} {loss_es} - {WLR} WLR
			{format_number(ghost_games)} ghost games - {cws} CWS - {bws} BWS""")
		elif mode == 'arena':
			div, div_num = get_division_info(kill_count, False)	
			division = f'{div} {roman.toRoman(div_num)}' if div_num != 1 and div != "None" else div
			message = sub(' +', ' ', f"""✫ {mode_clean} {oa_division if mode == 'oa' else division} {get_rank(ign, data)}{displayname} (~{playtime}h)
			{format_number(kill_count)} {kill_s} - {format_number(death_count)} {death_s} - {KDR} KDR
			{format_number(games_played)} games played - {cws} CWS - {bws} BWS""")
		else:
			message = sub(' +', ' ', f"""✫ {mode_clean} {oa_division if mode == 'oa' else division} {get_rank(ign, data)}{displayname} (~{playtime if mode != 'oa' else round(overall_playtime, 1)}h)
			{format_number(win_count)} {win_s} - {format_number(loss_count)} {loss_es} - {WLR} WLR
			{format_number(kill_count)} {kill_s} - {format_number(death_count)} {death_s} - {KDR} KDR
			{format_number(ghost_games)} ghost games - {cws} CWS - {bws} BWS""")
		await ctx.send(message)

@bot.command(name='kit')
async def kit(ctx, ign=None, mode='sw', kit='top10'):
	if ign == None:
		ign = ign_not_given(ctx.author.id, ctx.author.display_name, ctx.author.name)
	elif ign.lower() in kits:
		kit = ign.lower()
		ign = ign_not_given(ctx.author.id, ctx.author.display_name, ctx.author.name)
	elif ign.lower() in ['sw', 'blitz', 'mw']:
		mode = ign
		ign = ign_not_given(ctx.author.id, ctx.author.display_name, ctx.author.name)

	data = dataget(ign)

	if data == None:
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

	playerdb_data = playerdbget(ign)
	displayname = get_displayname(ign, playerdb_data)
	uuid = get_uuid(ign, playerdb_data)

	add_player(uuid, data, playerdb_data)

	duels_data = get_duels_data(data)

	if mode.lower() == 'sw':
		sw_wins = get_mode_stat('sw', 'wins', duels_data)
		message_lines_sw = [f"{get_rank(ign, data)}{displayname} has {sw_wins} SkyWars Duels wins."]
		if kit.lower() == 'top10':
			kit_wins_list = []
			for swd_kit in kits_sw:
				wins = get_kit_wins('sw', swd_kit, duels_data)
				update_kit_stats(uuid, kit, wins, mode.lower())
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					percentage = round((wins/sw_wins)*100, 2) if sw_wins > 0 else 0.0
					kit_wins_list.append((wins, f"{wins} {swd_kit.capitalize()} {win_s} ({percentage}%)"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_sw.extend(msg for _, msg in sorted_kits[:10])
			remaining = sorted_kits[10:]
			if remaining:
				remaining_wins = sw_wins - sum(w for w, _ in sorted_kits[:10])
				remaining_percentage = round((remaining_wins/sw_wins)*100, 2) if sw_wins > 0 else 0.0
				win_s = "win" if remaining_wins == 1 else "wins"
				message_lines_sw.append(f"+ {remaining_wins} {win_s} with other kits ({remaining_percentage}%)")
			await ctx.send('\n'.join(message_lines_sw))
		elif kit == 'all':
			kit_wins_list = []
			for swd_kit in kits:
				wins = get_kit_wins('sw', swd_kit, duels_data)
				update_kit_stats(uuid, kit, wins, mode.lower())
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					kit_wins_list.append((wins, f"{wins} {swd_kit.capitalize()} {win_s}"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_sw.extend(msg for _, msg in sorted_kits)
			await ctx.send('\n'.join(message_lines_sw))
		else:
			wins = get_kit_wins('sw', kit, duels_data)
			update_kit_stats(uuid, kit, wins, mode.lower())
			win_s = "win" if wins == 1 else "wins"
			percentage = round((wins/sw_wins)*100, 2) if sw_wins > 0 else 0.0
			message = f'{get_rank(ign, data)}{displayname} has {wins} {kit.capitalize()} {win_s} in SkyWars Duels. ({percentage}%)'
			await ctx.send(message)	
	elif mode.lower() == 'blitz':
		blitz_wins = get_mode_stat('blitz', 'wins', duels_data)
		message_lines_blitz = [f"{get_rank(ign, data)}{displayname} has {blitz_wins} Blitz Duels wins."] 
		if kit.lower() == 'top10':
			kit_wins_list = []
			for blitz_kit in kits_blitz:
				wins = get_kit_wins('blitz', blitz_kit, duels_data)
				update_kit_stats(uuid, blitz_kit, wins, mode.lower())
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					percentage = round((wins/blitz_wins)*100, 2) if blitz_wins > 0 else 0.0
					kit_wins_list.append((wins, f"{wins} {blitz_kit.capitalize()} {win_s} ({percentage}%)"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_blitz.extend(msg for _, msg in sorted_kits[:10])
			remaining = sorted_kits[10:]
			if remaining:
				remaining_wins = blitz_wins - sum(w for w, _ in sorted_kits[:10])
				remaining_percentage = round((remaining_wins/blitz_wins)*100, 2) if blitz_wins > 0 else 0.0
				win_s = "win" if remaining_wins == 1 else "wins" 
				message_lines_blitz.append(f"+ {remaining_wins} {win_s} with other kits ({remaining_percentage}%)")
			await ctx.send('\n'.join(message_lines_blitz))
		elif kit.lower() == 'all':
			kit_wins_list = []
			for blitz_kit in kits_blitz:
				wins = get_kit_wins('blitz', blitz_kit, duels_data)
				update_kit_stats(uuid, blitz_kit, wins, mode.lower())
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					kit_wins_list.append((wins, f"{wins} {blitz_kit.capitalize()} {win_s}"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_blitz.extend(msg for _, msg in sorted_kits)
			await ctx.send('\n'.join(message_lines_blitz))
		else:
			wins = get_kit_wins('blitz', kit, duels_data)
			update_kit_stats(uuid, kit, wins, mode.lower())
			win_s = "win" if wins == 1 else "wins"
			percentage = round((wins/blitz_wins)*100, 2) if blitz_wins > 0 else 0.0
			message = f"{get_rank(ign, data)}{displayname} has {wins} {kit.capitalize()} {win_s} in Blitz Duels. ({percentage}%)"
			await ctx.send(message)
	elif mode.lower() == 'mw':
		mw_wins = get_mode_stat('mw', 'wins', duels_data)
		message_lines_mw = [f"{get_rank(ign, data)}{displayname} has {mw_wins} MegaWalls Duels wins."] 
		if kit.lower() == 'top10':
			kit_wins_list = []
			for mw_kit in kits_mw:
				wins = get_kit_wins('mw', mw_kit, duels_data)
				update_kit_stats(uuid, mw_kit, wins, mode.lower())
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					percentage = round((wins/mw_wins)*100, 2) if mw_wins > 0 else 0.0
					kit_wins_list.append((wins, f"{wins} {mw_kit.capitalize()} {win_s} ({percentage}%)"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_mw.extend(msg for _, msg in sorted_kits[:10])
			remaining = sorted_kits[10:]
			if remaining:
				remaining_wins = mw_wins - sum(w for w, _ in sorted_kits[:10])
				remaining_percentage = round((remaining_wins/mw_wins)*100, 2) if mw_wins > 0 else 0.0
				win_s = "win" if remaining_wins == 1 else "wins" 
				message_lines_mw.append(f"+ {remaining_wins} {win_s} with other kits ({remaining_percentage}%)")
			await ctx.send('\n'.join(message_lines_mw))
		elif kit.lower() == 'all':
			kit_wins_list = []
			for mw_kit in kits_mw:
				wins = get_kit_wins('mw', mw_kit, duels_data)
				update_kit_stats(uuid, mw_kit, wins, mode.lower())
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					kit_wins_list.append((wins, f"{wins} {mw_kit.capitalize()} {win_s}"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_mw.extend(msg for _, msg in sorted_kits)
			await ctx.send('\n'.join(message_lines_mw))
		else:
			wins = get_kit_wins('mw', kit, duels_data)
			update_kit_stats(uuid, kit, wins, mode.lower())
			win_s = "win" if wins == 1 else "wins"
			percentage = round((wins/mw_wins)*100, 2) if mw_wins > 0 else 0.0
			message = f"{get_rank(ign, data)}{displayname} has {wins} {kit.capitalize()} {win_s} in Mega Walls Duels. ({percentage}%)"
			await ctx.send(message)
	else:
		wins = get_kit_wins(mode, kit, duels_data)
		win_s = "win" if wins == 1 else "wins"
		message = f"{get_rank(ign, data)}{displayname} has {wins} {kit.capitalize()} {win_s}."
		print('in !kit; mode wasnt swd blitz or mw, FYI')
		await ctx.send(message)

@bot.command(name='s')
async def s(ctx, ign=None):
	if ign == None:
		ign = ign_not_given(ctx.author.id, ctx.author.display_name, ctx.author.name)
	status = statusget(ign)
	session = status.get("session", {})
	playerdb_data = playerdbget(ign)
	displayname = get_displayname(ign, playerdb_data)
	if session.get("online"):
		game = session.get('gameType')
		mode = session.get('mode')
		map = session.get('map', False)
		message = f"{displayname}\nGame: {game}\nMode: {mode}\nMap: {map if map != False else mode}"
		await ctx.send(message)
	else:
		recent_games_data = recentgamesget(ign)["games"]
		if len(recent_games_data) != 0:
			messages_list = []
			for id in range(len(recent_games_data)):
				recentgames = recentgamesget(ign)["games"][id]
				start_time = round(recentgames.get('date', 'N/A')/1000)
				stop_time = round(recentgames.get('ended', 'N/A')/1000)
				game = recentgames.get('gameType')
				mode = recentgames.get('mode')
				map = recentgames.get('map', False)
				messages_list.append(f"{displayname}\nStarted: <t:{start_time}:T>\nEnded: <t:{stop_time}:T>\nGame: {game}\nMode: {mode}\nMap: {map if map != False else mode}")
			await ctx.send(f'{displayname} is (appearing) offline.\nRecent games:\n{'\n\n'.join(messages_list)}')
		else:
			await ctx.send(f'{displayname} is (appearing) offline. Recent games unavailable.')

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

@bot.command(name='uuid')
async def uuid(ctx, ign=None):
	if ign == None:
		ign = ign_not_given(ctx.author.id, ctx.author.display_name, ctx.author.name)
	playerdb_data = playerdbget(ign)
	displayname = get_displayname(ign, playerdb_data)
	uuid = get_uuid(ign, playerdb_data)
	await ctx.send(f"{displayname}'s UUID: `{uuid}`")

@bot.command(name='kits')
async def uuid(ctx, *, args=''):
	await ctx.send(f'Did you mean `!kit {args}`, {ctx.author.display_name}?')

@bot.command(name='dodge')
async def dodge(ctx, ign1, amount=7, ign2=None):
	if str(ctx.channel) == 'dodging':
		if ign2 == None:
			ign2 = ign_not_given(ctx.author.id, ctx.author.display_name, ctx.author.name)
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
			await ctx.send(f'{ign1}: {message1}\n{ign2}: {message2}\nIterations remaining: {amount-x-1}/{amount}')
			if message1 == message2:
				if message1 != list1[(len(list1))-2] or message2 != list2[(len(list2))-2]:
					await ctx.send(f'DODGE! {ctx.author.mention}')
			x += 1
			await asyncio.sleep(random.randint(7, 10))
	else:
		await ctx.send(f'Private command.')

@bot.command(name='test')
async def test(ctx, *, input):
	if ctx.author.name == 'poki95':
		test_commands_list = [f"{line.strip()}" for line in input.strip().split(',')]
		await ctx.reply(f'User `{ctx.author.name}` authorized.\nStarting the test of `{len(test_commands_list)}` commands.\nApprox. duration of the test: `{(len(test_commands_list)-1)*5}` seconds.')
		for test_command in test_commands_list:
			await ctx.send(test_command)
			await asyncio.sleep(5)
	else:
		await ctx.reply(f'User `{ctx.author.name}` not authorized.')

@bot.command(name='session') # WiP 
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

@bot.command(name='link')
async def link(ctx, ign=None):
	if ign == None:
		await ctx.send(already_linked(ctx.author.id))
	else:
		playerdb_data = playerdbget(ign)
		uuid = get_uuid(ign, playerdb_data)
		message = link_to(ctx.author.name, ctx.author.id, uuid, playerdb_data)
		conn.commit()
		await ctx.send(message)

@bot.command(name='unlink')
async def unlink(ctx):
	message = unlink_from(ctx.author.id)
	await ctx.send(message)

@bot.command(name='dbs')
async def dbs(ctx, table=None):
	if ctx.author.name == 'poki95':
		if table == 'modes':
			for mode_alias in mode_list:
				mode_db = mode_db_list[mode_list.index(mode_alias)]
				mode_clean = mode_names[mode_list.index(mode_alias)]
				try:
					cursor.execute(
						"INSERT INTO modes (mode_alias, mode_db, mode_clean) VALUES (?, ?, ?)",
						(mode_alias, mode_db, mode_clean)
					)
					conn.commit()
					print(f"Added {mode_alias} - {mode_db} - {mode_clean}")
				except Exception as e:
					print(f"error: {e}")
					break
			await ctx.send("Job done.")
		elif table == 'kits':
			for kit_alias in kits_sw:
				mode = 'sw'
				try:
					cursor.execute(
						"INSERT INTO kits (mode, kit) VALUES (?, ?)",
						(mode, kit_alias)
					)
					conn.commit()
				except Exception as e:
					print(e)
					break
			for kit_alias in kits_blitz:
				mode = 'blitz'
				try:
					cursor.execute(
						"INSERT INTO kits (mode, kit) VALUES (?, ?)",
						(mode, kit_alias)
					)
					conn.commit()
				except Exception as e:
					print(e)
					break
			for kit_alias in kits_mw:
				mode = 'mw'
				try:
					cursor.execute(
						"INSERT INTO kits (mode, kit) VALUES (?, ?)",
						(mode, kit_alias)
					)
					conn.commit()
				except Exception as e:
					print(e)
					break
			await ctx.send("Job done. (or not)")
		else:
			await ctx.send('Choose a table to setup; `modes`, `kits`')
			
	else:
		await ctx.send("Unauthorized.")

@bot.command(name='cak')
async def cak(ctx):
	if ctx.author.name == 'poki95':
		global api_key
		while True:
			try:
				r = requests.get(f'https://api.hypixel.net/player?key={api_key}&uuid=3e92f52f-03e8-4529-be93-353e3c360c63').json()["player"]
				print('Checked temp API key: VALID.')
				await asyncio.sleep(600)
			except KeyError:
				api_key = dev_api_key
				print('Temp API key expired, switched to dev API key.')
				await ctx.reply('api_key changed to dev_api_key')
				break

@bot.command(name='mrfdb')
async def mrfdb(ctx, *, mc_uuid):
	if ctx.author.name == 'poki95':
		try:
			cursor.execute(f'''
				SELECT discord_name
				FROM linked_users
				WHERE mc_uuid = ?
			''', (mc_uuid,))
			discord_name = cursor.fetchone()[0]
			cursor.execute(f'''
				DELETE FROM linked_users
				WHERE mc_uuid = ?
			''', (mc_uuid,))
			conn.commit()
			await ctx.send(f"Unlinked `{discord_name}` from `{mc_uuid}`")
		except Exception as e:
			if str(e) == "'NoneType' object is not subscriptable":
				await ctx.send(f"Account not currently linked.")
			else:
				raise e
	else:
		await ctx.send("Unauthorized.")

@bot.command(name='klb')
async def klb(ctx, kit='pyromancer', mode='sw'):
	leaderboard = [f"## Top 10 {mode.capitalize()} {kit.capitalize()} kit wins"]
	kit_wins_list = get_all_players_with_kit_wins(kit.lower(), mode.lower())
	if kit_wins_list == "Kit doesn't exist for the specified mode.":
		await ctx.send(kit_wins_list)
		return
	leaderboard_list = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)[:10]
	for pos, (_, msg) in enumerate(leaderboard_list, start=1):
		leaderboard.append(f"{pos}. {msg}")
	await ctx.send('\n'.join(leaderboard))

@bot.command(name='dbf')
async def dbf(ctx, what, *, input):
	if ctx.author.name == 'poki95':
		if what == 'players':
			igns_list = [f"{line.strip()}" for line in input.strip().split(' ')]
			await ctx.reply(f'User `{ctx.author.name}` authorized.\nStarting the addition of `{len(igns_list)}` players to the database.\nApprox. duration of the test: `{(len(igns_list)-1)*10-5}` seconds.')
			for ign in igns_list:
				await ctx.send(add_all_players_stats('ign', ign))
		elif what == 'guild':
			guild_data = guildget(input, what)['guild']
			igns_list = guild_data.get('members', {})
			for i in range(0, len(igns_list)):
				uuid = igns_list[i].get('uuid', '?')
				if uuid != '?':
					await ctx.send(add_all_players_stats('uuid', uuid))

		await ctx.reply(f"Done! Added `{len(igns_list)}` players to the database.")
	else:
		await ctx.reply(f'User `{ctx.author.name}` not authorized.')	

'''@bot.command(name='lb')
async def lb(ctx, mode):
	html = await getlb(mode)
	await ctx.send(len(html))'''

@bot.command(name='icons')
async def icons(ctx):
	message = []
	for icon in prefix_icons:
		message.append(f'{prefix_icons_db[prefix_icons.index(icon)]}: {icon}')
	await ctx.send('# Duels Prefix Icons:\n``' + '\n'.join(message) + '``')

# Run the bot 
bot.run(TOKEN)