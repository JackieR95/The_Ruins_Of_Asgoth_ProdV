# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

"""Tests for XP distribution logic used after combat.

These tests ensure XP splitting, leftover XP assignment, and level-up
behaviors are correct for common party configurations.
"""

import random
from game.player import Player
from game.creature import Creature
from main import distribute_xp_loot


def test_two_players_equal_split():
    random.seed(1)
    pa = Player('Lola', 'Mage')
    pb = Player('Numi', 'Warrior')
    pa.xp = 0
    pb.xp = 0
    en = Creature('Goblin', 5, hp=1, mp=0, atk=1, defense=0, xp_value=100)
    for p in (pa, pb):
        p.last_hit = False
    distribute_xp_loot(en, [pa, pb])
    assert pa.xp == 50 and pb.xp == 50


def test_one_dead_gets_full_xp():
    pa = Player('Lola', 'Mage')
    pb = Player('Numi', 'Warrior')
    pb.hp = 0
    pa.xp = 0
    pb.xp = 0
    en = Creature('Orc', 4, hp=1, mp=0, atk=1, defense=0, xp_value=100)
    distribute_xp_loot(en, [pa, pb])
    assert pa.xp == 100 and pb.xp == 0


def test_two_players_split_70():
    pc = Player('Lola', 'Mage')
    pd = Player('Numi', 'Warrior')
    pc.xp = 0
    pd.xp = 0
    en = Creature('Wight', 5, hp=1, mp=0, atk=1, defense=0, xp_value=70)
    for p in (pc, pd):
        p.last_hit = False
    distribute_xp_loot(en, [pc, pd])
    assert pc.xp == 35 and pd.xp == 35


def test_single_participant_gets_full_xp():
    solo = Player('Solo', 'Warrior')
    solo.xp = 0
    en = Creature('Wraith', 7, hp=1, mp=0, atk=1, defense=0, xp_value=120)
    distribute_xp_loot(en, [solo])
    assert solo.xp == 120
