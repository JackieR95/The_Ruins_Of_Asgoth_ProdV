Docstring Scan — 2025-11-30
===========================

Overview
--------
I scanned module headers for Python files under `game/` and `tests/` to detect whether each file begins with a module-level docstring. The goal is to identify remaining files that would benefit from concise module docstrings and short guidance for maintainers.

Summary
-------
- All `game/` modules (`game/*.py`) already include module-level docstrings and short inline comments as of the recent pass.
- Several test/support files currently lack a leading module docstring; adding short descriptions (1–3 lines) will improve discoverability for contributors and test-runners.

Files missing a module-level docstring (recommend adding brief docstrings)
------------------------------------------------------------------------
- `tests/conftest.py`  — provides fixtures and test environment tweaks (describe provided fixtures and any sys.path modifications).
- `tests/test_combat_edgecases.py`  — edge-case combat tests (flee/defend/revive flows).
- `tests/test_save_roundtrip.py`  — focused round-trip save/load test.
- `tests/test_smoke.py`  — light integration/smoke tests used for quick manual verification.
- `tests/test_adjacent_join.py`  — integration test for adjacency/joining combat flows.
- `tests/test_xp_edgecases.py`  — XP split and leftover distribution edge-cases.

Recommended next steps
----------------------
1. Add short (1–3 line) module docstrings to the listed test files describing their purpose and any fixtures they rely on.
2. Keep docstrings consistent: one-line summary followed by one short paragraph when needed.
3. Optionally, add a short note to `docs/FILE_ISSUES.md` mapping each test file to any outstanding items (e.g., flakiness, long runtime, PR references).
4. If you'd like, I can apply minimal docstrings to the listed files now (non-functional, descriptive only).

If you'd like me to proceed and add the docstrings automatically, say "Yes, add docstrings" and I'll patch those files and run the test suite to confirm nothing breaks.