# Video Automation CLI - Implementation Plan

## Overview

Build a Python CLI tool that creates a Ken Burns effect slideshow from ordered image/audio pairs.

**Tech Stack:**
- FFmpeg `zoompan` filter for Ken Burns effect
- FFmpeg `xfade` + `acrossfade` for transitions
- `ffprobe` for audio duration detection
- `concurrent.futures.ProcessPoolExecutor` for parallel processing
- `argparse` for CLI interface

**Workflow:**
```
images/image_001.jpg + audio/audio_001.mp3 
  → Ken Burns video (zoom-out from random position)
  → Mux with audio
  → Repeat for all pairs in parallel
  → Concatenate with transitions
  → Final output.mp4
```

---

## Project Structure

```
video-automation/
├── src/
│   ├── __init__.py
│   ├── cli.py                    # CLI interface (argparse)
│   ├── pipeline.py               # Main orchestration
│   ├── ken_burns.py              # Ken Burns effect generator
│   ├── audio_utils.py            # Audio duration detection
│   ├── video_concat.py           # Video concatenation with transitions
│   ├── transitions.py            # Transition types & management
│   └── utils.py                  # Common utilities (temp files, cleanup)
├── tests/
│   ├── __init__.py
│   ├── test_ken_burns.py
│   ├── test_audio_utils.py
│   ├── test_video_concat.py
│   └── test_pipeline_integration.py
├── examples/
│   ├── images/                   # Sample images
│   └── audio/                    # Sample audio
├── pyproject.toml
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Phase 1: Core Utilities

### 1.1 Audio Duration Detection (src/audio_utils.py)

```python
# src/audio_utils.py
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
        ValueError: If audio file is invalid
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
    """Verify audio file is valid and accessible."""
    return audio_path.exists() and audio_path.is_file()
```

### 1.2 Utilities (src/utils.py)

```python
# src/utils.py
import tempfile
import shutil
from pathlib import Path
from typing import List
from contextlib import contextmanager

@contextmanager
def temp_dir_context():
    """Context manager for temporary directory."""
    temp_dir = Path(tempfile.mkdtemp(prefix="video_automation_"))
    try:
        yield temp_dir
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

def create_temp_filename(base_name: str, suffix: str) -> Path:
    """Create a temporary filename with proper extension."""
    return Path(tempfile.mktemp(prefix=f"{base_name}_", suffix=suffix))

def ensure_directory(directory: Path) -> Path:
    """Ensure directory exists, create if not."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory

def cleanup_temp_files(files: List[Path]) -> None:
    """Remove temporary files safely."""
    for file in files:
        if file.exists():
            file.unlink()
```

---

## Phase 2: Ken Burns Effect Generator

### 2.1 Transitions Module (src/transitions.py)

```python
# src/transitions.py
import random
from typing import List

# Available transitions that work well for slideshows
TRANSITION_TYPES = [
    'fade',          # Classic crossfade (most common)
    'dissolve',      # Dissolve effect
    'pixelize',      # Pixelated transition
    'slideleft',     # Slide from right
    'slideright',    # Slide from left
    'slideup',       # Slide from bottom
    'slidedown',     # Slide from top
    'smoothleft',    # Smooth slide left
    'smoothright',   # Smooth slide right
    'smoothup',      # Smooth slide up
    'smoothdown',    # Smooth slide down
    'fadeblack',     # Fade through black
    'fadewhite',     # Fade through white
    'circleopen',    # Circle reveal
    'wipeleft',      # Wipe from right
    'wiperight',     # Wipe from left
]

def get_random_transition(exclude: List[str] = None) -> str:
    """
    Get a random transition type.
    
    Args:
        exclude: List of transitions to exclude from random selection
        
    Returns:
        Transition type string
    """
    available = TRANSITION_TYPES.copy()
    if exclude:
        available = [t for t in available if t not in exclude]
    
    return random.choice(available)

def validate_transition(transition: str) -> bool:
    """
    Validate that a transition type is supported.
    
    Args:
        transition: Transition type to validate
        
    Returns:
        True if valid, False otherwise
    """
    return transition in TRANSITION_TYPES
```

### 2.2 Ken Burns Module (src/ken_burns.py)

```python
# src/ken_burns.py
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
        Tuple of (x_expression, y_expression) for FFmpeg zoompan
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
        '-vf', zoompan_filter,
        '-vframes', str(total_frames),
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'fast',
        '-crf', '23',
        str(output_path)
    ]
    
    subprocess.run(cmd, check=True, capture_output=True)
    
    return output_path
```

---

## Phase 3: Video Concatenation

### 3.1 Video Concatenation (src/video_concat.py)

```python
# src/video_concat.py
import subprocess
from pathlib import Path
from typing import List, Tuple
from src.transitions import get_random_transition
import random

def get_video_duration(video_path: Path) -> float:
    """Get video duration using ffprobe."""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        str(video_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])

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
            # Chain: previous_result[i:v][{i+1}:v]xfade...
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
            # Chain: previous_result[a{a-1}][{i+1}:a]acrossfade...
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
```

---

## Phase 4: Pipeline Orchestration

### 4.1 Main Pipeline (src/pipeline.py)

```python
# src/pipeline.py
import os
import re
from pathlib import Path
from typing import List, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed
import tempfile
import shutil

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
    temp_dir: Path = None
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
        
    Returns:
        Path to final output video
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
            use_random_transitions=True
        )
        
        print(f"✨ Final video created: {output_path}")
        return final_video
        
    finally:
        # Cleanup temp directory
        if cleanup_temp and temp_context:
            temp_context.__exit__(None, None, None)
```

---

## Phase 5: CLI Interface

### 5.1 CLI Module (src/cli.py)

```python
# src/cli.py
import argparse
import sys
from pathlib import Path
from src.pipeline import run_pipeline

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Create Ken Burns effect slideshow from image/audio pairs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i images/ -a audio/ -o output.mp4
  %(prog)s -i images/ -a audio/ -o output.mp4 -w 1280 -h 720
  %(prog)s -i images/ -a audio/ -o output.mp4 --workers 4
        """
    )
    
    parser.add_argument(
        '-i', '--images',
        type=Path,
        required=True,
        help='Directory containing images (image_001.jpg, image_002.jpg, ...)'
    )
    
    parser.add_argument(
        '-a', '--audio',
        type=Path,
        required=True,
        help='Directory containing audio files (audio_001.mp3, audio_002.mp3, ...)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=Path,
        required=True,
        help='Output video file path'
    )
    
    parser.add_argument(
        '-w', '--width',
        type=int,
        default=1920,
        help='Output video width (default: 1920)'
    )
    
    parser.add_argument(
        '-H', '--height',
        type=int,
        default=1080,
        help='Output video height (default: 1080)'
    )
    
    parser.add_argument(
        '-f', '--fps',
        type=int,
        default=30,
        help='Output frame rate (default: 30)'
    )
    
    parser.add_argument(
        '-t', '--transition-duration',
        type=float,
        default=1.0,
        help='Duration of transitions between clips in seconds (default: 1.0)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=None,
        help='Number of parallel workers (default: CPU count)'
    )
    
    parser.add_argument(
        '--temp-dir',
        type=Path,
        default=None,
        help='Temporary directory for intermediate files (default: auto-created)'
    )
    
    return parser.parse_args()

def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    try:
        print("=" * 60)
        print("🎬 Video Automation CLI")
        print("=" * 60)
        
        output_path = run_pipeline(
            images_dir=args.images,
            audio_dir=args.audio,
            output_path=args.output,
            width=args.width,
            height=args.height,
            fps=args.fps,
            transition_duration=args.transition_duration,
            max_workers=args.workers,
            temp_dir=args.temp_dir
        )
        
        print("\n" + "=" * 60)
        print(f"✅ Success! Output saved to: {output_path}")
        print("=" * 60)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"❌ Error: File not found: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

---

## Phase 6: Configuration & Documentation

### 6.1 Requirements (requirements.txt)

```txt
# Video Automation CLI Requirements
# Python 3.9+

# Testing
pytest>=7.0.0
pytest-cov>=4.0.0

# FFmpeg must be installed separately
# macOS: brew install ffmpeg
# Ubuntu: sudo apt install ffmpeg
# Windows: Download from https://ffmpeg.org/download.html
```

### 6.2 Project Configuration (pyproject.toml)

```toml
[project]
name = "video-automation"
version = "0.1.0"
description = "CLI tool for creating Ken Burns effect slideshows from image/audio pairs"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Your Name"}
]

[project.scripts]
video-automation = "src.cli:main"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

### 6.3 .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Temporary files
video_automation_*/
temp_*/
*.temp
*.mp4
!examples/audio/*.mp3
!examples/images/*.jpg
```

---

## Implementation Checklist

### Phase 1: Core Utilities
- [ ] Create project structure directories
- [ ] Create `src/utils.py` (temp files, cleanup)
- [ ] Create `src/audio_utils.py` (ffprobe duration)
- [ ] Write tests for audio_utils
- [ ] Write tests for utils

### Phase 2: Ken Burns Generator
- [ ] Create `src/transitions.py` (transition types)
- [ ] Create `src/ken_burns.py` (zoom-out effect)
- [ ] Implement random position calculation
- [ ] Add pre-scaling for smoothness
- [ ] Write tests for ken_burns module
- [ ] Test with various image formats

### Phase 3: Video Concatenation
- [ ] Create `src/video_concat.py` (xfade chain)
- [ ] Implement audio crossfade
- [ ] Add random transition selection
- [ ] Handle multiple videos
- [ ] Write tests for video_concat
- [ ] Test concatenation with 2-5 videos

### Phase 4: Pipeline Orchestration
- [ ] Create `src/pipeline.py` file
- [ ] Implement file discovery and pairing
- [ ] Implement parallel processing with ProcessPoolExecutor
- [ ] Implement error handling
- [ ] Add progress output
- [ ] Write integration tests
- [ ] Test with 100 pairs

### Phase 5: CLI Interface
- [ ] Create `src/cli.py` with argparse
- [ ] Add help text and examples
- [ ] Implement error handling
- [ ] Test CLI with various arguments
- [ ] Test missing arguments validation

### Phase 6: Configuration & Documentation
- [ ] Create `requirements.txt`
- [ ] Create `pyproject.toml`
- [ ] Write comprehensive `README.md`
- [ ] Create `.gitignore`
- [ ] Add sample files in examples/
- [ ] Add LICENSE file

### Phase 7: Testing & Optimization
- [ ] Run full test suite
- [ ] Test with 100+ image/audio pairs
- [ ] Verify parallel processing performance
- [ ] Test on different OS (macOS, Linux, Windows)
- [ ] Add integration test with real files
- [ ] Document performance benchmarks

---

## Key Technical Decisions

1. **FFmpeg via subprocess** (not ffmpeg-python wrapper)
   - More direct control over filter graphs
   - Easier debugging
   - Avoids library overhead

2. **ProcessPoolExecutor** (not ThreadPoolExecutor)
   - True parallelism for CPU-bound FFmpeg tasks
   - Each worker gets its own process

3. **Pre-scaling 10x height** for Ken Burns
   - Reduces jitter from rounding errors
   - Industry best practice

4. **Random transitions** per segment
   - More dynamic final video
   - Variety without manual configuration

5. **Auto-created temp directory**
   - Cleanup handled automatically
   - Can override for debugging

---

## Potential Issues & Solutions

| Issue | Solution |
|-------|----------|
| FFmpeg not installed | Clear error message with installation instructions |
| Insufficient disk space | Add temp directory option to specify location |
| Image/audio file mismatch | Raise ValueError with details of missing files |
| Video format incompatibility | Always output as mp4 with h.264/aac |
| Slow processing | Implement progress bars, suggest lower worker count |
| Memory issues with large batches | Add chunked processing option |

---

## Estimated Timeline

| Phase | Duration |
|-------|----------|
| Phase 1: Core Utilities | 1 day |
| Phase 2: Ken Burns Generator | 1-2 days |
| Phase 3: Video Concatenation | 1-2 days |
| Phase 4: Pipeline Orchestration | 1-2 days |
| Phase 5: CLI Interface | 1 day |
| Phase 6: Configuration & Docs | 1 day |
| Phase 7: Testing & Optimization | 1-2 days |
| **Total** | **7-11 days** |
