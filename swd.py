#!/usr/bin/env python3
#
#  swd.py
#  
#  Copyright 2024 poki95
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#

import math

mode_list = ['oa', 'uhc', 'sw', 'mw', 'blitz', 'op', 'classic', 'bow', 'ndb', 'combo', 'tnt', 'sumo', 'bridge', 'pkd', 'boxing']
div_list = ['ASCENDED', 'DIVINE', 'CELESTIAL', 'Godlike', 'Grandmaster', 'Legend', 'Master', 'Diamond', 'Gold', 'Iron', 'Rookie', 'None']
div_req = [100000, 50000, 25000, 10000, 5000, 2000, 1000, 500, 250, 100, 50, 0]
div_step = [10000, 10000, 5000, 3000, 1000, 600, 200, 100, 50, 30, 10, 1]

div_number = 0

mode = str(input('Mode: ')).lower()
while mode == 'list':
	print(mode_list)
	mode = str(input('Mode: '))

wins = int(input(f'{mode} wins: '))

if mode == 'oa':
	practical_wins = wins/2

for req in div_req:
	if wins >= req:
		div = div_list[div_number]
		surplus = wins - (req - div_step[div_number])
		div_num = math.floor(surplus/div_step[div_number])
		break
	div_number += 1

print(f'{mode} {div} {div_num}')
	
'''
if wins >= 100000: # ASCENDED
	surplus = wins - 90000
	number = math.floor(surplus/10000)
	print(f'{mode} ASCENDED {number}') 
elif wins >= 50000: # DIVINE
	surplus = wins - 40000
	number = math.floor(surplus/10000)
	print(f'{mode} DIVINE {number}')
elif wins >= 25000: # CELESTIAL
	surplus = wins - 20000
	number = math.floor(surplus/5000)
	print(f'{mode} CELESTIAL {number}')
elif wins >= 10000: # Godlike
	surplus = wins - 7000
	number = math.floor(surplus/3000)
	print(f'{mode} Godlike {number}')
elif wins >= 5000: # Grandmaster
	surplus = wins - 4000
	number = math.floor(surplus/1000)
	print(f'{mode} Grandmaster {number}')
elif wins >= 2000: # Legend
	surplus = wins - 1400
	number = math.floor(surplus/600)
	print(f'{mode} Legend {number}')
elif wins >= 1000: # Master
	surplus = wins - 800
	number = math.floor(surplus/200)
	print(f'{mode} Master {number}')
elif wins >= 500: # Diamond
	surplus = wins - 400
	number = math.floor(surplus/100)
	print(f'{mode} Diamond {number}')
elif wins >= 250: # Gold
	surplus = wins - 200
	number = math.floor(surplus/50)
	print(f'{mode} Gold {number}')
elif wins >= 100: # Iron
	surplus = wins - 90
	number = math.floor(surplus/30)
	print(f'{mode} Iron {number}')
elif wins >= 50: # Rookie
	surplus = wins - 40
	number = math.floor(surplus/10)
	print(f'{mode} Rookie {number}')
elif wins < 50: # None
	print(f'{mode} None')
'''
