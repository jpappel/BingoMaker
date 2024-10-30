import json

import game
import serialization


def test_serialize_board():
    def test_board(size: int):
        board = game._example_game(size)
        serialized = json.dumps(board, cls=serialization.BoardEncoder)
        deserialized = json.loads(serialized)
        assert board.id == deserialized["id"]
        assert board.seed == deserialized["seed"]
        assert board.size == deserialized["size"]

        tiles = [tile for row in board.board for tile in row]
        for board_tile, deserialized_tile in zip(
            tiles, deserialized["tiles"], strict=True
        ):
            type = "text" if board_tile.image_url is None else "image"
            content = board_tile.image_url or board_tile.text
            assert type == deserialized_tile["type"]
            assert content == deserialized_tile["content"]

            if len(board_tile.tags) != 0:
                assert board_tile.tags == frozenset(deserialized_tile["tags"])

    for i in range(1, 7):
        test_board(i)
