import chess
import chess.engine


class MockEngine:
    def analyse(self, board, limit, multipv=1):
        return [
            {
                "score": chess.engine.PovScore(chess.engine.Cp(13), True),
                "pv": [chess.Move.from_uci("e2e4")],
            }
        ] * multipv

    def quit(self):
        pass
