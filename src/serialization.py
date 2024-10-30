import json
from typing import Any

import game


class BoardEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        match o:
            # fields that shouldn't be serialized
            case game.TilePool() | list(list(bool())):
                return ""
            # case list(list(game.Tile())):
            #     return ""
            case game.Board():
                return {
                    "id": o.id,
                    "seed": o.seed,
                    "size": o.size,
                    "tiles": [tile for row in o.board for tile in row],
                }
            case game.Tile():
                encoded: dict[str, str | list[str]] = {
                    "type": "text" if o.image_url is None else "image",
                    "content": o.image_url or o.text,
                }
                if len(o.tags) != 0:
                    encoded["tags"] = list(o.tags)

                return encoded

            case _:
                print(o)
                return super().default(o)


if __name__ == "__main__":
    board = game._example_game(3)
    print(json.dumps(board, cls=BoardEncoder))
