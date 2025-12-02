# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

"""Edge-case combat tests.

Contains small tests exercising flee/defend/revive and other
rare combat behaviors that are important to keep deterministic.
"""

from game.player import Player
from game.creature import Creature
from game.combat import combat


def test_player_flees_stops_distribution():
    p = Player('Solo', 'Warrior', level=5)
    e = Creature('Test Goblin', 5, hp=40, mp=0, atk=2, defense=1, xp_value=50)

    inputs = iter(['5'])
    def fake_input(prompt=''):
        return next(inputs, '5')
    called = {'distributed': False}

    def distribute_cb(enemy, players):
        called['distributed'] = True

    # silent printer to avoid clutter
    silent = lambda *a, **k: None

    combat([p], [e], distribute_cb=distribute_cb, input_handler=fake_input, printer=silent)
    # Because player fled, distribute_cb should not have been called
    assert called['distributed'] is False


def test_defend_increases_defense():
    p = Player('Defender', 'Warrior', level=5)
    """Edge-case tests for combat: flee/defend/revive and combat flows.

    These tests exercise less common combat behaviors to ensure the combat
    loop is robust under unexpected inputs and edge cases.
    """

    before = p.defense
    inputs = iter(['2'])
    def fake_input(prompt=''):
        return next(inputs, '2')
    silent = lambda *a, **k: None
    # Call player_turn directly to test defend action
    from game.combat import player_turn
    player_turn(p, [], input_handler=fake_input, printer=silent)
    assert p.defense == before + 3
