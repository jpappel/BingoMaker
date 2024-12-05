import json

from lambda_helper import get_pool_manager

from bingomaker.data.persistence import dict_to_tile, tile_to_dict
from bingomaker.game.game import TilePool


def lambda_handler(event, context):
    db = get_pool_manager()

    if not (data := json.loads(event["body"])):
        return {
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "statusCode": 400,
            "body": "Missing request data",
        }
    if not (name := data.get("name")) or not (recv_tiles := data.get("tiles")):
        return {
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "statusCode": 400,
            "body": "Missing tilepool name or tiles",
        }
    # TODO: get owner from cognito
    owner = "<SYSTEM OWNER>"

    try:
        tiles = frozenset(dict_to_tile(tile) for tile in recv_tiles)
        if free := data.get("free_tile"):
            pool = TilePool(tiles, dict_to_tile(free))
        else:
            pool = TilePool(tiles)
    except (ValueError, KeyError):
        return {
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "statusCode": 400,
            "body": "Incorrect tile format",
        }

    if not (id_ := db.insert_tile_pool(name, owner, pool)):
        return {
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "statusCode": 500,
            "body": "Internal Server Error",
        }

    if not (result := db.get_tile_pool(id_)):
        return {
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "statusCode": 500,
            "body": "Error storing tilepool in database",
        }

    body = {
        "id": id_,
        "name": result["name"],
        "owner": result["owner"],
        "created_at": result["created_at"],
        "tiles": [tile_to_dict(tile) for tile in result["tiles"].tiles],
    }
    if free := result["tiles"].free:
        body["free_tile"] = tile_to_dict(free)

    return {
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "statusCode": 201,
        "body": json.dumps(body),
    }
