# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

"""Statistical tests for loot generation behavior.

These tests exercise probabilistic behavior (drop rates and type checks).
They use large trial counts and relaxed assertions to avoid flakiness.
"""

import random
from game.loot import generate_loot
from game.items import Weapon


def test_generate_loot_drop_rate():
    # Use a fixed seed to make the test deterministic-ish
    random.seed(0)
    trials = 1000
    drops = 0
    for _ in range(trials):
        l = generate_loot(5)
        if l is not None:
            drops += 1
            assert isinstance(l, Weapon)
    # Expect roughly ~30% drop rate; allow wide tolerance
    assert 150 <= drops <= 450
