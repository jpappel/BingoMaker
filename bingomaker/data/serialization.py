import json
from typing import Any

# HACK: python pattern matching behaves weirdly
try:
    from bingomaker.game.game import Board, Tile, TilePool
except ModuleNotFoundError:
    from game.game import Board, Tile, TilePool


class BoardEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        match o:
            # fields that shouldn't be serialized
            case TilePool():
                return ""
            case Board():
                return {
                    "id": o.id,
                    "seed": o.seed,
                    "size": o.size,
                    "tiles": [tile for row in o.board for tile in row],
                }
            case Tile():
                encoded: dict[str, str | list[str]] = {
                    "type": "text" if o.image_url is None else "image",
                    "content": o.image_url or o.text,
                }
                if len(o.tags) != 0:
                    encoded["tags"] = list(o.tags)

                return encoded

            case _:
                return super().default(o)
