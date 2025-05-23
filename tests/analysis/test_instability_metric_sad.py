"""
safechess/tests/instability/test_instability_metric_sad.py
===========================================================

*First wave* of red (failing‑by‑design) tests for the `feat/instability-metric` branch.
Sad (Unhappy/Angry) path tests for `analyze_instability` in `safechess.instability`.

Running `pytest` **right now** will raise `ImportError` (no production code yet),
driving the TDD cycle.

Usage (once the module exists)::

    pytest -q safechess/tests/instability/test_instability_metric_sad.py
"""

import pytest

import safechess.instability as inst
from safechess.instability import (
    InsufficientSamplesError,
    InvalidFenError,
    ParameterError,
    analyze_instability,
)

# ----------------------------------------------------------------------------
# Sad / Angry path tests
# ----------------------------------------------------------------------------


def test_empty_fen_raises_value_error():
    with pytest.raises(ValueError):
        analyze_instability("", depth=10, N=5)


def test_whitespace_fen_raises_value_error():
    with pytest.raises(ValueError):
        analyze_instability("   ", depth=10, N=5)


def test_malformed_fen_raises_invalid_fen_error():
    with pytest.raises(InvalidFenError):
        analyze_instability("not/a/fen", depth=10, N=5)


def test_non_string_fen_raises_type_error():
    with pytest.raises(TypeError):
        analyze_instability(None, depth=10, N=5)


def test_invalid_parameters_raise_parameter_error():
    with pytest.raises(ParameterError):
        analyze_instability("valid FEN", depth=0, N=5)
    with pytest.raises(ParameterError):
        analyze_instability("valid FEN", depth=10, N=0)


def test_insufficient_engine_samples_raises_error(monkeypatch):
    # Stub engine to return fewer than N samples
    class FakeEngine:
        def __init__(self, path):
            pass

        def set_option(self, name, value):
            pass

        def analyse(self, fen, *, depth=None, time_ms=None):
            return []  # no samples

        def close(self):
            pass

    monkeypatch.setattr(
        "safechess.instability.StockfishEngine", lambda path: FakeEngine(path)
    )

    with pytest.raises(InsufficientSamplesError):
        analyze_instability("valid FEN", depth=5, N=3)
