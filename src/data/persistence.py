import abc
from collections.abc import Iterable
from enum import Enum
from typing import TypedDict

from game.game import Tile, TilePool


class DBResult(TypedDict):
    owner: str
    name: str
    tiles: TilePool
    id: str
    created_at: str


class TileType(Enum):
    TEXT = "text"
    IMAGE = "image"


class SortMethod(Enum):
    AGE = "created_at"
    NAME = "name"
    OWNER = "owner"
    DEFAULT = None


class TileDict(TypedDict):
    content: str
    type: str
    tags: list[str]


def tile_to_dict(tile: Tile) -> TileDict:
    """Concert a Tile object to a Tile dict"""
    return {
        "content": tile.text if tile.image_url is None else tile.image_url,
        "type": TileType.TEXT.value if tile.image_url is None else TileType.IMAGE.value,
        "tags": list(tile.tags),
    }


def dict_to_tile(item: TileDict) -> Tile:
    """Convert a Tile dict to a Tile object

    Raises:
        TypeError: incorrect type in dictionary
        KeyError: unable to parse item into Tile due to missing key
    """
    if not isinstance(item["content"], str):
        raise TypeError()
    type_ = TileType(item["type"])
    text = item["content"]
    tags = frozenset(item["tags"])
    image_url = item["content"] if type_ == TileType.IMAGE else None
    return Tile(text, tags, image_url)


class TilePoolDB(abc.ABC):
    """Abstract class of that can create, modify, delete TilePools from storage"""

    def paginate(self, count: int, size: int | None, page: int | None) -> tuple[int, int]:
        """Produce start and end indicies given a count, pagesize, and page number"""
        match page, size:
            case (None, None) | (_, None):
                start = 0
                end = count
            case (None, _):
                start = 0
                end = size
            case (_, _):
                start = (page - 1) * size
                end = start + min(count - start, size)

        return start, end

    def sort(self, data: Iterable[DBResult], sort: SortMethod, sort_asc: bool) -> list[DBResult]:
        """Sort DBResults by using a sort method and sort order"""
        if sort != SortMethod.DEFAULT:
            return sorted(data, key=lambda dbresult: dbresult[sort.value], reverse=not sort_asc)

        return list(data)

    @abc.abstractmethod
    def insert_tile_pool(self, name: str, owner: str, pool: TilePool) -> str | None:
        pass

    @abc.abstractmethod
    def delete_tile_pool(self, tile_pool_id: str) -> bool:
        pass

    @abc.abstractmethod
    def delete_tile_pool_by_owner(self, owner: str) -> bool:
        pass

    @abc.abstractmethod
    def update_tiles(
        self,
        tile_pool_id: str,
        removals: list[str] | None = None,
        insertions: list[Tile] | None = None,
    ) -> bool:
        pass

    @abc.abstractmethod
    def get_tile_pools(
        self,
        size: int | None = None,
        page: int | None = None,
        sort: SortMethod = SortMethod.DEFAULT,
        sort_asc: bool = True,
    ) -> list[DBResult] | None:
        pass

    @abc.abstractmethod
    def get_tile_pool(self, tile_pool_id: str) -> DBResult | None:
        pass
