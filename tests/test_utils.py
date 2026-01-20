"""
Tests for utility functions.
"""

import pytest
import tempfile
from pathlib import Path

from src.utils import (
    temp_dir_context,
    create_temp_filename,
    ensure_directory,
    cleanup_temp_files
)


def test_temp_dir_context():
    """Test temporary directory context manager."""
    with temp_dir_context() as temp_dir:
        assert temp_dir.exists()
        # Create a test file
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()

    # Directory should be cleaned up after exiting
    assert not temp_dir.exists()


def test_temp_dir_context_cleanup_on_exception():
    """Test that temp directory is cleaned up even on exception."""
    temp_dir = None
    try:
        with temp_dir_context() as temp_dir:
            assert temp_dir.exists()
            raise ValueError("Test exception")
    except ValueError:
        pass

    # Directory should still be cleaned up
    assert not temp_dir.exists()


def test_ensure_directory_new():
    """Test creating a new directory."""
    with tempfile.TemporaryDirectory() as temp_root:
        new_dir = Path(temp_root) / "new_test_dir"
        assert not new_dir.exists()

        result = ensure_directory(new_dir)
        assert result == new_dir
        assert new_dir.exists()
        assert new_dir.is_dir()


def test_ensure_directory_existing():
    """Test ensuring an existing directory."""
    with tempfile.TemporaryDirectory() as temp_root:
        existing_dir = Path(temp_root) / "existing"
        existing_dir.mkdir()

        result = ensure_directory(existing_dir)
        assert result == existing_dir
        assert existing_dir.exists()


def test_ensure_directory_nested():
    """Test creating nested directories."""
    with tempfile.TemporaryDirectory() as temp_root:
        nested_dir = Path(temp_root) / "level1" / "level2" / "level3"
        assert not nested_dir.exists()

        result = ensure_directory(nested_dir)
        assert result == nested_dir
        assert nested_dir.exists()


def test_cleanup_temp_files():
    """Test cleanup of temporary files."""
    with tempfile.TemporaryDirectory() as temp_root:
        # Create test files
        files = []
        for i in range(3):
            file_path = Path(temp_root) / f"temp_{i}.txt"
            file_path.write_text(f"content {i}")
            files.append(file_path)
            assert file_path.exists()

        # Cleanup
        cleanup_temp_files(files)

        # Verify files are deleted
        for file_path in files:
            assert not file_path.exists()


def test_cleanup_temp_files_nonexistent():
    """Test cleanup of files that don't exist (should not raise error)."""
    with tempfile.TemporaryDirectory() as temp_root:
        nonexistent_file = Path(temp_root) / "nonexistent.txt"
        assert not nonexistent_file.exists()

        # Should not raise error
        cleanup_temp_files([nonexistent_file])


def test_cleanup_temp_files_mixed():
    """Test cleanup when some files exist and some don't."""
    with tempfile.TemporaryDirectory() as temp_root:
        existing_file = Path(temp_root) / "existing.txt"
        existing_file.write_text("exists")

        nonexistent_file = Path(temp_root) / "nonexistent.txt"

        # Should not raise error
        cleanup_temp_files([existing_file, nonexistent_file])

        # Only existing file should be deleted
        assert not existing_file.exists()
        assert not nonexistent_file.exists()
