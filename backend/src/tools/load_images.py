from __future__ import annotations

import os
from pathlib import Path

from src.models.invoice import ImageRef

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif", ".webp"}

# Project root for resolving relative paths
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


async def load_images(folder_path: str | None = None, uploaded_files: list[str] | None = None) -> list[ImageRef]:
    """Load invoice images from a folder path or list of uploaded file paths."""
    image_refs: list[ImageRef] = []

    if folder_path:
        folder = Path(folder_path)
        # Resolve relative paths from project root
        if not folder.is_absolute():
            folder = _PROJECT_ROOT / folder
        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        if not folder.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {folder_path}")

        files = sorted(
            f for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        )
        for i, f in enumerate(files):
            image_refs.append(ImageRef(
                file_path=str(f.resolve()),
                file_name=f.name,
                index=i,
            ))

    if uploaded_files:
        offset = len(image_refs)
        for i, fp in enumerate(uploaded_files):
            p = Path(fp)
            if not p.exists():
                raise FileNotFoundError(f"Uploaded file not found: {fp}")
            image_refs.append(ImageRef(
                file_path=str(p.resolve()),
                file_name=p.name,
                index=offset + i,
            ))

    if not image_refs:
        raise ValueError("No invoice images found. Provide a folder_path or uploaded_files.")

    return image_refs
