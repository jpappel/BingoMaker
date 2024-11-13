import datetime
from collections.abc import Iterable
from uuid import uuid4

import boto3

from data.persistence import DBResult, SortMethod, TilePoolDB
from game.game import Tile, TilePool


class DynamoTilePoolDB(TilePoolDB):
    def __init__(self):
        self.client = boto3.client("dynamodb")

    def _iter_data(self) -> Iterable[DBResult]:
        pass

    def insert_tile_pool(self, name: str, owner: str, pool: TilePool) -> str | None:
        id_ = uuid4().hex
        data = {
            "id": id_,
            "owner": owner,
            "name": name,
            "tiles": pool,
            "createdAt": datetime.datetime.now().isoformat(),
            "freeTile": pool.free,
        }

        try:
            self.client.put_item(TableName="BingoMaker", Item=data)

        except Exception:
            return None

        return id_

    def delete_tile_pool(self, tile_pool_id: str) -> bool:
        try:
            self.client.delete_item(TableName="BingoMaker", Key={"id": tile_pool_id})

            return True
        except Exception:
            return False

    def delete_tile_pool_by_owner(self, owner: str) -> bool:
        try:
            self.client.delete_item(TableName="BingoMaker", Key={"owner": owner})

            return True
        except Exception:
            return False

    def update_tiles(self, tile_pool_id, removals=None, insertions=None):
        print(
            f"Updating tiles for pool ID: {tile_pool_id},\
                removals: {removals}, insertions: {insertions}"
        )
        if removals is None and insertions is None:
            return False

        current_pool = self.get_tile_pool(tile_pool_id)
        if current_pool is None:
            return False

        try:
            if removals:
                old_pool = current_pool["tiles"]
                new_tiles = frozenset(tile for tile in old_pool.tiles if tile.text not in removals)
                self._update_tiles(tile_pool_id, new_tiles)

            if insertions:
                old_pool = current_pool["tiles"]
                new_pool = TilePool(frozenset(insertions))
                self._update_tiles(tile_pool_id, new_pool)

            return True
        except Exception:
            return False

    def _update_tiles(self, tile_pool_id, new_pool):
        try:
            self.client.update_item(
                TableName="BingoMaker",
                Key={"id": tile_pool_id},
                UpdateExpression="SET tiles = :new_pool",
                ExpressionAttributeValues={":new_pool": new_pool},
            )

            return True
        except Exception:
            return False

    def get_tile_pools(self, size=None, page=None, sort=SortMethod.DEFAULT, sort_asc=True):
        print(
            f"Getting tile pools, size: {size}, page: {page}, sort: {sort}, ascending: {sort_asc}"
        )
        if (size is not None and size < 1) or (page is not None and page < 1):
            return
        pass

    def get_tile_pool(self, tile_pool_id: str) -> DBResult | None:
        try:
            response = self.client.get_item(TableName="BingoMaker", Key={"id": {"S": tile_pool_id}})

            if "Item" in response:
                item = response["Item"]

                # Extract values from the DynamoDB attributes
                tiles_data = item["tiles"]["L"]  # List of map items
                tiles = frozenset(
                    Tile(
                        text=tile["M"]["text"]["S"],
                        tags=frozenset(tag["S"] for tag in tile["M"]["tags"]["L"]),
                        image_url=tile["M"]["imageUrl"]["S"]
                        if tile["M"]["imageUrl"]["S"]
                        else None,
                    )
                    for tile in tiles_data
                )
                free = item.get("freeTile", {}).get("S", None)
                pool = TilePool(tiles, free)

                # Create the DBResult
                db_result: DBResult = {
                    "owner": item["owner"]["S"],
                    "name": item["name"]["S"],
                    "tiles": pool,
                    "id": item["id"]["S"],
                    "created_at": item["createdAt"]["S"],
                }

                return db_result

            return None
        except Exception:
            return None
