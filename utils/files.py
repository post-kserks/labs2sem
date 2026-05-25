from __future__ import annotations

from pathlib import Path

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def list_images(directory: Path) -> list[Path]:
    images = [
        path
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
    ]
    return sorted(images, key=lambda item: item.name.lower())


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
