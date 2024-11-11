from datetime import datetime

import boto3
from botocore.exceptions import ClientError


def get_dynamodb_resource(region=None, endpoint_url=None):
    """Initialize and return a DynamoDB resource."""
    if endpoint_url:
        return boto3.resource('dynamodb', endpoint_url=endpoint_url, region_name='us-east-1')
    elif region:
        return boto3.resource('dynamodb', region_name=region)
    else:
        return boto3.resource('dynamodb') 

def create_tile_pool_table(dynamodb, table_name):
    """Create a DynamoDB table with the specified schema for local deployment."""
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'Owner', 'KeyType': 'HASH'},  # Partition key
                {'AttributeName': 'TilePoolId', 'KeyType': 'RANGE'}  # Sort key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'Owner', 'AttributeType': 'S'},
                {'AttributeName': 'TilePoolId', 'AttributeType': 'S'}
            ]
            # No ProvisionedThroughput for local deployment
        )
        print(f"Table {table_name} created successfully.")
        return table
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {table_name} already exists.")
        else:
            print(f"Failed to create table {table_name}: {e.response['Error']['Message']}")
        return None

def insert_tile_pool(dynamodb, table_name, tile_pool_id, tiles, owner, free_tile=None):
    """Insert a tile pool item into the DynamoDB table."""
    table = dynamodb.Table(table_name)
    try:
        response = table.put_item(
            Item={
                'TilePoolId': tile_pool_id,
                'Owner': owner,
                'Tiles': tiles,
                'FreeTile': free_tile,
                'CreatedAt': datetime.utcnow().isoformat()
            }
        )
        print(f"Tile pool {tile_pool_id} added successfully for owner {owner}.")
        return response
    except ClientError as e:
        print(f"Failed to insert tile pool {tile_pool_id}: {e.response['Error']['Message']}")
        return None

def delete_tile_pool(dynamodb, table_name, tile_pool_id, owner):
    """Delete a tile pool item from the DynamoDB table."""
    table = dynamodb.Table(table_name)
    try:
        response = table.delete_item(
            Key={'TilePoolId': tile_pool_id, 'Owner': owner}
        )
        print(f"Tile pool {tile_pool_id} deleted successfully for owner {owner}.")
        return response
    except ClientError as e:
        print(f"Failed to delete tile pool {tile_pool_id}: {e.response['Error']['Message']}")
        return None

def insert_tile_in_pool(dynamodb, table_name, tile_pool_id, tile, owner):
    """Add a tile to an existing tile pool in the DynamoDB table."""
    table = dynamodb.Table(table_name)
    try:
        response = table.update_item(
            Key={'TilePoolId': tile_pool_id, 'Owner': owner},
            UpdateExpression="SET Tiles = list_append(Tiles, :tile)",
            ExpressionAttributeValues={':tile': [tile]},
            ReturnValues="UPDATED_NEW"
        )
        print(f"Tile {tile} added to pool {tile_pool_id} for owner {owner}.")
        return response
    except ClientError as e:
        print(f"Failed to insert tile {tile} in pool {tile_pool_id}: \
              {e.response['Error']['Message']}")
        return None

def remove_tile_from_pool(dynamodb, table_name, tile_pool_id, tile, owner):
    """Remove a tile from an existing tile pool in the DynamoDB table."""
    table = dynamodb.Table(table_name)
    try:
        response = table.update_item(
            Key={'TilePoolId': tile_pool_id, 'Owner': owner},
            UpdateExpression="REMOVE Tiles :tile",
            ExpressionAttributeValues={':tile': {tile}},
            ReturnValues="UPDATED_NEW"
        )
        print(f"Tile {tile} removed from pool {tile_pool_id} for owner {owner}.")
        return response
    except ClientError as e:
        print(f"Failed to remove tile {tile} from pool {tile_pool_id}: \
              {e.response['Error']['Message']}")
        return None

def update_free_tile(dynamodb, table_name, tile_pool_id, free_tile, owner):
    """Update the free tile in an existing tile pool in the DynamoDB table."""
    table = dynamodb.Table(table_name)
    try:
        response = table.update_item(
            Key={'TilePoolId': tile_pool_id, 'Owner': owner},
            UpdateExpression="SET FreeTile = :tile",
            ExpressionAttributeValues={':tile': free_tile},
            ReturnValues="UPDATED_NEW"
        )
        print(f"Free tile updated to {free_tile} in pool {tile_pool_id} for owner {owner}.")
        return response
    except ClientError as e:
        print(f"Failed to update free tile in pool {tile_pool_id}: \
              {e.response['Error']['Message']}")
        return None

if __name__ == '__main__':
    # Customize these variables
    dynamodb = get_dynamodb_resource(endpoint_url='http://localhost:8000')

    tile_pool = create_tile_pool_table(dynamodb, 'TilePools')
