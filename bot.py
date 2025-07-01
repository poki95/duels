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
div_req = [100000, 50000, 25000, 10000, 5000, 2000, 1000, 500, 250, 100, 50, 0] # requirements for each division twritle
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

uhc_submodes = ['uhc_duel_wins', 'uhc_doubles_wins', 'uhc_four_wins', 'uhc_meetup_wins']
bridge_submodes = ['bridge_duel_wins', 'bridge_doubles_wins', 'bridge_threes_wins', 'bridge_four_wins', 'bridge_2v2v2v2_wins', 'bridge_3v3v3v3_wins', 'capture_threes_wins']
uhc_submodes_losses = ['uhc_duel_losses', 'uhc_doubles_losses', 'uhc_four_losses', 'uhc_meetup_losses']
bridge_submodes_losses = ['bridge_duel_losses', 'bridge_doubles_losses', 'bridge_threes_losses', 'bridge_four_losses', 'bridge_2v2v2v2_losses', 'bridge_3v3v3v3_losses', 'capture_threes_losses']
min_wins_per_hour = [40, 75, 25, 80, 80, 100, 70, 20, 60, 80, 100, 20, 10, 20, 60]
max_wins_per_hour = [70, 85, 40, 100, 100, 150, 130, 40, 90, 110, 150, 30, 20, 30, 60]
gph = [70, 85, 40, 95, 85, 150, 120, 40, 75, 80, 160, 30, 12, 30, 60]
prefix_icons_db = ['STAR', 'FANCY_STAR', 'POINTY_STAR', 'SUN', 'BIOHAZARD', 'FLOWER', 'YIN_AND_YANG', 'SNOWMAN', 'HEART', 'GG', 'SMILEY', 'DIV_RANKING']
prefix_icons = ['✫', '✯', '✵', '☀', '☣', '❀', '☯', '☃', '❤', '**GG**', '^_^', '**#???**']
#
# sw classic arena pkd mwd

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
Available kits: All sw, mw and blitzd kits.

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
	equipped_icon = prefix_icons[prefix_icons_db.index(duels_data.get("equipped_prefix_icon", ''))]
	equipped_color = duels_data.get("equipped_prefix_color", '')
	equipped_title = duels_data.get("active_cosmetictitle", '')
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

	def get_mode_losses(mode_db):
		try:
			if mode_db == 'oa':
				return duels_data.get("losses", 0)
			elif mode_db == 'uhc':
				return sum(duels_data.get(submode, 0) for submode in uhc_submodes_losses)
			elif mode_db == 'bridge':
				return sum(duels_data.get(submode, 0) for submode in bridge_submodes_losses)
			elif mode_db in ['sw', 'mw', 'op']:
				return duels_data.get(f'{mode_db}_duel_losses', 0) + duels_data.get(f'{mode_db}_doubles_losses', 0)
			elif mode_db in ['parkour_eight', 'duel_arena']:
				return duels_data.get(f'{mode_db}_losses', 0)
			else:
				return duels_data.get(f'{mode_db}_duel_losses', 0)
		except KeyError:
			return 0
	
	wins = {}
	messages = {}
	
	modes = mode_db_list if mode == 'all' else [mode_db_list[mode_list.index(mode)]]
	wins_list = []
	overall_playtime = 0
	for mode_db in modes:
		win_count = get_mode_wins(mode_db)
		loss_count = get_mode_losses(mode_db)
		is_oa = (mode_db == 'oa')
		div, div_num = get_division_info(win_count, is_oa)	
		division = f'{div} {roman.toRoman(div_num)}' if div_num != 1 and div != "None" else div
#		min_wph = min_wins_per_hour[mode_db_list.index(mode_db)-1]
#		max_wph = max_wins_per_hour[mode_db_list.index(mode_db)-1]
#		min_playtime = round(win_count/max_wph)
#		max_playtime = round(win_count/min_wph)
		playtime = round((win_count + loss_count)/gph[mode_db_list.index(mode_db)-1])
		win_s = "win" if win_count == 1 else "wins"
		mode_clean = mode_names[mode_db_list.index(mode_db)]
		if mode_db != 'oa':			
			overall_playtime += playtime
			wins_list.append((win_count, f"{format_number(win_count)} {mode_clean} {win_s} - {mode_clean} {division} (~{playtime}h)"))
		else:
			overall_win_count = get_mode_wins(mode_db)
			div, div_num = get_division_info(win_count, True)	
			oa_division = f'{div} {roman.toRoman(div_num)}' if div_num != 1 and div != "None" else div
			win_s = "win" if win_count == 1 else "wins"
			mode_clean = mode_names[mode_db_list.index(mode_db)]
	sorted_modes = sorted(wins_list, key=lambda x: x[0], reverse=True)
	message_lines = [f"{equipped_icon} {equipped_title} {get_rank(ign, data)}{displayname}\n{format_number(overall_win_count)} Overall {win_s} - Overall {oa_division} (~{overall_playtime}h)"]
	message_lines.extend(msg for _, msg in sorted_modes)
	if mode == 'all':
		await ctx.send('\n'.join(message_lines))
	else:
		await ctx.send(message_lines[1])
		
@bot.command(name='kit')
async def kit(ctx, ign, *, kit_user='sw'):
	data = dataget(ign)

	error = False
	if "player" not in data:
		if str(data) == "{'success': False, 'cause': 'Invalid API key'}":
			await ctx.send("Invalid API key... Contact `poki95` on Discord. (hypixel won't give me a developer key bruh)")
			error = True
		else:
			await ctx.send('Unidentified error. Contact `poki95` on Discord. Thanks!')
		return

	kit = kit_user.lower()
	displayname = data["player"]["displayname"]
	duels_data = data["player"].get("stats", {}).get("Duels", {})

	sw_wins = duels_data.get("sw_duel_wins", 0) + duels_data.get("sw_doubles_wins", 0)
	blitz_wins = duels_data.get("blitz_duel_wins", 0)
	mw_wins = duels_data.get("mw_duel_wins", 0) + duels_data.get("mw_doubles_wins", 0)
	
	message_lines_sw = [f"{get_rank(ign, data)}{displayname} has {sw_wins} SkyWars Duels wins."]
	message_lines_blitz = [f"{get_rank(ign, data)}{displayname} has {blitz_wins} Blitz Duels wins."] 
	message_lines_mw = [f"{get_rank(ign, data)}{displayname} has {mw_wins} MegaWalls Duels wins."]
	if "sw" in kit:
		if "all" in kit:
			kit_wins_list = []
			for swd_kit in kits:
				wins = duels_data.get(f"sw_duel_{swd_kit}_kit_wins", 0) + duels_data.get(f"sw_doubles_{swd_kit}_kit_wins", 0)
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					kit_wins_list.append((wins, f"{wins} {swd_kit} {win_s}"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_sw.extend(msg for _, msg in sorted_kits)
			await ctx.send('\n'.join(message_lines_sw))

		else:
			kit_wins_list = []
			for swd_kit in kits:
				wins = duels_data.get(f"sw_duel_{swd_kit}_kit_wins", 0) + duels_data.get(f"sw_doubles_{swd_kit}_kit_wins", 0)
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					percentage = round((wins/sw_wins)*100, 2) if sw_wins > 0 else 0.0
					kit_wins_list.append((wins, f"{wins} {swd_kit} {win_s} ({percentage}%)"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_sw.extend(msg for _, msg in sorted_kits[:10])
			remaining = sorted_kits[10:]
			if remaining:
				remaining_wins = sum(w for w, _ in remaining)
				remaining_percentage = round((remaining_wins/sw_wins)*100, 2) if sw_wins > 0 else 0.0
				win_s = "win" if remaining_wins == 1 else "wins"
				message_lines_sw.append(f"+ {remaining_wins} {win_s} with other kits ({remaining_percentage}%)")
			await ctx.send('\n'.join(message_lines_sw))
			
	elif "blitz" in kit:
		if "all" in kit:
			kit_wins_list = []
			for blitz_kit in kits_blitz:
				wins = duels_data.get(f"blitz_duel_{blitz_kit}_kit_wins", 0)
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					kit_wins_list.append((wins, f"{wins} {blitz_kit} {win_s}"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_blitz.extend(msg for _, msg in sorted_kits)
			await ctx.send('\n'.join(message_lines_blitz))
		else:
			kit_wins_list = []
			for blitz_kit in kits_blitz:
				wins = duels_data.get(f"blitz_duel_{blitz_kit}_kit_wins", 0)
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					percentage = round((wins/blitz_wins)*100, 2) if blitz_wins > 0 else 0.0
					kit_wins_list.append((wins, f"{wins} {blitz_kit} {win_s} ({percentage}%)"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_blitz.extend(msg for _, msg in sorted_kits[:10])
			remaining = sorted_kits[10:]
			if remaining:
				remaining_wins = sum(w for w, _ in remaining)
				remaining_percentage = round((remaining_wins/blitz_wins)*100, 2) if blitz_wins > 0 else 0.0
				win_s = "win" if remaining_wins == 1 else "wins" 
				message_lines_blitz.append(f"+ {remaining_wins} {win_s} with other kits ({remaining_percentage}%)")
			await ctx.send('\n'.join(message_lines_blitz))

	if "mw" in kit:
		if "all" in kit:
			kit_wins_list = []
			for mwd_kit in kits_mw:
				wins = duels_data.get(f"mw_duel_{mwd_kit}_kit_wins", 0) + duels_data.get(f"mw_doubles_{mwd_kit}_kit_wins", 0)
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					kit_wins_list.append((wins, f"{wins} {mwd_kit} {win_s}"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_mw.extend(msg for _, msg in sorted_kits)
			await ctx.send('\n'.join(message_lines_mw))

		else:
			kit_wins_list = []
			for mwd_kit in kits_mw:
				wins = duels_data.get(f"mw_duel_{mwd_kit}_kit_wins", 0) + duels_data.get(f"mw_doubles_{mwd_kit}_kit_wins", 0)
				if wins > 0:
					win_s = "win" if wins == 1 else "wins"
					percentage = round((wins/mw_wins)*100, 2) if mw_wins > 0 else 0.0
					kit_wins_list.append((wins, f"{wins} {mwd_kit} {win_s} ({percentage}%)"))
			sorted_kits = sorted(kit_wins_list, key=lambda x: x[0], reverse=True)
			message_lines_mw.extend(msg for _, msg in sorted_kits[:10])
			remaining = sorted_kits[10:]
			if remaining:
				remaining_wins = sum(w for w, _ in remaining)
				remaining_percentage = round((remaining_wins/mw_wins)*100, 2) if mw_wins > 0 else 0.0
				win_s = "win" if remaining_wins == 1 else "wins"
				message_lines_mw.append(f"+ {remaining_wins} {win_s} with other kits ({remaining_percentage}%)")
			await ctx.send('\n'.join(message_lines_mw))

	elif kit in kits:
		wins = duels_data.get(f"sw_duel_{swd_kit}_kit_wins", 0) + duels_data.get(f"sw_doubles_{swd_kit}_kit_wins", 0)
		win_s = "win" if wins == 1 else "wins"
		message_lines = [f"{get_rank(ign, data)}{displayname} has {wins} {kit} {win_s}."]
		await ctx.send('\n'.join(message_lines))

	else:
		await ctx.send(f'`{kit}` is not a recognized kit. Type `!h` for help.')

@bot.command(name='s')
async def s(ctx, name):
	status = statusget(name)
	session = status.get("session", {})
	if session.get("online"):
		game = session.get('gameType')
		mode = session.get('mode')
		map = session.get('map', False)
		message = f"{ign}\nGame: {game}\nMode: {mode}\nMap: {map}"
		await ctx.send(message)
	else:
		await ctx.send('Player offline.')

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
	await ctx.send(f"{get_rank(displayname, data)}{displayname}'s best kit is {best_kit.capitalize()}, with {max_wins} wins. ({percentage}%)")

# Run the bot
bot.run(TOKEN)
