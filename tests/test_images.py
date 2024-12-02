import io
from pathlib import Path

import boto3
import pytest
from botocore.exceptions import ClientError

from src.images import (
    DynamoReferenceCounts,
    LocalImageManager,
    LocalReferenceCounts,
    MemoryReferenceCounts,
    ReferenceCounts,
    S3ImageManager,
)
from src.images.image_manager import Count, ImageManager


class S3ImageManagerTest(S3ImageManager):
    def __init__(self, references: ReferenceCounts):
        self._references = references
        self.bucket_name = "test-image-manager"
        self.region = "us-east-1"
        self.endpoint_hostname = "localhost.localstack.cloud:4566"
        self.client = boto3.client(
            "s3",
            region_name=self.region,
            endpoint_url=f"http://{self.endpoint_hostname}",
            aws_access_key_id="aVeryFakeKey",
            aws_secret_access_key="alsoVeryFake",
        )

        if self.bucket_exists():
            self.delete_bucket()
        self.create_bucket()

    def bucket_exists(self):
        """Check if the bucket exists."""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            else:
                print(f"Error checking bucket existence: {e}")
                raise

    def delete_bucket(self):
        try:
            # delete all objects in bucket
            response = self.client.list_objects_v2(Bucket=self.bucket_name)
            for obj in response.get("Contents", []):
                self.client.delete_object(Bucket=self.bucket_name, Key=obj["Key"])

            self.client.delete_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print(f"Bucket '{self.bucket_name}' does not exist.")
            else:
                print(f"Error deleting bucket: {e}")
                raise

    def create_bucket(self):
        try:
            self.client.create_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            print(f"Error creating bucket: {e}")
            raise


class DynamoRefernceCountsTest(DynamoReferenceCounts):
    def __init__(self, _):
        self.table_name = "TestRefenceCounts"
        self._counts = {}
        self.client = boto3.client(
            "dynamodb",
            region_name="us-east-1",
            endpoint_url="http://localhost.localstack.cloud:4566",
            aws_access_key_id="aVeryFakeAccessKey",
            aws_secret_access_key="alsoAVeryFakeSecretKey",
        )

        if self.table_exists():
            self.delete_table()
        self.create_table()

    def table_exists(self) -> bool:
        """Check if the table exists"""
        try:
            response = self.client.describe_table(TableName=self.table_name)
            return response["Table"]["TableStatus"] in ("ACTIVE", "CREATING")
        except self.client.exceptions.ResourceNotFoundException:
            return False

    def delete_table(self):
        """Delete the table"""
        try:
            self.client.delete_table(TableName=self.table_name)
            waiter = self.client.get_waiter("table_not_exists")
            waiter.wait(TableName=self.table_name)
        except self.client.exceptions.ResourceNotFoundException:
            return

    def create_table(self):
        """Create the table"""
        self.client.create_table(
            TableName=self.table_name,
            AttributeDefinitions=[
                {"AttributeName": "ImageID", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "ImageID", "KeyType": "HASH"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        waiter = self.client.get_waiter("table_exists")
        waiter.wait(TableName=self.table_name)


@pytest.fixture(
    params=[
        LocalReferenceCounts,
        MemoryReferenceCounts,
        pytest.param(DynamoRefernceCountsTest, marks=pytest.mark.localstack),
    ]
)
def refcounts(request: pytest.FixtureRequest, tmp_path: Path):
    driver = request.param
    if driver == LocalReferenceCounts:
        path = tmp_path / "LocalRefCounts"
        return driver(path, {})
    return driver({})


@pytest.fixture(
    params=[LocalImageManager, pytest.param(S3ImageManagerTest, marks=pytest.mark.localstack)]
)
def image_manager(request: pytest.FixtureRequest, tmp_path: Path):
    ref_counts = MemoryReferenceCounts({})
    driver = request.param
    if driver == LocalImageManager:
        return driver(tmp_path, ref_counts)
    return driver(ref_counts)


class TestRefenceCounts:
    def test_set_get_del(self, refcounts: ReferenceCounts):
        refcounts["img_1"] = Count(1, 1)
        assert len(refcounts) == 1
        assert refcounts["img_1"] == Count(1, 1)

        del refcounts["img_1"]
        assert len(refcounts) == 0
        with pytest.raises(KeyError):
            refcounts["img_1"]

    def test_add_prune(self, refcounts: ReferenceCounts):
        for i in range(10):
            refcounts[f"img_{i}"] = Count(1, 0)
        assert len(refcounts) == 10

        refcounts["img_0"] = Count(0, 0)
        refcounts.prune()
        assert len(refcounts) == 9


class TestImageManager:
    def test_add_get_image(self, image_manager: ImageManager):
        data = io.BytesIO(b"here is some text")
        assert (id_ := image_manager.add_image(data, {"mimetype": "text/plain", "size": 100}))
        assert image_manager.references[id_] == Count(1, 0)
        assert id_ in image_manager.get_image(id_)

    def test_bad_get_image(self, image_manager: ImageManager):
        with pytest.raises(FileNotFoundError):
            image_manager.get_image("does not exist")

    def test_bad_delete(self, image_manager: ImageManager):
        with pytest.raises(FileNotFoundError):
            image_manager.delete_image("does not exist :O")

    def test_add_delete(self, image_manager: ImageManager):
        data = io.BytesIO(b"here is some text")
        assert (id_ := image_manager.add_image(data, {"mimetype": "text/plain", "size": 100}))
        assert len(image_manager.references) == 1
        assert image_manager.delete_image(id_)

        with pytest.raises(FileNotFoundError):
            image_manager.get_image(id_)

    def test_deref_prune(self, image_manager: ImageManager):
        image_ids = []
        for i in range(10):
            image_ids.append(
                image_manager.add_image(
                    io.BytesIO(f"{i}".encode()), {"mimetype": "text/plain", "size": 1}
                )
            )

        assert len(image_manager.references) == 10
        image_manager.deref_image(image_ids[0])
        assert image_manager.prune_images() == 1
        with pytest.raises(FileNotFoundError):
            image_manager.get_image(image_ids[0])
