import json
import random

from lambda_helper import get_pool_manager

from bingomaker.data.persistence import tile_to_dict
from bingomaker.game import Board


def lambda_handler(event, context):
    try:
        tilepool_id = event["pathParameters"]["tilepoolId"]
    except KeyError:
        return {
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "statusCode": 404,
            "body": "Tile pool not found",
        }

    query_params = event.get("queryStringParameters", {}) or {}
    try:
        size = int(query_params.get("size", 5))
        seed = int(query_params.get("seed", random.randint(0, 1 << 16)))
    except ValueError:
        return {
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "statusCode": 400,
            "body": "Bad query params",
        }

    db = get_pool_manager()

    if not (result := db.get_tile_pool(tilepool_id)):
        return {
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "statusCode": 404,
            "body": "Tile pool not found",
        }

    pool = result["tiles"]
    board = Board(pool, size=size, free_square=pool.free is not None, seed=seed)
    board.id = str(seed)

    body = {
        "id": board.id,
        "size": board.size,
        "tiles": [tile_to_dict(tile) for row in board.board for tile in row],
    }

    return {
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "statusCode": 200,
        "body": json.dumps(body),
    }
