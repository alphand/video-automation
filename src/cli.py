"""
Command-line interface for video automation.
"""

import argparse
import sys
import subprocess
from pathlib import Path

from src.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
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
        '--audio-transition-mode',
        type=str,
        default='gap',
        choices=['gap', 'crossfade', 'none'],
        help='Audio transition between clips: gap (silence), crossfade, or none (default: gap)'
    )

    parser.add_argument(
        '--audio-gap-duration',
        type=float,
        default=0.5,
        help='Duration of silence gap between clips in seconds (default: 0.5, only for gap mode)'
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
    """
    Main entry point for the CLI.

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
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
            temp_dir=args.temp_dir,
            audio_transition_mode=args.audio_transition_mode,
            audio_gap_duration=args.audio_gap_duration
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
