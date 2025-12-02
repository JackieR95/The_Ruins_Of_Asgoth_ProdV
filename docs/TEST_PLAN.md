# Test Plan — Ruins of Asgoth (updated)

This file lists the automated and manual tests to run. It reflects the current state after the recent refactors: I/O decoupling, `GameState` save wrapper, centralized loot, and combat encapsulation.

# Test Plan — Ruins of Asgoth (updated)

This file lists the automated and manual tests to run and reflects the current project state after recent refactors (I/O decoupling, `GameState`, centralized loot, combat encapsulation and UI tweaks).

## Automated tests (pytest)

- Run full test suite:
```bash
pytest -q
```

- Key focused tests (present and passing):
  - `tests/test_combat_edgecases.py` — flee, defend, revive behavior and edge-case outcomes.
  - `tests/test_xp_edgecases.py` — XP split and last-hit leftover logic.
  - `tests/test_save_roundtrip.py` — `GameState` save/load roundtrip using `tmp_path`.
  - `tests/test_merchant_flows.py` — buy/sell flows and merchant policy (consumables-only).
  - `tests/test_generate_loot_stats.py` — statistical verification of loot distributions.

## Suggested additional automated tests (next)

- `tests/test_combat_manager.py` — unit tests targeting `game/combat.py::CombatManager` to validate:
  - multi-turn buff and temporary-effect expiry (defend, temporary stat boosts)
  - enemy action selection across rounds
  - XP/loot distribution after full combat run

- UI flow tests (using injected handlers):
  - merchant confirmation flows (buy/sell with confirmation/reject)
  - inventory-full purchase refusals

## Manual / Interactive tests (checklist)

1. New Game start:
   - Verify starter weapons and a potion are present for new players.
   - Confirm map legend and movement are readable and actions prompt clearly.

2. Inventory limit (30 slots):
   - Fill a player's inventory and verify pick-up and purchase rejections when full.

3. Merchant buy/sell flow:
   - Buy a potion and a Revive Token; verify gold changes.
   - Sell junk items and verify gold (2/5/10 rates).
   - Attempt to sell a super-rare item — should be prevented.

4. Revive & death penalties:
   - Validate revive consumption on death; check death penalties when no revive present.

5. Save/Load:
   - Modify merchant inventory, save, load, and verify merchant inventory and player state are restored.

6. XP & level-up:
   - Test two-player equal-split scenarios and single-survivor full XP scenarios.
   - Verify status line shows per-level `progress/required` values.

7. Boss/key flow (manual QA):
   - Verify boss key acquisition, boss room unlock, boss fight, and end-game triggers.

## Notes for testers
- If tests fail due to I/O, ensure tests inject `input_handler` and `printer` rather than relying on builtins.
- Capture console output and `player.save_state()` for any failing interactive scenario to aid debugging.

## Next testing priorities (short-term)

1. Add `CombatManager` unit tests (low priority but high value for future refactors).
2. Add merchant UI flow tests using injected handlers (next immediate item: UX polish + tests).
3. Convert remaining smoke harnesses to pytest-style tests with injected handlers (e.g., `test_run.py`).

## Quick commands
```bash
# Run full tests
pytest -q

# Run combat tests only
pytest -q tests/test_combat_edgecases.py
```


Automated unit tests
- `pytest` tests were added in `tests/test_xp_distribution.py` and `tests/test_save_load.py` converting key smoke-test scenarios to assert-based unit tests. Run them with `pytest -q` after installing dev requirements.

Static import verification
- A quick import check was run after adding docstrings/comments to core modules; all `game.*` modules imported successfully (no syntax errors).

## Manual / Interactive tests
1. New Game start:
   - Start a new run and verify both players receive starter weapons and a potion.
   - Verify `@` map shows and movement works.

2. Inventory limit (30 slots):
   - Fill a player's inventory to 30 items and attempt to pick up another item from a chest — should be denied.
   - Attempt to buy an item at the merchant when inventory is full — purchase should be refused.

3. Merchant buy/sell flow:
   - At the merchant, buy a potion and a Revive Token (costs 300).
   - Sell junk items (Bronze Scrap / Silver Rock / Gold Clump) and verify gold increases accordingly (2/5/10).
   - Sell a normal weapon and verify price = `level_req * 10`.
   - Attempt to sell a super-rare weapon (rarity <= 0.05) — should be prevented.

4. Revive behavior on death:
   - Give a player a `Revive Token`, die in combat, and verify the revive is consumed and no gold/items lost and death_count not incremented.
   - Die without a revive: verify gold penalty equals death_count (1, then 2, capped at 30) and 1–3 items removed (not super-rare or revive tokens).
   - UI now reports which items were lost on death; verify the printed list matches removed items.

5. Save/Load and merchant persistence:
   - Visit a merchant and buy/sell items, altering the merchant inventory.
   - Save the game, exit, reload via Load Game, and verify merchant inventory is restored and player states (pos, inventory, death_count) rehydrated.
   - Status: Verified — `save_game()` / `load_game()` persist `merchant.inventory` and player state; smoke-tests and an explicit save/load roundtrip confirmed the merchant inventory is restored.

6. XP distribution and display:
   - Verify two-player kills split XP equally when both participated and survived (e.g., 70 XP -> 35/35).
   - Verify a single surviving participant receives full XP when the other is dead or did not join.
   - Verify player status line shows per-level XP progress `progress/required` (e.g., `35/330`).
   - Status: Verified via `test_run.py` scenarios.

6. Loot & chest items:
   - Open chests until you find Bronze/Silver/Gold junk items; verify they are sellable.

7. Edge cases:
   - Sell when index invalid produces informative message.
   - Ensure no super-rare are removed by death or sold.

## Notes for testers
- If any behavior differs from expectations, capture console output and player state (print `player.save_state()`), and report the file and function where it occurs.
