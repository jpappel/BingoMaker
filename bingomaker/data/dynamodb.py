import contextlib
import datetime
from uuid import uuid4

import boto3
from data.persistence import DBResult, SortMethod, TilePoolDB, tile_to_dict
from game.game import Tile, TilePool


class DynamoTilePoolDB(TilePoolDB):
    def __init__(self, table_name: str = "BingoMaker", endpoint_url: str = "https://amazonaws.com"):
        self.client = boto3.client("dynamodb", region_name="us-east-1", endpoint_url=endpoint_url)
        self.table_name = table_name

        with contextlib.suppress(Exception):
            self.client.create_table(
                TableName=table_name,
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
                ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
            )

    def _dict_to_dynamodb(self, attr_dict):
        """Convert a standard dictionary to DynamoDB format."""
        dynamodb_dict = {}

        for key, value in attr_dict.items():
            # String
            if isinstance(value, str):
                dynamodb_dict[key] = {"S": value}
            # Number (int or float)
            elif isinstance(value, int | float):
                dynamodb_dict[key] = {"N": str(value)}
            # Boolean
            elif isinstance(value, bool):
                dynamodb_dict[key] = {"BOOL": value}
            # NoneType
            elif value is None:
                dynamodb_dict[key] = {"NULL": True}
            # List
            elif isinstance(value, list):
                dynamodb_dict[key] = {"L": [self._dict_to_dynamodb({"": v})[""] for v in value]}
            # Dictionary
            elif isinstance(value, dict):
                dynamodb_dict[key] = {"M": self._dict_to_dynamodb(value)}
            else:
                raise TypeError(f"Unsupported type for {key}: {type(value)}")

        return dynamodb_dict

    def _dynamodb_to_dict(self, dynamodb_dict):
        """Convert a DynamoDB formatted dictionary to a standard Python dictionary."""
        attr_dict = {}

        for key, value in dynamodb_dict.items():
            # Process each attribute type
            if "S" in value:
                attr_dict[key] = value["S"]
            elif "N" in value:
                attr_dict[key] = float(value["N"]) if "." in value["N"] else int(value["N"])
            elif "BOOL" in value:
                attr_dict[key] = value["BOOL"]
            elif "NULL" in value:
                attr_dict[key] = None
            elif "L" in value:
                attr_dict[key] = [self._dynamodb_to_dict({"": v})[""] for v in value["L"]]
            elif "M" in value:
                attr_dict[key] = self._dynamodb_to_dict(value["M"])
            else:
                raise TypeError(f"Unsupported DynamoDB type for {key}")

        return attr_dict

    def insert_tile_pool(self, name: str, owner: str, pool: TilePool) -> str | None:
        id_ = uuid4().hex
        data = self._dict_to_dynamodb(
            {
                "id": id_,
                "owner": owner,
                "name": name,
                "tiles": [
                    {
                        "content": tile.text,
                        "tags": list(tile.tags),
                        "imageUrl": tile.image_url,
                    }
                    for tile in pool.tiles
                ],
                "createdAt": datetime.datetime.now().isoformat(),
                "freeTile": {
                    "content": pool.free.text,
                    "tags": list(pool.free.tags),
                    "imageUrl": pool.free.image_url,
                },
            }
        )
        self.client.put_item(TableName=self.table_name, Item=data)

        return id_

    def delete_tile_pool(self, tile_pool_id: str) -> bool:
        print(f"Deleting tile pool with ID: {tile_pool_id}")
        try:
            self.client.delete_item(TableName=self.table_name, Key={"id": {"S": tile_pool_id}})
            print("Deletion successful")
            return True
        except Exception as e:
            print(f"Error deleting tile pool: {e}")
            return False

    def delete_tile_pool_by_owner(self, owner: str) -> bool:
        try:
            # Use expression attribute names to avoid the reserved keyword issue
            response = self.client.scan(
                TableName=self.table_name,
                FilterExpression="#o = :owner",
                ExpressionAttributeNames={"#o": "owner"},
                ExpressionAttributeValues={":owner": {"S": owner}},
            )

            # Extract the IDs of items to delete
            items = response.get("Items", [])
            print(f"Found {len(items)} items to delete for owner '{owner}'")

            # Delete each item individually
            for item in items:
                item = self._dynamodb_to_dict(item)
                id_ = item["id"]
                self.client.delete_item(TableName=self.table_name, Key={"id": {"S": id_}})
                print(f"Deleted item with id: {id_}")

            print("Deletion successful")
            return True
        except Exception as e:
            print(f"Error deleting items by owner: {e}")
            return False

    def update_tiles(self, tile_pool_id, removals=None, insertions=None):
        print(
            f"Updating tiles for pool ID: {tile_pool_id}, \
                removals: {removals}, insertions: {insertions}"
        )
        if removals is None and insertions is None:
            print("No changes to update")
            return False

        current_pool = self.get_tile_pool(tile_pool_id)
        if current_pool is None:
            print("Tile pool not found")
            return False

        try:
            if removals:
                old_pool = current_pool["tiles"]
                new_tiles = frozenset(tile for tile in old_pool.tiles if tile.text not in removals)
                self._update_tiles(tile_pool_id, new_tiles)
                print("Removed tiles successfully")

            if removals and insertions:
                current_pool = self.get_tile_pool(tile_pool_id)
                if current_pool is None:
                    print("Tile pool not found")
                    return False

            if insertions:
                old_pool = current_pool["tiles"]

                new_pool = list(old_pool.tiles) + insertions
                print(f"New pool: {new_pool}")

                self._update_tiles(tile_pool_id, new_pool)
                print("Inserted tiles successfully")

            return True
        except Exception as e:
            print(f"Error updating tiles: {e}")
            return False

    def _update_tiles(self, tile_pool_id, new_pool):
        print(f"Updating pool for ID: {tile_pool_id} with new pool data")

        new_tiles_list = [tile_to_dict(tile) for tile in new_pool]

        new_pool_dynamodb = self._dict_to_dynamodb({"new_pool": new_tiles_list})

        try:
            self.client.update_item(
                TableName=self.table_name,
                Key={"id": {"S": tile_pool_id}},
                UpdateExpression="SET tiles = :new_pool",
                ExpressionAttributeValues={":new_pool": new_pool_dynamodb["new_pool"]},
            )
            print("Update successful")
            return True
        except Exception as e:
            print(f"Error in _update_tiles: {e}")
            return False

    def get_tile_pools(self, size=None, page=None, sort=SortMethod.DEFAULT, sort_asc=True):
        print(
            f"Getting tile pools, size: {size}, page: {page}, sort: {sort}, ascending: {sort_asc}"
        )

        if size is None or size < 1:
            print(f"Invalid quantity: {size}")
            return

        response = self.client.scan(TableName=self.table_name)
        items = [self._dynamodb_to_dict(item) for item in response.get("Items", [])]

        sorted_items = self.sort(items, sort, sort_asc)

        start_index, end_index = self.paginate(len(sorted_items), size, page)
        paginated_items = sorted_items[start_index:end_index]

        return paginated_items

    def get_tile_pool(self, tile_pool_id: str) -> DBResult | None:
        print(f"Retrieving tile pool with ID: {tile_pool_id}")
        try:
            response = self.client.get_item(
                TableName=self.table_name, Key={"id": {"S": tile_pool_id}}
            )

            if "Item" in response:
                item = self._dynamodb_to_dict(response["Item"])

                tiles_data = item["tiles"]
                tiles = frozenset(
                    Tile(
                        text=tile.get("content"),
                        tags=frozenset(tag for tag in tile.get("tags")),
                        image_url=tile.get("imageUrl") or None,
                    )
                    for tile in tiles_data
                )

                free_tile_data = item.get("freeTile", {})
                img_url = free_tile_data.get("imageUrl", "")
                if not img_url:
                    img_url = None
                free = Tile(
                    text=free_tile_data.get("content", ""),
                    tags=frozenset(free_tile_data.get("tags", [])),
                    image_url=img_url,
                )

                print(f"!!Free tile: {free}")
                pool = TilePool(tiles, free)

                # Create the DBResult using standard dictionary accesses
                db_result: DBResult = {
                    "owner": item["owner"],
                    "name": item["name"],
                    "tiles": pool,
                    "id": item["id"],
                    "created_at": item["createdAt"],
                }
                print(f"Tile pool retrieved successfully: {db_result}")
                return db_result

            print("Tile pool not found")
            return None
        except Exception as e:
            print(type(e), e)
            print(f"Error retrieving tile pool: {e}")
            return None
