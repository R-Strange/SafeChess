# SafeChess

[![CI](https://github.com/R-Strange/safechess/actions/workflows/ci.yml/badge.svg)](https://github.com/R-Strange/safechess/actions/workflows/ci.yml) [![Codecov](https://codecov.io/gh/R-Strange/safechess/branch/main/graph/badge.svg)](https://codecov.io/gh/R-Strange/safechess) [![Black Logo](https://raw.githubusercontent.com/psf/black/main/docs/_static/logo2-readme.png)](https://black.readthedocs.io/en/stable/)


A Python tool to analyze the *instability* (risk) of engine-preferred opening moves in chess. SafeChess processes PGN files (and later FEN or Polyglot books) to compute a continuous “Instability Metric” over the first ~15 plies, helping players understand the volatility of opening lines.  

## Features

- **Engine Integration** via Stockfish UCI to evaluate candidate moves  
- **Batch Analysis** of PGN files with caching and multiprocessing  
- **SQLite Storage** of positions, analysis results, and known lines  
- **CLI Interface** (`safechess analyze`) for easy invocation  
- **Export** to CSV/JSON and Jupyter notebooks for deeper exploration  

## Installation

1. **Clone the repo**  
   ```bash
   git clone git@github.com:R-Strange/safechess.git
   cd safechess
2. Create & activate a virtual environment
  python3.12 -m venv .venv
  source .venv/bin/activate
3. Install core dependencies
  pip install -r requirements.txt
4. (Optional) Install development tools
  pip install -r requirements-dev.txt
  pre-commit install

## Usage

Run a basic instability analysis on a PGN:

```bash
  safechess analyze \
    --input games.pgn \
    --depth 18 \
    --samples 5 \
    --output results.db
```
For more options, use:
  ```bash
  safechess analyze --help
```


## Contributing

1. Fork the repository
2. Create a feature branch (git checkout -b feat/my-feature)
3. Commit your changes (git commit -m "feat: add …")
4. Push to your branch (git push origin feat/my-feature)
5. Open a Pull Request against main

Please ensure all tests pass and formatting checks are green via pre-commit run --all-files.

## Documentation

Full documentation and tutorials are available on the ReadTheDocs site: https://safechess.readthedocs.io


## License

This project is licensed under the MIT License. See LICENSE for details.
