import math

# given data
mode_list = ['oa', 'uhc', 'sw', 'mw', 'blitz', 'op', 'classic', 'bow', 'ndb', 'combo', 'tnt', 'sumo', 'bridge', 'pkd', 'boxing']
mode_names = ['Overall', 'UHC', 'SkyWars', 'MW', 'Blitz', 'OP', 'Classic', 'Bow', 'NoDebuff', 'Combo', 'TNT', 'Sumo', 'Bridge', 'Parkour', 'Boxing']
div_list = ['ASCENDED', 'DIVINE', 'CELESTIAL', 'Godlike', 'Grandmaster', 'Legend', 'Master', 'Diamond', 'Gold', 'Iron', 'Rookie', 'None']
div_req = [100000, 50000, 25000, 10000, 5000, 2000, 1000, 500, 250, 100, 50, 0]
div_step = [10000, 10000, 5000, 3000, 1000, 600, 200, 100, 50, 30, 10, 1]

mode = str(input('Mode: ')).lower()										# ask for mode

while mode not in mode_list:											# check that the mode is valid
	if mode == 'help':
		print(f'Available modes: {mode_list}')
		mode = str(input('Mode: '))
	else:
		print('Invalid mode.')
		print("Type 'help' to get the mode aliases.")
		mode = str(input('Mode: ')).lower()

mode_index = mode_list.index(mode)        								# convert the alias to the mode's full name
mode = mode_names[mode_index]

wins = int(input(f'{mode} wins: '))										# ask for wincount

if mode == 'Overall':													# overall titles require 2x the wins compared to mode titles
	practical_wins = wins/2												# so divide practical wincount by 2
else:
    practical_wins = wins												# use practical wincount 

wincount = str(wins)[::-1]												# seperate every 3 digits by a comma (e.g. 139,813)
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
	
if div_num != 1:
	if wins == 1:
			print(f'{mode} {div} {div_num} - {wincount} win')			# hide the division number when it's 1
	else:
			print(f'{mode} {div} {div_num} - {wincount} wins')
else:
	if wins == 1:
			print(f'{mode} {div} - {wincount} win')			
	else:
			print(f'{mode} {div} - {wincount} wins')
