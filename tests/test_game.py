from src.game.game import Board, Tile, TilePool


def _example_game(size: int, seed: int = 0, free_square: bool = False) -> Board:
    assert size > 0
    tiles = frozenset(
        [
            Tile(f"Tile {i}", tags=frozenset([str(i), f"tag_{i % size}"]))
            for i in range((size + 1) ** 2)
        ]
    )
    free_tile = Tile("Free", frozenset(), "free_url") if free_square else None
    pool = TilePool(tiles, free_square=free_tile)
    return Board(pool, size=size, free_square=free_square, seed=seed)


def test_consistent_get_tile():
    seed = 0
    length = 30

    tiles = frozenset([Tile(f"{x}") for x in range(length)])
    pool = TilePool(tiles, None)
    tiles_2 = frozenset([Tile(f"{x}") for x in range(length)])
    pool_2 = TilePool(tiles_2, None)

    for _ in range(length):
        assert pool.get_tile(seed=seed) == pool_2.get_tile(seed=seed)


def test_set_free_tile():
    # test an odd size board
    game = _example_game(5, 0, True)
    middle_tile = game.board[2][2]
    assert middle_tile.text == "Free"
    assert middle_tile.image_url == "free_url"

    # test an even size board
    game = _example_game(6, 0, True)
    middle_tile = game.board[3][3]
    assert middle_tile.text == "Free"
    assert middle_tile.image_url == "free_url"
