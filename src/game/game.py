import random
from collections.abc import Iterable


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

    def __str__(self):
        s = self.text
        if self.image_url:
            s += f" <{self.image_url}>"
        s += f" {list(self.tags)}"

        return s

    def __eq__(self, other):
        # NOTE: because of how the tests import this module,
        #       it is easiest to just check for an exception
        try:
            return all(
                (
                    self.text == other.text,
                    self.tags == other.tags,
                    self.image_url == other.image_url,
                )
            )
        except Exception:
            return False


class TilePool:
    def __init__(
        self,
        tiles: frozenset[Tile],
        free_square: Tile | None = None,
    ):
        self.tiles = tiles
        self.free = free_square
        self._random = random.Random()

    def __len__(self):
        return len(self.tiles)

    def __sub__(self, other):
        return TilePool(self.tiles - other.tiles, self.free)

    def __add__(self, other):
        return TilePool(self.tiles | other.tiles, self.free)

    def __str__(self):
        tiles = ", ".join(map(lambda tile: str(tile), self.tiles))
        s = f"[ {tiles} ]"
        if self.free:
            s += f" : {str(self.free)}"
        return s

    def _filter_by_tags(self, exclude_tags: list[str]) -> Iterable[Tile]:
        """Return an iterable over tiles which do not container any excluded tags"""
        return filter(
            lambda tile: len(tile.tags.intersection(exclude_tags)) == 0, self.tiles
        )

    def get_free(self) -> Tile:
        if self.free is None:
            raise NoMatchingTile("Pool does not have a free square")

        return self.free

    def get_tile(
        self, exclude_tags: list[str] | None = None, seed: None | int = None
    ) -> Tile:
        """Get a tile from the tile pool"""
        tiles = (
            self.tiles if exclude_tags is None else self._filter_by_tags(exclude_tags)
        )
        try:
            self._random.seed(seed)
            tile = self._random.choice(tuple(tiles))
        except IndexError as e:
            raise NoMatchingTile("No more valid tiles in pool") from e

        return tile


class Board:
    def __init__(
        self,
        pool: TilePool,
        size: int = 5,
        free_square: bool = True,
        seed: int = 0,
    ):
        self.board = []
        self.size = size
        self.seed = seed
        self.id = ""

        used = []
        for x in range(size):
            self.board.append([])
            for y in range(size):
                new_tile = pool.get_tile(seed=self.seed * x + y, exclude_tags=used)
                self.board[x].append(new_tile)
                used.append(new_tile.text)

        if free_square:
            mid = size // 2
            self.board[mid][mid] = pool.get_free()
