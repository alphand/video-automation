# Video Automation CLI

A Python CLI tool that creates professional Ken Burns effect slideshows from ordered image/audio pairs. Perfect for creating dynamic video presentations from static images with narration or background music.

## Features

- **Ken Burns Effect**: Smooth zoom-out animations from random positions on each image
- **Parallel Processing**: Multi-core processing for faster generation of large batches
- **Smart Transitions**: Random transition effects (fade, dissolve, slide, wipe, and more)
- **Audio Sync**: Each slide duration matches its paired audio file automatically
- **Crossfade**: Smooth audio transitions between segments
- **Multiple Formats**: Supports JPG, PNG, JPEG, HEIC images and MP3, WAV, M4A, OGG, AAC audio

## Installation

### Prerequisites

- **Python 3.9 or higher**
- **FFmpeg** (must be installed separately)

#### Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

### Install the CLI

```bash
# Clone or download the repository
cd video-automation

# Install dependencies
pip install -r requirements.txt

# Optional: Install in development mode
pip install -e .
```

## Quick Start

### 1. Prepare Your Files

Create two directories with matching numbered files:

```
my-project/
├── images/
│   ├── image_001.jpg
│   ├── image_002.jpg
│   └── image_003.jpg
└── audio/
    ├── audio_001.mp3
    ├── audio_002.mp3
    └── audio_003.mp3
```

**Important**: Files must be named with 3-digit numbers:
- Images: `image_001.jpg`, `image_002.jpg`, etc.
- Audio: `audio_001.mp3`, `audio_002.mp3`, etc.

### 2. Run the CLI

```bash
python -m src.cli -i images/ -a audio/ -o output.mp4
```

That's it! The CLI will:
1. Discover and pair your image/audio files
2. Process each pair in parallel with Ken Burns effect
3. Concatenate all videos with smooth transitions
4. Save the final video to `output.mp4`

## Usage

### Basic Usage

```bash
python -m src.cli -i <images-dir> -a <audio-dir> -o <output-file>
```

### Full Options

```bash
python -m src.cli \
  -i images/ \
  -a audio/ \
  -o output.mp4 \
  --width 1920 \
  --height 1080 \
  --fps 30 \
  --transition-duration 1.5 \
  --workers 4
```

### Command-Line Arguments

| Argument | Short | Description | Default |
|----------|--------|-------------|---------|
| `--images` | `-i` | Directory containing images (image_*.jpg) | **Required** |
| `--audio` | `-a` | Directory containing audio (audio_*.mp3) | **Required** |
| `--output` | `-o` | Output video file path | **Required** |
| `--width` | `-w` | Output video width | 1920 |
| `--height` | `-H` | Output video height | 1080 |
| `--fps` | `-f` | Output frame rate | 30 |
| `--transition-duration` | `-t` | Duration of transitions (seconds) | 1.0 |
| `--audio-transition-mode` | | Audio transition: gap, crossfade, or none (default: gap) |
| `--audio-gap-duration` | | Silence gap duration in seconds (default: 0.5, gap mode only) |
| `--workers` | | Number of parallel workers | CPU count |
| `--temp-dir` | | Custom temp directory for intermediate files | Auto-created |

### Examples

**Create a 720p video:**
```bash
python -m src.cli -i images/ -a audio/ -o output.mp4 -w 1280 -h 720
```

**Use 8 parallel workers:**
```bash
python -m src.cli -i images/ -a audio/ -o output.mp4 --workers 8
```

**Longer transitions (2 seconds):**
```bash
python -m src.cli -i images/ -a audio/ -o output.mp4 -t 2.0
```

**Keep temporary files for debugging:**
```bash
python -m src.cli -i images/ -a audio/ -o output.mp4 --temp-dir /tmp/my-debug
```

**Use silence gaps between clips (default):**
```bash
python -m src.cli -i images/ -a audio/ -o output.mp4
```

**Use crossfade (old behavior):**
```bash
python -m src.cli -i images/ -a audio/ -o output.mp4 --audio-transition-mode crossfade
```

**Custom gap duration:**
```bash
python -m src.cli -i images/ -a audio/ -o output.mp4 --audio-gap-duration 1.0
```

**Hard cuts (no audio transition):**
```bash
python -m src.cli -i images/ -a audio/ -o output.mp4 --audio-transition-mode none
```

## How It Works

### The Pipeline

```
1. File Discovery
   ├── Scans images/ for image_###.ext
   ├── Scans audio/ for audio_###.ext
   └── Pairs matching indices (001, 002, 003, ...)

2. Parallel Processing (Ken Burns)
   ├── For each image/audio pair:
   │   ├── Read audio duration with ffprobe
   │   ├── Calculate zoom parameters
   │   ├── Apply zoompan filter (zoom-out from random position)
   │   └── Mux with audio
   └── Process all pairs simultaneously (ProcessPoolExecutor)

3. Concatenation
   ├── Calculate video durations
   ├── Build xfade filter chain (random transitions)
   ├── Build acrossfade filter chain (audio)
   └── Concatenate with smooth transitions

4. Output
   └── Final video saved to specified path
```

### Ken Burns Effect

- **Zoom**: Starts at 1.15x zoom, smoothly zooms out to 1.0x
- **Position**: Randomly chosen from 9 regions (center, corners, edges)
- **Smoothness**: Uses 10x pre-scaling to eliminate jitter
- **Duration**: Automatically matches audio file duration

### Transitions

Randomly selects from 16 transition types:
- `fade`, `dissolve`, `pixelize`
- `slideleft`, `slideright`, `slideup`, `slidedown`
- `smoothleft`, `smoothright`, `smoothup`, `smoothdown`
- `fadeblack`, `fadewhite`, `circleopen`
- `wipeleft`, `wiperight`

## Project Structure

```
video-automation/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── cli.py                # CLI interface (argparse)
│   ├── pipeline.py           # Main orchestration
│   ├── ken_burns.py          # Ken Burns effect generator
│   ├── audio_utils.py         # Audio duration detection
│   ├── video_concat.py        # Video concatenation with transitions
│   ├── transitions.py         # Transition types & management
│   └── utils.py              # Common utilities (temp files, cleanup)
├── tests/
│   ├── __init__.py
│   ├── test_ken_burns.py
│   ├── test_audio_utils.py
│   ├── test_video_concat.py
│   └── test_pipeline_integration.py
├── examples/
│   ├── images/               # Sample images
│   └── audio/                # Sample audio
├── pyproject.toml            # Project configuration
├── requirements.txt           # Python dependencies
├── README.md                 # This file
└── .gitignore               # Git ignore rules
```

## Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_ken_burns.py
```

## Performance

Processing speed depends on:
- Number of CPU cores (parallel workers)
- Image resolution and audio duration
- Transition duration
- Output codec settings

**Typical performance on 8-core machine:**
- 10 pairs (30s each): ~2 minutes
- 100 pairs (30s each): ~15 minutes

## Troubleshooting

### "FFmpeg not found"
**Error**: `FileNotFoundError: ffprobe not found`

**Solution**: Install FFmpeg (see Prerequisites section)

### "No matching image/audio pairs found"
**Error**: `ValueError: No matching image/audio pairs found`

**Solution**: Check file naming:
- Images must match pattern: `image_###.ext` (e.g., `image_001.jpg`)
- Audio must match pattern: `audio_###.ext` (e.g., `audio_001.mp3`)
- Use 3-digit numbers with leading zeros: `001`, `002`, `003`

### "Missing matching files for: ..."
**Error**: `ValueError: Missing matching files for: image_003, audio_005`

**Solution**: Ensure every image has a matching audio file with the same index

### "ffprobe failed"
**Error**: `subprocess.CalledProcessError: ffprobe returned non-zero`

**Solution**:
- Check audio file is valid and not corrupted
- Try playing the audio file in a media player
- Ensure file format is supported (MP3, WAV, M4A, OGG, AAC)

### Slow processing
**Solution**:
- Reduce `--workers` if your system is struggling
- Lower resolution with `--width` and `--height`
- Shorten audio files to reduce processing time

### Low disk space
**Error**: `No space left on device`

**Solution**:
- Use custom temp directory on different drive: `--temp-dir /path/to/other/drive`
- Clean up temporary files manually
- Process fewer pairs at a time

## Technical Details

### FFmpeg Filters

**Ken Burns (zoompan)**:
```
scale=-2:ih*10,zoompan=z='...':x='...':y='...':d=...:s=1920x1080:fps=30
```

**Transitions (xfade)**:
```
[0:v][1:v]xfade=transition=fade:duration=1.0:offset=29.0[v0]
[0:a][1:a]acrossfade=d=1.0[a0]
```

**Audio Transitions**:
- Gap mode (default): `aevalsrc=exprs=0:d=0.5` creates silence + `concat=n=5:v=0:a=1` chains audio+silence
- Crossfade mode: `acrossfade=d=1.0` overlaps audio clips
- None mode: `concat=n=3:v=0:a=1` simple hard cut

### Design Decisions

1. **FFmpeg via subprocess** (not ffmpeg-python wrapper)
   - Direct control over filter graphs
   - Easier debugging
   - No library overhead

2. **ProcessPoolExecutor** (not ThreadPoolExecutor)
   - True parallelism for CPU-bound FFmpeg tasks
   - Each worker gets its own process

3. **10x pre-scaling** for Ken Burns
   - Reduces jitter from rounding errors
   - Industry best practice for smooth zoom

4. **Random transitions** per segment
   - More dynamic final video
   - Variety without manual configuration

5. **Auto-created temp directory**
   - Cleanup handled automatically
   - Can override for debugging

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Include your OS, Python version, and FFmpeg version

## Acknowledgments

- **FFmpeg**: The powerful multimedia framework that makes this all possible
- **pytest**: Excellent testing framework
- All contributors who help improve this tool
