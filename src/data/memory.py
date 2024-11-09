import datetime
from collections.abc import Iterable
from uuid import uuid4

from data.persistence import DBResult, SortMethod, TilePoolDB
from game.game import Tile, TilePool


class MemoryTilePoolDB(TilePoolDB):
    def __init__(self):
        self.data: dict[str, DBResult] = {}

    def _iter_data(self) -> Iterable[DBResult]:
        yield from self.data.values()

    def insert_tile_pool(self, name: str, owner: str, pool: TilePool) -> str | None:
        id_ = uuid4().hex
        self.data[id_] = {
            "owner": owner,
            "name": name,
            "tiles": pool,
            "id": id_,
            "created_at": datetime.datetime.now().isoformat(),
        }
        return id_

    def delete_tile_pool(self, tile_pool_id: str) -> bool:
        try:
            del self.data[tile_pool_id]
            return True
        except KeyError:
            pass
        return False

    def delete_tile_pool_by_owner(self, owner: str) -> bool:
        try:
            ids_to_delete = [id_ for id_ in self.data if self.data[id_]["owner"] == owner]
            for id_ in ids_to_delete:
                del self.data[id_]
            return True
        except Exception:
            pass
        return False

    def update_tiles(
        self,
        tile_pool_id: str,
        removals: list[str] | None = None,
        insertions: list[Tile] | None = None,
    ) -> bool:
        if (not removals and not insertions) or tile_pool_id not in self.data:
            return False
        try:
            if removals:
                old_pool = self.data[tile_pool_id]["tiles"]
                new_tiles = frozenset(tile for tile in old_pool.tiles if tile.text not in removals)
                self.data[tile_pool_id]["tiles"] = TilePool(new_tiles, old_pool.free)

            if insertions:
                old_pool = self.data[tile_pool_id]["tiles"]
                new_pool = TilePool(frozenset(insertions))
                self.data[tile_pool_id]["tiles"] += new_pool

            return True

        except KeyError:
            pass
        return False

    def get_tile_pools(
        self,
        size: int | None = None,
        page: int | None = None,
        sort: SortMethod = SortMethod.DEFAULT,
        sort_asc: bool = True,
    ) -> list[DBResult] | None:
        count = len(self.data)
        # TODO: make sure page number is not too large
        if (size is not None and size < 1) or count == 0 or (page is not None and page < 1):
            return

        start, end = self.paginate(count, size, page)
        lst = self.sort(self._iter_data(), sort, sort_asc)

        return lst[start:end]

    def get_tile_pool(self, tile_pool_id: str) -> DBResult | None:
        try:
            return self.data[tile_pool_id]
        except KeyError:
            return
