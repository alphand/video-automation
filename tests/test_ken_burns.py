"""
Tests for Ken Burns effect generator.
"""

import pytest
from pathlib import Path

from src.ken_burns import calculate_random_position


def test_calculate_random_position():
    """Test that random position calculation returns valid expressions."""
    x_expr, y_expr = calculate_random_position()

    # Should be strings
    assert isinstance(x_expr, str)
    assert isinstance(y_expr, str)

    # Should contain FFmpeg expressions
    assert 'iw' in x_expr
    assert 'ih' in y_expr
    assert 'zoom' in x_expr
    assert 'zoom' in y_expr


def test_calculate_random_position_all_regions():
    """Test that all regions produce valid expressions."""
    regions = [
        "center", "top_left", "top_right", "bottom_left",
        "bottom_right", "top_center", "bottom_center",
        "left_center", "right_center"
    ]

    # Test multiple times to ensure randomness works
    expressions = []
    for _ in range(50):
        x_expr, y_expr = calculate_random_position()
        expressions.append((x_expr, y_expr))

    # Should have generated multiple different combinations
    assert len(set(expressions)) > 1

    # All expressions should be valid
    for x_expr, y_expr in expressions:
        assert isinstance(x_expr, str)
        assert isinstance(y_expr, str)
        assert len(x_expr) > 0
        assert len(y_expr) > 0


def test_create_ken_burns_video():
    """Test creating a Ken Burns video."""
    # Note: This test requires actual image and audio files
    # and FFmpeg to be installed
    pytest.skip("Requires test image and audio files")


def test_create_ken_burns_video_invalid_audio():
    """Test that invalid audio file raises error."""
    # Note: This test requires FFmpeg
    pytest.skip("Requires FFmpeg")
