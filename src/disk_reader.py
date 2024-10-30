import game


def read_text(path: str) -> game.TilePool:
    tiles = []
    with open(path) as f:
        for line in f:
            tiles.append(game.Tile(line.strip()))

    return game.TilePool(frozenset(tiles))
