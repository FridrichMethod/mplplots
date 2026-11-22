# Development

To work on mplplots itself, clone the repository, install it in editable mode with its
development dependencies, and run the checks:

```bash
git clone https://github.com/FridrichMethod/mplplots.git
cd mplplots
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

pre-commit run --all-files  # whitespace, YAML/TOML, ASCII, spelling, ruff lint + format, mypy
pytest
```

Both checks must pass before you commit. CI runs them on Python 3.12 and 3.13 for pushes and pull
requests to `main`, and runs the tests once more against the oldest supported versions (Python
3.12 with Matplotlib 3.8.0). Agent and contributor conventions are in [`AGENTS.md`](../AGENTS.md).
