## SafeChess Project Master Record

This document captures the core definitions, scope, and roadmap agreed upon for the SafeChess project, to serve as the master reference for all related work.

---

### 1. Project Objective
- **Goal**: Build a Python program to identify and quantify the "instability" (risk) of engine-preferred chess moves/lines in opening theory (first ~15 plies).
- **Target Users**: Intermediate and above players, offline batch analysis.
- **Metric Name**: **Instability Metric** (continuous score; widget later called “Risk-o-Meter”).

### 2. Scope & Inputs
- **Phase 1 (MVP)**: PGN-based opening files ingestion.
- **Later Phases**: Add support for Polyglot `.bin` ECO books, single-position FENs, public PGN database imports.
- **Engine**: Stockfish UCI wrapper (configurable depth/time/hash via function parameters). MockEngine stub for testing.

### 3. Instability Metric Definition
- **Calculation**: Score = average(eval₂…eval…eval\u208N) – eval₁, where eval₁ is top engine eval; N configurable at runtime.
- **Variants**:
  - Optionally record the ply at which worst-case swing occurs.
  - Later explore alternative scoring (mate vulnerabilities, human-like reply sampling).

### 4. Architecture & Storage
- **Language**: Pure Python.
- **Libraries**: `python-chess`, `stockfish` UCI bindings, `pytest`, `sqlite3`.
- **Storage**: SQLite with tables:
  - `positions` (FEN, metadata)
  - `analyses` (position_id, depth, N, score, PV, timestamp)
  - `known_lines` (ECO code, name, PGN, tags) in R2.
- **Performance**: Caching by (FEN, depth, N); multiprocessing for batch jobs.

### 5. Project Roadmap
#### MVP: Core Engine + Batch Analysis
- Repo scaffold, CI & linting.
- Engine interface + MockEngine.
- Instability calculator function: `analyze_instability(fen, depth, N)`.
- PGN loader → stream positions.
- SQLite schema & caching layer; multiprocessing.
- CLI to analyze PGN into DB; tests for core modules.

#### Release 1 (R1): Exports & Notebooks
- CSV/JSON export functions.
- Jupyter notebooks for sensitivity analysis.
- Basic Matplotlib plots in notebooks.
- CI pipeline builds docs; ReadTheDocs site.
- Regression tests against curated lines.

#### Release 2 (R2): Extensibility & Tuning
- Add Polyglot `.bin` and FEN loaders.
- YAML/TOML config for defaults.
- `known_lines` table in SQLite.
- Threshold-sweeping scripts for tuning.

#### Later Releases
- Interactive Web UI with "Risk-o-Meter" gauge.
- Packaging as a pip-installable CLI (`safechess analyze`).
- Natural-language explanation generation.
- Optional live-engine integrations and user feedback loops.

---

This record will be referenced in all future SafeChess conversations to maintain consistency and context.

