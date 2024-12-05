import json

from lambda_helper import get_pool_manager

from bingomaker.data.persistence import dict_to_tile, tile_to_dict


def lambda_handler(event, context):
    tilepool_id = event["pathParameters"]["tilepoolId"]
    db = get_pool_manager()

    if not (data := json.loads(event["body"])):
        return {
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "statusCode": 404,
            "body": "Tile pool not found",
        }

    removals = data.get("removals")
    insertions = data.get("insertions")
    if removals is None and insertions is None:
        return {
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "statusCode": 400,
            "body": "Missing update payload",
        }

    if removals is not None and not isinstance(removals, list):
        return {
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "statusCode": 400,
            "body": "removals is not a list",
        }
    if insertions is not None and not isinstance(insertions, list):
        return {
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "statusCode": 400,
            "body": "insertions is not a list",
        }

    if insertions:
        try:
            parsed_insertions = [dict_to_tile(tile) for tile in insertions]
        except (TypeError, KeyError):
            return {
                "headers": {
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                },
                "statusCode": 400,
                "body": "Malformed tile insertions",
            }
    else:
        parsed_insertions = None

    if not db.update_tiles(tilepool_id, removals, parsed_insertions):
        return {
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "statusCode": 404,
            "body": "Tile pool not found",
        }

    if not (result := db.get_tile_pool(tilepool_id)):
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
        "id": tilepool_id,
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
        "statusCode": 200,
        "body": json.dumps(body),
    }
