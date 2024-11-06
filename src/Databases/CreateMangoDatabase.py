import logging
from datetime import UTC, datetime

from bson.objectid import ObjectId
from pymongo import MongoClient, errors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TilePoolDB:
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

    def insert_tile_pool(
        self,
        name: str,
        tiles: list[str],
        owner: str,
        free_tile: str | None = None,
    ) -> str | None:
        """Insert a tile pool into the MongoDB collection."""

        timestamp = datetime.now(UTC)

        item = {
            "Owner": owner,
            "Name": name,
            "Tiles": tiles,
            "CreatedAt": timestamp.isoformat(),
        }

        if free_tile:
            item["FreeTile"] = free_tile

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
                logger.info(
                    f"Deleted {result.deleted_count} tile pools for owner '{owner}'."
                )
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
        insertions: list[Tiles] | None = None,
    ):
        """Update tiles within a tile pool.

        Removals are performed before insertions
        """
        if removals is None and insertions is None:
            return False

        try:
            operation = {}
            if removals is not None:
                operation["$pull"] = {"Tiles": {"Content": {"$in": removals}}}
            if insertions is not None:
                # TODO: correctly parse insertions
                operation["$set"] = {}
            if removals is not None:
                self.collection.update_one(
                    {"_id": tile_pool_id},
                    operation,
                )
            return True
        except Exception as e:
            logger.error(f"Failed to update tile pool {tile_pool_id}: {str(e)}")
        return False

    def delete_specific_tiles(
        self,
        tile_pool_id: str,
        tiles_to_delete: list[str],
    ) -> bool:
        """Delete specific tiles from a tile pool"""
        try:
            tile_pool = self.collection.find_one({"TilePoolId": tile_pool_id})
            if tile_pool is None:
                logger.info(f"Tile pool with TilePoolId '{tile_pool_id}' not found.")
                return False

            # Remove specified tiles
            updated_tiles = [
                tile for tile in tile_pool["Tiles"] if tile not in tiles_to_delete
            ]
            result = self.collection.update_one(
                {"TilePoolId": tile_pool_id}, {"$set": {"Tiles": updated_tiles}}
            )
            if result.modified_count > 0:
                logger.info(
                    f"Tiles {tiles_to_delete} deleted from tile pool '{tile_pool_id}'."
                )
                return True
        except Exception as e:
            logger.error(f"Failed to delete tiles from tile pool: {str(e)}")
        return False

    def get_tile_pools(self, quantity: int | None = None):
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
            return items

        except Exception as e:
            print(f"Failed to retrieve tile pools: {str(e)}")
            return

    def get_tile_pool(
        self,
        tile_pool_id: str,
    ):
        try:
            item = self.collection.find_one({"_id": ObjectId(tile_pool_id)})
            return item

        except Exception as e:
            print(f"Failed to retrieve tile pool: {str(e)}")
        return None
