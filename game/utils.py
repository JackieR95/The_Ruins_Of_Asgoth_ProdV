# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

"""Small utilities and game-wide constants.

This module collects lightweight helpers used across the codebase so the
public game logic can stay focused on rules and flow. Typical contents are
constants (caps, tuning knobs), small random helpers, and UI formatting
helpers that should be stable and testable.

Keep functions deterministic where possible and accept injected IO
callables (`printer`, `input_handler`) to make unit tests robust without
patching builtins.
"""

import random
from typing import Iterable, List

# Gameplay constants
MAX_LEVEL = 25
BOSS_LEVEL = 25

# Enemy targeting mode: 'random' (default) or 'weakest' (target lowest HP)
ENEMY_TARGET_MODE = 'random'


def rnd(a, b=None):
    """Small wrapper around Python's ``random``.

    Usage:
    - ``rnd(a, b)`` -> returns a random integer in the inclusive range
      ``[a, b]`` using ``random.randint``.
    - ``rnd(a)`` or ``rnd()`` -> legacy behavior preserved: when ``b`` is
      ``None`` it returns ``random.random()`` (a float in [0.0, 1.0)). Some
      older code relies on that behavior, so keep it here for compatibility.
    """
    if b is None:
        return random.random()
    return random.randint(a, b)


def xp_for_level(lvl: int) -> int:
    """Return the cumulative XP threshold required to reach ``lvl``.

    The XP curve is intentionally simple (quadratic) and uses a multiplier
    to tune pacing. Adjust the multiplier to globally speed up or slow down
    leveling during playtests.
    """
    return 30 * (lvl ** 2)


def alive_entities(seq: Iterable) -> List:
    """Filter ``seq`` and return only entities where ``is_alive()`` is True.

    The helper tolerates objects missing an ``is_alive`` method by assuming
    they are alive (useful for tests and mixed sequences).
    """
    return [e for e in seq if getattr(e, 'is_alive', lambda: True)()]


def prompt_confirm(prompt: str, input_handler=input, printer=print, default: bool = False) -> bool:
    """Ask a yes/no confirmation and return True/False.

    Parameters:
    - ``prompt``: message shown to the user via ``printer``.
    - ``input_handler``: function called to read user input (defaults to
      the builtin ``input``). Tests should pass a fake handler to simulate
      responses.
    - ``printer``: function used to display the prompt; injected for tests.
    - ``default``: boolean returned when input is empty or on input errors.

    The function treats any input starting with ``'y'`` (case-insensitive)
    as confirmation.
    """
    printer(prompt)
    try:
        ans = input_handler('> ').strip().lower()
    except Exception:
        return default
    if not ans:
        return default
    return ans.startswith('y')


def inventory_to_lines(items: Iterable, include_index: bool = True) -> List[str]:
    """Return formatted lines representing ``items`` for display.

    This centralizes inventory formatting so the UI is consistent across
    menus and tests. Each item is converted with ``str(item)`` so item
    classes control their display formatting.

    Args:
        items: iterable of inventory entries (objects or strings).
        include_index: when True, prefix lines with a 1-based index.

    Returns:
        A list of strings, one per inventory entry, ready to be printed.
    """
    lines: List[str] = []
    for i, it in enumerate(items, 1):
        if include_index:
            lines.append(f"{i}) {it}")
        else:
            lines.append(f"{it}")
    return lines
