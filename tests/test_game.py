from examples import example_game

from bingomaker.game.game import Tile, TilePool


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
    game = example_game(5, 0, True)
    middle_tile = game.board[2][2]
    assert middle_tile.text == "Free"
    assert middle_tile.image_url == "free_url"

    # test an even size board
    game = example_game(6, 0, True)
    middle_tile = game.board[3][3]
    assert middle_tile.text == "Free"
    assert middle_tile.image_url == "free_url"
