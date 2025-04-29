Development Environment

1. Machine & OS
* Hardware: MacBook Pro 16" 2019 intel
* Operating System: macOS (latest stable release)

2. Shell & Prompt
* Shell: zsh
* Framework: Oh My Zsh
* Prompt Theme: Powerlevel10k (p10k), with instant-prompt enabled via ~/.cache/p10k-instant-prompt-<user>.zsh
* Enabled Plugins:
  * git
  * python, pip, virtualenv (for seamless Python venv usage)
  * vscode, github, docker (CLI helpers)
  * zsh-autosuggestions, zsh-syntax-highlighting
* Custom Function:
```bash
mkvenv() { python -m venv .venv && source .venv/bin/activate; }
```
* Auto-activate venv if .venv/bin/activate exists on cd
* pyenv initialization in ~/.zshrc for multi-Python management
* direnv hook for per-project env vars

3. Homebrew & System Packages
* Homebrew Installed, with the following formulae & casks:
* ripgrep (rg): Fast, Rust-based code search tool – brew install ripgrep
* watchman: Low-latency file-watching service – brew install watchman
* htop: Interactive process viewer – brew install htop
* Docker: Container runtime & CLI – brew install --cask docker (then launch Docker.app)
* Node.js: JavaScript runtime & package manager – brew install node

4. Editor & IDE
* Primary Editor: Visual Studio Code
* Project-local settings: .vscode/settings.json present to standardize editor behavior
* Sample .vscode/settings.json
```json
{
  "python.pythonPath": "${workspaceFolder}/.venv/bin/python",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.linting.mypyEnabled": true,
  "python.formatting.provider": "black",
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true
  }
}
```
5. Python Toolchain
* Interpreter: Python 3.12 (via system or Homebrew)
* Virtual Environments:
    * Per-project .venv/ folder
    * Auto-activated by .zshrc hook
* Package Management:
    * Runtime deps → requirements.txt
    * Dev deps → requirements-dev.txt ​

6. Project Layout (safechess/)
safechess/
├── src/               
├── tests/             
├── docs/              
├── .venv/             
├── .gitignore         
├── README.md          
├── pyproject.toml     
├── .pre-commit-config.yaml
├── requirements.txt
├── requirements-dev.txt
└── .github/
    └── workflows/
        └── ci.yml     

7. Pre-commit & Linting
* pre-commit hooks: Black, isort, flake8, mypy
* Config in .pre-commit-config.yaml ​

8. Continuous Integration
   1. Platform: GitHub Actions
   2. Workflow (`.github/workflows/ci.yml`):
   3. Run on push & pull_request (`branch: main`)
   4. Setup Ubuntu & Python 3.12
   5. Install `requirements*.txt`
   6. Check formatting & lint via pre-commit
   7. Run `pytest --cov`
   8. Upload to Codecov ​

9. Local Development Workflow
   1. `git clone ... && cd safechess/`
   2. `python3.12 -m venv .venv && source .venv/bin/activate`
   3. `pip install -r requirements.txt -r requirements-dev.txt && pre-commit install`
   4. Code in `src/`, tests in `tests/`, run `pytest` & ensure hooks pass
   5. Push & open PR—CI will validate

10. Other Tooling & Languages
* Containers: none currently
* Languages: Rust, Julia, SQL dialects, Haskell (future: consider a Rust core for performance)
* Version Managers: pyenv, (optionally asdf for multi-lang)

11.  Secrets & Environment Variables
* `.env` file in the root directory of the project.

```ini
# Path to your Stockfish engine binary
STOCKFISH_PATH=/usr/local/bin/stockfish

# Database connection URL (SQLite or other)
DATABASE_URL=sqlite:///safechess.db

# Optional Polyglot opening book
POLYGLOT_BOOK_PATH=./data/openings.bin

# Logging settings
LOG_LEVEL=INFO

# Engine settings
ENGINE_DEPTH=15
ENGINE_TIME=1000  # milliseconds per position

# Caching directory
CACHE_DIR=./.cache

# API tokens (uncomment and set if needed)
# CODECOV_TOKEN=your_codecov_token_here
# SENTRY_DSN=your_sentry_dsn_here
```