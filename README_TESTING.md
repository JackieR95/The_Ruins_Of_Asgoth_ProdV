Testing and contributor setup
===========================

Quick steps for another contributor to reproduce your dev environment and run the tests.

Prerequisites
- Python 3.8+ installed and available as `python3`.

Create and activate a virtual environment (recommended)
```bash
# create venv in project root
python3 -m venv .venv

# activate (zsh / bash)
source .venv/bin/activate
```

Install development requirements
```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements-dev.txt
```

Run tests
```bash
pytest -q
# or run a single file
pytest -q tests/test_xp_distribution.py
```

Run the smoke-test runner
```bash
python3 test_run.py
```

Run without activating the venv
```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

Notes
- The repository includes `requirements-dev.txt` with minimal dev dependencies (currently `pytest`).
- The `.gitignore` excludes `.venv/` and `savegame.json` so local state won't be committed.
- If you prefer not to use `venv`, CI or Docker workflows can install the same deps directly.
