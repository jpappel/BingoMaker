import bingomaker
from lambda_helper import get_pool_manager


def lambda_handler(event, context):
    # TODO: get values from event/context
    size: int | None
    page: int | None
    sort: "age" | "name" | "owner" | None
    sort_asc: bool
    db = get_pool_manager()

    if (results := db.get_tile_pools(size, page, sort, sort_asc)) is None:
        return {"status_code": 200, "body": jsonify([])}

    response_body = []
    # TODO: add try catch
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
        response_body.append(item)

    return {"status_code": 200, "body": jsonify(response_body)}
