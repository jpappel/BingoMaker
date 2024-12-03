import bingomaker
from lambda_helper import get_tilepool_manager


def lambda_handler(event, context):
    # TODO: get tilepool_id from event
    tilepool_id: int
    db = get_tilepool_manager()

    status_code = 204 if db.delete_tile_pool(tilepool_id) else 404

    return {"status_code": status_code}
