import pytest
from flask import Flask
from flask.testing import FlaskClient

from src.app import create_app
from src.data import MemoryTilePoolDB
from src.data.persistence import DBResult, TilePoolDB, tile_to_dict
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
    }
}


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


def test_bad_bingocard_request(client: FlaskClient):
    # no matching tilepool
    response = client.get("/bingocard/does-not-exist")
    assert response.status_code == 404

    # incorrect parameters
    response = client.get("/bingocard/basic?size=foo")
    assert response.status_code == 400
    response = client.get("/bingocard/basic?seed=foo")
    assert response.status_code == 400


def test_all_good(client: FlaskClient):
    response = client.get("/bingocard/basic?seed=20")
    assert response.status_code == 200
    assert (body := response.json)

    assert body["id"] == "20"
    assert body["size"] == 5
    assert len(body["grid"]) == 25
    assert body["grid"][12]["Content"] == "Free"


def test_get_tilepool(client: FlaskClient):
    response = client.get("/tilepools/does-not-exist")
    assert response.status_code == 404

    response = client.get("/tilepools/basic")
    assert response.status_code == 200
    assert (body := response.json)

    assert body["id"] == "basic"
    assert body["name"] == "Basic Pool"
    assert body["owner"] == "owner"
    assert body["created_at"] == "2024-11-08T01:02:03"
    assert len(body["tiles"]) == len(EXAMPLES["basic"]["tiles"])

    for recieved, expected in zip(
        body["tiles"],
        (tile_to_dict(tile) for tile in EXAMPLES["basic"]["tiles"].tiles),
        strict=True,
    ):
        assert expected["Content"] == recieved["Content"]
        assert expected["Type"] == recieved["Type"]
        assert set(expected["Tags"]) == set(recieved["Tags"])
