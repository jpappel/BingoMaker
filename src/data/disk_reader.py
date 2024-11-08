import json
import os
import uuid
from pathlib import Path

from game.game import Tile, TilePool
from src.data.persistence import DBResult, TilePoolDB, tile_to_dict, dict_to_tile


def read_text(path: str) -> TilePool:
    tiles = []
    with open(path) as f:
        for line in f:
            tiles.append(Tile(line.strip()))

    return TilePool(frozenset(tiles))


class DiskTilePoolDB(TilePoolDB):
    def __init__(self, root_dir: str | Path):
        self.root = root_dir if isinstance(root_dir, Path) else Path(root_dir)

        if self.root.exists() and not self.root.is_dir():
            raise NotADirectoryError("path exists but is not a directory")

        if not self.root.exists():
            self.root.mkdir()

    def _find_first_by_id(self, tile_pool_id: str) -> Path | None:
        filename = f"{tile_pool_id}.json"
        for dirpath, _, filenames in self.root.walk():
            if filename in filenames:
                return dirpath / filename

    def insert_tile_pool(self, name: str, owner: str, pool: TilePool) -> str | None:
        dir_ = self.root / owner
        dir_.mkdir(exist_ok=True)

        id_ = uuid.uuid1().hex + ".json"
        with open(dir_ / id_, "w") as f:
            to_write = {
                "Owner": owner,
                "Name": name,
                "Tiles": [tile_to_dict(tile) for tile in pool.tiles],
                "CreatedAt": 0,
            }
            if pool.free:
                to_write["FreeTile"] = tile_to_dict(pool.free)
            json.dump(to_write, f)

    def delete_tile_pool(self, tile_pool_id: str) -> bool:
        try:
            filepath = self._find_first_by_id(tile_pool_id)
            if filepath:
                os.remove(filepath)
                return True
        except Exception as e:
            print(e)

        return False

    def delete_tile_pool_by_owner(self, owner: str) -> bool:
        dir_ = self.root / owner
        try:
            for _, _, filenames in dir_.walk():
                for filename in filenames:
                    filepath = dir_ / filename
                    os.remove(filepath)
            dir_.rmdir()
            return True
        except Exception as e:
            print(e)
        return False

    def update_tiles(
        self,
        tile_pool_id: str,
        removals: list[str] | None = None,
        insertions: list[Tile] | None = None,
    ) -> bool:
        if removals is None and insertions is None:
            return False

        try:
            result = self.get_tile_pool(tile_pool_id)
            if result is None:
                return False
            pool = result["tiles"]
            raise NotImplementedError()

        except Exception as e:
            print(e)
        return False

    def get_tile_pools(self, quantity: int | None = None) -> list[DBResult] | None:
        pass

    def get_tile_pool(self, tile_pool_id: str) -> DBResult | None:
        try:
            filepath = self._find_first_by_id(tile_pool_id)
            if filepath is None:
                return

            with open(filepath) as file:
                unparsed = json.load(file)
                tiles = frozenset(dict_to_tile(item) for item in unparsed["Tiles"])
                free = (
                    dict_to_tile(unparsed["FreeTile"])
                    if "FreeTile" in unparsed
                    else None
                )
                pool = TilePool(tiles, free)
                return {
                    "id": tile_pool_id,
                    "owner": unparsed["Owner"],
                    "name": unparsed["Name"],
                    "created_at": unparsed["CreatedAt"],
                    "tiles": pool,
                }
        except Exception as e:
            print(e)
