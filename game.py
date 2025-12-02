#!/usr/bin/env python3
# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05
"""Entry-point launcher for the Ruins Of Asgoth.

This module provides a tiny executable wrapper so the game can be started
via ``python3 game.py``. It intentionally keeps logic minimal — the main
interactive behavior lives in ``main.py``. The wrapper attempts to call a
``main_menu`` function if present (useful for future menu-driven runners)
and falls back to the existing ``game_loop`` function.

Design intent:
- Keep this module small and non-opinionated so tests and imports do not
  accidentally execute the full game loop. It only runs when invoked as
  a script (``__main__``).
"""


def _run():
    try:
        from main import main_menu
        main_menu()
    except Exception:
        # Fallback: run the simpler loop for interactive play
        from main import game_loop
        while True:
            result = game_loop()
            if result == 'restart':
                continue
            break


if __name__ == '__main__':
    _run()
