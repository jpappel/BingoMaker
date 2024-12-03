import bingomaker
from lambda_helper import get_tilepool_manager


def lambda_handler(event, context):
    # TODO: get tilepool_id from event
    tilepool_id: str
    db = get_tilepool_manager()

    if not (result := db.get_tile_pool(tilepool_id)):
        return {"status_code": 404, "body": "No tilepool found"}

    body = {
        "id": result["id"],
        "name": result["name"],
        "owner": result["owner"],
        "created_at": result["created_at"],
        "tiles": [tile_to_dict(tile) for tile in result["tiles"].tiles],
    }

    if (free := result["tiles"].free):
        body["free_tile"] = tile_to_dict(free)

    return {
            "status_code": 200,
            "body": jsonify(body)
            }

