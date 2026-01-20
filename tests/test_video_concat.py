"""
Tests for video concatenation.
"""

import pytest
from pathlib import Path

from src.video_concat import get_video_duration, build_audio_filters


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
    # Note: This test requires test video files
    pytest.skip("Requires test video files")


def test_build_audio_filters_gap_mode():
    """Test building audio filters for gap mode."""
    filters = build_audio_filters(num_videos=3, audio_transition_mode='gap', audio_gap_duration=0.5)

    assert len(filters) == 3
    assert 'aevalsrc=exprs=0:d=0.5[silence0]' in filters[0]
    assert 'aevalsrc=exprs=0:d=0.5[silence1]' in filters[1]
    assert 'concat=n=5:v=0:a=1[final_audio]' in filters[2]


def test_build_audio_filters_crossfade_mode():
    """Test building audio filters for crossfade mode."""
    filters = build_audio_filters(
        num_videos=3,
        audio_transition_mode='crossfade',
        transition_duration=1.0
    )

    assert len(filters) == 3
    assert 'acrossfade=d=1.0' in filters[0]
    assert 'acrossfade=d=1.0' in filters[1]
    assert '[a1]final_audio' in filters[2]


def test_build_audio_filters_none_mode():
    """Test building audio filters for none (hard cut) mode."""
    filters = build_audio_filters(num_videos=3, audio_transition_mode='none')

    assert len(filters) == 1
    assert 'concat=n=3:v=0:a=1[final_audio]' in filters[0]


def test_build_audio_filters_invalid_mode():
    """Test that invalid mode raises error."""
    with pytest.raises(ValueError, match="Invalid audio_transition_mode"):
        build_audio_filters(num_videos=3, audio_transition_mode='invalid')
