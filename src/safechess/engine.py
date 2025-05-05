from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

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
        raise NotImplementedError

    def set_option(self, name: str, value: str | int) -> None:
        raise NotImplementedError

    def analyse(
        self, fen: str, *, depth: int | None = None, time_ms: int | None = None
    ) -> Evaluation:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError


class MockEngine(Engine):
    def __init__(self, path: str) -> None:
        raise NotImplementedError

    def set_option(self, name: str, value: str | int) -> None:
        raise NotImplementedError

    def analyse(
        self, fen: str, *, depth: int | None = None, time_ms: int | None = None
    ) -> Evaluation:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError
