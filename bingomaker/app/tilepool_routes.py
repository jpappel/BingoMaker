from data.persistence import SortMethod, TilePoolDB, dict_to_tile, tile_to_dict
from flask import Blueprint, current_app, request
from game.game import TilePool

bp = Blueprint("tilepools", __name__)


@bp.get("/tilepools")
def get_tilepools():
    db: TilePoolDB = current_app.config["DB"]
    size = request.args.get("size", type=int)
    page = request.args.get("page", type=int)
    sort = request.args.get("sort", SortMethod.DEFAULT, type=SortMethod)
    sort_asc = request.args.get(
        "sortAsc", True, type=lambda x: x.lower() in ("true", "1", "t", "yes")
    )
    results = db.get_tile_pools(size, page, sort, sort_asc)
    if results is None:
        return [], 200

    response = []
    for result in results:
        item = {
            "id": result["id"],
            "name": result["name"],
            "owner": result["owner"],
            "created_at": result["created_at"],
            "tiles": [tile_to_dict(tile) for tile in result["tiles"].tiles],
        }
        if (free := result["tiles"].free) is not None:
            item["free_tile"] = tile_to_dict(free)
        response.append(item)

    return response, 200


@bp.post("/tilepools")
def new_tilepool():
    # TODO: get tilepool owner
    db: TilePoolDB = current_app.config["DB"]

    if (data := request.json) is None:
        return "Missing request data", 400
    if not (name := data.get("name")) or not (recv_tiles := data.get("tiles")):
        return "Missing tilepool name or tiles", 400

    try:
        tiles = frozenset(dict_to_tile(tile) for tile in recv_tiles)
        if (free := data.get("free_tile")) is not None:
            pool = TilePool(tiles, dict_to_tile(free))
        else:
            pool = TilePool(tiles)
    except (ValueError, KeyError):
        return "Incorrect tile format", 400

    if (id_ := db.insert_tile_pool(name, "<SYSTEM OWNER>", pool)) is None:
        return "Internal Server Error", 500

    response, status_code = get_tilepool(id_)
    if status_code != 200:
        return "Internal Server Error", 500

    return response, 201


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
    if (free := result["tiles"].free) is not None:
        response["free_tile"] = tile_to_dict(free)
    return response, 200


@bp.patch("/tilepools/<tilepoolId>")
def update_tilepool(tilepoolId):
    db: TilePoolDB = current_app.config["DB"]

    if (data := request.json) is None:
        return "Missing request data", 400

    removals = data.get("removals")
    insertions = data.get("insertions")
    if removals is None and insertions is None:
        return "Missing update payload", 400

    if removals is not None and not isinstance(removals, list):
        return "removals is not a list", 400
    if insertions is not None and not isinstance(insertions, list):
        return "insertions is not a list", 400

    if insertions:
        try:
            parsed_insertions = [dict_to_tile(tile) for tile in insertions]
        except (TypeError, KeyError):
            return "Malformed tile insertions", 400
    else:
        parsed_insertions = None

    if not db.update_tiles(tilepoolId, removals, parsed_insertions):
        return "Tile pool not found", 404

    response, status_code = get_tilepool(tilepoolId)
    if status_code != 200:
        return "Internal Server Error", 500

    return response, 200


@bp.delete("/tilepools/<tilepoolId>")
def delete_tilepool(tilepoolId):
    db: TilePoolDB = current_app.config["DB"]
    deleted = db.delete_tile_pool(tilepoolId)
    if deleted:
        return "", 204
    else:
        return "Tilepool not found", 404
