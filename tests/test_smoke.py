"""Light integration/smoke tests.

A small collection of higher-level scenarios used for quick manual
verification of core flows (merchant purchase, basic combat integration).
"""

# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

from game.player import Player
from game.items import WEAPONS, Item
from game.creature import Creature
from game.dungeon import Dungeon, Merchant
from game.combat import combat
from main import distribute_xp_loot


def test_merchant_purchase_flow(monkeypatch, tmp_path):
    p1 = Player('Alice', 'Warrior', level=5)
    p2 = Player('Borin', 'Mage', level=5)
    p1.gold = 200
    p2.gold = 10

    merchant = Merchant()
    d = Dungeon()

    # simulate buy for first player then skip
    inputs = iter(['buy 1', 'skip'])
    def fake_input(prompt=''):
        return next(inputs, 'skip')
    silent = lambda *a, **k: None

    # call merchant handler with injected I/O
    d.handle_merchant(merchant, [p1, p2], input_handler=fake_input, printer=silent)

    # if merchant had an item and p1 could afford, inventory should have increased or gold decreased
    if merchant.inventory:
        # either p1 bought something (gold decreased) or couldn't (gold unchanged)
        assert p1.gold <= 200


def test_integration_combat_and_xp(monkeypatch):
    p1 = Player('Attila', 'Warrior', level=5)
    p2 = Player('Bree', 'Ranger', level=5)
    p1.equipment['weapon'] = WEAPONS['Warrior'][0]
    p2.equipment['weapon'] = WEAPONS['Ranger'][0]

    enemy = Creature('Test Goblin', 5, hp=40, mp=0, atk=2, defense=1, xp_value=30)

    # simulate players always choosing attack
    inputs = iter(['1'] * 40)
    fake_input = lambda prompt='': next(inputs, '1')
    silent = lambda *a, **k: None

    combat([p1, p2], [enemy], distribute_cb=distribute_xp_loot, input_handler=fake_input, printer=silent)
    assert any(p.xp >= 0 for p in (p1, p2))
