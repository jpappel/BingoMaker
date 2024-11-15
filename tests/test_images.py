import io
from pathlib import Path

import pytest

from src.images import (
    LocalImageManager,
    LocalReferenceCounts,
    MemoryReferenceCounts,
    ReferenceCounts,
)
from src.images.image_manager import Count, ImageManager


@pytest.fixture(params=[LocalReferenceCounts, MemoryReferenceCounts])
def refcounts(request: pytest.FixtureRequest, tmp_path: Path):
    driver = request.param
    if driver == LocalReferenceCounts:
        path = tmp_path / "LocalRefCounts"
        return driver(path, {})
    return driver({})


@pytest.fixture(params=[LocalImageManager])
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
        assert (id_ := image_manager.add_image(data, {"extentsion": ".txt", "size": 100}))
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
        assert (id_ := image_manager.add_image(data, {"extentsion": ".txt", "size": 100}))
        assert len(image_manager.references) == 1
        assert image_manager.delete_image(id_)

        with pytest.raises(FileNotFoundError):
            image_manager.get_image(id_)

    def test_prune(self, image_manager: ImageManager):
        image_ids = []
        for i in range(10):
            image_ids.append(
                image_manager.add_image(
                    io.BytesIO(f"{i}".encode()), {"extentsion": ".txt", "size": 1}
                )
            )

        assert len(image_manager.references) == 10
        # FIXME: ref counts should not manually be changed, even in testing
        #        once decreasing ref counts is implemented this should be removed
        image_manager.references[image_ids[0]] = Count(0, 0)
        assert image_manager.prune_images() == 1
        with pytest.raises(FileNotFoundError):
            image_manager.get_image(image_ids[0])
