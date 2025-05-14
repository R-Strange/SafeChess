from __future__ import annotations

import subprocess
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from subprocess import PIPE
from typing import Dict, List, Optional

from chess import Board

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

        self._options: Dict[str, str] = {}

        self.best_evaluation: Evaluation | None = None

    def set_option(self, name: str, value: str | int) -> None:
        value = str(value)
        command: str = f"setoption name {name} value {value}\n"

        assert self._proc.stdin is not None
        self._proc.stdin.write(command)
        self._options[name] = value
        # TODO error handling if proc cmd fails,
        # so that our options dict doesn't go out of sync

    def analyse(
        self, fen: str, *, depth: int | None = None, time_ms: int | None = None
    ) -> Evaluation:
        def build_go_command(
            depth: int | None = None, time_ms: int | None = None
        ) -> str:
            match (depth, time_ms):
                case (None, None):
                    return "go"

                case (d, None) if isinstance(d, int):
                    return f"go depth {d}"

                case (None, t) if isinstance(t, int):
                    return f"go movetime {t}"

                case (d, t) if isinstance(d, int) and isinstance(t, int):
                    return f"go depth {d} movetime {t}"

                case _:
                    raise OptionValidationError(
                        f"Invalid Parameters: Depth = {depth}, Movetime = {time}"
                    )
            raise OptionValidationError("Engine wrapper failed to construct a command")

        # def parse_bestmove_line(line: str) -> bool:
        #    pass

        def handle_info_line(line: str) -> Evaluation:
            line_components: List[str] = line.split()

            if "score" not in line_components:
                raise EngineParseError(
                    "Error, malformed line: no score component returned by Engine"
                )

            score_index: int = line_components.index("score")

            expected_next_commands: List[str] = ["cp", "mate"]

            if line_components[score_index + 1] not in expected_next_commands:
                raise EngineParseError(
                    "Error, malformed line. Score component missing cp/mate statement"
                )

            try:
                int(line_components[score_index + 2])
            except ValueError:
                raise EngineParseError(
                    "Error, malformed line. Score CP or Mate missing value."
                )

            score_value: int = int(line_components[score_index + 2])
            pv: List[str] = line_components[score_index + 4 :]

            match line_components[score_index + 1]:
                case "cp":
                    latest_evaluation = Evaluation(
                        score_cp=score_value, mate=None, pv=pv
                    )

                case "mate":
                    latest_evaluation = Evaluation(
                        score_cp=None, mate=score_value, pv=pv
                    )

                case _:
                    raise EngineParseError(
                        "Error, malformed line. \
                        Score component missing cp/mate statement"
                    )

            return latest_evaluation

        try:
            _ = Board(fen)
        except ValueError:
            raise InvalidFenError("FEN not valid")

        go_command: str = build_go_command(depth=depth, time_ms=time_ms)

        full_command: List[str] = [f"position fen {fen}\n", go_command]

        start_time: float | None = time.monotonic() if time_ms else None

        for command in full_command:
            assert self._proc.stdin is not None
            self._proc.stdin.write(command)

        while True:
            if time_ms is not None:
                assert start_time is not None
                elapsed_time: float = (time.monotonic() - start_time) * 1000

                if elapsed_time >= time_ms:
                    self._proc.terminate()
                    raise EngineTimeoutError(
                        f"Engine analysis exceeded maximum time: {time_ms}"
                    )

            rc = self._proc.poll()

            if rc is not None:
                raise EngineProcessError(f"Engine exited with code {rc}")

            assert self._proc.stdout is not None
            line = self._proc.stdout.readline()
            if not line:
                time.sleep(0.005)
                continue

            line = line.strip()

            if line.startswith("bestmove "):
                assert self.best_evaluation is not None
                return self.best_evaluation

            if line.startswith("info "):
                self.best_evaluation = handle_info_line(line)
                continue

        return EngineProcessError("Analysis exited loop without producing a result")

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
