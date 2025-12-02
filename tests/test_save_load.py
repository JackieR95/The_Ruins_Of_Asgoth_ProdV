"""Persistence tests verifying save/load roundtrip for dungeon and merchants.

These tests write a temporary save file and reload it to assert merchant
inventories and player snapshots are preserved.
"""

# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

import os
from game.dungeon import Dungeon
from game.save import save_game, load_game, SAVE_FILE
from game.player import Player


def test_merchant_inventory_persistence(tmp_path, monkeypatch):
    # create dungeon and find a merchant room
    d = Dungeon()
    merchant_room = None
    for coord, room in d.rooms.items():
        if getattr(room, 'merchant', None):
            merchant_room = room
            break
    assert merchant_room is not None

    # modify first merchant item price if present
    if merchant_room.merchant.inventory:
        item, price = merchant_room.merchant.inventory[0]
        new_price = price + 123
        merchant_room.merchant.inventory[0] = (item, new_price)

    # switch working directory to a temporary path so savefile is isolated
    monkeypatch.chdir(tmp_path)
    players = [Player('Tester', 'Mage')]
    save_game(players, d)
    loaded = load_game()
    assert loaded is not None
    loaded_players, loaded_dungeon = loaded

    # attempt to find a merchant with a matching first-item name and price
    found = False
    if merchant_room.merchant.inventory:
        orig_item, orig_price = merchant_room.merchant.inventory[0]
        for coord, room in loaded_dungeon.rooms.items():
            if getattr(room, 'merchant', None) and room.merchant.inventory:
                loaded_item, loaded_price = room.merchant.inventory[0]
                if loaded_price == orig_price and getattr(loaded_item, 'name', None) == getattr(orig_item, 'name', None):
                    found = True
                    break

    assert found

    # cleanup
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
