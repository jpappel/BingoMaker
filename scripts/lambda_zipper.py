"""Utility for zipping a directory with python code

Does not copy cached or compiled python files
"""

import sys
import zipfile
from pathlib import Path


def zip_handler(filename) -> zipfile.ZipFile:
    return zipfile.ZipFile(filename, "w", zipfile.ZIP_DEFLATED)


def zip_dir(zipf: zipfile.ZipFile, root_path: str | Path):
    path = root_path if isinstance(root_path, Path) else Path(root_path)
    for root, _, files in path.walk(top_down=False, follow_symlinks=False):
        for file in files:
            file_path = root / file
            if "__pycache__" in file_path.parts or file_path.suffix in (".pyc", ".pyo"):
                continue
            zipf.write(root / file, file_path.relative_to(path.parent))


if __name__ == "__main__":
    archive_filename = sys.argv[1]
    directory = sys.argv[2]

    with zip_handler(archive_filename) as zf:
        zip_dir(zf, directory)
