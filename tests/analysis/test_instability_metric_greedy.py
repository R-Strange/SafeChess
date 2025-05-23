"""
safechess/tests/instability/test_instability_metric_greedy.py
================================================================

*First wave* of red (failing‑by‑design) tests for the `feat/instability-metric` branch.
Greedy path tests for `analyze_instability` in `safechess.instability`.

Running `pytest` **right now** will raise `ImportError` (no production code yet),
driving the TDD cycle.

Usage (once the module exists)::
    pytest -q safechess/tests/instability/test_instability_metric_greedy.py
"""

import pytest

from safechess.engine import Evaluation, MockEngine
from safechess.instability import ParameterError, analyze_instability


# ----------------------------------------------------------------------------
# Fixture to stub out the StockfishEngine for red‑by‑design tests
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
# G-001 – depth=1000 or N=10_000 validated and rejected before engine call
# ----------------------------------------------------------------------------
def test_excessive_depth_or_N_raises_parameter_error():
    with pytest.raises(ParameterError):
        analyze_instability("fen", depth=1000, N=5)
    with pytest.raises(ParameterError):
        analyze_instability("fen", depth=5, N=10000)


# ----------------------------------------------------------------------------
# G-002 – N=0 or negative → ParameterError
# ----------------------------------------------------------------------------
def test_zero_or_negative_N_raises_parameter_error():
    with pytest.raises(ParameterError):
        analyze_instability("fen", depth=5, N=0)
    with pytest.raises(ParameterError):
        analyze_instability("fen", depth=5, N=-1)


# ----------------------------------------------------------------------------
# G-003 – boundary values (depth=1, N=1) execute successfully
# ----------------------------------------------------------------------------
def test_boundary_values_executes(stub_stockfish):
    stub_stockfish([0])
    score = analyze_instability("fen", depth=1, N=1)
    assert isinstance(score, float)


# ----------------------------------------------------------------------------
# G-004 – mixed extremes (high depth, low N) complete within limit
# ----------------------------------------------------------------------------
def test_high_depth_low_N_executes(stub_stockfish):
    stub_stockfish([10])
    score = analyze_instability("fen", depth=50, N=1)
    assert isinstance(score, float)


# ----------------------------------------------------------------------------
# G-005 – very large valid combos throttle internally to avoid OOM
# ----------------------------------------------------------------------------
def test_large_valid_combos_throttled(stub_stockfish):
    # assume MAX_SAMPLES=1000, request N=500
    stub_stockfish([i for i in range(500)])
    score = analyze_instability("fen", depth=20, N=500)
    assert isinstance(score, float)
