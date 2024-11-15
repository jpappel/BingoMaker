import logging
from datetime import UTC, datetime
from typing import TypedDict

from bson.objectid import ObjectId
from pymongo import MongoClient, errors

from src.game.game import Tile, TilePool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _tile_to_dict(tile: Tile) -> dict[str, str | list[str]]:
    return {
        "Content": tile.text if tile.image_url is None else tile.image_url,
        "Type": "text" if tile.image_url is None else "image",
        "Tags": list(tile.tags),
    }


def _dict_to_tile(item: dict[str, str | list[str]]) -> Tile:
    text = item["Content"]
    assert isinstance(text, str)
    tags = frozenset(item["Tags"])
    image_url = item["Content"] if item["Type"] == "image" else None
    assert isinstance(image_url, str) or image_url is None
    return Tile(text, tags, image_url)


class DBResult(TypedDict):
    owner: str
    name: str
    tiles: TilePool
    id: str
    created_at: str


class MongoTilePoolDB:
    def __init__(self, uri: str, database_name: str, collection_name: str):
        try:
            self.client = MongoClient(uri)
            self.db = self.client[database_name]
            self.collection = self.db[collection_name]
            logger.info(
                f"Connected to MongoDB collection '{collection_name}' \
                    in database '{database_name}'."
            )
            self.collection.create_index("Name", unique=True)
            logger.info("Unique index created for 'Name'.")
        except errors.ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")

    def insert_tile_pool(self, name: str, owner: str, pool: TilePool) -> str | None:
        """Insert a tile pool into the MongoDB collection."""

        timestamp = datetime.now(UTC)

        tiles = list(_tile_to_dict(tile) for tile in pool.tiles)

        item = {
            "Owner": owner,
            "Name": name,
            "Tiles": tiles,
            "CreatedAt": timestamp.isoformat(),
        }

        if pool.free:
            item["FreeTile"] = _tile_to_dict(pool.free)

        try:
            result = self.collection.insert_one(item)
            logger.info(f"{owner} created tile pool '{name}' ({result.inserted_id})")
            return str(result.inserted_id)
        except errors.DuplicateKeyError:
            logger.warning(f"Tile pool '{name}' already exists.")
        except Exception as e:
            logger.error(f"Failed to insert tile pool: {str(e)}")
        return None

    def delete_tile_pool(self, tile_pool_id: str) -> bool:
        """Delete a tile pool document by its TilePoolId"""
        try:
            result = self.collection.delete_one({"_id": ObjectId(tile_pool_id)})

            if result.deleted_count > 0:
                logger.info(f"Deleted Tile Pool ({tile_pool_id})")
                return True
        except Exception as e:
            logger.error(f"Failed to delete tile pool: {str(e)}")
        return False

    def delete_tile_pool_by_owner(self, owner: str) -> bool:
        """Delete all tile pools for a specific owner."""
        try:
            result = self.collection.delete_many({"Owner": owner})
            if result.deleted_count > 0:
                logger.info(f"Deleted {result.deleted_count} tile pools for owner '{owner}'.")
                return True
            else:
                logger.info(f"No tile pools found for owner '{owner}'.")
        except Exception as e:
            logger.error(f"Failed to delete tile pools for owner '{owner}': {str(e)}")
        return False

    def update_tiles(
        self,
        tile_pool_id: str,
        removals: list[str] | None = None,
        insertions: list[Tile] | None = None,
    ):
        """Update tiles within a tile pool.

        Removals are performed before insertions
        """
        if removals is None and insertions is None:
            return False

        try:
            operation = {}
            if removals:
                operation["$pull"] = {"Tiles": {"Content": {"$in": removals}}}
            if insertions:
                operation["$push"] = {
                    "Tiles": {"$each": [_tile_to_dict(tile) for tile in insertions]}
                }
            result = self.collection.find_one_and_update(
                {"_id": ObjectId(tile_pool_id)},
                operation,
            )
            return result is not None
        except Exception as e:
            logger.error(f"Failed to update tile pool {tile_pool_id}: {str(e)}")
        return False

    def get_tile_pools(self, quantity: int | None = None) -> list[DBResult] | None:
        """Get multiple tile pools from the database, defaults to all"""
        if quantity is not None and quantity < 1:
            print(f"Invalid quantity: {quantity}")
            return

        try:
            items = (
                list(self.collection.find())
                if quantity is None
                else list(self.collection.find(batch_size=quantity))
            )
            results = []
            for item in items:
                tiles = frozenset(_dict_to_tile(tile) for tile in item["Tiles"])
                free = _dict_to_tile(item["FreeTile"]) if "FreeTile" in item else None
                pool = TilePool(tiles, free)
                results.append(
                    {
                        "owner": item["Owner"],
                        "name": item["Name"],
                        "tiles": pool,
                        "id": str(item["_id"]),
                        "created_at": item["CreatedAt"],
                    }
                )
            return results

        except Exception as e:
            print(f"Failed to retrieve tile pools: {str(e)}")
            return

    def get_tile_pool(
        self,
        tile_pool_id: str,
    ) -> DBResult | None:
        try:
            item = self.collection.find_one({"_id": ObjectId(tile_pool_id)})
            if item is not None:
                tiles = frozenset(_dict_to_tile(tile) for tile in item["Tiles"])
                free = _dict_to_tile(item["FreeTile"]) if "FreeTile" in item else None
                pool = TilePool(tiles, free)
                return {
                    "owner": item["Owner"],
                    "name": item["Name"],
                    "tiles": pool,
                    "id": str(item["_id"]),
                    "created_at": item["CreatedAt"],
                }

        except Exception as e:
            print(f"Failed to retrieve tile pool: {str(e)}")
        return
