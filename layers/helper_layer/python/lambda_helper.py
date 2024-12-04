import boto3

from bingomaker.data import DynamoTilePoolDB
from bingomaker.images import DynamoReferenceCounts, S3ImageManager


def get_pool_manager() -> DynamoTilePoolDB:
    table_name = "BingoMaker"
    return DynamoTilePoolDB(table_name)


def get_counts_manager() -> DynamoReferenceCounts:
    table_name = "BingoMakerImageCounts"
    return DynamoReferenceCounts(table_name)


def get_image_manager() -> S3ImageManager:
    client = boto3.client("secretsmanager")
    bucket_name = client.get_secret_value(SecretId="S3BucketName")["SecretString"]
    counts = get_counts_manager()
    return S3ImageManager(bucket_name, counts)
