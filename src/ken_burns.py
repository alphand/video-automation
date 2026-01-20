"""
Ken Burns effect generator for creating dynamic video from static images.
"""

import subprocess
from pathlib import Path
import random
from typing import Tuple

from src.audio_utils import get_audio_duration


# Random position regions
POSITION_REGIONS = [
    "center",           # Center of image
    "top_left",         # Top-left quadrant
    "top_right",        # Top-right quadrant
    "bottom_left",      # Bottom-left quadrant
    "bottom_right",     # Bottom-right quadrant
    "top_center",       # Top edge center
    "bottom_center",    # Bottom edge center
    "left_center",      # Left edge center
    "right_center",     # Right edge center
]


def calculate_random_position() -> Tuple[str, str]:
    """
    Calculate random starting position for zoom.

    Returns:
        Tuple of (x_expression, y_expression) for FFmpeg zoompan filter

    Example:
        x_expr, y_expr = calculate_random_position()
        # Returns: ("'iw/2-(iw/zoom/2)'", "'ih/2-(ih/zoom/2)'") for center
    """
    region = random.choice(POSITION_REGIONS)

    if region == "center":
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih/2-(ih/zoom/2)'"
    elif region == "top_left":
        x_expr = "'iw/20-(iw/zoom/2)'"
        y_expr = "'ih/20-(ih/zoom/2)'"
    elif region == "top_right":
        x_expr = "'iw-(iw/20)-(iw/zoom/2)'"
        y_expr = "'ih/20-(ih/zoom/2)'"
    elif region == "bottom_left":
        x_expr = "'iw/20-(iw/zoom/2)'"
        y_expr = "'ih-(ih/20)-(ih/zoom/2)'"
    elif region == "bottom_right":
        x_expr = "'iw-(iw/20)-(iw/zoom/2)'"
        y_expr = "'ih-(ih/20)-(ih/zoom/2)'"
    elif region == "top_center":
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih/15-(ih/zoom/2)'"
    elif region == "bottom_center":
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih-(ih/15)-(ih/zoom/2)'"
    elif region == "left_center":
        x_expr = "'iw/15-(iw/zoom/2)'"
        y_expr = "'ih/2-(ih/zoom/2)'"
    elif region == "right_center":
        x_expr = "'iw-(iw/15)-(iw/zoom/2)'"
        y_expr = "'ih/2-(ih/zoom/2)'"
    else:
        # Default to center
        x_expr = "'iw/2-(iw/zoom/2)'"
        y_expr = "'ih/2-(ih/zoom/2)'"

    return x_expr, y_expr


def create_ken_burns_video(
    image_path: Path,
    audio_path: Path,
    output_path: Path,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    start_zoom: float = 1.15,
    end_zoom: float = 1.0
) -> Path:
    """
    Create a Ken Burns zoom-out video from image with duration matching audio.

    Args:
        image_path: Path to input image
        audio_path: Path to audio file (for duration)
        output_path: Path for output video
        width: Output width (default 1920)
        height: Output height (default 1080)
        fps: Frame rate (default 30)
        start_zoom: Starting zoom level (default 1.15 = 15% zoom)
        end_zoom: Ending zoom level (default 1.0)

    Returns:
        Path to output video

    Raises:
        subprocess.CalledProcessError: If FFmpeg fails
        ValueError: If parameters are invalid

    Example:
        video_path = create_ken_burns_video(
            image_path=Path("photo.jpg"),
            audio_path=Path("narration.mp3"),
            output_path=Path("output.mp4")
        )
    """
    # Get duration from audio
    duration = get_audio_duration(audio_path)
    total_frames = int(fps * duration)

    # Calculate zoom increment per frame
    zoom_increment = (start_zoom - end_zoom) / total_frames

    # Get random position
    x_expr, y_expr = calculate_random_position()

    # Build zoompan filter
    # 1. Pre-scale to 10x height for smoothness
    # 2. Apply zoompan with zoom out
    # 3. Smooth easing: start zoomed, gradually zoom out
    zoompan_filter = (
        f"scale=-2:ih*10,"
        f"zoompan="
        f"z='if(eq(on,1),{start_zoom},max(zoom-{zoom_increment},{end_zoom}))':"
        f"x={x_expr}:"
        f"y={y_expr}:"
        f"d={total_frames}:"
        f"s={width}x{height}:"
        f"fps={fps}"
    )

    # Build FFmpeg command
    cmd = [
        'ffmpeg',
        '-y',  # Overwrite output file
        '-r', str(fps),
        '-loop', '1',
        '-t', str(duration),
        '-i', str(image_path),
        '-i', str(audio_path),  # Add audio input
        '-vf', zoompan_filter,
        '-vframes', str(total_frames),
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'fast',
        '-crf', '23',
        '-c:a', 'aac',
        '-shortest',  # Match audio duration
        str(output_path)
    ]

    subprocess.run(cmd, check=True, capture_output=True)

    return output_path
