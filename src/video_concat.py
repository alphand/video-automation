"""
Video concatenation with smooth transitions using FFmpeg xfade filter.
"""

import subprocess
import json
from pathlib import Path
from typing import List

from src.transitions import get_random_transition


def get_video_duration(video_path: Path) -> float:
    """
    Get video duration using ffprobe.

    Args:
        video_path: Path to video file

    Returns:
        Duration in seconds as float

    Raises:
        subprocess.CalledProcessError: If ffprobe fails
        ValueError: If video duration is invalid
    """
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        str(video_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    duration = float(data['format']['duration'])

    if duration <= 0:
        raise ValueError(f"Invalid duration: {duration}")

    return duration


def concatenate_videos_with_transitions(
    video_paths: List[Path],
    output_path: Path,
    transition_duration: float = 1.0,
    transition_type: str = None,
    use_random_transitions: bool = True,
    excluded_transitions: List[str] = None
) -> Path:
    """
    Concatenate multiple videos with smooth transitions.

    Args:
        video_paths: List of video file paths in order
        output_path: Path for final output video
        transition_duration: Duration of each transition (default 1.0s)
        transition_type: Specific transition to use (None = random)
        use_random_transitions: Use different transition for each segment
        excluded_transitions: Transitions to exclude from random selection

    Returns:
        Path to output video

    Raises:
        ValueError: If less than 2 videos provided
        subprocess.CalledProcessError: If FFmpeg fails

    Example:
        final_video = concatenate_videos_with_transitions(
            video_paths=[Path("clip1.mp4"), Path("clip2.mp4")],
            output_path=Path("final.mp4"),
            transition_duration=1.5,
            use_random_transitions=True
        )
    """
    if len(video_paths) < 2:
        raise ValueError("At least 2 videos required for concatenation with transitions")

    # Get video durations
    durations = [get_video_duration(vp) for vp in video_paths]

    # Build filter chain
    # xfade only accepts 2 inputs at a time, so we chain them
    video_filters = []
    audio_filters = []

    # Track cumulative offset for xfade
    cumulative_duration = durations[0]

    for i in range(len(video_paths) - 1):
        # Determine transition type
        if use_random_transitions:
            trans = get_random_transition(exclude=excluded_transitions)
        else:
            trans = transition_type if transition_type else 'fade'

        # Calculate offset: previous video duration minus transition duration - small buffer
        offset = cumulative_duration - transition_duration - 0.05

        # xfade for video
        if i == 0:
            # First transition: [0:v][1:v]xfade...
            video_filters.append(
                f"[{i}:v][{i+1}:v]xfade=transition={trans}:duration={transition_duration}:offset={offset}[v{i}]"
            )
        else:
            # Chain: previous_result[v{i-1}][{i+1}:v]xfade...
            video_filters.append(
                f"[v{i-1}][{i+1}:v]xfade=transition={trans}:duration={transition_duration}:offset={offset}[v{i}]"
            )

        # acrossfade for audio
        if i == 0:
            # First transition: [0:a][1:a]acrossfade...
            audio_filters.append(
                f"[{i}:a][{i+1}:a]acrossfade=d={transition_duration}[a{i}]"
            )
        else:
            # Chain: previous_result[a{i-1}][{i+1}:a]acrossfade...
            audio_filters.append(
                f"[a{i-1}][{i+1}:a]acrossfade=d={transition_duration}[a{i}]"
            )

        # Update cumulative duration
        cumulative_duration += durations[i + 1] - transition_duration

    # Join all filters
    filter_complex = ";".join(video_filters + audio_filters)

    # Build FFmpeg command
    input_args = []
    for vp in video_paths:
        input_args.extend(['-i', str(vp)])

    cmd = [
        'ffmpeg',
        '-y',
    ] + input_args + [
        '-filter_complex', filter_complex,
        '-map', f'[v{len(video_paths)-2}]',
        '-map', f'[a{len(video_paths)-2}]',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-preset', 'fast',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        '-movflags', '+faststart',
        str(output_path)
    ]

    subprocess.run(cmd, check=True, capture_output=True)

    return output_path
