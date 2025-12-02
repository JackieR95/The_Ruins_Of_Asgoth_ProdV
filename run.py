#!/usr/bin/env python3
"""Safe launcher for the Ruins of Asgoth game.

Use this instead of `python3 game.py` to avoid the top-level `game.py`
script shadowing the `game/` package when running from the project root.

Run with:
    python3 run.py
or
    PYTHONPATH=. python3 run.py
"""

from main import game_loop

if __name__ == '__main__':
    game_loop()
