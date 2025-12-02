"""Tests covering elite key drops and boss-room key gating.

These tests verify that an elite with `special='elite_key'` awards the
`KEY_ITEM` to the correct player and that the boss room correctly
requires and consumes the key to unlock the boss chamber.
"""

import random

from game.player import Player
from game.creature import Creature
from game.dungeon import Dungeon
from game.items import KEY_ITEM
from main import distribute_xp_loot


def test_elite_awards_key_to_last_hitter():
    random.seed(1)
    p1 = Player('HeroA', 'Warrior')
    p2 = Player('HeroB', 'Mage')
    # ensure deterministic winner: set last_hit on p2
    p1.xp = 0
    p2.xp = 0
    p1.last_hit = False
    p2.last_hit = True

    elite = Creature('Mini Sentinel', 10, hp=1, mp=0, atk=1, defense=0, special='elite_key', xp_value=500)
    distribute_xp_loot(elite, [p1, p2])

    # p2 (last hitter) should have received the KEY_ITEM
    assert any(getattr(it, 'kind', None) == 'key' for it in p2.inventory)


def test_boss_room_unlocks_and_consumes_key(monkeypatch):
    d = Dungeon(4, 4)
    # boss is at (width-1, height-1)
    boss_coord = (d.width - 1, d.height - 1)
    room = d.rooms[boss_coord]

    p = Player('Solo', 'Warrior')
    p.pos = boss_coord
    # give the key to the player
    p.inventory.append(KEY_ITEM)

    # stub out combat so we don't run the full encounter during this test
    def fake_combat(players, monsters, distribute_cb, death_cb, input_handler=None, printer=None):
        # do nothing; this test only asserts unlocking and key consumption
        return None

    monkeypatch.setattr('game.dungeon.combat', fake_combat)
    # ensure distribute_boss_loot won't raise if called; accept optional printer
    def fake_distribute_boss_loot(boss, weapon, players, printer=None):
        return None
    monkeypatch.setattr('game.dungeon.distribute_boss_loot', fake_distribute_boss_loot)

    # call enter_room_for_player; it should detect the key, unlock, and remove it
    d.enter_room_for_player(room, p, [p], distribute_cb=lambda e, ps: None, death_cb=lambda ps: None, input_handler=lambda prompt='': 'n', printer=lambda *a, **k: None)

    assert d.boss_locked is False
    # key should have been removed from inventory
    assert all(getattr(it, 'kind', None) != 'key' for it in p.inventory)


def test_boss_room_requires_key_if_missing(monkeypatch):
    d = Dungeon(4, 4)
    boss_coord = (d.width - 1, d.height - 1)
    room = d.rooms[boss_coord]

    p = Player('NoKey', 'Mage')
    p.pos = boss_coord

    # stub combat again to be safe (should not be called when no key)
    called = {'combat': False}

    def fake_combat(players, monsters, distribute_cb, death_cb, input_handler=None, printer=None):
        called['combat'] = True

    monkeypatch.setattr('game.dungeon.combat', fake_combat)
    # protect distribute_boss_loot in case it's called
    def fake_distribute_boss_loot(boss, weapon, players, printer=None):
        return None
    monkeypatch.setattr('game.dungeon.distribute_boss_loot', fake_distribute_boss_loot)

    # attempt to enter without key
    d.enter_room_for_player(room, p, [p], distribute_cb=lambda e, ps: None, death_cb=lambda ps: None, input_handler=lambda prompt='': 'n', printer=lambda *a, **k: None)

    # boss should remain locked and combat should not have been invoked
    assert d.boss_locked is True
    assert called['combat'] is False
