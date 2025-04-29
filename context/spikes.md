Over the course of these spikes we:

Streamed PGNs game-by-game with python-chess to confirm low-memory ingestion.
Defined and exercised an in-memory SQLite schema for positions and analyses, inserting and querying sample data.
Built a simple on-disk cache (via shelve) to key analysis results by (fen, depth, multipv) and avoid redundant engine calls.
Swapped out process-based multiprocessing—which was failing to pickle in notebooks—for a ThreadPoolExecutor-based pattern, so each thread spins up its own Stockfish and returns scores in parallel.
Wired up a minimal click CLI prototype (safechess analyze) that reads PGN, depth, multipv, and prints scores per game.
Created a MockEngine stub with a matching .analyse() signature and wrote a pytest against it—then fixed the import error by adding import chess.engine and an __init__.py so that pytest could discover the module.
Built a threshold-sweep script to run the same sample FEN across a grid of depths and multipv values, collecting scores for later sensitivity analysis.
Together these spikes prove out the core pieces of SafeChess’s engine interface, storage, caching, parallelism, CLI, and testing strategy—giving us the confidence to move on to integrating them into a unified pipeline.

They can be found in the spikes folder.