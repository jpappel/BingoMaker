import os

from bingomaker.data import DynamoTilePoolDB, FileTilePoolDB, MemoryTilePoolDB
from bingomaker.images import (
    LocalImageManager,
    LocalReferenceCounts,
    MemoryReferenceCounts,
    S3ImageManager,
)


class Config:
    TESTING = False
    DEBUG = False

    @property
    def DB(self):
        raise NotImplementedError("No Tile Pool Database defined for this config")

    @property
    def IMAGES(self):
        raise NotImplementedError("Not Image Manager defined for this config")


class DebugConfig(Config):
    DEBUG = True

    @property
    def DB(self):
        return FileTilePoolDB("debug_tiles")

    @property
    def IMAGES(self):
        return LocalImageManager("debug_image_store", LocalReferenceCounts("debug_counts"))


class TestingConfig(Config):
    DEBUG = True

    @property
    def DB(self):
        return MemoryTilePoolDB()

    @property
    def IMAGES(self):
        return LocalImageManager("testing_image_store", MemoryReferenceCounts())


class LocalDiskConfig(Config):
    @property
    def DB(self):
        return FileTilePoolDB("tiles")

    @property
    def IMAGES(self):
        return LocalImageManager("image_store", LocalReferenceCounts("counts"))


class LocalAWSConfig(Config):
    @property
    def DB(self):
        return DynamoTilePoolDB(endpoint_url="http://localhost.localstack.cloud:4566")

    @property
    def IMAGES(self):
        return S3ImageManager(
            "bingo-maker",
            LocalReferenceCounts("counts"),
            endpoint_hostname="localhost.localstack.cloud:4566",
        )


class CloudAWSConfig(Config):
    @property
    def DB(self):
        return DynamoTilePoolDB()

    @property
    def IMAGES(self):
        return S3ImageManager(os.environ["S3_BUCKET_NAME"], LocalReferenceCounts("counts"))
