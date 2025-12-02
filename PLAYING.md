Ruins of Asgoth — Player Guide

Welcome! This short guide explains how to get the game running locally, the minimal requirements, common commands, and the in-game controls so you can start playing quickly.

1) Requirements

- Python 3.10+ (3.11 recommended)
- A terminal (zsh, bash, etc.) on macOS, Linux, or a compatible shell on Windows
- (Optional) A virtual environment for clean installs

2) Setup (recommended)

Open a terminal in the project root (the folder that contains `game.py` and the `game/` directory).

- Create & activate a virtualenv (optional but recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

- Install developer/test dependencies (if you want to run tests):

```bash
pip install -r requirements-dev.txt
```

3) How to run (recommended)

There is a small name conflict between the top-level `game.py` launcher and the `game/` package. To avoid import shadowing, run the safe launcher we added or run the main loop directly with `PYTHONPATH=.`.

- Preferred, safe launcher (recommended):

```bash
PYTHONPATH=. python3 run.py
```

- Direct (explicit package) invocation:

```bash
PYTHONPATH=. python3 -c "from main import game_loop; game_loop()"
```

- Scripted reproduction (non-interactive test of a scenario):

```bash
PYTHONPATH=. python3 tools/repro_interactive_session.py
```

Notes:
- If you get "ModuleNotFoundError: No module named 'game'", make sure your current working directory is the project root and that you set `PYTHONPATH=.` as shown.
- If you prefer `python3 game.py`, it can misbehave because `game.py` shares the module name `game` with the package; prefer `run.py`.

4) In-game controls (quick reference)

Top-level map / navigation menu (when shown): type the number and press Enter
- 1) Forward — move forward
- 2) Left
- 3) Right
- 4) Back
- 5) Inventory — shows inventory and accepts commands
- 6) Save — write progress to `savegame.json`
- 7) Quit
- 8) Restart — confirms before resetting
- 9) Help

Inventory prompt (after choosing `5`):
- `equip <index>` — equip weapon at inventory slot index (1-based)
- `use <index>` — use a consumable
- `give <index>` — give item to teammate (two-player games)
- `skip` — exit inventory

Combat actions (when in combat): type 1–5 and press Enter
- 1) Attack — then type the target number shown
- 2) Defend
- 3) Use Item — chooses an item from inventory to use
- 4) Special — class special (cost/behavior varies)
- 5) Run — attempt to flee

Merchant and chest interactions follow on-screen prompts.

5) How XP is shown & what it means

- The UI displays per-level progress as `current/required` (for example `48/330`) where `current` is XP gained toward the next level and `required` is how much is needed to reach the next level from the current level.
- After combat the game prints explicit XP gain messages (e.g. `Hero gains 50 XP.`) and refreshes the stats so you can see updated progress immediately.

6) Troubleshooting

- If you see weird import errors, ensure you are in the project root and run with `PYTHONPATH=.`.
- If XP doesn't display as expected, restart the game process (the code must be reloaded after edits). Use the `run.py` launcher.
- To reproduce deterministic tests or scenarios, run the pytest cases or the `tools/repro_interactive_session.py` script.

7) Developer / testing notes (optional)

- Tests: run `pytest -q` from the project root.
- Formatting / linting: project does not enforce a formatter in repo — standard Python formatting is used.

8) Want changes?

If you'd like the UI to show both cumulative XP and per-level progress (e.g. `440 (110/330)`), or prefer a different run command (for example `python -m game`), tell me and I can add that change.

Enjoy the game — if anything breaks while you play, paste the exact status lines or the error trace and I'll fix it immediately.