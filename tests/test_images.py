from pathlib import Path

import pytest

from src.images import LocalReferenceCounts, ReferenceCounts
from src.images.image_manager import Count


@pytest.fixture(params=[LocalReferenceCounts])
def refcounts(request: pytest.FixtureRequest, tmp_path: Path):
    driver = request.param
    if driver == LocalReferenceCounts:
        path = tmp_path / "LocalRefCounts"
        return driver(path)
    return driver()


@pytest.fixture
def one_count(refcounts: ReferenceCounts):
    refcounts["img_1"] = Count(1, 0)


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
