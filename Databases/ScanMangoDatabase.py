import json

from pymongo import MongoClient


def get_all_pools(
    database_name, collection_name, host: str = "localhost", port: int = 27017
):
    # Initialize MongoDB client
    client = MongoClient(host=host, port=port)
    db = client[database_name]
    collection = db[collection_name]

    try:
        # Find all documents in the collection
        items = list(collection.find())
        return items

    except Exception as e:
        print(f"Failed to retrieve tile pools: {str(e)}")
        return None


def get_tile_pool(
    database_name,
    collection_name,
    tile_pool_id,
    owner,
    host: str = "localhost",
    port: int = 27017,
):
    # Initialize MongoDB client
    client = MongoClient(host=host, port=port)
    db = client[database_name]
    collection = db[collection_name]

    try:
        # Find the specific document by TilePoolId and Owner
        item = collection.find_one({"TilePoolId": tile_pool_id, "Owner": owner})
        return item

    except Exception as e:
        print(f"Failed to retrieve tile pool: {str(e)}")
        return None


# Example usage
if __name__ == "__main__":
    database_name = "BingoBakerDB"
    collection_name = "TilePools"

    # Retrieve all tile pools
    tile_pools = get_all_pools(database_name, collection_name)
    if tile_pools:
        # Write the tile pools to a JSON file
        with open("tiles.json", "w") as f:
            json.dump(
                tile_pools, f, default=str, indent=4
            )  # Pretty-print with indent for readability
        print("Tile pools have been written to tiles.json")

    # Retrieve a specific tile pool
    tile_pool_id = "example-tilepool-1730676412"
    owner = "us-east-1:example-cognito-id"
    tile_pool = get_tile_pool(database_name, collection_name, tile_pool_id, owner)
    if tile_pool:
        print(f"Retrieved tile pool: {tile_pool}")
    else:
        print(f"Tile pool with ID '{tile_pool_id}' and Owner '{owner}' not found.")


if __name__ == "__main__":
    # Customize these variables
    database_name = "BingoBakerDB"
    collection_name = "TilePools"
    tile_pool_id = "example-tilepool-1730676412"
    owner = "us-east-1:example-cognito-id"

    # Retrieve a specific tile pool
    tile_pool = get_tile_pool(database_name, collection_name, tile_pool_id, owner)
    if tile_pool:
        print(f"Retrieved tile pool: {tile_pool}")
    else:
        print(f"Tile pool with ID '{tile_pool_id}' and Owner '{owner}' not found.")
