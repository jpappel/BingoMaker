from datetime import datetime

import pytest
from flask import Flask
from flask.testing import FlaskClient

from src.app import create_app
from src.data import MemoryTilePoolDB
from src.data.persistence import DBResult, TilePoolDB, dict_to_tile, tile_to_dict
from src.game.game import Tile, TilePool

EXAMPLES: dict[str, DBResult] = {
    "basic": {
        "owner": "owner",
        "tiles": TilePool(
            frozenset(Tile(f"{j}", frozenset([f"{j}"])) for j in range(25)), Tile("Free")
        ),
        "name": "Basic Pool",
        "created_at": "2024-11-08T01:02:03",
        "id": "basic",
    },
    "no_free": {
        "owner": "some owner",
        "tiles": TilePool(frozenset(Tile(f"{j}", frozenset([f"{j}"])) for j in range(25))),
        "name": "No Free Tile",
        "created_at": "2024-11-09T01:02:03",
        "id": "no_free",
    },
    "update_me": {
        "owner": "absent owner",
        "tiles": TilePool(frozenset(Tile(f"{j}", frozenset([f"{j}"])) for j in range(25))),
        "name": "Will be updated :)",
        "created_at": "2024-11-09T01:02:03",
        "id": "update_me",
    },
    "delete_me": {
        "owner": "absent owner",
        "tiles": TilePool(frozenset(Tile(f"{j}", frozenset([f"{j}"])) for j in range(25))),
        "name": "Will be deleted :(",
        "created_at": "2024-11-09T01:02:03",
        "id": "delete_me",
    },
}


def dummy_api_tile(type: str = "text", content: str = "0"):
    return {"type": type, "content": content, "tags": [content]}


def dummy_api_tiles(count: int):
    lst = []
    for i in range(count):
        type_ = "text" if not i % 2 else "image"
        lst.append(dummy_api_tile(type_, str(i)))
    return lst


# NOTE: parametrize this database fixture to perform integration tests
@pytest.fixture
def db():
    return MemoryTilePoolDB()


@pytest.fixture
def db_data(db: MemoryTilePoolDB):
    db.data = EXAMPLES
    return db


@pytest.fixture
def app(db_data: TilePoolDB):
    app = create_app()
    app.config.update(TESTING=True, DB=db_data)
    return app


@pytest.fixture
def client(app: Flask):
    return app.test_client()


@pytest.fixture
def runner(app: Flask):
    return app.test_cli_runner()


class TestBingoCard:
    def test_bad_bingocard_request(self, client: FlaskClient):
        # no matching tilepool
        response = client.get("/bingocard/does-not-exist")
        assert response.status_code == 404

        # incorrect parameters
        response = client.get("/bingocard/basic", query_string={"size": "foo"})
        assert response.status_code == 400
        response = client.get("/bingocard/basic", query_string={"seed": "foo"})
        assert response.status_code == 400

    def test_get_bingocard(self, client: FlaskClient):
        response = client.get("/bingocard/basic", query_string={"seed": 20})
        assert response.status_code == 200
        assert (body := response.json)

        assert body["id"] == "20"
        assert body["size"] == 5
        assert len(body["grid"]) == 25
        assert body["grid"][12]["content"] == "Free"


class TestGetPool:
    def test_get_missing_tilepool(self, client: FlaskClient):
        response = client.get("/tilepools/does-not-exist")
        assert response.status_code == 404

    @pytest.mark.parametrize("example", [example for example in EXAMPLES.values()])
    def test_get_tilepool(self, client: FlaskClient, example: DBResult):
        response = client.get(f"/tilepools/{example['id']}")
        assert response.status_code == 200
        assert (body := response.json)

        assert body["id"] == example["id"]
        assert body["name"] == example["name"]
        assert body["owner"] == example["owner"]
        assert body["created_at"] == example["created_at"]
        if example["tiles"].free is not None:
            assert body["free_tile"] == tile_to_dict(example["tiles"].free)
        else:
            assert "free_tile" not in body and example["tiles"].free is None
        assert len(body["tiles"]) == len(example["tiles"])

        for recieved, expected in zip(
            body["tiles"],
            (tile_to_dict(tile) for tile in example["tiles"].tiles),
            strict=True,
        ):
            assert expected["content"] == recieved["content"]
            assert expected["type"] == recieved["type"]
            assert set(expected["tags"]) == set(recieved["tags"])


class TestDeletePool:
    def test_delete_missing_tilepool(self, client: FlaskClient):
        response = client.delete("/tilepools/does-not-exist")
        assert response.status_code == 404

    @pytest.mark.parametrize("example", [EXAMPLES["delete_me"]])
    def test_delete_tilepool(self, client: FlaskClient, example: DBResult):
        response = client.delete(f"/tilepools/{example['id']}")
        assert response.status_code == 204

        response = client.get(f"/tilepools/{example['id']}")
        assert response.status_code == 404


class TestCreatePool:
    def _is_iso_format(self, string: str) -> bool:
        try:
            datetime.fromisoformat(string)
            return True
        except ValueError:
            return False

    def test_bad_create_tilepool(self, client: FlaskClient):
        # missing tiles
        response = client.post("/tilepools", json={"name": "only a name"})
        assert response.status_code == 400
        # missing name
        response = client.post(
            "/tilepools",
            json={"tiles": dummy_api_tiles(6)},
        )
        assert response.status_code == 400
        # incorrect content type
        response = client.post(
            "/tilepools",
            json={
                "name": "malformated tilepool",
                "tiles": [
                    {"type": "text", "content": "1", "tags": ["1"]},
                    {"type": "image", "content": "2", "tags": ["2"]},
                    {"type": "invalid", "content": "3", "tags": ["3"]},
                    {"type": "invalid", "content": "4", "tags": ["4"]},
                    {"type": "invalid", "content": "5", "tags": ["5"]},
                    {"type": "invalid", "content": "6", "tags": ["6"]},
                ],
            },
        )
        assert response.status_code == 400

    def test_create_tilepool_nofree(self, client: FlaskClient):
        tiles = dummy_api_tiles(10)
        response = client.post(
            "/tilepools",
            json={
                "name": "a good pool sans free tile",
                "tiles": tiles,
            },
        )
        assert response.status_code == 201
        assert (body := response.json)

        assert body["name"] == "a good pool sans free tile"
        assert isinstance(body["id"], str)
        assert body["owner"] == "<SYSTEM OWNER>"
        assert self._is_iso_format(body["created_at"]), "Non ISO formatted timestamp"
        for tile in body["tiles"]:
            assert tile in tiles

    def test_create_tilepool_free(self, client: FlaskClient):
        tiles = [{"type": "text", "content": f"{i}", "tags": [f"{i}"]} for i in range(10)]
        free = {"type": "text", "content": "Free", "tags": ["free"]}
        response = client.post(
            "/tilepools",
            json={
                "name": "a good pool with free tile",
                "tiles": tiles,
                "free_tile": free,
            },
        )
        assert response.status_code == 201
        assert (body := response.json)

        assert body["name"] == "a good pool with free tile"
        assert isinstance(body["id"], str)
        assert body["owner"] == "<SYSTEM OWNER>"
        assert self._is_iso_format(body["created_at"]), "Non ISO formatted timestamp"
        assert body["free_tile"] == free
        for tile in body["tiles"]:
            assert tile in tiles


class TestGetPools:
    def test_get_all_tilepools(self, client: FlaskClient):
        response = client.get("/tilepools")
        assert response.status_code == 200
        assert (body := response.json)

        assert len(body) == len(EXAMPLES)
        for pool in body:
            assert (id_ := pool["id"]) in EXAMPLES
            expected = EXAMPLES[id_]
            assert pool["owner"] == expected["owner"]
            assert pool["created_at"] == expected["created_at"]
            assert pool["name"] == expected["name"]
            assert all(dict_to_tile(tile) in expected["tiles"] for tile in pool["tiles"])

    def test_get_paginated_tilepools(self, client: FlaskClient):
        pass

    def test_get_sorted_tilepools(self, client: FlaskClient):
        pass


class TestUpdatePools:
    def test_update_bad_request(self, client: FlaskClient):
        # no body
        response = client.patch("/tilepools/basic")
        assert response.status_code == 415

        # body but missing relavent fields
        response = client.patch("/tilepools/basic", json={"some-useless-key": 1})
        assert response.status_code == 400

        # removals and insertions are not lists
        response = client.patch(
            "/tilepools/basic",
            json={"removals": ["valid", "request"], "insertions": "an invalid input"},
        )
        assert response.status_code == 400
        response = client.patch(
            "/tilepools/basic",
            json={"removals": "an invalid input", "insertions": dummy_api_tiles(10)},
        )
        assert response.status_code == 400

        # bad tile format
        response = client.patch(
            "/tilepools/basic",
            json={"insertions": {"type": "bad type", "content": "abc", "tags": ["0"]}},
        )
        assert response.status_code == 400

    def test_update_missing_pool(self, client: FlaskClient):
        response = client.patch(
            "/tilepools/does-not-exist", json={"removals": ["these", "won't", "be", "removed"]}
        )
        assert response.status_code == 404

    @pytest.mark.parametrize("example", [EXAMPLES["update_me"]])
    def test_update_pool(self, client: FlaskClient, example: DBResult):
        response = client.patch(
            f"/tilepools/{example['id']}", json={"removals": [f"{i}" for i in range(25)]}
        )
        assert response.status_code == 200
        assert (body := response.json)
        assert body["owner"] == example["owner"]
        assert body["name"] == example["name"]
        assert body["created_at"] == example["created_at"]
        assert len(body["tiles"]) == len(example["tiles"])
