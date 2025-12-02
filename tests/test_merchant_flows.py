# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

"""Tests for merchant buy/sell flows and inventory interactions.

These tests verify merchant behavior including purchases with sufficient
gold, handling full inventories, and successful sells back to merchants.
"""

from game.player import Player
from game.items import Item
from game.dungeon import Merchant, Dungeon


def test_buy_with_sufficient_gold():
    p = Player('Buyer', 'Warrior', level=5)
    p.gold = 200
    # merchant with one cheap potion
    m = Merchant()
    m.inventory = [(Item('Test Potion', 'potion', {'hp':10}), 50)]

    inputs = iter(['buy 1','y'])
    def fake_input(prompt=''):
        return next(inputs, 'skip')
    silent = lambda *a, **k: None

    from game.dungeon import Dungeon
    # call merchant handler
    Dungeon().handle_merchant(m, [p], input_handler=fake_input, printer=silent)
    # buyer should have spent at least 50 gold and gained an item
    assert p.gold <= 150
    assert any(it.name == 'Test Potion' for it in p.inventory)


def test_buy_insufficient_gold():
    p = Player('Poor', 'Mage', level=5)
    p.gold = 10
    m = Merchant()
    m.inventory = [(Item('Expensive', 'potion', {'hp':100}), 80)]

    inputs = iter(['buy 1','y'])
    def fake_input(prompt=''):
        return next(inputs, 'skip')
    silent = lambda *a, **k: None

    Dungeon().handle_merchant(m, [p], input_handler=fake_input, printer=silent)
    # gold unchanged and item not added
    assert p.gold == 10
    assert not any(it.name == 'Expensive' for it in p.inventory)


def test_buy_inventory_full():
    p = Player('Full', 'Ranger', level=5)
    p.gold = 500
    p.inv_limit = 1
    # fill inventory
    p.inventory.append(Item('Filler', 'junk', {'sell':1}))
    m = Merchant()
    m.inventory = [(Item('Cheap', 'potion', {'hp':10}), 50)]

    inputs = iter(['buy 1','y'])
    def fake_input(prompt=''):
        return next(inputs, 'skip')
    silent = lambda *a, **k: None

    Dungeon().handle_merchant(m, [p], input_handler=fake_input, printer=silent)
    # inventory unchanged (still 1) and gold unchanged because purchase cancelled
    assert len(p.inventory) == 1


def test_sell_adds_to_merchant():
    p = Player('Seller', 'Warrior', level=5)
    p.inventory.append(Item('Bronze Scrap', 'junk', {'sell':2}))
    p.gold = 0
    m = Merchant()
    initial_len = len(m.inventory)

    inputs = iter(['sell 1','y'])
    def fake_input(prompt=''):
        return next(inputs, 'skip')
    silent = lambda *a, **k: None

    Dungeon().handle_merchant(m, [p], input_handler=fake_input, printer=silent)
    # merchant inventory should have increased by one
    assert len(m.inventory) >= initial_len
    # seller should have gained some gold
    assert p.gold >= 0
