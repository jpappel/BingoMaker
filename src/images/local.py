import hashlib
import json
import shutil
from collections.abc import Iterable
from pathlib import Path

from .image_manager import Count, ImageID, ImageInfo, ImageManager, ReferenceCounts


class CountEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Count):
            return {"confirmed": o.confirmed, "unconfirmed": 0}
        return super().default(o)


class LocalReferenceCounts(ReferenceCounts):
    def __init__(self, path: str | Path, initial_counts: dict[ImageID, Count] | None = None):
        self._path = path if isinstance(path, Path) else Path(path)
        self._counts = initial_counts or self.read()

    def read(self):
        with open(self._path) as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("JSON data is not an object")

        for image_id in data:
            try:
                assert isinstance(data[image_id]["confirmed"], int)
                assert isinstance(data[image_id]["unconfirmed"], int)
            except (KeyError, AssertionError) as e:
                raise ValueError from e

        self._counts = data

    def write(self):
        """Write current counts to local storage"""
        with open(self._path, "w") as f:
            json.dump(self._counts, f, cls=CountEncoder)


class LocalImageManager(ImageManager):
    def __init__(self, root: str | Path, counter: ReferenceCounts):
        self.manager_id = "PROBABLY WILL DELETE THIS FIELD"
        self.root = root if isinstance(root, Path) else Path(root)
        self._references = counter

    def _iter_files(self) -> Iterable[str]:
        for _, _, filenames in self.root.walk():
            yield from filenames

    def _find_file(self, id_: ImageID) -> Path | None:
        for path in self.root.glob(f"{id_[1]}.*"):
            return path

    @property
    def references(self) -> ReferenceCounts:
        return self._references

    def add_image(self, data, info: ImageInfo) -> ImageID:
        hash_ = hashlib.file_digest(data, "sha256").hexdigest()
        data.seek(0)

        id_ = self.manager_id, hash_

        filename = hash_ + info["extentsion"]
        filepath = self.root / filename

        if filepath.exists():
            if filepath.is_file():
                count = self.references[id_]
                count += Count(1, 0)
                return id_
            raise FileExistsError(f"{filename} already exists but isn't a regular file")

        with open(filepath, "w") as dest:
            shutil.copyfileobj(data, dest)

        return id_

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
        super().prune_images()
        raise NotImplementedError()
