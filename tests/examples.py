from src.game.game import Board, Tile, TilePool


def example_game(size: int, seed: int = 0, free_square: bool = False) -> Board:
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
