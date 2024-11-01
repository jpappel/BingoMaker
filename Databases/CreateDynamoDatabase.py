import boto3
from botocore.exceptions import ClientError
from datetime import datetime

def create_tile_pool_table(table_name):
    # Initialize a session using Amazon DynamoDB
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Change to your preferred region

    # Define the table schema and attributes
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'Owner',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'TilePoolId',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'Owner',
                    'AttributeType': 'S'  # S = String, storing a unique Cognito identifier
                },
                {
                    'AttributeName': 'TilePoolId',
                    'AttributeType': 'S'  # S = String, storing the unique pool identifier
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        # Wait until the table exists
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"Table {table_name} created successfully.")
        return table
    
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Table {table_name} already exists.")
        else:
            print(f"Failed to create table {table_name}: {e.response['Error']['Message']}")
        return None

def insert_tile_pool(table_name, tile_pool_id, tiles, free_tile, owner):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(table_name)
    
    try:
        response = table.put_item(
            Item={
                'TilePoolId': tile_pool_id,
                'Owner': owner,
                'Tiles': tiles,
                'FreeTile': free_tile,
                'CreatedAt': datetime.utcnow().isoformat()  # Timestamp in ISO format
            }
        )
        print(f"Tile pool {tile_pool_id} added successfully for owner {owner}.")
        return response
    except ClientError as e:
        print(f"Failed to insert tile pool {tile_pool_id}: {e.response['Error']['Message']}")
        return None
    

if __name__ == '__main__':
    # Customize these variables
    table_name = 'TilePools'
    tile_pool_id = 'example-tilepool-123'
    tiles = ['tile1', 'tile2', 'tile3']
    free_tile = 'tile4'
    owner = 'us-east-1:example-cognito-id'

    # Create the table
    create_tile_pool_table(table_name)
    
    # Insert a sample tile pool
    insert_tile_pool(table_name, tile_pool_id, tiles, free_tile, owner)
