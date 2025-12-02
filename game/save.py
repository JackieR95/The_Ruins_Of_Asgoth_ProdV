# Written by: Jacqueline Rael and Github Copilot agent
# Date: 11/30/2025
# Lab: 05

"""Saving and loading helpers.

This module centralizes the game's persistence helpers. It provides a small
``GameState`` convenience class that knows how to serialize the set of
players and minimal dungeon information (merchant inventories, boss lock
state, player position). The serialization format is intentionally small —
only the data required to resume a session is persisted.

Design notes:
- Players are serialized via `Player.save_state` and rehydrated using
  `Player.load_state` to keep item/weapon serialization logic colocated with
  the item implementation.
- Merchant inventories store item dicts (`Item.to_dict`) alongside prices so
  merchant state can be restored reliably.
- File helpers `save_to_file`/`load_from_file` accept paths to make testing
  and temporary saves straightforward.
"""

import json
import os
from .player import Player
from .dungeon import Dungeon
from .items import Item

SAVE_FILE = 'savegame.json'


class GameState:
    """Encapsulate game save/load state and serialization helpers.

    The class provides ``to_dict``/``from_dict`` for in-memory conversion and
    convenience file helpers for writing/reading JSON. Tests should prefer
    the dict forms to avoid filesystem dependencies.
    """

    def __init__(self, players=None, dungeon=None):
        # Ensure `players` is a list for uniform handling elsewhere.
        self.players = [] if players is None else (players if isinstance(players, (list, tuple)) else [players])
        self.dungeon = dungeon

    def to_dict(self) -> dict:
        """Return a JSON-serializable mapping for the current game state.

        The structure includes a list of player snapshots and a small
        ``dungeon`` mapping with boss state and merchant inventories keyed
        by room coordinates (``"x,y"``).
        """
        data = {
            'players': [p.save_state() for p in self.players],
            'pos': getattr(self.dungeon, 'pos', (0, 0)),
            'dungeon': {
                'boss_locked': getattr(self.dungeon, 'boss_locked', True),
                'merchant_inventories': {}
            }
        }

        # Serialize merchant inventories as a mapping of coord -> list[(item_dict, price)].
        for coord, room in getattr(self.dungeon, 'rooms', {}).items():
            if getattr(room, 'merchant', None):
                inv = []
                for it, price in room.merchant.inventory:
                    try:
                        inv.append((it.to_dict(), price))
                    except Exception:
                        # Fallback: best-effort dictionary for unknown item-like objects
                        inv.append(({
                            'name': getattr(it, 'name', str(it)),
                            'kind': getattr(it, 'kind', 'misc'),
                            'effect': getattr(it, 'effect', None)
                        }, price))
                data['dungeon']['merchant_inventories'][f"{coord[0]},{coord[1]}"] = inv
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'GameState':
        """Create a ``GameState`` from its dict representation.

        This method reconstructs `Player` instances using
        `Player.load_state` and repopulates merchant inventories. It prefers
        using `Item.from_dict` for item reconstruction and falls back to a
        simple `Item(name, kind, effect)` when necessary.
        """
        players = [Player.load_state(d) for d in data.get('players', [])]
        dungeon = Dungeon()
        dungeon.pos = tuple(data.get('pos', (0, 0)))
        dungeon.boss_locked = data.get('dungeon', {}).get('boss_locked', True)
        m_invs = data.get('dungeon', {}).get('merchant_inventories', {})

        for coord_str, invlist in m_invs.items():
            x, y = [int(z) for z in coord_str.split(',')]
            room = dungeon.rooms.get((x, y))
            if room and room.merchant:
                room.merchant.inventory = []
                for item_dict, price in invlist:
                    try:
                        room.merchant.inventory.append((Item.from_dict(item_dict), price))
                    except Exception:
                        # Best-effort fallback for legacy or malformed item entries.
                        name = item_dict.get('name') if isinstance(item_dict, dict) else str(item_dict)
                        kind = item_dict.get('kind') if isinstance(item_dict, dict) else 'misc'
                        eff = item_dict.get('effect') if isinstance(item_dict, dict) else None
                        room.merchant.inventory.append((Item(name, kind, eff), price))
        gs = cls(players, dungeon)
        return gs

    def save_to_file(self, path: str = SAVE_FILE) -> None:
        """Write the serialized game state to `path` as JSON."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f)

    @classmethod
    def load_from_file(cls, path: str = SAVE_FILE):
        """Load a game state from `path` and return a `GameState` instance.

        Returns ``None`` when the save file does not exist.
        """
        if not os.path.exists(path):
            return None
        with open(path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


def save_game(players, dungeon):
    """Convenience helper to persist a live `players` + `dungeon` pair.

    This function is intended for interactive use and prints a short
    confirmation message. Tests should prefer using `GameState(...).to_dict()`
    to avoid filesystem I/O.
    """
    gs = GameState(players, dungeon)
    gs.save_to_file(SAVE_FILE)
    print(f'Game saved. ({len(gs.players)} player(s) written)')


def load_game():
    """Convenience helper to load the default save file.

    Returns a tuple ``(players, dungeon)`` on success or ``None`` when no
    save exists. Interactive callers expect the printed status messages.
    """
    gs = GameState.load_from_file(SAVE_FILE)
    if not gs:
        print('No save found.')
        return None
    print('Game loaded.')
    return gs.players, gs.dungeon
