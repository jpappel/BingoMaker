from game.game import Tile, TilePool


def read_text(path: str) -> TilePool:
    tiles = []
    with open(path) as f:
        for line in f:
            tiles.append(Tile(line.strip()))

    return TilePool(frozenset(tiles))
