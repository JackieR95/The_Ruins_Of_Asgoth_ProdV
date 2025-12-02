```markdown
# Project TODO (updated)

This file summarizes the current project status after recent refactors, tests, and UX tweaks, and it lists the next recommended actions.

## Summary — What’s Done
- Core gameplay modules refactored for testability and clarity:
  - `game/combat.py`: `CombatManager` wrapper, `player_turn`/`enemy_action` moved into manager methods; I/O injection supported.
  - `game/dungeon.py`: I/O decoupled — handlers accept `input_handler` and `printer`.
  - `game/save.py`: `GameState` save/load encapsulation and round-trip tests.
  - `game/loot.py`: centralized loot/chest generation; statistical tests added.
  - `game/utils.py`: added `prompt_confirm()` and `inventory_to_lines()` helpers.
- Tests: multiple smoke-tests converted to `pytest`, plus focused tests added and passing:
  - `tests/test_combat_edgecases.py`, `tests/test_xp_edgecases.py`, `tests/test_save_roundtrip.py`, `tests/test_merchant_flows.py`, `tests/test_generate_loot_stats.py`.
- UX tweaks applied:
  - CLI movement menu clarified in `main.py`.
  - Combat action menu clarified in `game/combat.py` (multi-line menu and `Action (1-5):` prompt).

## What remains (short list)
- `main.py` is still the interactive CLI and retains many `input()`/`print()` calls. Intentional — keeps a runnable CLI. Consider refactoring to accept `input_handler`/`printer` for full automated UI testing.
- Inventory display: `inventory_to_lines()` helper added, but not all call-sites have been converted (some `main.py` prints and other UI places still show raw `player.inventory`).
- Centralize confirmation prompts: `prompt_confirm()` exists; update all call-sites to use it for consistency.
- Convert remaining legacy smoke harnesses/tests (e.g., `test_run.py`) from `builtins.input` monkeypatch to injected handlers.
- Add `CombatManager`-focused unit tests (multi-turn buff expiry, multi-enemy scenarios).
- Add concise comments and docstrings across modules (you requested starting this next).

## Next recommended actions (priority order)
1. Start adding concise comments/docstrings to core modules (recommended start: `game/combat.py`, `game/dungeon.py`, then `game/items.py`).
2. Centralize inventory display across UI: replace direct prints with `inventory_to_lines()` outputs (start with `main.py`).
3. Convert remaining tests/smoke runners to injected handlers and add `CombatManager` unit tests.
4. Optionally refactor `main.py` into a `GameSession`/CLI wrapper that accepts `input_handler`/`printer`.

## Quick commands
```bash
# Run full tests
pytest -q

# Run only combat tests
pytest -q tests/test_combat_edgecases.py
```

If you want me to start with commenting, say "start commenting" and I will begin with `game/combat.py` and proceed module-by-module, running tests after each change.

``` 
# TODO (current)

This file summarises current priorities and status after recent refactors, tests, and CI additions.

## High Priority — Done
- Tests: combat & XP edge cases — completed (`tests/test_combat_edgecases.py`, `tests/test_xp_edgecases.py`).
- Save API: `GameState` — completed (`game/save.py`, `tests/test_save_roundtrip.py`).
- Dungeon I/O decoupling — completed (`game/dungeon.py` accepts `input_handler` and `printer`).

## Medium Priority — Done
- Centralize loot (`game/loot.py`) — completed and statistical tests added.
- Expand tests: merchant flows + loot stats — completed (`tests/test_merchant_flows.py`, `tests/test_generate_loot_stats.py`).
- Merchant consumables policy — completed (merchants do not resell weapons).

## Low Priority — Current
- Full CombatManager refactor — completed. `player_turn` and `enemy_action` logic moved into `CombatManager` and module wrappers retained.
- UX polish & small tweaks — not started.
  - Merchant prompts and confirmations
  - Inventory display formatting
  - Map legend and room descriptions

## Next recommended actions (pick one)
1. UX polish & small tests (recommended next): implement merchant confirmation flows and add tests that exercise merchant UI via injected handlers.
2. `CombatManager` unit tests: add `tests/test_combat_manager.py` for multi-turn buff expiry and multi-enemy fights.

If you want, I can start on (1) immediately and update `game/dungeon.py` prompts, add tests, and run `pytest -q`.
# Project TODO — concise tracker

Purpose: short, prioritized list showing what is Completed, In Progress, and Next.

Status legend
- DONE: finished and verified
- IN-PROGRESS: currently being worked on
- TODO: not started / optional

Key status (high level)
- DONE: Core gameplay modules (`game/*.py`), starter weapons, save/load basics, smoke-tests converted to pytest examples, combat refactor for injected I/O handlers.
- IN-PROGRESS: Expand unit tests (focused tests for combat, XP, save/load). — initial tests added in `tests/`.
- TODO: polish merchant UX, centralize loot, GameState save API, balance tuning.
 - IN-PROGRESS: Expand unit tests (focused tests for combat, XP, save/load). — initial tests added in `tests/`.
 - DONE: centralize loot into `game/loot.py` and move chest/drop helpers out of `game/items.py`.
 - DONE: encapsulated save/load via `GameState` in `game/save.py` (round-trip test added).
 - TODO: polish merchant UX, balance tuning.

Top next actions (priority order)
1. Tests: add focused unit tests for edge cases
  - Files: `tests/test_xp.py`, `tests/test_items.py`, `tests/test_combat_edgecases.py` (flee/defend/revive). Priority: High.
  - Status: initial edge-case tests added: `tests/test_combat_edgecases.py`, `tests/test_xp_edgecases.py`, `tests/test_save_roundtrip.py`.
2. Dungeon UI decoupling
   - Remove direct `input()`/`print()` from `game/dungeon.py` (merchant, room entry). Allow `input_handler`/`printer`. Priority: High.
3. Save API cleanup
   - Encapsulate save/load with a `GameState` or `Dungeon.save_state()` API; confirm round-trip. Priority: Medium.
4. Loot centralization
  - DONE: `game/loot.py` added and `game/items.py` updated to remove loot generators. Priority: Medium.
5. Playbalance & tuning
   - Run playthrough simulations and document tuning changes (XP curve, encounter rates). Priority: Low.

Tests & dev notes
- Running tests (recommended):
  ```bash
  # activate your venv
  source .venv/bin/activate
  pytest -q
  ```
- Use `pytest -q tests/test_combat.py` to run combat tests only.

If you'd like, I can now implement item (1) or (2). Tell me which and I'll continue.
# Project TODO

This TODO file mirrors the project tracker and shows what has been completed, what is in-progress, and suggested next steps. Edit this file as you work to keep track.

## Status legend
- [x] Completed
- [-] In-progress
- [ ] Not started

## High-level tasks

# Project TODO — Prioritized and Categorized

Purpose: concise, actionable tracker split into High (must), Medium (important), and Low (nice-to-have) priority items.

Notes:
- "High" items are required for correctness, testing, or preventing major bugs.
- "Medium" items improve quality, testability, and maintainability.
- "Low" items are cosmetics, optional features, or small UX tweaks.
- Merchant policy: merchants should sell only consumable items (potions, revives, gold pouches). The code enforces that sold weapons are not added back into merchant inventory.

---

**High Priority — Implement Now**
- Tests: add focused unit tests for combat edge cases (flee/defend/revive), XP split and level-up thresholds.
  - Files: `tests/test_combat_edgecases.py`, `tests/test_xp_edgecases.py`. (Status: initial tests added — passing)
- Save API: encapsulate save/load into `GameState` with round-trip tests.
  - Files: `game/save.py`, `tests/test_save_roundtrip.py`. (Status: implemented)
- Dungeon I/O decoupling: ensure `game/dungeon.py` handlers accept `input_handler` and `printer` for testability.
  - Files: `game/dungeon.py`. (Status: implemented)

**Medium Priority — Important Improvements**
- Centralize loot generation into `game/loot.py` and add distribution/statistical tests.
  - Files: `game/loot.py`, `tests/test_generate_loot_stats.py`. (Status: implemented)
- Expand tests for merchant buy/sell flows and edge cases (inventory-full, insufficient funds, selling junk).
  - Files: `tests/test_merchant_flows.py`. (Status: implemented)
- Combat refactor: add `CombatManager` wrapper and plan full refactor to encapsulate `player_turn` and `enemy_action` as methods.
  - Files: `game/combat.py`. (Status: wrapper added; full refactor TBD)

**Low Priority — Quality of Life / Optional**
- Add GitHub Actions CI to run `pytest` on push/PR (`.github/workflows/python-tests.yml`). (Status: added)
- Merchant UX polish: clearer buy/sell prompts, avoid showing internal objects, add confirmation flows.
- Inventory UI polish: nicer grid display, equip/use confirmations.
- Playbalance tuning: tweak `xp_for_level`, encounter rates, chest probabilities; run simulation harness.

---

Developer notes
- Merchant policy enforced: merchants' initial inventory contains only consumables; selling weapons to merchant will give gold but does not add weapons to merchant stock (prevents weapon resale to players).
- Tests run locally via `pytest -q` (use project venv if present).

Quick commands
```
# activate venv (if used)
source .venv/bin/activate
# run full test suite
pytest -q
```

If you want, I can now: (a) finish the CombatManager full refactor, (b) further expand merchant tests, or (c) add stricter statistical tests for each weapon rarity tier. Which should I do next?
- [ ] Boss/key playthrough: verify players can obtain the boss key, open boss room, and face the Ancient Dragon; validate loot and ending trigger.
