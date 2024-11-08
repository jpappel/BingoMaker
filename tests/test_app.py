import pytest
from flask import Flask
from flask.testing import FlaskClient

from src.app import create_app
from src.data import MemoryTilePoolDB
from src.data.persistence import DBResult, TilePoolDB
from src.game.game import Tile, TilePool

EXAMPLES: dict[str, DBResult] = {
    "basic": {
        "owner": "owner",
        "tiles": TilePool(
            frozenset(Tile(f"{j}", frozenset([f"{j}"])) for j in range(25)), Tile("Free")
        ),
        "name": "Basic Pool",
        "created_at": "",
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
    response = client.get("/bingocard/1")
    assert response.status_code == 404

    # incorrect parameters
    response = client.get("/bingocard/1?size=foo")
    assert response.status_code == 400
    response = client.get("/bingocard/1?seed=foo")
    assert response.status_code == 400


def test_all_good(client: FlaskClient):
    response = client.get("/bingocard/basic?seed=20")
    assert response.status_code == 200
    assert response.json

    body = response.json
    assert body["id"] == "20"
    assert body["size"] == 5
    assert len(body["grid"]) == 25
    print(body["grid"])
    assert body["grid"][12]["Content"] == "Free"
