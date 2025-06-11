import math
import requests
import json
import roman
import csv
   
# given data
mode_list = ['oa', 'uhc', 'sw', 'mw', 'blitz', 'op', 'classic', 'bow', 'ndb', 'combo', 'tnt', 'sumo', 'bridge', 'pkd', 'boxing', 'arena', 'all', 'kit'] # mode aliases
mode_db_list = ['oa', 'uhc', 'sw', 'mw', 'blitz', 'op', 'classic', 'bow', 'potion', 'combo', 'bowspleef', 'sumo', 'bridge', 'parkour_eight', 'boxing', 'duel_arena'] # mode database aliases
mode_names = ['Overall', 'UHC', 'SkyWars', 'MW', 'Blitz', 'OP', 'Classic', 'Bow', 'NoDebuff', 'Combo', 'TNT', 'Sumo', 'Bridge', 'Parkour', 'Boxing', 'Arena'] # clean mode names
div_list = ['ASCENDED', 'DIVINE', 'CELESTIAL', 'Godlike', 'Grandmaster', 'Legend', 'Master', 'Diamond', 'Gold', 'Iron', 'Rookie', 'None'] # divisions
div_req = [100000, 50000, 25000, 10000, 5000, 2000, 1000, 500, 250, 100, 50, 0] # requirements for each division title
div_step = [10000, 10000, 5000, 3000, 1000, 600, 200, 100, 50, 30, 10, 1] # requirements to go up a level within a division title

api_key = "hypixel_api_key"						# update every 3 days 


error = True
while error == True:
	ign = str(input('Name: '))											# ask for the player's ign whose stats are going to be checked
	try:															
		response = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{ign}")
		uuid = response.json()["id"]
		error = False
	except KeyError:
		error = True
		print('Invalid IGN. Try again.')
	

mode = str(input('> ')).lower()											# ask for mode

while mode not in mode_list:											# check that the mode is valid
	if mode == 'help':
		print('Available modes:')
		for i in mode_list:
			if i != 'all':
				print(f'{i},', end=' ')
			else:
				print('all.')
		mode = str(input('Mode: '))
	if mode == 'all':
		break
	elif mode not in mode_list:
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
try:
	data.json()["player"]["stats"]
except KeyError:
	print(f'{ign} has no Hypixel stats.')
try:
	data.json()["player"]["stats"]["Duels"]
except KeyError:
	print(f'{ign} has no Hypixel Duels stats.')

if mode == 'all':
	for mode_db in mode_db_list:
		if mode_db == 'oa':
			try:
				globals()[f'{mode_db}_wins'] = data.json()["player"]["stats"]["Duels"]["wins"]
			except KeyError:  
				globals()[f'{mode_db}_wins'] = 0
		elif mode_db == 'uhc':
			try:
				globals()[f'{mode_db}_duel_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_duel_wins"]
			except KeyError:  
				globals()[f'{mode_db}_duel_wins'] = 0
			try:
				globals()[f'{mode_db}_doubles_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_doubles_wins"]
			except KeyError:
				globals()[f'{mode_db}_doubles_wins'] = 0
			try:	
				globals()[f'{mode_db}_four_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_four_wins"]
			except KeyError:
				globals()[f'{mode_db}_four_wins'] = 0
			try:
				globals()[f'{mode_db}_meetup_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_meetup_wins"]
			except KeyError:
				globals()[f'{mode_db}_meetup_wins'] = 0
			globals()[f'{mode_db}_wins'] = (
			globals()[f'{mode_db}_duel_wins']
			+ globals()[f'{mode_db}_doubles_wins']
			+ globals()[f'{mode_db}_four_wins']
			+ globals()[f'{mode_db}_meetup_wins'])
		elif mode_db in ['sw', 'mw', 'op']:
			try:
				globals()[f'{mode_db}_duel_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_duel_wins"]
			except KeyError:  
				globals()[f'{mode_db}_duel_wins'] = 0
			try:
				globals()[f'{mode_db}_doubles_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_doubles_wins"]
			except KeyError:
				globals()[f'{mode_db}_doubles_wins'] = 0
			globals()[f'{mode_db}_wins'] = (globals()[f'{mode_db}_duel_wins'] + globals()[f'{mode_db}_doubles_wins'])
		elif mode_db == 'bridge':
			try:
				globals()[f'{mode_db}_duel_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_duel_wins"]
			except KeyError:
				globals()[f'{mode_db}_duel_wins'] = 0
			try:
				globals()[f'{mode_db}_doubles_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_doubles_wins"]
			except KeyError:
				globals()[f'{mode_db}_doubles_wins'] = 0
			try:	
				globals()[f'{mode_db}_threes_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_threes_wins"]
			except KeyError:
				globals()[f'{mode_db}_threes_wins'] = 0
			try:	
				globals()[f'{mode_db}_four_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_four_wins"]
			except KeyError:
				globals()[f'{mode_db}_four_wins'] = 0
			try:	
				globals()[f'{mode_db}_2v2v2v2_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_2v2v2v2_wins"]
			except KeyError:
				globals()[f'{mode_db}_2v2v2v2_wins'] = 0
			try:	
				globals()[f'{mode_db}_3v3v3v3_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_3v3v3v3_wins"]
			except KeyError:
				globals()[f'{mode_db}_3v3v3v3_wins'] = 0
			try:	
				globals()[f'{mode_db}_capture_threes_wins'] = data.json()["player"]["stats"]["Duels"]["capture_threes_wins"]
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
				globals()[f'{mode_db}_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_wins"]
			except KeyError:
				globals()[f'{mode_db}_wins'] = 0
		else:	
			try:
				globals()[f'{mode_db}_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_duel_wins"]
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
					print(f'{mode_clean} {div} {div_num} - {wincount} win')		
			else:
					print(f'{mode_clean} {div} {div_num} - {wincount} wins')
		else:															# hide the division number when it's 1
			if globals()[f'{mode_db}_wins'] == 1:													
					print(f'{mode_clean} {div} - {wincount} win')			
			else:
					print(f'{mode_clean} {div} - {wincount} wins')
	try:
		capture_duel_wins = data.json()["player"]["stats"]["Duels"]["capture_duel_wins"]
	except KeyError:
		capture_duel_wins = 0
	ghost_wins = (capture_duel_wins)
	print(f'Ghost wins: {ghost_wins}')


else:
	mode_index = mode_list.index(mode)
	mode_db = mode_db_list[mode_index]
	if mode_db == 'oa':
		try:
			globals()[f'{mode_db}_wins'] = data.json()["player"]["stats"]["Duels"]["wins"]
		except KeyError:  
			globals()[f'{mode_db}_wins'] = 0
	elif mode_db == 'uhc':
		
		try:
			globals()[f'{mode_db}_duel_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_duel_wins"]
		except KeyError:  
			globals()[f'{mode_db}_duel_wins'] = 0
		try:
			globals()[f'{mode_db}_doubles_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_doubles_wins"]
		except KeyError:
			globals()[f'{mode_db}_doubles_wins'] = 0
		try:	
			globals()[f'{mode_db}_four_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_four_wins"]
		except KeyError:
			globals()[f'{mode_db}_four_wins'] = 0
		try:
			globals()[f'{mode_db}_meetup_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_meetup_wins"]
		except KeyError:
			globals()[f'{mode_db}_meetup_wins'] = 0
		globals()[f'{mode_db}_wins'] = (
		globals()[f'{mode_db}_duel_wins']
		+ globals()[f'{mode_db}_doubles_wins']
		+ globals()[f'{mode_db}_four_wins']
		+ globals()[f'{mode_db}_meetup_wins'])
	elif mode_db in ['sw', 'mw', 'op']:
		try:
			globals()[f'{mode_db}_duel_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_duel_wins"]
		except KeyError:  
			globals()[f'{mode_db}_duel_wins'] = 0
		try:
			globals()[f'{mode_db}_doubles_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_doubles_wins"]
		except KeyError:
			globals()[f'{mode_db}_doubles_wins'] = 0
		globals()[f'{mode_db}_wins'] = (globals()[f'{mode_db}_duel_wins'] + globals()[f'{mode_db}_doubles_wins'])
	elif mode_db == 'bridge':
		try:
			globals()[f'{mode_db}_duel_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_duel_wins"]
		except KeyError:
			globals()[f'{mode_db}_duel_wins'] = 0
		try:
			globals()[f'{mode_db}_doubles_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_doubles_wins"]
		except KeyError:
			globals()[f'{mode_db}_doubles_wins'] = 0
		try:	
			globals()[f'{mode_db}_threes_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_threes_wins"]
		except KeyError:
			globals()[f'{mode_db}_threes_wins'] = 0
		try:	
			globals()[f'{mode_db}_four_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_four_wins"]
		except KeyError:
			globals()[f'{mode_db}_four_wins'] = 0
		try:	
			globals()[f'{mode_db}_2v2v2v2_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_2v2v2v2_wins"]
		except KeyError:
			globals()[f'{mode_db}_2v2v2v2_wins'] = 0
		try:	
			globals()[f'{mode_db}_3v3v3v3_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_3v3v3v3_wins"]
		except KeyError:
			globals()[f'{mode_db}_3v3v3v3_wins'] = 0
		try:	
			globals()[f'{mode_db}_capture_threes_wins'] = data.json()["player"]["stats"]["Duels"]["capture_threes_wins"]
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
			globals()[f'{mode_db}_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_wins"]
		except KeyError:
			globals()[f'{mode_db}_wins'] = 0
	else:	
		try:
			globals()[f'{mode_db}_wins'] = data.json()["player"]["stats"]["Duels"][f"{mode_db}_duel_wins"]
		except KeyError:
			globals()[f'{mode_db}_wins'] = 0
	# print(f'{globals()[f'{mode_db}_wins']}')
	
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
				print(f'{mode_clean} {div} {div_num} - {wincount} win')		
		else:
				print(f'{mode_clean} {div} {div_num} - {wincount} wins')
	else:																# hide the division number when it's 1
		if globals()[f'{mode_db}_wins'] == 1:												
				print(f'{mode_clean} {div} - {wincount} win')			
		else:
				print(f'{mode_clean} {div} - {wincount} wins')

submode = str(input('> ')).lower()

if submode == 'eta':
	goal = int(input('Goal: '))
	wph = int(input('Wins per hour: '))
	win_diff = goal - globals()[f'{mode_db}_wins']
	eta = win_diff/wph
	print(f'{ign} will hit their {mode_clean} wins goal in {win_diff} wins, which equates to ~{eta} hours')
elif submode == 'kit':
	print('This will check for SkyWars Duels ranked kit wins.')
	kit = str(input('SkyWars Duels ranked kit: ')).lower()
	try:
		globals()[f'{kit}_wins'] = data.json()["player"]["stats"]["Duels"][f"{kit}_kit_wins"]
	except KeyError:  
		globals()[f'{kit}_wins'] = 0
print(f'{ign} has {globals()[f'{kit}_wins']} {kit} wins in SkyWars Duels.')
		

