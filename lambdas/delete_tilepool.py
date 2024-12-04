from lambda_helper import get_pool_manager


def lambda_handler(event, context):
    try:
        tilepool_id = event["pathParameters"]["tilepoolId"]
    except KeyError:
        return {"statusCode": 404, "body": "No tilepool found"}
    db = get_pool_manager()

    statusCode = 204 if db.delete_tile_pool(tilepool_id) else 404

    return {"statusCode": statusCode}
