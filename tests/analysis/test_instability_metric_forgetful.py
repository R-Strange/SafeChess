"""
safechess/tests/instability/test_instability_metric_forgetful.py
================================================================

*First wave* of red (failing‑by‑design) tests for the `feat/instability-metric` branch.
Forgetful path tests for `analyze_instability` in `safechess.instability`.

Running `pytest` **right now** will raise `ImportError` (no production code yet),
driving the TDD cycle.

Usage (once the module exists)::

    pytest -q safechess/tests/instability/test_instability_metric_forgetful.py

These tests simulate transient failures (resource exhaustion, timeouts,
and database errors) to ensure `analyze_instability` surfaces them appropriately.
"""

import sqlite3

import pytest

import safechess.db.cache as cache
from safechess.engine import StockfishEngine
from safechess.instability import analyze_instability

# ----------------------------------------------------------------------------
# Fixtures and helpers
# ----------------------------------------------------------------------------


class _DummyEngine:
    def __init__(self, exc):
        self._exc = exc

    def set_option(self, name, value):
        pass

    def analyse(self, fen, *, depth=None, time_ms=None):
        raise self._exc

    def close(self):
        pass


@pytest.fixture(autouse=True)
def stub_engine(monkeypatch):
    """
    Replace StockfishEngine with dummy that raises a configured exception.
    """

    def _stub(exc):
        monkeypatch.setattr(
            "safechess.instability.StockfishEngine", lambda path: _DummyEngine(exc)
        )

    return _stub


# ----------------------------------------------------------------------------
# F-001 – simulate OS-killed engine → ResourceError
# ----------------------------------------------------------------------------


def test_engine_out_of_memory_raises_resource_error(stub_engine):
    from safechess.instability import ResourceError

    stub_engine(OSError("Killed"))
    with pytest.raises(ResourceError):
        analyze_instability("fen", depth=1, N=1)


# ----------------------------------------------------------------------------
# F-002 – engine timeout → EngineTimeoutError
# ----------------------------------------------------------------------------


def test_engine_timeout_raises_engine_timeout_error(stub_engine):
    from safechess.instability import EngineTimeoutError

    stub_engine(TimeoutError("analysis timed out"))
    with pytest.raises(EngineTimeoutError):
        analyze_instability("fen", depth=1, N=1)


# ----------------------------------------------------------------------------
# F-003 – SQLite insert disk full → DatabaseError
# ----------------------------------------------------------------------------


def test_db_insert_disk_full_raises_database_error(monkeypatch, stub_engine):
    from safechess.instability import DatabaseError

    # stub engine to return one sample
    stub_engine(lambda *args, **kwargs: None)
    # cache.get returns miss
    monkeypatch.setattr(cache, "get", lambda *args: None)

    # cache.set raises disk full
    def fake_set(fen, depth, N, values):
        raise sqlite3.OperationalError("disk I/O error")

    monkeypatch.setattr(cache, "set", fake_set)
    with pytest.raises(DatabaseError):
        analyze_instability("fen", depth=1, N=1)


# ----------------------------------------------------------------------------
# F-004 – sqlite3.OperationalError retried then surfaced
# ----------------------------------------------------------------------------


def test_db_locked_operational_error_retried_then_error(monkeypatch, stub_engine):
    from safechess.instability import DatabaseError

    stub_engine(None)
    monkeypatch.setattr(cache, "get", lambda *args: None)
    call_count = {"n": 0}

    def fake_set(fen, depth, N, values):
        call_count["n"] += 1
        raise sqlite3.OperationalError("database is locked")

    monkeypatch.setattr(cache, "set", fake_set)
    with pytest.raises(DatabaseError):
        analyze_instability("fen", depth=1, N=1)
    assert call_count["n"] > 1


# ----------------------------------------------------------------------------
# F-005 – excessive N pre-check failure
# ----------------------------------------------------------------------------


def test_excessive_N_precheck_raises_parameter_error():
    from safechess.instability import ParameterError

    # assume MAX_SAMPLES = 100
    with pytest.raises(ParameterError):
        analyze_instability("fen", depth=1, N=1000)
