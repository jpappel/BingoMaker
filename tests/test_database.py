import boto3
import mongomock
import pytest
from botocore.client import ClientError

from src.data import DynamoTilePoolDB, FileTilePoolDB, MemoryTilePoolDB, mongo
from src.data.persistence import TilePoolDB
from src.game.game import Tile, TilePool

DB_NAME = "BingoMakerTestDB"
COLLECTION_NAME = "BingoMakerTestCollection"


class MongoTilePoolDBTest(mongo.MongoTilePoolDB):
    def __init__(self):
        self.client = mongomock.MongoClient()
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION_NAME]
        self.collection.create_index("Name", unique=True)


class DynamoTilePoolDBTest(DynamoTilePoolDB):
    def __init__(self):
        self.client = boto3.client(
            "dynamodb",
            region_name="us-east-1",
            endpoint_url="http://localhost.localstack.cloud:4566",
            aws_access_key_id="notARealAccessKey",
            aws_secret_access_key="notARealSecretKey",
        )
        self.table_name = "TestBingoMaker"

        try:
            self.client.delete_table(TableName=self.table_name)
        except ClientError as e:
            print(e)
        finally:
            self.client.create_table(
                TableName=self.table_name,
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
                ProvisionedThroughput={"ReadCapacityUnits": 1, "WriteCapacityUnits": 1},
            )


@pytest.fixture(
    params=[MongoTilePoolDBTest, FileTilePoolDB, MemoryTilePoolDB, DynamoTilePoolDBTest]
)
def db(request, tmp_path):
    driver = request.param(tmp_path) if request.param is FileTilePoolDB else request.param()
    return driver


@pytest.fixture
def one_pool(db: TilePoolDB):
    free_tile = Tile("Free")
    tiles = frozenset(Tile(f"{i}") for i in range(3))
    pool = TilePool(tiles, free_tile)
    pool_id = db.insert_tile_pool("NAME", "owner", pool)
    assert pool_id is not None
    return db, pool_id


@pytest.fixture
def many_pools(db: TilePoolDB):
    pool_ids: list[str] = []
    for i in range(10):
        free = Tile(f"Free {i}")
        tiles = frozenset(Tile(f"{j+i}") for j in range(3))
        pool = TilePool(tiles, free)

        name = f"Pool {i}"
        pool_id = db.insert_tile_pool(name, "owner", pool)
        assert pool_id is not None
        pool_ids.append(pool_id)
    return db, pool_ids


class TestTilePoolDB:
    def test_insert_query(self, db: TilePoolDB):
        free_tile = Tile("Free")
        tiles = frozenset(Tile(f"{i}") for i in range(3))
        in_pool = TilePool(tiles, free_tile)
        pool_id = db.insert_tile_pool("NAME", "owner", in_pool)
        assert pool_id is not None

        result = db.get_tile_pool(pool_id)
        assert result is not None

        assert result["owner"] == "owner"
        assert result["name"] == "NAME"
        for tile in result["tiles"].tiles:
            assert tile in in_pool.tiles
        # assert result["tiles"].tiles == in_pool.tiles
        assert result["tiles"].free == in_pool.free

    def test_insert_delete(self, one_pool: tuple[TilePoolDB, str]):
        db, pool_id = one_pool
        assert db.delete_tile_pool(pool_id)
        assert db.get_tile_pool(pool_id) is None

    def test_get_quantity_tile_pools(self, many_pools: tuple[TilePoolDB, list[str]]):
        db, pool_ids = many_pools
        assert db.get_tile_pools(0) is None
        assert db.get_tile_pools(-1) is None

        results = db.get_tile_pools(5)
        assert results is not None

        for result in results:
            assert result["id"] in pool_ids
            assert result["owner"] == "owner"

    def test_delete_by_owner(self, many_pools: tuple[TilePoolDB, list[str]]):
        db, pool_ids = many_pools
        assert db.delete_tile_pool_by_owner("owner")
        for pool_id in pool_ids:
            assert db.get_tile_pool(pool_id) is None

    def test_remove_tiles(self, one_pool: tuple[TilePoolDB, str]):
        db, pool_id = one_pool

        assert db.update_tiles(pool_id, ["0", "1", "2"])

        result = db.get_tile_pool(pool_id)
        assert result

        tiles = result["tiles"].tiles
        assert len(tiles) == 0

    def test_add_tiles(self, one_pool: tuple[TilePoolDB, str]):
        db, pool_id = one_pool

        tiles = [Tile(f"{i}") for i in (4, 5, 6)]
        assert db.update_tiles(pool_id, insertions=tiles)

        result = db.get_tile_pool(pool_id)
        assert result

        tiles = result["tiles"].tiles
        assert len(tiles) == 6

    def test_update_tiles(self, one_pool: tuple[TilePoolDB, str]):
        db, pool_id = one_pool

        tiles = [Tile(f"{i}") for i in (4, 5, 6)]
        assert db.update_tiles(pool_id, ["0", "1", "2"], insertions=tiles)

        result = db.get_tile_pool(pool_id)
        assert result

        tiles = result["tiles"].tiles
        assert len(tiles) == 3
        for tile in tiles:
            assert tile.text in ("4", "5", "6")
