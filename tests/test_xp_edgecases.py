
"""XP edge-case tests.

Validates XP-splitting rules and leftover assignment (last-hit behavior)
under small-party scenarios.
"""

# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

from game.player import Player
from game.creature import Creature
from main import distribute_xp_loot


def test_two_player_xp_split_equal():
    p1 = Player('A', 'Warrior', level=5)
    p2 = Player('B', 'Mage', level=5)
    enemy = Creature('Test Goblin', 5, hp=0, mp=0, atk=0, defense=0, xp_value=31)
    # both alive and no last_hit -> logic will split equally among alive
    distribute_xp_loot(enemy, [p1, p2])
    # base_xp 31 -> 31//2 = 15 each, leftover 1 goes to winner (random or last_hit)
    # ensure both have at least 15 XP
    assert p1.xp >= 15 and p2.xp >= 15


def test_last_hit_gets_leftover():
    p1 = Player('A', 'Warrior', level=5)
    p2 = Player('B', 'Mage', level=5)
    enemy = Creature('Test Goblin', 5, hp=0, mp=0, atk=0, defense=0, xp_value=31)
    p1.last_hit = True
    distribute_xp_loot(enemy, [p1, p2])
    # p1 should have at least 16 (15 + leftover)
    assert p1.xp >= 16
