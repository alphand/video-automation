"""
Tests for audio utilities.
"""

import pytest
import subprocess
from pathlib import Path

from src.audio_utils import get_audio_duration, verify_audio_file


def test_get_audio_duration_real_file():
    """Test getting duration from a real audio file."""
    # Note: This test requires an actual audio file to exist
    # For CI/CD, you may want to skip or create a test audio file
    pytest.skip("Requires test audio file")


def test_get_audio_duration_invalid_file():
    """Test that get_audio_duration raises error for non-existent file."""
    with pytest.raises(subprocess.CalledProcessError):
        get_audio_duration(Path("/nonexistent/audio.mp3"))


def test_verify_audio_file_exists():
    """Test verification of existing audio file."""
    # Note: This test requires an actual audio file
    pytest.skip("Requires test audio file")


def test_verify_audio_file_nonexistent():
    """Test verification of non-existent file."""
    result = verify_audio_file(Path("/nonexistent/audio.mp3"))
    assert result is False


def test_verify_audio_file_directory():
    """Test verification of directory (should be False)."""
    result = verify_audio_file(Path("/tmp"))  # Assuming /tmp exists
    assert result is False
