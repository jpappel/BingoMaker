import json
import logging
import os
from datetime import UTC, datetime

from bson import ObjectId, json_util
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
            self.collection.create_index("TilePoolName", unique=True)
            logger.info("Unique index created for 'TilePoolName'.")
        except errors.ConnectionError as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")

    def insert_tile_pool(
        self,
        tile_pool_name: str,
        tiles: list[str],
        owner: str,
        is_admin: bool = False,
        free_tile: str | None = None,
    ) -> str | None:
        """Insert a tile pool into the MongoDB collection.
        Only the owner or an admin can perform this operation.
        """
        if not is_admin:
            logger.error("Only admins can add a new tile pool.")
            return None

        timestamp = datetime.now(UTC)
        tile_pool_id = f"{tile_pool_name}-{int(timestamp.timestamp())}"

        item = {
            "TilePoolId": tile_pool_id,
            "Owner": owner,
            "TilePoolName": tile_pool_name,
            "Tiles": tiles,
            "CreatedAt": timestamp.isoformat(),
        }

        if free_tile:
            item["FreeTile"] = free_tile

        try:
            result = self.collection.insert_one(item)
            logger.info(
                f"Tile pool '{tile_pool_name}' (ID: {tile_pool_id})\
                      added successfully for owner '{owner}'."
            )
            return str(result.inserted_id)
        except errors.DuplicateKeyError:
            logger.warning(
                f"Tile pool with TilePoolName '{tile_pool_name}' already exists."
            )
        except Exception as e:
            logger.error(f"Failed to insert tile pool: {str(e)}")
        return None

    def delete_tile_pool(
        self, tile_pool_id: str, requester: str, is_admin: bool = False
    ) -> bool:
        """Delete a tile pool document by its TilePoolId if 
        the requester is the owner or an admin."""
        try:
            tile_pool = self.collection.find_one({"TilePoolId": tile_pool_id})
            if tile_pool is None:
                logger.info(f"Tile pool with TilePoolId '{tile_pool_id}' not found.")
                return False

            if tile_pool["Owner"] != requester and not is_admin:
                logger.error("Only the owner or an admin can delete this tile pool.")
                return False

            result = self.collection.delete_one({"TilePoolId": tile_pool_id})
            if result.deleted_count > 0:
                logger.info(
                    f"Tile pool with TilePoolId '{tile_pool_id}' deleted successfully."
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete tile pool: {str(e)}")
            return False

    def delete_tile_pool_by_owner(
        self, owner: str, requester: str, is_admin: bool = False
    ) -> bool:
        """Delete all tile pools for a specific owner if the requester is the owner or an admin."""
        if requester != owner and not is_admin:
            logger.error(
                "Only the owner or an admin can delete all tile pools for this owner."
            )
            return False

        try:
            result = self.collection.delete_many({"Owner": owner})
            if result.deleted_count > 0:
                logger.info(
                    f"Deleted {result.deleted_count} tile pools for owner '{owner}'."
                )
                return True
            else:
                logger.info(f"No tile pools found for owner '{owner}'.")
                return False
        except Exception as e:
            logger.error(f"Failed to delete tile pools for owner '{owner}': {str(e)}")
            return False

    def delete_specific_tiles(
        self,
        tile_pool_id: str,
        tiles_to_delete: list[str],
        requester: str,
        is_admin: bool = False,
    ) -> bool:
        """Delete specific tiles from a tile pool if the requester is the owner or an admin."""
        try:
            tile_pool = self.collection.find_one({"TilePoolId": tile_pool_id})
            if tile_pool is None:
                logger.info(f"Tile pool with TilePoolId '{tile_pool_id}' not found.")
                return False

            if tile_pool["Owner"] != requester and not is_admin:
                logger.error(
                    "Only the owner or an admin can delete tiles from this tile pool."
                )
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
            return False
        except Exception as e:
            logger.error(f"Failed to delete tiles from tile pool: {str(e)}")
            return False

    def save_tile_pool_to_json(self, tile_pool: dict, filename: str) -> None:
        """Save a tile pool document to a JSON file by appending to an array."""
        try:
            data = []
            # Load existing data if file exists
            if os.path.exists(filename):
                with open(filename) as f:
                    try:
                        data = json.load(f)
                        if not isinstance(data, list):
                            data = [data]
                    except json.JSONDecodeError:
                        logger.warning(
                            "Existing JSON file is invalid or empty, starting with an empty list."
                        )

            # Append the new tile pool data
            data.append(tile_pool)

            # Write the updated data back to the file
            with open(filename, "w") as f:
                json.dump(data, f, default=json_util.default, indent=4)
            logger.info(f"Tile pool appended and saved to {filename}")

        except Exception as e:
            logger.error(f"Failed to save tile pool to file: {str(e)}")


if __name__ == "__main__":
    db = TilePoolDB("mongodb://localhost:27017/", "BingoBakerDB", "TilePools")

    tile_pool_name = "example-tilepool4"
    tiles = ["tile1", "tile2", "tile3"]
    owner = "us-east-1:example-cognito-id"

    # Insert only if user is an admin
    result = db.insert_tile_pool(tile_pool_name, tiles, owner, is_admin=True)

    if result:
        tile_pool = db.collection.find_one({"_id": ObjectId(result)})
        logger.info(f"Retrieved tile pool: {tile_pool}")
        db.save_tile_pool_to_json(tile_pool, "tile_pool.json")
    else:
        logger.error("Failed to insert tile pool.")

    # Delete specific tiles if the user is the owner

    # Clean up all data if user is admin
    if is_admin := True:
        db.collection.delete_many({})
        print("deleted all data")
