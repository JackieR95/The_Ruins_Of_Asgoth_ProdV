"""Automated smoke-test runner.

This script simulates a simple combat scenario without user interaction by
patching `input()` to provide predetermined choices. It creates two players,
one enemy, and performs a combat to verify the modules interoperate.
"""

# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

import builtins
import random
from game.player import Player
from game.items import WEAPONS
from game.creature import Creature
from game.combat import combat

# deterministic seed for repeatability
random.seed(1)

enemy = Creature('Goblin', 5, hp=60, mp=10, atk=8, defense=2, xp_value=40)
enemies = [enemy]
# ---------- Test 1: Combat + XP distribution ----------
# prepare players
p1 = Player('Alice', 'Warrior', level=5)
p2 = Player('Borin', 'Mage', level=5)
# give starter weapons
starter1 = WEAPONS['Warrior'][0]
starter2 = WEAPONS['Mage'][0]
p1.equipment['weapon'] = starter1
p2.equipment['weapon'] = starter2

# single enemy near player level
enemy = Creature('Goblin', 5, hp=60, mp=10, atk=8, defense=2, xp_value=40)
enemies = [enemy]

# simulate input sequence: both players always '1' to attack, and target '1'
responses = []
for _ in range(20):
    responses.append('1')
    responses.append('1')

resp_iter = iter(responses)
orig_input = builtins.input
builtins.input = lambda prompt='': next(resp_iter, '1')

try:
    print('Starting automated combat + XP distribution test...')
    # import distribution callback from main so XP is applied
    from main import distribute_xp_loot
    combat([p1, p2], enemies, distribute_cb=distribute_xp_loot)
    print('Combat finished. Verifying XP was awarded:')
    for p in [p1, p2]:
        print(f'- {p.name}: XP {p.xp}, Level {p.level}')
finally:
    builtins.input = orig_input

# ---------- Test 2: Merchant room purchase ----------
print('\nStarting merchant room test...')
from game.dungeon import Merchant
from game.items import Item

# give players some gold to buy
p1.gold = 200
p2.gold = 10

merchant = Merchant()
print('Merchant inventory:', merchant.inventory)

# Simulate buying: first player will 'buy 1', second will 'skip'
resp_iter = iter(['buy 1', 'skip'])
builtins.input = lambda prompt='': next(resp_iter, 'skip')
try:
    # call handle_merchant directly
    from game.dungeon import Dungeon
    d = Dungeon()
    d.handle_merchant(merchant, [p1, p2])
    print('Post-merchant player states:')
    for p in [p1, p2]:
        print(f'- {p.name}: Gold {p.gold}, Inventory {p.inventory}')
finally:
    builtins.input = orig_input

print('\nAll automated tests complete.')

# ---------- Test 3: Adjacent player join behavior ----------
print('\nStarting adjacent-join test...')
from game.dungeon import Dungeon

# create fresh players and dungeon
pa = Player('Attila', 'Warrior', level=5)
pb = Player('Bree', 'Ranger', level=5)
pa.equipment['weapon'] = WEAPONS['Warrior'][0]
pb.equipment['weapon'] = WEAPONS['Ranger'][0]

# positions: pa will be at (0,1); pb at (0,0) is adjacent
pa.pos = (0,1)
pb.pos = (0,0)

d = Dungeon()
# place a single monster in room (0,1)
room = d.rooms[(0,1)]
room.monsters = [Creature('Test Goblin', 5, hp=50, mp=10, atk=7, defense=2, xp_value=30)]

# prepare responses: first prompt is join? for adjacent player pb -> 'y',
# then combat actions: players choose attack '1' and target '1'
responses = ['y']
for _ in range(20):
    responses.append('1')
    responses.append('1')

resp_iter = iter(responses)
builtins.input = lambda prompt='': next(resp_iter, '1')
try:
    # call enter_room_for_player which should prompt pb to join and then run combat
    d.enter_room_for_player(room, pa, [pa, pb], distribute_cb=lambda e, ps: print('distributed xp for', e.name), death_cb=lambda ps: None)
    print('After join-combat, player positions and HP:')
    print(f'- {pa.name}: pos={pa.pos} HP={pa.hp}/{pa.max_hp}')
    print(f'- {pb.name}: pos={pb.pos} HP={pb.hp}/{pb.max_hp}')
finally:
    builtins.input = orig_input

print('Adjacent-join test complete.')

# ---------- Test 4: XP distribution scenarios (unit-like checks)
print('\nStarting XP distribution scenarios...')
from main import distribute_xp_loot

def _print_xp(players):
    for p in players:
        status = 'alive' if p.is_alive() else 'dead'
        print(f'- {p.name}: XP={p.xp} ({status})')

random.seed(1)
print('\nScenario A: Two players involved, both alive (equal split expected)')
pa = Player('Lola','Mage')
pb = Player('Numi','Warrior')
en = Creature('Goblin', 5, hp=1, mp=0, atk=1, defense=0, xp_value=100)
for p in (pa, pb):
    p.xp = 0
    p.last_hit = False
print('Before:')
_print_xp([pa, pb])
distribute_xp_loot(en, [pa, pb])
print('After:')
_print_xp([pa, pb])

print('\nScenario B: Two players, one dead (single survivor gets full XP)')
pa = Player('Lola','Mage')
pb = Player('Numi','Warrior')
pb.hp = 0
pa.xp = 0
pb.xp = 0
en = Creature('Orc', 4, hp=1, mp=0, atk=1, defense=0, xp_value=100)
distribute_xp_loot(en, [pa, pb])
_print_xp([pa, pb])

print('\nScenario C: Two players involved, both alive, enemy gives 70 XP (split 35/35)')
pc = Player('Lola','Mage')
pd = Player('Numi','Warrior')
pc.xp = 0
pd.xp = 0
en = Creature('Wight', 5, hp=1, mp=0, atk=1, defense=0, xp_value=70)
for p in (pc, pd):
    p.last_hit = False
distribute_xp_loot(en, [pc, pd])
_print_xp([pc, pd])

print('\nScenario D: Single participant gets full XP')
solo = Player('Solo','Warrior')
solo.xp = 0
en = Creature('Wraith', 7, hp=1, mp=0, atk=1, defense=0, xp_value=120)
distribute_xp_loot(en, [solo])
_print_xp([solo])

print('XP distribution scenarios complete.')
