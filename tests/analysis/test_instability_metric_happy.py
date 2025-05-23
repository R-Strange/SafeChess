"""
safechess/tests/instability/test_instability_metric.py
=========================================================

*First wave* of red (failing‑by‑design) tests for the `feat/instability-metric` branch.
These tests codify the public contract of the forthcoming instability‑metric core
function (`analyze_instability`) within `safechess.instability`.

Running `pytest` **right now** will raise `ImportError` (no production code yet),
which is exactly the starting point for true TDD.

Usage (once the package skeleton exists)::_

    pytest -q safechess/tests/instability/test_instability_metric.py

The tests rely only on the *public* API; implementation strategy is left open.
"""

import pytest

import safechess.db.cache as cache
from safechess.engine import Evaluation, MockEngine
from safechess.instability import analyze_instability


# ----------------------------------------------------------------------------
# Fixture: stub out the real StockfishEngine with a fast in-memory FakeEngine
# ----------------------------------------------------------------------------
@pytest.fixture
def stub_stockfish(monkeypatch):
    def _stub(evals):
        class FakeEngine(MockEngine):
            def __init__(self, path):
                pass

            def set_option(self, name, value):
                pass

            def analyse(self, fen, *, depth=None, time_ms=None):
                # Return next cp-score from our predefined list
                cp = evals.pop(0)
                return Evaluation(score_cp=cp, mate=None, pv=None)

            def close(self):
                pass

        monkeypatch.setattr("safechess.instability.StockfishEngine", FakeEngine)
        return FakeEngine

    return _stub


# ----------------------------------------------------------------------------
# E‑H001 – returns float for valid inputs
# ----------------------------------------------------------------------------
def test_returns_float_for_valid_inputs(stub_stockfish):
    stub_stockfish([10, 20, 30, 40, 50])
    score = analyze_instability("valid FEN", depth=10, N=5)
    assert isinstance(score, float)


# ----------------------------------------------------------------------------
# E‑H002 – computes expected average swing
# ----------------------------------------------------------------------------
def test_computes_expected_average_swing(stub_stockfish):
    # evals [20,40,60,80,100] → avg swing = 50
    stub_stockfish([20, 40, 60, 80, 100])
    score = analyze_instability("fen", depth=5, N=5)
    assert pytest.approx(score, rel=1e-3) == 50.0


# ----------------------------------------------------------------------------
# E‑H003 – returns zero for single sample
# ----------------------------------------------------------------------------
def test_returns_zero_for_single_sample(stub_stockfish):
    stub_stockfish([123])
    score = analyze_instability("fen", depth=8, N=1)
    assert score == 0.0


# ----------------------------------------------------------------------------
# E‑H004 – cache key includes castling and en-passant
# ----------------------------------------------------------------------------
def test_cache_key_fields_includes_castling_and_ep(monkeypatch, stub_stockfish):
    stub_stockfish([1, 2, 3, 4, 5])
    called = {}
    monkeypatch.setattr(cache, "get", lambda fen, depth, N: None)

    def fake_set(fen, depth, N, values):
        called["fen"] = fen

    monkeypatch.setattr(cache, "set", fake_set)
    analyze_instability(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR KQkq e3 0 1", depth=10, N=5
    )
    assert "KQkq" in called["fen"] and "e3" in called["fen"]


# ----------------------------------------------------------------------------
# E‑H005 – cache miss triggers the engine and then persists any values
# ----------------------------------------------------------------------------
def test_cache_miss_invokes_engine_and_persists(monkeypatch, stub_stockfish):
    stub_stockfish([10, 20, 30, 40, 50])
    monkeypatch.setattr(cache, "get", lambda fen, depth, N: None)
    recorded = {}
    monkeypatch.setattr(
        cache,
        "set",
        lambda fen, depth, N, values: recorded.setdefault("values", values),
    )
    _ = analyze_instability("fen", depth=10, N=5)
    assert recorded["values"] == [10, 20, 30, 40, 50]


# ----------------------------------------------------------------------------
# E‑H006 – a repeat call hits cache without invoking the engine
# ----------------------------------------------------------------------------
def test_repeat_call_uses_cache_without_engine(monkeypatch):
    monkeypatch.setattr(cache, "get", lambda fen, depth, N: [3, 6, 9])
    monkeypatch.setattr(
        "safechess.instability.StockfishEngine",
        lambda path: (_ for _ in ()).throw(AssertionError("Engine called")),
    )
    score = analyze_instability("fen", depth=4, N=3)
    assert isinstance(score, float)


# ----------------------------------------------------------------------------
# E‑H007 – accepts uppercase and lowercase FEN identically
# ----------------------------------------------------------------------------
def test_accepts_uppercase_and_lowercase_fen_identically(stub_stockfish):
    stub_stockfish([5, 5, 5])
    score1 = analyze_instability(
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", depth=5, N=3
    )
    stub_stockfish([5, 5, 5])
    score2 = analyze_instability(
        "RNBQKBNR/PPPPPPPP/8/8/8/8/pppppppp/rnbqkbnr w kq - 0 1", depth=5, N=3
    )
    assert score1 == score2


# ----------------------------------------------------------------------------
# E‑H008 – minimum depth command returns a valid score
# ----------------------------------------------------------------------------
def test_minimum_depth_returns_valid_score(stub_stockfish):
    stub_stockfish([0, 0, 0, 0])
    score = analyze_instability("fen", depth=1, N=4)
    assert isinstance(score, float)


# ----------------------------------------------------------------------------
# E‑H009 – large N within limits returns float
# ----------------------------------------------------------------------------
def test_large_n_within_limits_returns_float(stub_stockfish):
    # assume MAX_SAMPLES ≥ 50
    stub_stockfish(list(range(50)))
    score = analyze_instability("fen", depth=2, N=50)
    assert isinstance(score, float)


# ----------------------------------------------------------------------------
# E‑H010 – non-zero baseline for oscillating position
# ----------------------------------------------------------------------------
def test_non_zero_baseline_for_oscillating_position(stub_stockfish):
    stub_stockfish([10, 20, 10, 20, 10])
    score = analyze_instability("oscillate", depth=6, N=5)
    assert score > 0.0


# ----------------------------------------------------------------------------
# E‑H011 – a zero-variability position returns zero
# ----------------------------------------------------------------------------
def test_zero_variability_position_returns_zero(stub_stockfish):
    stub_stockfish([10, 10, 10, 10, 10])
    score = analyze_instability("locked endgame", depth=5, N=5)
    assert score == 0.0


# ----------------------------------------------------------------------------
# E‑H012 – return values rounded to two decimal places
# ----------------------------------------------------------------------------
def test_return_rounded_to_two_decimal_places(stub_stockfish):
    stub_stockfish([10, 20, 30])
    score = analyze_instability("fen", depth=1, N=3)
    assert round(score, 2) == score


# ----------------------------------------------------------------------------
# E‑H013 – MultiPV response select the top N evaluations
# ----------------------------------------------------------------------------
def test_multipv_response_selects_top_n(stub_stockfish):
    evals = [1, 2, 3, 4, 5]
    stub_stockfish(evals)
    score = analyze_instability("fen", depth=5, N=3)
    # ensure only first N evals consumed
    assert evals == [4, 5]
    assert isinstance(score, float)


# ----------------------------------------------------------------------------
# E‑H014 – Handle extreme evaluations
# ----------------------------------------------------------------------------
def test_handles_extreme_evals(stub_stockfish):
    stub_stockfish([1000000, -1000000, 1000000])
    score = analyze_instability("fen", depth=5, N=3)
    assert isinstance(score, float)


# ----------------------------------------------------------------------------
# E‑H015 – Ingores identical consecutive evaluations
# ----------------------------------------------------------------------------
def test_ignores_identical_consecutive_evals(stub_stockfish):
    stub_stockfish([10, 10, 20, 20, 30, 30, 40, 40])
    score = analyze_instability("fen", depth=5, N=8)
    assert isinstance(score, float) and score > 0.0


# ----------------------------------------------------------------------------
# E‑H016 – Test consistency acoss runs
# ----------------------------------------------------------------------------
def test_consistency_across_runs(stub_stockfish):
    stub_stockfish([5, 10, 15])
    score1 = analyze_instability("fen", depth=5, N=3)
    stub_stockfish([5, 10, 15])
    score2 = analyze_instability("fen", depth=5, N=3)
    assert score1 == score2


# ----------------------------------------------------------------------------
# E‑H017 – Accepts the maximum length FEN
# ----------------------------------------------------------------------------
def test_accepts_maximum_length_fen(stub_stockfish):
    longfen = "r" * 100 + " " + "-" * 10 + " 0 1"
    stub_stockfish([1, 2, 3])
    score = analyze_instability(longfen, depth=5, N=3)
    assert isinstance(score, float)


# ----------------------------------------------------------------------------
# E‑H018 – non-zero baseline for oscillating position
# ----------------------------------------------------------------------------
def test_position_types_opening_middlegame_endgame(stub_stockfish):
    opening = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    middlegame = "rnbq1rk1/pp3ppp/2p2n2/3p4/3P4/2N1PN2/PPP2PPP/R1BQ1RK1 w - - 0 1"
    endgame = "8/8/8/8/8/8/6k1/6KR w - - 0 1"
    stub_stockfish([10, 20, 30])
    score_o = analyze_instability(opening, depth=5, N=3)
    stub_stockfish([15, 15, 15])
    score_m = analyze_instability(middlegame, depth=5, N=3)
    stub_stockfish([0, 0, 0])
    score_e = analyze_instability(endgame, depth=5, N=3)
    assert all(isinstance(s, float) for s in (score_o, score_m, score_e))
