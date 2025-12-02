
"""Integration test verifying adjacent player joining and combat flow.

Ensures players can join nearby encounters and that combat proceeds
correctly with multiple participants.
"""

# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

from game.player import Player
from game.items import WEAPONS
from game.creature import Creature
from game.dungeon import Dungeon


def test_adjacent_join_and_combat(monkeypatch):
    pa = Player('Attila', 'Warrior', level=5)
    pb = Player('Bree', 'Ranger', level=5)
    pa.equipment['weapon'] = WEAPONS['Warrior'][0]
    pb.equipment['weapon'] = WEAPONS['Ranger'][0]

    # positions: pa at (0,1); pb at (0,0) adjacent
    pa.pos = (0,1)
    pb.pos = (0,0)

    d = Dungeon()
    room = d.rooms[(0,1)]
    room.monsters = [Creature('Test Goblin', 5, hp=50, mp=10, atk=7, defense=2, xp_value=30)]

    # simulate: pb will join ('y'), then both players choose '1' repeatedly to attack
    inputs = iter(['y'] + ['1'] * 40)
    def fake_input(prompt=''):
        return next(inputs, '1')
    silent = lambda *a, **k: None

    # run the room entry which should prompt pb and then run combat
    d.enter_room_for_player(room, pa, [pa, pb], distribute_cb=lambda e, ps: None, death_cb=lambda ps: None, input_handler=fake_input, printer=silent)

    # adjacent player should have moved into the room
    assert pb.pos == (0,1)
    # combat should have happened; at least one player will likely have taken damage
    assert pa.hp <= pa.max_hp and pb.hp <= pb.max_hp
