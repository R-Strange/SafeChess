"""safechess/tests/engine/test_engine_api.py
================================================

*First wave* of red (failing‑by‑design) tests for the `feat/engine-interface` branch.
These tests codify the public contract of the forthcoming Stockfish engine
adapter (`StockfishEngine`) and its deterministic stub (`MockEngine`).

Running `pytest` **right now** will raise `ImportError` (no production code yet),
which is exactly the starting point for true TDD.

Usage (once the package skeleton exists)::

    pytest -q safechess/tests/engine/test_engine_api.py

The tests rely only on the *public* API; implementation strategy is left open.
"""

import io
import subprocess
from typing import List

import pytest

import safechess.engine as eng  # type: ignore  # noqa: F401,E402

# ----------------------------------------------------------------------------
# Import the yet‑to‑be‑written production module.  This will fail initially —
# flip tests red so we can begin the TDD cycle.
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Helper / fixture infrastructure
# ----------------------------------------------------------------------------


class _FakeProcess:
    """Mimics *just enough* of ``subprocess.Popen`` for unit tests."""

    def __init__(self, scripted_stdout: List[str]):
        self._stdout_lines = iter(scripted_stdout)
        self.stdout = io.StringIO("\n".join(scripted_stdout))
        self.stdin_buffer: List[str] = []
        self.returncode = None  # engine is *running*

    # Popen‑compatible API -------------------------------------------------
    def write(self, line: str) -> None:  # bound to .stdin by monkeypatching
        self.stdin_buffer.append(line)

    @property
    def stdin(self):  # pragma: no cover – trivial pass‑through
        return self

    def poll(self):  # noqa: D401 – mirror Popen
        return self.returncode

    def readline(self):  # bound to .stdout by monkeypatching
        try:
            return next(self._stdout_lines)
        except StopIteration:
            return ""

    def terminate(self):  # noqa: D401
        self.returncode = -1


# ---------------------------------------------------------------------------
# Universal test data
# ---------------------------------------------------------------------------

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
MATE_IN_THREE_FEN = (
    "8/8/8/8/8/8/6k1/6KR w - - 0 1"  # White mates in 3 (simple study position)
)


# ---------------------------------------------------------------------------
# E‑001  – set_option caches value and emits UCI command
# ---------------------------------------------------------------------------


def test_set_option_updates_cache_and_sends_command(monkeypatch):
    _: List[str] = []

    # Scripted engine outputs nothing (analysis not requested here)
    fake_proc = _FakeProcess(scripted_stdout=[])

    def fake_popen(*_a, **_kw):
        return fake_proc

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    engine = eng.StockfishEngine(path="/usr/local/bin/stockfish")
    engine.set_option("Hash", "128")

    # 1️⃣ Public accessor returns value
    assert engine.get_option("Hash") == "128"

    # 2️⃣ Internal: proper UCI command emitted – captured on fake stdin
    assert any(
        cmd.strip() == "setoption name Hash value 128" for cmd in fake_proc.stdin_buffer
    )

    engine.close()


# ---------------------------------------------------------------------------
# E‑002  – deterministic evaluation from MockEngine
# ---------------------------------------------------------------------------


def test_mock_engine_basic_evaluation():
    mock = eng.MockEngine()
    evaluation = mock.analyse(START_FEN, depth=1)

    # Type guarantees
    assert isinstance(evaluation, eng.Evaluation)

    # Deterministic baseline (defined by project spec)
    assert evaluation.score_cp == 20  # ±20 cp advantage for White
    assert evaluation.mate is None
    assert evaluation.pv == ["e2e4"]


# ---------------------------------------------------------------------------
# E‑003  – timeout during analysis triggers EngineTimeoutError
# ---------------------------------------------------------------------------


def test_analyse_timeout_triggers_error(monkeypatch):
    # Engine never returns "bestmove" → should timeout
    fake_proc = _FakeProcess(scripted_stdout=["info depth 1 score cp 0"] * 1000)

    def fake_popen(*_a, **_kw):
        return fake_proc

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    engine = eng.StockfishEngine(path="dummy")

    with pytest.raises(eng.EngineTimeoutError):
        engine.analyse(START_FEN, depth=1, time_ms=25)  # absurdly low timeout

    engine.close()


# ---------------------------------------------------------------------------
# E‑004  – malformed info line raises EngineParseError
# ---------------------------------------------------------------------------


def test_malformed_info_line_raises_parse_error(monkeypatch):
    fake_proc = _FakeProcess(scripted_stdout=["info foo bar baz", "bestmove e2e4"])

    def fake_popen(*_a, **_kw):
        return fake_proc

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    engine = eng.StockfishEngine(path="dummy")

    with pytest.raises(eng.EngineParseError):
        engine.analyse(START_FEN, depth=1)

    engine.close()


# ---------------------------------------------------------------------------
# E‑005  – invalid FEN rejected before UCI command is sent
# ---------------------------------------------------------------------------


def test_invalid_fen_rejected(monkeypatch):
    fake_proc = _FakeProcess(scripted_stdout=[])  # engine never contacted

    def fake_popen(*_a, **_kw):
        return fake_proc

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    engine = eng.StockfishEngine(path="dummy")

    with pytest.raises(eng.InvalidFenError):
        engine.analyse("this_is_not_a_fen", depth=1)

    # Assert that stdin is **empty** – no UCI position command posted
    assert fake_proc.stdin_buffer == []

    engine.close()


# ---------------------------------------------------------------------------
# E‑006  – mate score parsing support
# ---------------------------------------------------------------------------


def test_mate_score_parsed_correctly(monkeypatch):
    fake_proc = _FakeProcess(
        scripted_stdout=[
            "info depth 1 score mate 3 pv h1h8",
            "bestmove h1h8",
        ]
    )

    def fake_popen(*_a, **_kw):
        return fake_proc

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    engine = eng.StockfishEngine(path="dummy")
    evaluation = engine.analyse(MATE_IN_THREE_FEN, depth=1)

    assert evaluation.score_cp is None
    assert evaluation.mate == 3  # plies until mate
    assert evaluation.pv == ["h1h8"]

    engine.close()
