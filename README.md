# The Ruins Of Asgoth - Text Quest (Console)

Quick play: see `PLAYING.md` for step-by-step instructions and troubleshooting.

Run the game (recommended):

```bash
make run
```

Or directly:

```bash
PYTHONPATH=. python3 run.py
```

Controls:
- Text prompts: choose numbered options or type simple commands when asked.
- Inventory: `equip <index>` or `use <index>` when managing inventory.

Notes / Design:
- Two players play locally, taking turns in combat.
- Start at level 5. Boss (Ancient Dragon) is level 25.
- Weapons: 5 per class; rare ones have low drop rates.
- Save file: `savegame.json` in the same directory.

Testing & development
- Use a virtual environment for development. See `requirements-dev.txt` and `README_TESTING.md` for setup steps.
- Run the automated smoke tests:

```bash
python3 test_run.py
```

- Run the unit tests (requires `pytest`):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pytest -q
```

If you'd like further features (networked multiplayer, GUI, more classes, animations), tell me which and I'll add them.
