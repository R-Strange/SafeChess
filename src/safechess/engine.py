from __future__ import annotations

import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from subprocess import PIPE
from typing import IO, Dict, List, Optional, cast

# --- ERROR TAXONOMY ---


class EngineError(BaseException):
    pass


class EngineTimeoutError(EngineError):
    pass


class EngineLaunchError(EngineError):
    pass


class EngineProcessError(EngineError):
    pass


class EngineParseError(EngineError):
    pass


class InvalidFenError(EngineError):
    pass


class OptionValidationError(EngineError):
    pass


# --- DATACLASSES ---


@dataclass
class Evaluation:
    score_cp: Optional[int] = None
    mate: Optional[int] = None
    pv: Optional[List[str]] = None


# --- ABSTRACT BASES ---


class Engine(ABC):
    @abstractmethod
    def set_option(self, name: str, value: str | int) -> None:
        pass

    @abstractmethod
    def analyse(
        self, fen: str, *, depth: int | None = None, time_ms: int | None = None
    ) -> Evaluation:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


# -- CONCRETE CLASSES ---


class StockfishEngine(Engine):
    def __init__(self, path: str) -> None:
        self._proc = subprocess.Popen(
            path, stdin=PIPE, stdout=PIPE, text=True
        )  # text mode is critical, don't forget newlines!

        self._proc_stdin: IO[str] = cast(IO[str], self._proc.stdin)  # mypy helpers
        self._proc_stdout: IO[str] = cast(IO[str], self._proc.stdout)

        self._options: Dict[str, str] = {}

    def set_option(self, name: str, value: str | int) -> None:
        value = str(value)
        command: str = f"setoption name {name} value {value}\n"
        self._proc_stdin.write(command)
        self._options[name] = value
        # TODO error handling if proc cmd fails,
        # so that ouroptions dict doesn't go out of sync

    def analyse(
        self, fen: str, *, depth: int | None = None, time_ms: int | None = None
    ) -> Evaluation:
        raise NotImplementedError

    def close(self) -> None:
        # stub to be updated
        try:
            self._proc.terminate()
        except Exception:
            pass

    def get_option(self, name: str) -> str:
        return self._options[name]


class MockEngine(Engine):
    def __init__(self) -> None:
        pass

    def set_option(self, name: str, value: str | int) -> None:
        raise NotImplementedError

    def analyse(
        self, fen: str, *, depth: int | None = None, time_ms: int | None = None
    ) -> Evaluation:
        deterministic_evaluation: Evaluation = Evaluation(
            score_cp=20, mate=None, pv=["e2e4"]
        )

        return deterministic_evaluation

    def close(self) -> None:
        pass
