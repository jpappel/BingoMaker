import hashlib

import boto3
from botocore.exceptions import ClientError

from .image_manager import Count, ImageID, ImageInfo, ImageManager, ReferenceCounts


class S3ImageManager(ImageManager):
    def __init__(
        self,
        bucket_name: str,
        references: ReferenceCounts,
        region: str = "us-east-1",
        endpoint_hostname: str = "amazonaws.com",
    ):
        self._references = references
        self.bucket_name = bucket_name
        self.region = region
        self.endpoint_hostname = endpoint_hostname
        self.client = boto3.client("s3", region=region)

    @property
    def references(self) -> ReferenceCounts:
        return self._references

    def _object_exists(self, id_: ImageID) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=id_)
            return True
        except ClientError:
            return False

    def add_image(self, data, info: ImageInfo) -> ImageID:
        hash_ = hashlib.file_digest(data, "sha256").hexdigest()
        data.seek(0)

        if hash_ in self.references:
            return hash_

        self.client.upload_fileobj(data, self.bucket_name, hash_)
        self.references[hash_] = Count(1, 0)

        return hash_

    def get_image(self, id_: ImageID) -> str:
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=id_)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                raise FileNotFoundError() from e

        return f"{self.bucket_name}.s3.{self.region}.{self.endpoint_hostname}/{id_}"

    def delete_image(self, image_id: ImageID) -> bool:
        if not self._object_exists(image_id):
            raise FileNotFoundError()

        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=image_id)
            del self.references[image_id]
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                raise FileNotFoundError() from e
            return False
        return True

    def prune_images(self) -> int:
        delete = {
            "Objects": [
                {"Key": key}
                for key in self.references
                if self.references[key].confirmed == 0 and self.references[key].unconfirmed == 0
            ],
        }
        try:
            response = self.client.delete_objects(Bucket=self.bucket_name, Delete=delete)
            self.references.prune()
        except Exception as e:
            print("Something went wrong!")
            print(e)
            return -1

        pruned = len(response["Deleted"])
        if pruned != len(delete["Objects"]):
            print("Did not prune everything!")

        return pruned
