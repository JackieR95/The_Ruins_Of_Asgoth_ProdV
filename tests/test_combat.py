# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

"""Core combat integration tests covering typical fight flows.

These tests simulate standard fights to validate attack/defend mechanics,
XP awarding and item application during combat.
"""

import builtins
import pytest
from game.player import Player
from game.creature import Creature
from game.combat import combat
from game.items import WEAPONS
from main import distribute_xp_loot


def test_simple_combat_awards_xp():
    # prepare players and starter weapons
    p1 = Player('A', 'Warrior', level=5)
    p2 = Player('B', 'Mage', level=5)
    p1.equipment['weapon'] = WEAPONS['Warrior'][0]
    p2.equipment['weapon'] = WEAPONS['Mage'][0]

    enemy = Creature('Goblin', 5, hp=20, mp=0, atk=1, defense=0, xp_value=40)

    # simulate both players always choose '1' (attack)
    inputs = iter(['1'] * 40)
    fake_input = lambda prompt='': next(inputs, '1')
    # silence printer in tests
    silent = lambda *a, **k: None

    combat([p1, p2], [enemy], distribute_cb=distribute_xp_loot, input_handler=fake_input, printer=silent)

    # at least one player should have gained XP (enemy killed)
    assert any(p.xp > 0 for p in (p1, p2))
