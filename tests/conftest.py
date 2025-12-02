"""Test fixtures and test environment setup for pytest.

Provides common fixtures (`players`, `dungeon`) and ensures the
project root is on `sys.path` so `import game` works during test runs.
"""

# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

import os
import sys
import pytest

# Ensure project root is on sys.path so `import game` works when pytest runs
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from game.player import Player
from game.dungeon import Dungeon


@pytest.fixture
def players():
    return [Player('Alice', 'Warrior', level=5), Player('Borin', 'Mage', level=5)]


@pytest.fixture
def dungeon():
    return Dungeon()
