from abc import ABC, abstractmethod
from typing import TypedDict

ImageID = str


class ImageInfo(TypedDict):
    extentsion: str
    size: int


class Count:
    def __init__(self, confirmed: int = 0, unconfirmed: int = 0):
        self.confirmed = confirmed
        self.unconfirmed = unconfirmed

    def __str__(self):
        return f"confirmed: {self.confirmed}, unconfirmed: {self.unconfirmed}"

    def __repr__(self):
        return f"Count(confirmed={self.confirmed}, unconfirmed={self.unconfirmed})"

    def __eq__(self, other) -> bool:
        try:
            return self.confirmed == other.confirmed and self.unconfirmed == other.unconfirmed
        except AttributeError:
            return False

    def __iadd__(self, other):
        original = self.confirmed, self.unconfirmed
        try:
            self.confirmed += other.confirmed
            self.unconfirmed += other.unconfirmed
        except AttributeError as e:
            self.confirmed, self.unconfirmed = original
            raise AttributeError from e

        if self.confirmed < 0 or self.unconfirmed < 0:
            self.confirmed, self.unconfirmed = original
            raise ValueError("Count cannot be less than zero")

    def __isub__(self, other):
        original = self.confirmed, self.unconfirmed
        try:
            self.confirmed += other.confirmed
            self.unconfirmed += other.unconfirmed
        except AttributeError as e:
            self.confirmed, self.unconfirmed = original
            raise AttributeError from e

        if self.confirmed < 0 or self.unconfirmed < 0:
            self.confirmed, self.unconfirmed = original
            raise ValueError("Count cannot be less than zero")


class ReferenceCounts(ABC):
    @abstractmethod
    def __init__(self, initial_counts: dict[ImageID, Count]):
        self._counts = initial_counts

    @property
    def counts(self) -> dict[ImageID, Count]:
        """Get reference counts for all images"""
        return self._counts

    def __len__(self) -> int:
        return len(self._counts)

    def __contains__(self, other) -> bool:
        """Return if an object is counted"""
        self.read()
        try:
            return other in self._counts
        except Exception:
            return False

    def __iter__(self):
        """Iterator over image id's"""
        yield from self._counts

    def __getitem__(self, key: ImageID) -> Count:
        """Get the reference count of an image"""
        self.read()
        return self._counts[key]

    def __setitem__(self, key: ImageID, count: Count):
        """Set the reference count of an image"""
        self.read()
        self._counts[key] = count
        self.write()

    def __delitem__(self, key: ImageID):
        """Delete the reference count of an image"""
        del self._counts[key]
        self.write()

    def prune(self):
        """Delete counts for images with no counts"""
        self.read()
        to_be_deleted = [k for k, v in self.counts.items() if v.confirmed < 1 and v.unconfirmed < 1]
        for id_ in to_be_deleted:
            del self._counts[id_]
        self.write()

    @abstractmethod
    def write(self):
        """Write the current counts to a persistent store

        If running in a multi-threaded environment this MUST be atomic
        """
        pass

    @abstractmethod
    def read(self):
        """Read counts from a persistent store

        If running in a multi-threaded environment this MUST be atomic

        Raises:
            ValueError: error occured while parsing data
        """
        pass


class ImageManager(ABC):
    # TODO: handle unconfirmed images
    @property
    @abstractmethod
    def references(self) -> ReferenceCounts:
        pass

    @abstractmethod
    def add_image(self, data, info: ImageInfo) -> ImageID:
        """Add an image to be managed"""
        pass

    def confirm_image(self, id: ImageID):
        """Confirm an image

        Raises:
            KeyError: image with id is not currently tracked
        """
        self.references[id] = Count(1, -1)

    def deref_image(self, id: ImageID):
        """Remove a reference to an image

        Raises:
            KeyError: image with id is not currently tracked
        """
        count = self.references[id]
        count += Count(-1, 0)

    @abstractmethod
    def get_image(self, id: ImageID) -> str:
        """Get the public url for an image"""
        pass

    @abstractmethod
    def delete_image(self, image_id) -> bool:
        """Immediately remove an image

        Call the super class method after deleting data to ensure references are removed
        """
        del self.references[image_id]

    @abstractmethod
    def prune_images(self) -> int:
        """Remove all images with zero confirmed references, returning the number removed

        Call the super class method after deleting data to ensure refrences are removed
        """
        self.references.prune()
