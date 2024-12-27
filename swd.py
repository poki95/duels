import math

mode_list = ['oa', 'uhc', 'sw', 'mw', 'blitz', 'op', 'classic', 'bow', 'ndb', 'combo', 'tnt', 'sumo', 'bridge', 'pkd', 'boxing']
mode_names = ['Overall', 'UHC', 'SkyWars', 'MW', 'Blitz', 'OP', 'Classic', 'Bow', 'NoDebuff', 'Combo', 'TNT', 'Sumo', 'Bridge', 'Parkour', 'Boxing']
div_list = ['ASCENDED', 'DIVINE', 'CELESTIAL', 'Godlike', 'Grandmaster', 'Legend', 'Master', 'Diamond', 'Gold', 'Iron', 'Rookie', 'None']
div_req = [100000, 50000, 25000, 10000, 5000, 2000, 1000, 500, 250, 100, 50, 0]
div_step = [10000, 10000, 5000, 3000, 1000, 600, 200, 100, 50, 30, 10, 1]

div_number = 0

mode = str(input('Mode: ')).lower()
while mode == 'list':
	print(mode_list)
	mode = str(input('Mode: '))

mode_index = mode_list.index(mode)
mode = mode_names[mode_index]

wins = int(input(f'{mode} wins: '))

if mode == 'Overall':
	practical_wins = wins/2
else:
    practical_wins = wins

for req in div_req:
	if practical_wins >= req:
		div = div_list[div_number]
		surplus = practical_wins - (req - div_step[div_number])
		div_num = math.floor(surplus/div_step[div_number])
		break
	div_number += 1

print(f'{mode} {div} {div_num}')
