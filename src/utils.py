"""
Common utilities for video automation.
"""

import tempfile
import shutil
from pathlib import Path
from typing import List
from contextlib import contextmanager


@contextmanager
def temp_dir_context():
    """
    Context manager for temporary directory.

    Yields:
        Path: Path to temporary directory

    Example:
        with temp_dir_context() as temp_dir:
            # Use temp_dir
            pass
        # Directory is automatically cleaned up
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="video_automation_"))
    try:
        yield temp_dir
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def create_temp_filename(base_name: str, suffix: str) -> Path:
    """
    Create a temporary filename with proper extension.

    Args:
        base_name: Base name for the file
        suffix: File suffix/extension (e.g., ".mp4")

    Returns:
        Path: Path to temporary filename

    Example:
        temp_path = create_temp_filename("output", ".mp4")
        # Returns something like: /tmp/output_XYz123.mp4
    """
    return Path(tempfile.mktemp(prefix=f"{base_name}_", suffix=suffix))


def ensure_directory(directory: Path) -> Path:
    """
    Ensure directory exists, create if not.

    Args:
        directory: Directory path to ensure exists

    Returns:
        Path: Same directory path (now guaranteed to exist)
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def cleanup_temp_files(files: List[Path]) -> None:
    """
    Remove temporary files safely.

    Args:
        files: List of file paths to remove

    Example:
        cleanup_temp_files([Path("/tmp/file1.mp4"), Path("/tmp/file2.mp4")])
    """
    for file in files:
        if file.exists():
            file.unlink()
