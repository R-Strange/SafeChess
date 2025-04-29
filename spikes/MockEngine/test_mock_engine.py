import chess
from mock_engine import MockEngine


def test_mock_engine_analysis():
    engine = MockEngine()
    board = chess.Board()
    info = engine.analyse(board, None, multipv=2)

    assert isinstance(info, list) and len(info) == 2
    assert info[0]["score"].white().score() == 13
    assert info[0]["pv"][0] == chess.Move.from_uci("e2e4")


if __name__ == "__main__":
    test_mock_engine_analysis()
    print("All tests passed.")
