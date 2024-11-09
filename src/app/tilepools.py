from flask import Blueprint, current_app, jsonify

from data.persistence import TilePoolDB, tile_to_dict
from game.game import TilePool

bp = Blueprint("tilepools", __name__)


@bp.get("/tilepools")
def get_tilepools():
    # TODO: implement
    return jsonify(TilePool(frozenset()))


@bp.post("/tilepools")
def new_tilepool():
    # TODO: implement
    return "", 400


@bp.get("/tilepools/<tilepoolId>")
def get_tilepool(tilepoolId):
    db: TilePoolDB = current_app.config["DB"]
    result = db.get_tile_pool(tilepoolId)
    if not result:
        return "No tilepool found", 404
    response = {
        "id": result["id"],
        "name": result["name"],
        "owner": result["owner"],
        "created_at": result["created_at"],
        "tiles": [tile_to_dict(tile) for tile in result["tiles"].tiles],
    }
    return response, 200


@bp.patch("/tilepools/<tilepoolId>")
def update_tilepool(tilepoolId):
    # TODO: implement
    return "", 404


@bp.delete("/tilepools/<tilepoolId>")
def delete_tilepool(tilepoolId):
    # TODO: implement
    return "", 404
