"""Test that adjacent/co-located teammates are prompted to join and XP is split.

This test uses injectable `input_handler` and `printer` to simulate a
player entering a room with another teammate nearby. The monster has
an `xp_value` so we can assert XP split behavior deterministically.
"""

from game.dungeon import Room, Dungeon
from game.creature import Creature
from game.player import Player
from main import distribute_xp_loot


def test_join_prompt_and_xp_split():
    # Setup two players co-located at (0,1)
    p1 = Player('HeroA', 'Warrior')
    p2 = Player('HeroB', 'Mage')
    p1.pos = (0, 1)
    p2.pos = (0, 1)

    # Create a room at that position with a single monster worth 100 XP
    room = Room(0, 1)
    monster = Creature('Test Goblin', 1, hp=0, mp=0, atk=1, defense=0, xp_value=100)
    room.monsters = [monster]

    # Simple input handler that always answers 'y' to join prompts
    inputs = iter(['y'])
    def input_handler(prompt=''):
        try:
            return next(inputs)
        except StopIteration:
            return ''

    outputs = []
    def printer(msg=''):
        outputs.append(str(msg))

    # Call enter_room_for_player which should prompt and then distribute XP
    dungeon = Dungeon(3, 3)
    # We call the function directly to avoid full game loop complexity
    dungeon.enter_room_for_player(room, p1, [p1, p2], distribute_cb=distribute_xp_loot, death_cb=lambda ps: None, input_handler=input_handler, printer=printer)

    # Both players should have received half the XP (50 each)
    assert p1.xp == 50
    assert p2.xp == 50

    # The printer should have been called with a join prompt
    assert any('Join' in o or 'join' in o.lower() for o in outputs)
