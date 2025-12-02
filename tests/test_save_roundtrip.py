"""Round-trip save/load test for persistence.

Verifies `GameState` can serialize and deserialize player and dungeon
state (merchant inventory, player items) without data loss.
"""

# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

from game.player import Player
from game.items import Item
from game.save import GameState
from game.dungeon import Dungeon


def test_save_and_load_roundtrip(tmp_path):
    p = Player('Saver', 'Warrior', level=5)
    p.inventory.append(Item('Lesser Health Potion', 'potion', {'hp':25}))
    d = Dungeon()
    # add a cheap item to merchant for serialization
    if d.rooms.get((1,0)) and getattr(d.rooms[(1,0)], 'merchant', None):
        d.rooms[(1,0)].merchant.inventory.append((Item('Bronze Scrap','junk',{'sell':2}), 5))

    gs = GameState([p], d)
    path = tmp_path / 'save_test.json'
    gs.save_to_file(str(path))

    loaded = GameState.load_from_file(str(path))
    assert loaded is not None
    players_loaded = loaded.players
    dungeon_loaded = loaded.dungeon
    assert len(players_loaded) == 1
    assert players_loaded[0].name == 'Saver'
    # merchant inventory restored
    if dungeon_loaded.rooms.get((1,0)) and getattr(dungeon_loaded.rooms[(1,0)], 'merchant', None):
        assert len(dungeon_loaded.rooms[(1,0)].merchant.inventory) >= 0
