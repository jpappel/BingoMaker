from game import Tile, TilePool


def test_consistent_get_tile():
    seed = 0
    length = 30

    tiles = frozenset([Tile(f"{x}") for x in range(length)])
    pool = TilePool(tiles, None, seed)
    tiles_2 = frozenset([Tile(f"{x}") for x in range(length)])
    pool_2 = TilePool(tiles_2, None, seed)

    for _ in range(length):
        assert pool.get_tile() == pool_2.get_tile()
