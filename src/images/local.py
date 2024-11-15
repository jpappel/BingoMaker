import hashlib
import json
import shutil
from collections.abc import Iterable
from pathlib import Path

from .image_manager import Count, ImageID, ImageInfo, ImageManager, ReferenceCounts


class CountEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Count):
            return {"confirmed": o.confirmed, "unconfirmed": o.unconfirmed}
        return super().default(o)


class LocalReferenceCounts(ReferenceCounts):
    def __init__(self, path: str | Path, initial_counts: dict[ImageID, Count] | None = None):
        self._path = path if isinstance(path, Path) else Path(path)
        if not self._path.exists():
            self._counts = initial_counts or {}
            self.write()
        elif initial_counts:
            self._counts = initial_counts
        else:
            self.read()

    def read(self):
        with open(self._path) as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("JSON data is not an object")

        del self._counts
        self._counts = {}
        for image_id in data:
            try:
                assert isinstance(data[image_id]["confirmed"], int)
                assert isinstance(data[image_id]["unconfirmed"], int)
                self._counts[image_id] = Count(
                    data[image_id]["confirmed"], data[image_id]["unconfirmed"]
                )
            except (KeyError, AssertionError) as e:
                raise ValueError from e

    def write(self):
        """Write current counts to local storage"""
        with open(self._path, "w") as f:
            if len(self._counts) == 0:
                f.write("{}")
            else:
                json.dump(self._counts, f, cls=CountEncoder)


class LocalImageManager(ImageManager):
    def __init__(self, root: str | Path, counter: ReferenceCounts):
        self.root = root if isinstance(root, Path) else Path(root)
        self._references = counter

    def _iter_files(self) -> Iterable[str]:
        for _, _, filenames in self.root.walk():
            yield from filenames

    def _find_file(self, id_: ImageID) -> Path | None:
        for path in self.root.glob(f"{id_}.*"):
            return path
        raise FileNotFoundError()

    @property
    def references(self) -> ReferenceCounts:
        return self._references

    def add_image(self, data, info: ImageInfo) -> ImageID:
        hash_ = hashlib.file_digest(data, "sha256").hexdigest()
        data.seek(0)

        filename = hash_ + info["extentsion"]
        filepath = self.root / filename

        if not filepath.exists():
            self.references[hash_] = Count(0, 0)
        elif not filepath.is_file():
            raise FileExistsError(f"{filename} already exists but isn't a regular file")

        self.references[hash_] = self.references[hash_] + Count(1, 0)
        if filepath.exists():
            return hash_

        with open(filepath, "wb") as dest:
            shutil.copyfileobj(data, dest)

        return hash_

    def get_image(self, id: ImageID) -> str:
        path = self._find_file(id)
        if path:
            return path.as_uri()
        raise FileNotFoundError("Could not find file")

    def delete_image(self, image_id: ImageID) -> bool:
        path = self._find_file(image_id)
        if path:
            path.unlink()
            return True
        del self.references[image_id]
        return False

    def prune_images(self) -> int:
        zero_count = Count(0, 0)
        delete_ids = [
            image_id for image_id in self.references if self.references[image_id] == zero_count
        ]
        for image_id in delete_ids:
            if not self.delete_image(image_id):
                raise Exception(f"Failed to delete image: {image_id}")

        return len(delete_ids)
