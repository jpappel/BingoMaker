import json

from botocore.exceptions import ClientError

from Database.CreateDynamo import get_dynamodb_resource


def get_all_pools(dynamodb,table_name):
    table = dynamodb.Table(table_name)
    try:
        # Scan the table to get all items
        response = table.scan()
        items = response.get('Items', [])
        # Continue scanning if there are more items
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        return items
    except ClientError as e:
        print(f"Failed to retrieve tile pools: {e.response['Error']['Message']}")
        return None
    
def get_tile_pool(dynamodb, table_name, tile_pool_id, owner):
    table = dynamodb.Table(table_name)
    try:
        # Get the item with the specified key
        response = table.get_item(
            Key={
                'TilePoolId': tile_pool_id,
                'Owner': owner
            }
        )
        item = response.get('Item', None)
        return item
    except ClientError as e:
        print(f"Failed to retrieve tile pool: {e.response['Error']['Message']}")
        return None
    
# Example usage
if __name__ == '__main__':
    # call get_dynamodb_resource() to get the DynamoDB resource
    dynamodb = get_dynamodb_resource()

    table_name = 'TilePools'
    tile_pools = get_all_pools(dynamodb,table_name)
    if tile_pools:
        # Write the tile pools to a JSON file
        with open('tiles.json', 'w') as f:
            json.dump(tile_pools, f, indent=4)  # Pretty-print with indent for readability
        print("Tile pools have been written to tiles.json")
        # example-tilepool-123 = tile_pool_id
        # owner = "us-east-1:example-cognito-id"
        tile_pool_id = 'example-tilepool-123'
        owner = 'us-east-1:example-cognito-id'
        tile_pool = get_tile_pool(dynamodb,table_name, tile_pool_id, owner)
        print(get_tile_pool(dynamodb, table_name, tile_pool_id, owner))