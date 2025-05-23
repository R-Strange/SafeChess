"""
safechess/tests/instability/test_instability_metric_indecisive.py
================================================================

*First wave* of red (failing‑by‑design) tests for the `feat/instability-metric` branch.
Indecisive path tests for `analyze_instability` in `safechess.instability`.

Running `pytest` **right now** will raise `ImportError` (no production code yet),
driving the TDD cycle.

Usage (once the module exists)::
    pytest -q safechess/tests/instability/test_instability_metric_indecisive.py
"""

import pytest

from safechess.engine import Evaluation, MockEngine
from safechess.instability import analyze_instability


# ----------------------------------------------------------------------------
# Fixture to stub out the StockfishEngine class for red‑by‑design tests
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
                cp = evals.pop(0)
                return Evaluation(score_cp=cp, mate=None, pv=None)

            def close(self):
                pass

        monkeypatch.setattr("safechess.instability.StockfishEngine", FakeEngine)
        return FakeEngine

    return _stub


# ----------------------------------------------------------------------------
# I-001 – all N eval samples identical → instability = 0
# ----------------------------------------------------------------------------
def test_all_samples_identical_returns_zero(stub_stockfish):
    stub_stockfish([50, 50, 50, 50])
    score = analyze_instability("fen", depth=5, N=4)
    assert score == 0.0


# ----------------------------------------------------------------------------
# I-002 – one outlier among identical evals → computes correct small swing
# ----------------------------------------------------------------------------
def test_one_outlier_computes_small_swing(stub_stockfish):
    # evals [10,10,10,50] → swings 0,0,40 → avg ≈ 13.33
    stub_stockfish([10, 10, 10, 50])
    score = analyze_instability("fen", depth=5, N=4)
    assert pytest.approx(score, rel=1e-3) == pytest.approx((0 + 0 + 40) / 3, rel=1e-3)


# ----------------------------------------------------------------------------
# I-003 – floats within tolerance aggregated sensibly
# ----------------------------------------------------------------------------
def test_float_tolerance_aggregation(stub_stockfish):
    stub_stockfish([0.1, 0.1000001, 0.1000002])
    score = analyze_instability("fen", depth=3, N=3)
    # nearly zero variance → near-zero instability
    assert score < 1e-4


# ----------------------------------------------------------------------------
# I-004 – rounding behavior to two decimal places
# ----------------------------------------------------------------------------
def test_rounding_behavior(stub_stockfish):
    stub_stockfish([10.1234, 20.5678, 30.91011])
    score = analyze_instability("fen", depth=4, N=3)
    # raw swings: 10.4444,10.34233 → avg ~10.3934 → rounded to two decimals
    assert score == round(score, 2)


# ----------------------------------------------------------------------------
# I-005 – minor eval variance under threshold → near-zero
# ----------------------------------------------------------------------------
def test_minor_variance_reports_near_zero(stub_stockfish):
    stub_stockfish([5.001, 5.002, 5.000])
    score = analyze_instability("fen", depth=3, N=3)
    assert score < 0.01
