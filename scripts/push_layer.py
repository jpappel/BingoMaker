#!/usr/bin/env python
import boto3
from botocore.exceptions import ClientError

layer_name = "bingomaker-layer"
layer_archive = "layer/layer.zip"

lambda_client = boto3.client("lambda")

try:
    with open(layer_archive, "rb") as f:
        layer_data = f.read()

    response = lambda_client.publish_layer_version(
        LayerName=layer_name,
        Content={"ZipFile": layer_data},
        CompatibleRuntimes=["python3.13"],
    )

    print(f"Layer published: {response['LayerVersionArn']}")
except ClientError as e:
    print(f"Error publishing layer: {e}")
