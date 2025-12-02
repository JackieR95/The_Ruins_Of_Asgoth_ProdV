#!/usr/bin/env python3
"""Scripted reproduction of the interactive session: two co-located players,
enter a room with a dead goblin (hp=0). This should trigger the join prompt
and call `distribute_xp_loot`, printing the debug trace added earlier.
"""
from game.dungeon import Room, Dungeon
from game.creature import Creature
from game.player import Player
from main import distribute_xp_loot

# Setup players
p1 = Player('Suzie', 'Warrior')
p2 = Player('Nomi', 'Mage')
# place both in same room (0,1)
p1.pos = (0,1)
p2.pos = (0,1)

# Create room with a dead goblin (hp=0) worth 100 XP
room = Room(0,1)
goblin = Creature('Goblin', 3, hp=0, mp=0, atk=5, defense=1, xp_value=100)
room.monsters = [goblin]

# Input handler: always say 'y' to join prompts
def input_handler(prompt=''):
    print(prompt, end='')
    return 'y'

# Printer collects and prints messages
def printer(msg=''):
    print(msg)

# Make a small dungeon for context
d = Dungeon(3,3)

print('\n--- Starting scripted reproduction ---\n')
d.enter_room_for_player(room, p1, [p1, p2], distribute_cb=distribute_xp_loot, death_cb=lambda ps: None, input_handler=input_handler, printer=printer)

print('\nPlayers after encounter:')
for pl in [p1, p2]:
    print(f"{pl.name} XP={pl.xp} Gold={pl.gold} Pos={pl.pos} Alive={pl.is_alive()}")

print('\n--- End reproduction ---')
