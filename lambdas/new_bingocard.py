import bingomaker
from lambda_helper import get_tilepool_manager


def lambda_handler(event, context):
    # TODO: get size, seed, tilepool_id from event
    size: int
    seed: int
    tilepool_id: str
    db = get_tilepool_manager()

    if not (result := db.get_tile_pool(tilepool_id)):
        return {"status_code": 404, "body": "Tile pool not found"}

    pool = result["tiles"]
    board = Board(pool, size=sie, free_square=pool.free is not None, seed=seed)
    board.id = str(seed)

    body = {
        "id": board.id,
        "size": board.size,
        "grid": [tile_to_dict(tile) for row in board.board for tile in row],
    }

    return {"status_code": 200, "body": jsonify(body)}
