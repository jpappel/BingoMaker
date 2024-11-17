from .image_manager import Count, ImageID, ReferenceCounts


class MemoryReferenceCounts(ReferenceCounts):
    """An in memory reference counter"""
    def __init__(self, initial_counts: dict[ImageID, Count] | None = None):
        self._counts = initial_counts or {}

    def read(self):
        pass

    def write(self):
        pass
