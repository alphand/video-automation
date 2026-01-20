"""
Integration tests for the complete pipeline.
"""

import pytest
import tempfile
from pathlib import Path

from src.pipeline import discover_and_pair_files


def test_discover_and_pair_files_no_files():
    """Test file discovery with no matching files."""
    with tempfile.TemporaryDirectory() as temp_root:
        images_dir = Path(temp_root) / "images"
        audio_dir = Path(temp_root) / "audio"
        images_dir.mkdir()
        audio_dir.mkdir()

        with pytest.raises(ValueError, match="No matching image/audio pairs"):
            discover_and_pair_files(images_dir, audio_dir)


def test_discover_and_pair_files_missing_pairs():
    """Test file discovery with mismatched pairs."""
    with tempfile.TemporaryDirectory() as temp_root:
        images_dir = Path(temp_root) / "images"
        audio_dir = Path(temp_root) / "audio"
        images_dir.mkdir()
        audio_dir.mkdir()

        # Create image_001.jpg but no audio_001.mp3
        (images_dir / "image_001.jpg").write_text("fake image")

        with pytest.raises(ValueError, match="Missing matching files"):
            discover_and_pair_files(images_dir, audio_dir)


def test_discover_and_pair_files_valid_pairs():
    """Test file discovery with valid matching pairs."""
    with tempfile.TemporaryDirectory() as temp_root:
        images_dir = Path(temp_root) / "images"
        audio_dir = Path(temp_root) / "audio"
        images_dir.mkdir()
        audio_dir.mkdir()

        # Create matching pairs
        (images_dir / "image_001.jpg").write_text("image 1")
        (audio_dir / "audio_001.mp3").write_text("audio 1")
        (images_dir / "image_002.jpg").write_text("image 2")
        (audio_dir / "audio_002.mp3").write_text("audio 2")

        pairs = discover_and_pair_files(images_dir, audio_dir)

        assert len(pairs) == 2
        assert pairs[0][2] == 1  # Index 1
        assert pairs[1][2] == 2  # Index 2
        assert pairs[0][0].name == "image_001.jpg"
        assert pairs[0][1].name == "audio_001.mp3"


def test_run_pipeline():
    """Test running the complete pipeline."""
    # Note: This test requires FFmpeg, real images and audio
    pytest.skip("Requires FFmpeg and test media files")


def test_discover_and_pair_files_wrong_format():
    """Test file discovery with wrong naming format."""
    with tempfile.TemporaryDirectory() as temp_root:
        images_dir = Path(temp_root) / "images"
        audio_dir = Path(temp_root) / "audio"
        images_dir.mkdir()
        audio_dir.mkdir()

        # Create files with wrong naming format
        (images_dir / "photo_1.jpg").write_text("wrong format")
        (audio_dir / "sound_1.mp3").write_text("wrong format")

        with pytest.raises(ValueError, match="No matching image/audio pairs"):
            discover_and_pair_files(images_dir, audio_dir)
