import random
from typing import Iterable


class NoMatchingTile(Exception):
    pass


class Tile:
    def __init__(
        self,
        text: str,
        tags: frozenset[str] = frozenset(),
        image_url: str | None = None,
    ):
        self.text = text
        self.tags = tags
        self.image_url = image_url

    def __hash__(self):
        return hash((self.text, self.tags, self.image_url))

    def __eq__(self, other):
        if not isinstance(other, Tile):
            return False

        return all(
            (
                self.text == other.text,
                self.tags == other.tags,
                self.image_url == other.image_url,
            )
        )


class TilePool:
    def __init__(
        self,
        tiles: frozenset[Tile],
        free_square: Tile | None = None,
        seed: None | int = None,
    ):
        self.tiles = tiles
        self.free = free_square
        self.seed = seed

    def __len__(self):
        return len(self.tiles)

    def __sub__(self, other):
        return TilePool(self.tiles - other.tiles, self.free)

    def _filter_by_tags(self, exclude_tags: list[str]) -> Iterable[Tile]:
        """Return an iterable over tiles which do not container any excluded tags"""
        return filter(
            lambda tile: len(tile.tags.intersection(exclude_tags)) == 0, self.tiles
        )

    def get_free(self) -> Tile:
        if self.free is None:
            raise NoMatchingTile("Pool does not have a free square")

        return self.free

    def get_tile(self, exclude_tags: list[str] | None = None) -> Tile:
        """Get a tile from the tile pool"""
        tiles = (
            self.tiles if exclude_tags is None else self._filter_by_tags(exclude_tags)
        )
        try:
            random.seed(self.seed)
            tile = random.choice(tuple(tiles))
        except IndexError:
            raise NoMatchingTile("No more valid tiles in pool")

        return tile


class Board:
    def __init__(self, pool: TilePool, size: int = 5, free_square: bool = True):
        self.board = [[Tile("")] * size] * size
        self.checked = [[False] * size] * size
        for x in range(size):
            for y in range(size):
                self.board[x][y] = pool.get_tile()

        if free_square:
            mid = size // 2
            self.board[mid][mid] = pool.get_free()
            self.checked[mid][mid] = True
