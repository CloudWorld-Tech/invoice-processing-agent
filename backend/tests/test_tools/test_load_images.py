"""Tests for load_images tool."""
import os
import tempfile

import pytest

from src.tools.load_images import SUPPORTED_EXTENSIONS, load_images


@pytest.fixture
def sample_folder(tmp_path):
    """Create a temp folder with fake invoice images."""
    for name in ["invoice1.png", "invoice2.jpg", "invoice3.jpeg"]:
        (tmp_path / name).write_bytes(b"\x89PNG\r\n")
    # Non-image file
    (tmp_path / "notes.txt").write_text("not an image")
    return tmp_path


@pytest.fixture
def empty_folder(tmp_path):
    return tmp_path


class TestLoadImages:
    @pytest.mark.asyncio
    async def test_load_from_folder(self, sample_folder):
        refs = await load_images(folder_path=str(sample_folder))
        assert len(refs) == 3
        assert all(r.file_name.endswith((".png", ".jpg", ".jpeg")) for r in refs)

    @pytest.mark.asyncio
    async def test_indexes_are_sequential(self, sample_folder):
        refs = await load_images(folder_path=str(sample_folder))
        indexes = [r.index for r in refs]
        assert indexes == [0, 1, 2]

    @pytest.mark.asyncio
    async def test_nonexistent_folder_raises(self):
        with pytest.raises(FileNotFoundError):
            await load_images(folder_path="/nonexistent/folder")

    @pytest.mark.asyncio
    async def test_empty_folder_raises(self, empty_folder):
        with pytest.raises(ValueError, match="No invoice images found"):
            await load_images(folder_path=str(empty_folder))

    @pytest.mark.asyncio
    async def test_load_uploaded_files(self, tmp_path):
        f1 = tmp_path / "up1.png"
        f1.write_bytes(b"\x89PNG")
        refs = await load_images(uploaded_files=[str(f1)])
        assert len(refs) == 1
        assert refs[0].file_name == "up1.png"

    @pytest.mark.asyncio
    async def test_no_input_raises(self):
        with pytest.raises(ValueError):
            await load_images()

    @pytest.mark.asyncio
    async def test_ignores_non_image_files(self, sample_folder):
        refs = await load_images(folder_path=str(sample_folder))
        names = [r.file_name for r in refs]
        assert "notes.txt" not in names

    @pytest.mark.asyncio
    async def test_supported_extensions(self):
        assert ".png" in SUPPORTED_EXTENSIONS
        assert ".jpg" in SUPPORTED_EXTENSIONS
        assert ".jpeg" in SUPPORTED_EXTENSIONS
