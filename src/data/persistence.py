import abc
from typing import TypedDict

from game.game import Tile, TilePool


class DBResult(TypedDict):
    owner: str
    name: str
    tiles: TilePool
    id: str
    created_at: str


class TileDict(TypedDict):
    Content: str
    Type: str
    Tags: list[str]


def tile_to_dict(tile: Tile) -> TileDict:
    return {
        "Content": tile.text if tile.image_url is None else tile.image_url,
        "Type": "text" if tile.image_url is None else "image",
        "Tags": list(tile.tags),
    }


def dict_to_tile(item: dict[str, str | list[str]]) -> Tile:
    if not isinstance(item["Content"], str):
        raise Exception()
    text = item["Content"]
    tags = frozenset(item["Tags"])
    image_url = item["Content"] if item["Type"] == "image" else None
    return Tile(text, tags, image_url)

class TilePoolDB(abc.ABC):
    """Abstract class of that can create, modify, delete TilePools from storage"""

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
    def get_tile_pools(self, quantity: int | None = None) -> list[DBResult] | None:
        pass

    @abc.abstractmethod
    def get_tile_pool(self, tile_pool_id: str) -> DBResult | None:
        pass
