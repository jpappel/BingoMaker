import json

from lambda_helper import get_pool_manager

from bingomaker.data.persistence import SortMethod, tile_to_dict


def lambda_handler(event, context):
    query_params = event.get("queryStringParameters", {}) or {}
    try:
        size = int(query_params.get("size", 25))
        page = int(query_params.get("page", 1))
    except ValueError:
        return {
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "statusCode": 400,
            "body": "Incorrect query param type",
        }

    try:
        sort = SortMethod(query_params.get("sort", SortMethod.DEFAULT))
    except ValueError:
        return {
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "statusCode": 400,
            "body": "Invalid sort method",
        }

    if "sortAsc" in query_params:
        sort_asc = query_params["sortAsc"].lower() in ("true", "1", "t", "yes")
    else:
        sort_asc = True
    db = get_pool_manager()

    if (results := db.get_tile_pools(size, page, sort, sort_asc)) is None:
        return {
            "headers": {
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
            },
            "statusCode": 200,
            "body": json.dumps([]),
        }

    body = []
    for result in results:
        item = {
            "id": result["id"],
            "name": result["name"],
            "owner": result["owner"],
            "created_at": result["created_at"],
            "tiles": [tile_to_dict(tile) for tile in result["tiles"].tiles],
        }
        if free := result["tiles"].free:
            item["free_tile"] = tile_to_dict(free)
        body.append(item)

    return {
        "headers": {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "statusCode": 200,
        "body": json.dumps(body),
    }
