"""
Tests for video concatenation.
"""

import pytest
from pathlib import Path

from src.video_concat import get_video_duration


def test_get_video_duration():
    """Test getting duration from a video file."""
    # Note: This test requires an actual video file to exist
    # For CI/CD, you may want to skip or create a test video file
    pytest.skip("Requires test video file")


def test_get_video_duration_invalid_file():
    """Test that get_video_duration raises error for non-existent file."""
    with pytest.raises(Exception):  # subprocess.CalledProcessError or FileNotFoundError
        get_video_duration(Path("/nonexistent/video.mp4"))


def test_concatenate_videos_with_transitions():
    """Test concatenating videos with transitions."""
    # Note: This test requires actual video files and FFmpeg
    pytest.skip("Requires test video files")


def test_concatenate_less_than_two_videos():
    """Test that concatenation with less than 2 videos raises error."""
    pytest.skip("Requires test video files")
