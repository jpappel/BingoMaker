import json

from bingomaker.data.persistence import tile_to_dict
from lambda_helper import get_pool_manager


def lambda_handler(event, context):
    try:
        tilepool_id = event["pathParameters"]["tilepoolId"]
    except KeyError:
        return {"statusCode": 404, "body": "No tilepool found"}

    db = get_pool_manager()

    if not (result := db.get_tile_pool(tilepool_id)):
        return {"statusCode": 404, "body": "No tilepool found"}

    body = {
        "id": result["id"],
        "name": result["name"],
        "owner": result["owner"],
        "created_at": result["created_at"],
        "tiles": [tile_to_dict(tile) for tile in result["tiles"].tiles],
    }

    if free := result["tiles"].free:
        body["free_tile"] = tile_to_dict(free)

    return {"statusCode": 200, "body": json.dumps(body)}
