"""
Main pipeline orchestration for video automation.
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed

from src.ken_burns import create_ken_burns_video
from src.video_concat import concatenate_videos_with_transitions
from src.utils import temp_dir_context, ensure_directory


def discover_and_pair_files(
    images_dir: Path,
    audio_dir: Path
) -> List[Tuple[Path, Path, int]]:
    """
    Discover and pair image/audio files based on naming convention.

    Expected format: image_001.jpg with audio_001.mp3

    Args:
        images_dir: Directory containing images
        audio_dir: Directory containing audio files

    Returns:
        List of tuples: [(image_path, audio_path, index), ...] sorted by index

    Raises:
        ValueError: If no pairs found or mismatched files

    Example:
        pairs = discover_and_pair_files(
            images_dir=Path("images/"),
            audio_dir=Path("audio/")
        )
        # Returns: [(Path("images/image_001.jpg"), Path("audio/audio_001.mp3"), 1), ...]
    """
    # Pattern: image_###.ext or audio_###.ext
    image_pattern = re.compile(r'^image_(\d+)\.(jpg|jpeg|png|heic)$', re.IGNORECASE)
    audio_pattern = re.compile(r'^audio_(\d+)\.(mp3|wav|m4a|ogg|aac)$', re.IGNORECASE)

    # Find all matching files
    images = {}
    audio_files = {}

    for img_path in images_dir.iterdir():
        if img_path.is_file():
            match = image_pattern.match(img_path.name)
            if match:
                index = int(match.group(1))
                images[index] = img_path

    for audio_path in audio_dir.iterdir():
        if audio_path.is_file():
            match = audio_pattern.match(audio_path.name)
            if match:
                index = int(match.group(1))
                audio_files[index] = audio_path

    # Verify we have matching pairs
    all_indices = sorted(set(images.keys()) | set(audio_files.keys()))

    if not all_indices:
        raise ValueError(f"No matching image/audio pairs found in {images_dir} and {audio_dir}")

    pairs = []
    missing = []

    for index in all_indices:
        if index in images and index in audio_files:
            pairs.append((images[index], audio_files[index], index))
        elif index in images:
            missing.append(f"audio_{index:03d}")
        else:
            missing.append(f"image_{index:03d}")

    if missing:
        raise ValueError(f"Missing matching files for: {', '.join(missing)}")

    # Sort by index
    pairs.sort(key=lambda x: x[2])

    return pairs


def process_single_pair(args: Tuple[Path, Path, Path]) -> Path:
    """
    Process a single image/audio pair - designed for parallel execution.

    Args:
        args: Tuple of (image_path, audio_path, temp_output_path)

    Returns:
        Path to generated video

    Example:
        video_path = process_single_pair((
            Path("image.jpg"),
            Path("audio.mp3"),
            Path("output.mp4")
        ))
    """
    image_path, audio_path, temp_output = args
    return create_ken_burns_video(image_path, audio_path, temp_output)


def run_pipeline(
    images_dir: Path,
    audio_dir: Path,
    output_path: Path,
    width: int = 1920,
    height: int = 1080,
    fps: int = 30,
    transition_duration: float = 1.0,
    max_workers: int = None,
    temp_dir: Path = None,
    audio_transition_mode: str = 'gap',
    audio_gap_duration: float = 0.5
) -> Path:
    """
    Run complete video automation pipeline.

    Args:
        images_dir: Directory containing images
        audio_dir: Directory containing audio files
        output_path: Path for final output video
        width: Output video width (default 1920)
        height: Output video height (default 1080)
        fps: Output frame rate (default 30)
        transition_duration: Duration of transitions (default 1.0s)
        max_workers: Max parallel workers (default: os.cpu_count())
        temp_dir: Temporary directory for intermediate files (auto-created if None)
        audio_transition_mode: Audio transition mode: 'gap', 'crossfade', or 'none' (default 'gap')
        audio_gap_duration: Duration of silence gap in seconds for gap mode (default 0.5)

    Returns:
        Path to final output video

    Raises:
        ValueError: If file discovery fails
        subprocess.CalledProcessError: If FFmpeg fails

    Example:
        final_video = run_pipeline(
            images_dir=Path("images/"),
            audio_dir=Path("audio/"),
            output_path=Path("output.mp4"),
            width=1280,
            height=720
        )
    """
    # Ensure directories exist
    images_dir = Path(images_dir)
    audio_dir = Path(audio_dir)
    output_path = Path(output_path)

    ensure_directory(images_dir)
    ensure_directory(audio_dir)

    # Discover and pair files
    print(f"🔍 Discovering files in {images_dir} and {audio_dir}...")
    pairs = discover_and_pair_files(images_dir, audio_dir)
    print(f"✅ Found {len(pairs)} image/audio pairs")

    # Setup temp directory
    if temp_dir is None:
        temp_context = temp_dir_context()
        temp_dir = temp_context.__enter__()
        cleanup_temp = True
    else:
        temp_dir = ensure_directory(temp_dir)
        cleanup_temp = False
        temp_context = None

    try:
        # Process pairs in parallel
        max_workers = max_workers or os.cpu_count()
        print(f"🚀 Processing {len(pairs)} pairs with {max_workers} workers...")

        temp_videos = []
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all jobs
            futures = {}
            for i, (image_path, audio_path, index) in enumerate(pairs):
                temp_output = temp_dir / f"pair_{index:03d}.mp4"
                future = executor.submit(
                    process_single_pair,
                    (image_path, audio_path, temp_output)
                )
                futures[future] = index

            # Collect results
            for i, future in enumerate(as_completed(futures)):
                index = futures[future]
                try:
                    temp_video = future.result()
                    temp_videos.append((temp_video, index))
                    print(f"  ✓ Completed pair {index:03d} ({i+1}/{len(pairs)})")
                except Exception as e:
                    print(f"  ✗ Failed pair {index:03d}: {e}")
                    raise

        # Sort by index
        temp_videos.sort(key=lambda x: x[1])
        video_paths = [tv[0] for tv in temp_videos]

        # Concatenate with transitions
        print(f"🎞️  Concatenating {len(video_paths)} videos with transitions...")
        final_video = concatenate_videos_with_transitions(
            video_paths=video_paths,
            output_path=output_path,
            transition_duration=transition_duration,
            use_random_transitions=True,
            audio_transition_mode=audio_transition_mode,
            audio_gap_duration=audio_gap_duration
        )

        print(f"✨ Final video created: {output_path}")
        return final_video

    finally:
        # Cleanup temp directory
        if cleanup_temp and temp_context:
            temp_context.__exit__(None, None, None)
