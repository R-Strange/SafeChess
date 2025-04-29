# SafeChess Project Setup Summary

## Local Environment

- **OS & Shell**: macOS with zsh
- **Python**: 3.12
- **Package Management**: pip
- **Virtual Environment**: created at `safechess/.venv` and activated via:
  ```bash
  source .venv/bin/activate
  ```

## Project Scaffold (`safechess/`)

- **Directories**:
  - `src/`
  - `tests/`
  - `docs/`
- **Configuration & Metadata**:
  - `.gitignore` (ignores `.venv/`, `__pycache__/`, `.DS_Store`, etc.)
  - `README.md` (with badges, installation & usage)
  - `pyproject.toml` (Black & isort settings)
  - `.pre-commit-config.yaml` (pre-commit hooks setup)
- **Dependency Files**:
  - `requirements.txt` (runtime dependencies)
  - `requirements-dev.txt` (development dependencies)

## Runtime Dependencies (`requirements.txt`)

```yaml
python-chess>=1.9.0
stockfish>=0.13.2
click>=8.0.0
PyYAML>=6.0
toml>=0.10.2
pandas>=2.0.0
cachetools>=5.3.0
tqdm>=4.64.0
matplotlib>=3.6.0
jupyter>=1.0.0
```

## Development Dependencies (`requirements-dev.txt`)

```yaml
pytest>=7.2.0
pytest-cov>=4.0.0
black>=23.3.0
isort>=5.12.0
flake8>=6.0.0
mypy>=0.991
pre-commit>=2.20.0
tox>=3.27.0
```

## Git & GitHub Configuration

- **Repository**: `github.com/R-Strange/safechess.git`
- **GitHub Actions**: workflow at `.github/workflows/ci.yml` that:
  1. Runs on `push` and `pull_request` to `main`
  2. Uses Ubuntu latest with Python 3.12
  3. Installs `requirements.txt` & `requirements-dev.txt`
  4. Executes pre-commit hooks
  5. Runs tests with coverage (`pytest --cov`)
  6. Uploads coverage report to Codecov
- **Badges** in `README.md`:
  - CI: ![CI](https://github.com/R-Strange/safechess/actions/workflows/ci.yml/badge.svg)
  - Codecov: ![Codecov](https://codecov.io/gh/R-Strange/safechess/branch/main/graph/badge.svg)

## Next Steps

1. Implement CLI (`safechess analyze`)
2. Develop engine interface & core instability metric logic
3. Design SQLite schema, caching, and multiprocessing for batch analysis
4. Create Jupyter notebooks, CSV/JSON exports, and ReadTheDocs site
5. Plan for R2 features: Polyglot/FEN support, YAML/TOML configs, known-lines table

