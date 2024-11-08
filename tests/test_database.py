import mongomock
import pytest

from src.data import mongo
from src.game.game import Tile, TilePool

DB_NAME = "BingoMakerTestDB"
COLLECTION_NAME = "BingoMakerTestCollection"


class TilePoolDBTest(mongo.TilePoolDB):
    def __init__(self):
        self.client = mongomock.MongoClient()
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION_NAME]
        self.collection.create_index("Name", unique=True)


@pytest.fixture
def db():
    return TilePoolDBTest()


@pytest.fixture
def one_pool(db: TilePoolDBTest):
    free_tile = Tile("Free")
    tiles = frozenset(Tile(f"{i}") for i in range(3))
    pool = TilePool(tiles, free_tile)
    pool_id = db.insert_tile_pool("NAME", "owner", pool)
    assert pool_id is not None
    return db, pool_id


@pytest.fixture
def many_pools(db: TilePoolDBTest):
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


def test_insert_query(db: TilePoolDBTest):
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


def test_insert_delete(one_pool: tuple[TilePoolDBTest, str]):
    db, pool_id = one_pool
    assert db.delete_tile_pool(pool_id)
    assert db.get_tile_pool(pool_id) is None


def test_get_quantity_tile_pools(many_pools: tuple[TilePoolDBTest, list[str]]):
    db, pool_ids = many_pools
    assert db.get_tile_pools(0) is None
    assert db.get_tile_pools(-1) is None

    results = db.get_tile_pools(5)
    assert results is not None

    for result in results:
        assert result["id"] in pool_ids
        assert result["owner"] == "owner"


def test_delete_by_owner(many_pools: tuple[TilePoolDBTest, list[str]]):
    db, pool_ids = many_pools
    assert db.delete_tile_pool_by_owner("owner")
    for pool_id in pool_ids:
        assert db.get_tile_pool(pool_id) is None


def test_remove_tiles(one_pool: tuple[TilePoolDBTest, str]):
    db, pool_id = one_pool

    assert db.update_tiles(pool_id, ["0", "1", "2"])

    result = db.get_tile_pool(pool_id)
    assert result

    tiles = result["tiles"].tiles
    assert len(tiles) == 0


def test_add_tiles(one_pool: tuple[TilePoolDBTest, str]):
    db, pool_id = one_pool

    tiles = [Tile(f"{i}") for i in (4, 5, 6)]
    assert db.update_tiles(pool_id, insertions=tiles)

    result = db.get_tile_pool(pool_id)
    assert result

    tiles = result["tiles"].tiles
    assert len(tiles) == 6


def test_update_tiles(one_pool: tuple[TilePoolDBTest, str]):
    db, pool_id = one_pool

    tiles = [Tile(f"{i}") for i in (4, 5, 6)]
    assert db.update_tiles(pool_id, ["0", "1", "2"], insertions=tiles)

    result = db.get_tile_pool(pool_id)
    assert result

    tiles = result["tiles"].tiles
    assert len(tiles) == 3
    for tile in tiles:
        assert tile.text in ("4", "5", "6")
