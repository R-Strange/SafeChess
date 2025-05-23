"""
safechess/tests/instability/test_instability_metric_desolate.py
================================================================

*First wave* of red (failing‑by‑design) tests for the `feat/instability-metric` branch.
Desolate path tests for `analyze_instability` in `safechess.instability`.

Running `pytest` **right now** will raise `ImportError` (no production code yet),
driving the TDD cycle.

Usage (once the module exists)::

    pytest -q safechess/tests/instability/test_instability_metric_desolate.py

"""

import pytest

import safechess.db.cache as cache
from safechess.engine import Evaluation, MockEngine
from safechess.instability import analyze_instability


# ----------------------------------------------------------------------------
# Stub fixture for StockfishEngine to return controlled evals and PVs
# ----------------------------------------------------------------------------
@pytest.fixture
def stub_stockfish(monkeypatch):
    def _stub(evals_pv_list):
        class FakeEngine(MockEngine):
            def __init__(self, path):
                pass

            def set_option(self, name, value):
                pass

            def analyse(self, fen, *, depth=None, time_ms=None):
                cp, pv = evals_pv_list.pop(0)
                return Evaluation(score_cp=cp, mate=None, pv=pv)

            def close(self):
                pass

        monkeypatch.setattr("safechess.instability.StockfishEngine", FakeEngine)
        return FakeEngine

    return _stub


# ----------------------------------------------------------------------------
# D‑001 – no legal moves (e.g., checkmate/stalemate) → instability = 0
# ----------------------------------------------------------------------------


def test_no_legal_moves_returns_zero(stub_stockfish):
    stub_stockfish([(0, [])])
    score = analyze_instability("8/8/8/8/8/8/6k1/6KR w - - 0 1", depth=5, N=1)
    assert score == 0.0


# ----------------------------------------------------------------------------
# D‑002 – engine emits zero PV lines → returns score = 0
# ----------------------------------------------------------------------------


def test_zero_pv_lines_returns_zero(stub_stockfish):
    stub_stockfish([(10, [])])
    score = analyze_instability("some_fen", depth=5, N=1)
    assert score == 0.0


# ----------------------------------------------------------------------------
# D‑003 – FEN with '-' castling rights parsed as “no castling” correctly
# ----------------------------------------------------------------------------


def test_castling_rights_dash_parsed_correctly(monkeypatch, stub_stockfish):
    stub_stockfish([(5, ["e2e4"])])
    called = {}
    monkeypatch.setattr(cache, "get", lambda fen, depth, N: None)
    monkeypatch.setattr(
        cache, "set", lambda fen, depth, N, values: called.setdefault("fen", fen)
    )

    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 1"
    analyze_instability(fen, depth=5, N=1)
    assert "-" in called["fen"]


# ----------------------------------------------------------------------------
# D‑004 – engine eval missing 'multipv' entries handled via defaults
# ----------------------------------------------------------------------------


def test_missing_multipv_defaults_handled(stub_stockfish):
    # two samples without explicit multipv info
    stub_stockfish([(10, ["e2e4"]), (12, ["d2d4"])])
    score = analyze_instability("fen", depth=5, N=2)
    assert isinstance(score, float)


# ----------------------------------------------------------------------------
# D‑005 – CACHE_DIR=None → fallback to in-memory cache
# ----------------------------------------------------------------------------


def test_none_cache_dir_fallback(monkeypatch, stub_stockfish):
    stub_stockfish([(1, ["a2a3"])])
    monkeypatch.setattr(cache, "get", lambda fen, depth, N: None)
    monkeypatch.setattr(cache, "set", lambda fen, depth, N, values: None)
    monkeypatch.setattr("safechess.db.cache.CACHE_DIR", None)

    score = analyze_instability("fen", depth=5, N=1)
    assert isinstance(score, float)
