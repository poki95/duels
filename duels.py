import math
import requests
import json

# given data
mode_list = ['oa', 'uhc', 'sw', 'mw', 'blitz', 'op', 'classic', 'bow', 'ndb', 'combo', 'tnt', 'sumo', 'bridge', 'pkd', 'boxing'] # mode aliases
mode_db_list = ['oa', 'uhc', 'sw', 'mw', 'blitz', 'op', 'classic', 'bow', 'potion', 'combo', 'bowspleef', 'sumo', 'bridge', 'parkour_eight', 'boxing'] # mode database aliases
mode_names = ['Overall', 'UHC', 'SkyWars', 'MW', 'Blitz', 'OP', 'Classic', 'Bow', 'NoDebuff', 'Combo', 'TNT', 'Sumo', 'Bridge', 'Parkour', 'Boxing'] # clean mode names
div_list = ['ASCENDED', 'DIVINE', 'CELESTIAL', 'Godlike', 'Grandmaster', 'Legend', 'Master', 'Diamond', 'Gold', 'Iron', 'Rookie', 'None'] # divisions
div_req = [100000, 50000, 25000, 10000, 5000, 2000, 1000, 500, 250, 100, 50, 0] # requirements for each division title
div_step = [10000, 10000, 5000, 3000, 1000, 600, 200, 100, 50, 30, 10, 1] # requirements to go up a level within a division title

api_key = "API KEY HERE"												# update every 3 days 

ign = str(input('Name: '))												# ask for the player's ign whose stats are going to be checked
response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{ign}")
uuid = response.json()["id"]

mode = str(input('Mode: ')).lower()										# ask for mode

while mode not in mode_list:											# check that the mode is valid
	if mode == 'help':
		print(f'Available modes: {mode_list}')
		mode = str(input('Mode: '))
	if mode == 'all':
		break
	else:
		print('Invalid mode.')
		print("Type 'help' to get the mode aliases.")
		mode = str(input('Mode: ')).lower()
if mode != 'all':		
	mode_index = mode_list.index(mode)        							# convert the alias to the mode's full name
	mode_clean = mode_names[mode_index]

data = requests.get(													# load the player's stats
    url = "https://api.hypixel.net/player",
    params = {
        "key": api_key,
        "uuid": uuid
    }
)

if mode == 'all':
	for mode_wins in mode_db_list:
		if mode_wins == 'oa':
			globals()[f'{mode_wins}_wins'] = data.json()["player"]["stats"]["Duels"]["wins"]
		elif mode_wins == 'parkour_eight':
			globals()[f'{mode_wins}_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_wins}_wins"]
		else:	
			globals()[f'{mode_wins}_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_wins}_duel_wins"]

		mode_index = mode_db_list.index(mode_wins)        				# convert the database alias to the mode's full name
		mode_clean = mode_names[mode_index]
		print(f'{mode_clean} wins: {mode_wins_wins}')					# print the wins for every mode
else:
	mode_wins = mode
	if mode_wins == 'oa':
			globals()[f'{mode_wins}_wins'] = data.json()["player"]["stats"]["Duels"]["wins"]
	if mode_wins == 'uhc':
			globals()[f'{mode_wins}_wins'] = (
			data.json()["player"]["stats"]["Duels"][f"{mode_wins}_duel_wins"]
			+ data.json()["player"]["stats"]["Duels"][f"{mode_wins}_doubles_wins"]
			+ data.json()["player"]["stats"]["Duels"][f"{mode_wins}_four_wins"]
			+ data.json()["player"]["stats"]["Duels"][f"{mode_wins}_meetup_wins"])
	elif mode_wins == 'parkour_eight':
			globals()[f'{mode_wins}_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_wins}_wins"]
	else:	
			globals()[f'{mode_wins}_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_wins}_duel_wins"]
	print(f'{globals()[f'{mode_wins}_wins']}')
	# print('Not implemented yet, sorry!')
	
	
	
	
	
'''
if mode == 'oa':														# overall titles require 2x the wins compared to mode titles
	practical_wins = wins/2												# so divide practical wincount by 2
else:
    practical_wins = wins												# use practical wincount 

wincount = str(wins)[::-1]												# group digits by 3 for readability (e.g. 139,813)
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
for req in div_req:														# choose the right division + division number
	if practical_wins >= req:
		div = div_list[div_number]
		surplus = practical_wins - (req - div_step[div_number])
		div_num = math.floor(surplus/div_step[div_number])
		break
	div_number += 1
	
if div_num > 50:														# make sure ASCENDED L is the maximum division
	div_num = 50	
elif div == 'None':														# remove any division number when below Rookie
	div_num = 1
	
if div_num != 1:														# show the division number when it's not 1
	if wins == 1:
			print(f'{mode_clean} {div} {div_num} - {wincount} win')		
	else:
			print(f'{mode_clean} {div} {div_num} - {wincount} wins')
else:																	# hide the division number when it's 1
	if wins == 1:													
			print(f'{mode_clean} {div} - {wincount} win')			
	else:
			print(f'{mode_clean} {div} - {wincount} wins')
'''
