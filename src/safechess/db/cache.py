# src/safechess/db/cache.py
from typing import List


def get(fen: str, depth: int, N: int) -> List[float] | None:
    """
    Retrieve a previously saved list of eval-scores for (fen, depth, N),
    or return None if not cached.
    """
    raise NotImplementedError


def set(fen: str, depth: int, N: int, values: List[float]) -> None:
    """
    Persist a list of eval-scores for (fen, depth, N).
    """
    raise NotImplementedError
