import json
import os
import uuid
from collections.abc import Iterable
from pathlib import Path
from typing import TextIO

from data.persistence import DBResult, TilePoolDB, dict_to_tile, tile_to_dict
from game.game import Tile, TilePool


def read_text(path: str) -> TilePool:
    tiles = []
    with open(path) as f:
        for line in f:
            text = line.strip()
            tiles.append(Tile(text, frozenset([text])))

    return TilePool(frozenset(tiles))


class FileTilePoolDB(TilePoolDB):
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

    def _iterate_over_pools(self) -> Iterable[tuple[Path, str]]:
        for dirpath, _, filenames in self.root.walk():
            for filename in filenames:
                if not filename.endswith(".json"):
                    continue
                id_ = filename.rstrip(".json")
                yield dirpath / filename, id_

    def _parse(self, fp: TextIO, id_: str) -> DBResult:
        unparsed = json.load(fp)
        tiles = frozenset(dict_to_tile(item) for item in unparsed["Tiles"])
        free = dict_to_tile(unparsed["FreeTile"]) if "FreeTile" in unparsed else None
        pool = TilePool(tiles, free)
        return {
            "id": id_,
            "owner": unparsed["Owner"],
            "name": unparsed["Name"],
            "created_at": unparsed["CreatedAt"],
            "tiles": pool,
        }

    def insert_tile_pool(self, name: str, owner: str, pool: TilePool) -> str | None:
        dir_ = self.root / owner
        dir_.mkdir(exist_ok=True)

        id_ = uuid.uuid1().hex
        with open(dir_ / (id_ + ".json"), "w") as f:
            to_write = {
                "Owner": owner,
                "Name": name,
                "Tiles": [tile_to_dict(tile) for tile in pool.tiles],
                "CreatedAt": 0,
            }
            if pool.free:
                to_write["FreeTile"] = tile_to_dict(pool.free)
            json.dump(to_write, f)

        return id_

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
            if result is None or (not removals and not insertions):
                return False

            if removals:
                old_pool = result["tiles"]
                new_tiles = frozenset(tile for tile in old_pool.tiles if tile.text not in removals)
                result["tiles"] = TilePool(new_tiles, old_pool.free)

            if insertions:
                old_pool = result["tiles"]
                new_pool = TilePool(frozenset(insertions))
                result["tiles"] += new_pool

            filepath = self._find_first_by_id(tile_pool_id)
            if filepath is None:
                return False

            with open(filepath, "w") as f:
                to_write = {
                    "Owner": result["owner"],
                    "Name": result["name"],
                    "Tiles": [tile_to_dict(tile) for tile in result["tiles"].tiles],
                    "CreatedAt": result["created_at"],
                }
                if result["tiles"].free:
                    to_write["FreeTile"] = tile_to_dict(result["tiles"].free)
                json.dump(to_write, f)

            return True

        except Exception as e:
            print(e)
        return False

    def get_tile_pools(self, quantity: int | None = None) -> list[DBResult] | None:
        if quantity is not None and quantity < 1:
            print(f"Invalid quantity: {quantity}")
            return

        try:
            results = []
            for filepath, tile_pool_id in self._iterate_over_pools():
                with open(filepath) as file:
                    results.append(self._parse(file, tile_pool_id))

            return results
        except Exception as e:
            print("Failed to retrieve tile pools:", str(e))
            return

    def get_tile_pool(self, tile_pool_id: str) -> DBResult | None:
        try:
            filepath = self._find_first_by_id(tile_pool_id)
            if filepath is None:
                return

            with open(filepath) as file:
                return self._parse(file, tile_pool_id)
        except Exception as e:
            print(e)
