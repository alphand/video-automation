"""
Audio utilities for duration detection.
"""

import subprocess
import json
from pathlib import Path


def get_audio_duration(audio_path: Path) -> float:
    """
    Get audio duration in seconds using ffprobe.

    Args:
        audio_path: Path to audio file

    Returns:
        Duration in seconds as float

    Raises:
        subprocess.CalledProcessError: If ffprobe fails
        ValueError: If audio file is invalid or duration is zero/negative

    Example:
        duration = get_audio_duration(Path("audio.mp3"))
        # Returns: 30.5
    """
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        str(audio_path)
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )

    data = json.loads(result.stdout)
    duration = float(data['format']['duration'])

    if duration <= 0:
        raise ValueError(f"Invalid duration: {duration}")

    return duration


def verify_audio_file(audio_path: Path) -> bool:
    """
    Verify audio file is valid and accessible.

    Args:
        audio_path: Path to audio file

    Returns:
        True if file exists and is accessible, False otherwise

    Example:
        if verify_audio_file(Path("audio.mp3")):
            print("Audio file is valid")
    """
    return audio_path.exists() and audio_path.is_file()
