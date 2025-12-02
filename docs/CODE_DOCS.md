Code & Module Summary (short)
================================

Short purpose summary for each major module and notable recent changes:

- `game/items.py` — Item and `Weapon` dataclasses, serialization helpers. Loot generation has been moved to `game/loot.py` to keep `items.py` focused on data structures and (de)serialization.
- `game/player.py` — `Player` state and inventory management, equip/unequip logic, level-up and death/revive behavior. Save/load rehydration is supported via `to_dict`/`from_dict` helpers.
- `game/creature.py` — `Creature` class (HP/MP/atk/def/xp_value). Small and focused; consider `to_dict`/`from_dict` if you need to persist creatures.
- `game/combat.py` — Turn-based combat. Refactor highlights:
	- `CombatManager` encapsulates combat state and loop.
	- `player_turn` and `enemy_action` are implemented as methods that use injected `input_handler` and `printer` for testability.
	- Combat menu formatting improved (multi-line menu and `Action (1-5):` prompt).
- `game/dungeon.py` — Dungeon grid, room events, merchants and chests. Handlers now accept `input_handler` and `printer` so tests can inject deterministic inputs. Merchant policy enforces consumables-only stock.
- `game/save.py` — Save/load helpers and `GameState` wrapper. Round-trip tests added to ensure fidelity.
- `game/loot.py` — Centralized loot and chest generation functions. Statistical tests added to validate drop distributions.
- `game/utils.py` — Small helpers and global constants. New helpers include:
	- `prompt_confirm(prompt, input_handler, printer, default)` — consistent yes/no prompt across UI.
	- `inventory_to_lines(items, include_index=True)` — centralizes inventory formatting for UI.

- `main.py` — CLI runner and UI glue. Intentionally retains direct `input()`/`print()` to remain a usable CLI; consider refactoring to accept injected handlers for full automated UI testing.

Recommended documentation actions
- Add module-level docstrings (1–3 lines) and short function docstrings to clarify non-obvious behavior (XP split rules, loot weighting, save format).
- For commenting work: start with `game/combat.py` (combat flow and XP distribution), then `game/dungeon.py` (room flow and merchant rules), then `game/items.py` and `game/save.py`.

If you want, I can start adding docstrings and inline comments — tell me which module to begin with and I'll patch it and run tests after each change.
