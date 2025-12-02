## File issues & action items (concise)

Purpose: quick, actionable per-file notes. Each item is short: what, status, and next step.

- `game/combat.py`
  - Status: DONE (core turn logic encapsulated in `CombatManager`, I/O injection added).
  - Next: add `CombatManager`-targeted unit tests for multi-turn scenarios (buff expiry, multi-enemy fights) and add concise module/function docstrings.

- `game/dungeon.py`
  - Status: DONE (I/O decoupled; `enter_room_for_player`, merchant and chest handlers accept `input_handler`/`printer`).
  - Next: UX polish — ensure all merchant prompts use `prompt_confirm()` and centralize inventory display formatting.

- `game/save.py`
  - Status: DONE (`GameState` implemented; round-trip tests pass).
  - Next: optional: add versioning/migrations for save format and document save schema in `docs/CODE_DOCS.md`.

- `game/items.py`
  - Status: DONE (dataclasses and serialization only; loot generation moved to `game/loot.py`).
  - Next: add more serialization edge-case tests and document `Item`/`Weapon` fields.

- `game/player.py`
  - Status: DONE (starter weapons, save/load rehydration, give-transfer protections implemented).
  - Next: add class config centralization (optional) and document inventory constraints in code comments.

- `game/creature.py`
  - Status: OK. No immediate changes required.
  - Next: add `to_dict`/`from_dict` if creatures need to be persisted in the future.

- `main.py` / `game.py`
  - Status: PARTIAL (CLI runner kept interactive for manual play).
  - Next: optionally refactor into a `GameSession` wrapper that accepts `input_handler`/`printer` for testability.

- `tests/` and `test_run.py`
  - Status: MIXED — many tests converted to pytest and passing, but some legacy smoke harnesses still monkeypatch `builtins.input` (e.g., `test_run.py`).
  - Next: convert remaining smoke-tests to injected handlers and add `tests/test_combat_manager.py`.

Priority quick wins (current)
- Finish centralizing inventory display using `game/utils.inventory_to_lines()` across `main.py`, `game/dungeon.py`, and `game/combat.py`.
- Add module-level docstrings and short function docstrings for non-obvious logic (XP split, loot weighting, death penalties).

Playtesting & QA checks (new)
- Monster scaling tests, boss/key flow, and ending-trigger checks are recommended next manual QA items; see `docs/TEST_PLAN.md` for test steps.

Notes
- Use `docs/TODO.md` as the canonical task tracker and `docs/CODE_DOCS.md` for module summaries. I'll keep `FILE_ISSUES.md` concise and actionable.
## File issues & action items (concise)

Purpose: quick, actionable per-file notes. Each item is short: what, status, and next step.

- `game/combat.py`
  - Status: DONE (refactored to accept `input_handler` and `printer`).
  - Next: consider extracting a `CombatManager` class if you want clearer state encapsulation and easier unit testing.

- `game/dungeon.py`
  - Status: TODO (UI mixed with logic).
  - Next: replace `input()`/`print()` calls with injected `input_handler`/`printer` and move event-generation into pure functions. This will make merchant and room handlers testable. (Refactor: `enter_room_for_player` and merchant/chest handlers now accept `input_handler`/`printer`.)

- `game/save.py`
  - Status: PARTIAL (save/load implemented; item/weapon dict helpers exist).
  - Next: wrap save/load into `GameState` (or `Dungeon.save_state()` / `GameState.load()`) — DONE: `GameState` added to `game/save.py`. Round-trip test added (`tests/test_save_roundtrip.py`).

- `game/items.py`
  - Status: TODO (loot logic present).
  - Next: loot generation moved to `game/loot.py` for clarity; `items.py` now focuses on dataclasses and serialization. Consider adding statistical tests for drop distributions.

- `game/player.py`
  - Status: DONE (starter weapon protections, basic save/load rehydration).
  - Next: move class configs (base stats/gains) into `Player.CLASS_CONFIG` for clarity.

- `game/creature.py`
  - Status: OK.
  - Next: add `to_dict`/`from_dict` if creatures need to be saved.

- `main.py` / `game.py`
  - Status: DONE (runner split between `game.py` thin entry and `main.py` logic).
  - Next: consolidate duplicate UI helpers into `main.py` and keep logic in `game/` modules.

- `tests/` and `test_run.py`
  - Status: IN-PROGRESS (some smoke tests converted to pytest; `tests/` scaffolding present).
  - Next: add focused tests for `generate_loot`, XP boundaries, combat edge cases (flee/defend/revive), merchant buy/sell flows. (Done: added `tests/test_combat_edgecases.py`, `tests/test_xp_edgecases.py`, and `tests/test_save_roundtrip.py`.)

Priority quick wins
- Add unit tests for XP and combat edge cases (high priority). — initial edge-case tests added and passing.
- Decouple merchant/room UI from logic (high priority). — `game/dungeon.py` refactored to accept I/O handlers.
- Create a `GameState` save wrapper and add round-trip tests (medium priority). — implemented and tested.

Notes
- Keep this file short — use `docs/TODO.md` for the project-level prioritized list and `docs/CODE_DOCS.md` for module summaries.
## Per-file issues and TODOs

This file lists files that need edits, the specific issues found, and quick status markers so we don't forget work to do. Use this as an actionable checklist.

---

`game/combat.py`
    - Encapsulation: consider wrapping combat functions into a `CombatManager` class for clearer state handling and easier testing.

    - Input coupling: `player_turn` calls `input()` directly; consider injecting an input handler for testability.

    - [Done] Add Run (flee) option and avoid distributing loot when players flee. (implemented)

    - Tests: convert smoke-tests to unit tests covering edge cases (flee, defend buff reset).

`game/save.py`
    - [Done] Equipment rehydration implemented via `Player.load_state` + `game/items.get_weapon_by_name` (re-equip by template name).

    - [Done] Merchant inventory persisted: merchant.inventory is serialized/deserialized on save/load.

    - [Done] `to_dict` / `from_dict` implemented for `Weapon` and `Item` to support nested weapon/item serialization.

    - TODO: Move save/load into a `GameState` or `Dungeon.save_state()` for better encapsulation.

`game/dungeon.py`
    - Issue: `enter_room_for_player` mixes I/O (prompts), generation, and event handling; separate UI prompts from room logic if you want pure logic for testing.
    - Suggestion: Extract `EncounterFactory.generate_enemy_from_players` into a dedicated factory module for tuning and testing.
    - [Done] Merchant inventory persistence implemented and restored on load.

`game/items.py`
    - Minor: manual weighted sampling in `generate_loot` could be replaced by `random.choices(..., weights=...)` for clarity.

    - TODO: Add `Weapon.to_dict()` / `Weapon.from_dict()` or central registry to support save/load rehydration.

`game/player.py`
    - [Done] `load_state` now rehydrates equipped weapon by name; `save_state`/`load_state` now use `Item.to_dict`/`Item.from_dict` and `Weapon.from_dict` for fidelity.

    - [Done] Starter weapons implemented: players receive a class starter weapon that is bound and not droppable/sellable.

    - Suggestion: Move `class_base_stats` and `class_level_gains` into a `Player.CLASS_CONFIG` constant for clearer encapsulation.

`game/creature.py`
    - Mostly fine; consider adding `to_dict()` / `from_dict()` if creature persistence is desired.

`game/utils.py`
    - Fine as-is. Consider adding a small config object/class if more global settings accumulate.

`main.py`
    - Duplication: some helper UI functions are duplicated between `main.py` and `game.py` (e.g., `show_stats`, `choose_class`). Consolidate UI into `main.py` only.

    - Encapsulation: consider a `GameSession` or `GameManager` class to encapsulate `distribute_xp_loot`, `handle_deaths`, and overall session state.

    - [Done] `distribute_xp_loot` callback implemented and used by combat (present in `main.py`).

User-reported issues to address (priority):
1. [Done] Players cannot give items to each other. Implemented `give <index>` which auto-targets the other player in two-player games and prevents transferring bound/starter/super-rare items. Confirmation prompt added.

2. [Done] Inventory grid view added. A 5×6 (30-slot) bracketed grid now displays indices and full item names, with an `Equipped` line and gold above the grid.

3. [Done] Starter weapons inconsistency: players sometimes spawn with non-starter weapons (e.g., Crystal Staff). Ensure starter-bound weapons are given upon new game and persisted correctly.

4. [Done] Missing starter weapon on player death: on respawn the game now runs a defensive `ensure_equipped_weapon()` that equips any ancient/super-rare weapon if present, otherwise guarantees the class starter weapon is present and equipped.

6. [Done] XP distribution (two-player): `distribute_xp_loot` was updated to explicitly handle two-player games — when both players participate and survive the kill, XP is split equally; if only one participant/survivor, that player gets 100% of the XP. `test_run.py` included XP scenarios and `tests/test_xp_distribution.py` converts these to pytest assertions.

7. [Done] XP display (per-level): the status line now shows per-level XP progress as `progress/required` (e.g., `35/330`) instead of raw cumulative XP, and max-level is handled specially.

8. [Done] XP curve adjusted: `game/utils.py:xp_for_level` multiplier reduced from 50 → 30 to speed up leveling. Further tuning recommended.

5. [Done] Map UX: legend added for map markers and movement from start is blocked with a friendly message. (See `main.py` / `game/dungeon.py`)

I'll start implementing the 'give' transfer feature first (in-progress).

`game.py` (top-level runner)
    - [Done] Converted into a thin entrypoint delegating to `main.py` (`main_menu` or `game_loop`).
    - Note: this removes the duplicated monolithic definitions so canonical code lives under `game/` and `main.py`.

`test_run.py`
    - Currently a good smoke-test harness using input monkeypatching; convert to `pytest` functions for CI and more granular assertions.
    - Suggest adding focused tests for: `generate_loot`, `Player.level_up_check`, `Dungeon.enter_room_for_player` (with mocked I/O), and `combat` edge cases.

`tests/`
    - [Done] `tests/test_xp_distribution.py` and `tests/test_save_load.py` added — converts key smoke-test scenarios into pytest tests (XP splitting and merchant save/load). Consider adding further unit tests expanding coverage.

`README.md` / `TODO.md`
    - `TODO.md` updated to be clearer — keep it in sync with `FILE_ISSUES.md` when tasks are completed.

---

Priority quick wins (suggested order):
    1. [Done] Equipment rehydration (implemented).
    2. [Done] Convert `game.py` into a thin runner (completed).
    3. Persist `Merchant.inventory` during save/load.
    4. Add `to_dict`/`from_dict` helpers in `game/items.py` for weapons/items if you prefer full serialization.
    5. Optionally refactor combat into a class for encapsulation and testability.

Future / follow-up items (discussed)
- Merchant UX polish: clearer buy/sell prompts, price breakdowns, and prevention of buying when inventory full.
- Full unit test coverage: expand `tests/` to cover `generate_loot`, `combat` edge cases, merchant buy/sell, give transfers, and death penalties.
- Encapsulate save/load into a `GameState` or `Dungeon.save_state()` API for cleaner responsibility separation.
- Refactor combat into a `CombatManager` class for easier testing and state handling.
- CI: add GitHub Actions workflow to run `pytest` on push/PR and optionally collect coverage.

Playtesting & QA checks (new)
- [ ] Monster scaling: verify whether monsters gain level/stats when players level; document expected behavior and add a config option if dynamic scaling is desired.
- [ ] Elite encounter test: verify Elite rooms are reachable and that player kits/weapons allow the fight to be playable; log balance notes.
- [ ] Boss/key flow: test obtaining the boss key, opening the boss room, fighting the Ancient Dragon, and receiving end-game loot.
- [ ] Ending narrative & treasure: add and test a final treasure chest and short ending epilogue triggered on boss defeat.
- [ ] Starting narrative: add an opening intro that explains setting and objectives to new players.

Documentation / Code comments
- [ ] Add concise module-level docstrings and function docstrings to `game/*.py`; explain non-obvious algorithms (loot weighting, XP split rules, death penalties) in plain language.
- [ ] Create `docs/CODE_DOCS.md` summarizing each module and listing places that would benefit from clearer comments and short examples.

Documentation / Code comments
- [Done] Add concise module-level docstrings and function docstrings to `game/*.py` for key modules: `items.py`, `player.py`, `combat.py`, `dungeon.py`, `creature.py`, `utils.py`, and `save.py`.
- [Done] Create `docs/CODE_DOCS.md` summarizing each module and listing places that would benefit from clearer comments and short examples.

Static verification
- [Done] Quick import/syntax check executed: all `game.*` modules imported successfully after docstring and comment updates.

If you want, I can start with task (1) now and patch the relevant files and tests. Tell me to proceed and I'll apply the changes and run the tests.

---

## Test files — docstring additions & follow-ups

The following test files had minimal module docstrings added on 2025-11-30. Below are short follow-up notes you can track here.

- `tests/conftest.py`
  - Purpose: provides `players` and `dungeon` fixtures and adjusts `sys.path` for tests.
  - Follow-ups: document any additional global fixtures added in future and note if `sys.path` modifications can be avoided by packaging the module.

- `tests/test_combat_edgecases.py`
  - Purpose: edge-case combat tests (flee/defend/revive).
  - Follow-ups: mark tests that are slow or flaky; consider parametrizing similar scenarios to reduce duplicated code.

- `tests/test_save_roundtrip.py`
  - Purpose: round-trip persistence checks for `GameState`.
  - Follow-ups: expand to include merchant/elite-state checks; flag as "IO-heavy" (uses tmp files).

- `tests/test_smoke.py`
  - Purpose: light integration tests for merchant and combat flows.
  - Follow-ups: convert long scenarios into smaller focused tests that use injected `input_handler` for determinism.

- `tests/test_adjacent_join.py`
  - Purpose: integration test for adjacent player joining into combats.
  - Follow-ups: can be converted into a focused unit test by mocking `enter_room_for_player` internals; mark any flakiness.

- `tests/test_xp_edgecases.py`
  - Purpose: XP-splitting and leftover distribution edge-cases.
  - Follow-ups: add explicit assertions for leftover distribution (e.g., deterministic `last_hit` scenarios) and document expectations for ties.

Add these follow-ups to the project board or `docs/TODO.md` if you want them scheduled.
