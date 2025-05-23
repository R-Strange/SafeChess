# src/safechess/instability.py


from safechess.db.cache import get as cache_get
from safechess.db.cache import set as cache_set
from safechess.engine import StockfishEngine

__all__ = [
    "analyze_instability",
    "ParameterError",
    "InsufficientSamplesError",
    "ResourceError",
    "EngineTimeoutError",
    "EngineCrashError",
    "DatabaseError",
    "DBCorruptionError",
]

# reference them so flake8 sees “usage”
_dummy_refs = cache_get, cache_set, StockfishEngine


# ---- Exceptions ----
class ParameterError(Exception):
    """Invalid parameters (e.g. non-positive N or depth, excessive values)."""


class InsufficientSamplesError(Exception):
    """Engine returned fewer samples than requested (N)."""


class ResourceError(Exception):
    """Engine ran out of memory or other OS resource."""


class EngineTimeoutError(Exception):
    """Engine did not produce a bestmove within allotted time."""


class EngineCrashError(Exception):
    """Engine process crashed (e.g. segfault)."""


class DatabaseError(Exception):
    """Generic SQLite failure (e.g. disk full)."""


class DBCorruptionError(Exception):
    """Detected corruption in the SQLite file."""


# ---- Public API ----
def analyze_instability(fen: str, depth: int, N: int) -> float:
    """
    Compute the instability metric for a position.

    :raises ParameterError:        invalid depth or N
    :raises InsufficientSamplesError: fewer than N evals returned
    :raises ResourceError:         engine OOM, etc.
    :raises EngineTimeoutError:    engine timeout
    :raises EngineCrashError:      engine process crash
    :raises DatabaseError:         SQLite failures
    :raises DBCorruptionError:     corrupted DB file
    """
    # stub: tests will drive this red until implemented
    raise NotImplementedError
