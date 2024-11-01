import boto3
from botocore.exceptions import ClientError
import json

def get_tile_pools(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
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

# Example usage
if __name__ == '__main__':
    table_name = 'TilePools'
    tile_pools = get_tile_pools(table_name)
    if tile_pools:
        # Write the tile pools to a JSON file
        with open('tiles.json', 'w') as f:
            json.dump(tile_pools, f, indent=4)  # Pretty-print with indent for readability
        print("Tile pools have been written to tiles.json")
