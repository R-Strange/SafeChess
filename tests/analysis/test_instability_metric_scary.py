"""
safechess/tests/instability/test_instability_metric_scary.py
===========================================================

*First wave* of red (failing‑by‑design) tests for the `feat/instability-metric` branch.
Scary path tests for `analyze_instability` in `safechess.instability`.

Running `pytest` **right now** will raise `ImportError` (no production code yet),
driving the TDD cycle.

Usage (once the module exists)::

    pytest -q safechess/tests/instability/test_instability_metric_scary.py
"""

import sqlite3
import time

import pytest

import safechess.db.cache as cache
from safechess.engine import Evaluation, StockfishEngine
from safechess.instability import (
    DBCorruptionError,
    EngineCrashError,
    analyze_instability,
)

# ----------------------------------------------------------------------------
# E‑S‑001 – engine binary not found
# ----------------------------------------------------------------------------


def test_engine_binary_not_found(monkeypatch):
    # Simulate missing binary on instantiation
    def fake_init(self, path):
        raise FileNotFoundError("Stockfish binary not found")

    monkeypatch.setattr(StockfishEngine, "__init__", fake_init)

    with pytest.raises(FileNotFoundError):
        analyze_instability("fen", depth=5, N=3)


# ----------------------------------------------------------------------------
# E‑S‑002 – engine binary lacks execute permission
# ----------------------------------------------------------------------------


def test_engine_no_execute_permission(monkeypatch):
    def fake_init(self, path):
        raise PermissionError("No execute permission for Stockfish binary")

    monkeypatch.setattr(StockfishEngine, "__init__", fake_init)

    with pytest.raises(PermissionError):
        analyze_instability("fen", depth=5, N=3)


# ----------------------------------------------------------------------------
# E‑S‑003 – engine crashes with segfault
# ----------------------------------------------------------------------------


def test_engine_segfault_wrapped(monkeypatch):
    def fake_init(self, path):
        pass

    class FakeEngine(StockfishEngine):
        def analyse(self, fen, *, depth=None, time_ms=None):
            # Simulate subprocess crash
            raise OSError("Segmentation fault")

    monkeypatch.setattr(StockfishEngine, "__init__", fake_init)
    monkeypatch.setattr("safechess.instability.StockfishEngine", FakeEngine)

    with pytest.raises(EngineCrashError):
        analyze_instability("fen", depth=5, N=3)


# ----------------------------------------------------------------------------
# E‑S‑004 – corrupted SQLite file detected
# ----------------------------------------------------------------------------


def test_sqlite_corruption_raises_dbcorruption(monkeypatch):
    # Simulate write failure on cache.set
    def fake_set(fen, depth, N, values):
        raise sqlite3.DatabaseError("file is not a database")

    monkeypatch.setattr(cache, "get", lambda fen, depth, N: None)
    monkeypatch.setattr(cache, "set", fake_set)

    with pytest.raises(DBCorruptionError):
        analyze_instability("fen", depth=5, N=3)


# ----------------------------------------------------------------------------
# E‑S‑005 – system clock skew does not break function
# ----------------------------------------------------------------------------


def test_system_clock_skew_handled(monkeypatch):
    # Simulate clock going backward between calls
    times = [1000.0, 900.0, 1100.0]
    monkeypatch.setattr(time, "time", lambda: times.pop(0))

    # Stub engine to return minimal samples
    class FakeEngine(StockfishEngine):
        def __init__(self, path):
            pass

        def analyse(self, fen, *, depth=None, time_ms=None):
            return Evaluation(score_cp=0, mate=None, pv=None)

        def close(self):
            pass

    monkeypatch.setattr("safechess.instability.StockfishEngine", FakeEngine)

    # Should complete without exception despite time skew
    score = analyze_instability("fen", depth=3, N=1)
    assert isinstance(score, float)
