#!/usr/bin/env python3
"""
Video Converter - Convert MKV and AVI files to QuickTime-compatible MP4
with French audio as default
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from typing import Optional, List
import re
import time

import config
import utils


class VideoConverter:
    """Main video converter class"""

    def __init__(self, logger, crf: Optional[int] = None, preset: Optional[str] = None):
        """
        Initialize video converter

        Args:
            logger: Logger instance
            crf: Optional custom CRF value
            preset: Optional custom preset
        """
        self.logger = logger
        self.crf = crf if crf is not None else config.VIDEO_CRF
        self.preset = preset if preset is not None else config.VIDEO_PRESET

    def build_ffmpeg_command(
        self,
        input_path: str,
        output_path: str,
        probe_data: dict
    ) -> List[str]:
        """
        Build FFmpeg command with proper flags

        Args:
            input_path: Path to input file
            output_path: Path to output file
            probe_data: FFprobe data

        Returns:
            FFmpeg command as list of arguments
        """
        video_streams, audio_streams, subtitle_streams = utils.get_streams_info(probe_data, self.logger)

        # Start building command
        cmd = ['ffmpeg', '-i', input_path]

        # Video encoding settings
        if config.USE_GPU_ACCELERATION:
            self.logger.info(f"Using GPU acceleration: {config.GPU_ENCODER}")
            cmd.extend(['-c:v', config.GPU_ENCODER])
        else:
            cmd.extend(['-c:v', config.VIDEO_CODEC])
            cmd.extend(['-preset', self.preset])
            cmd.extend(['-crf', str(self.crf)])

        # Pixel format for QuickTime compatibility
        cmd.extend(['-pix_fmt', config.PIXEL_FORMAT])

        # Audio encoding settings
        cmd.extend(['-c:a', config.AUDIO_CODEC])
        cmd.extend(['-b:a', config.AUDIO_BITRATE])
        cmd.extend(['-ac', str(config.AUDIO_CHANNELS)])

        # Map video stream (always use first video stream)
        if video_streams:
            cmd.extend(['-map', '0:v:0'])
        else:
            self.logger.warning("No video stream found!")

        # Map audio streams with French first
        if audio_streams:
            audio_mapping = utils.get_audio_mapping(audio_streams, self.logger)

            for output_idx, input_idx in enumerate(audio_mapping):
                cmd.extend(['-map', f'0:a:{input_idx}'])

            # Set French audio as default (first audio track after mapping)
            cmd.extend(['-disposition:a:0', 'default'])

            # Preserve language metadata for all audio tracks
            for output_idx, input_idx in enumerate(audio_mapping):
                original_stream = audio_streams[input_idx]
                tags = original_stream.get('tags', {})
                language = tags.get('language', '')
                title = tags.get('title', '')

                # Set language metadata if available
                if language:
                    cmd.extend([f'-metadata:s:a:{output_idx}', f'language={language}'])
                    self.logger.debug(f"Audio track {output_idx}: language={language}")

                # Set title metadata if available
                if title:
                    cmd.extend([f'-metadata:s:a:{output_idx}', f'title={title}'])
                    self.logger.debug(f"Audio track {output_idx}: title={title}")

        # Map subtitles if enabled
        if config.INCLUDE_SUBTITLES and subtitle_streams:
            french_sub_idx = utils.find_french_subtitle_stream(subtitle_streams, self.logger)

            # Build subtitle mapping (French first if available)
            subtitle_mapping = []
            if french_sub_idx is not None:
                subtitle_mapping.append(french_sub_idx)
                for idx in range(len(subtitle_streams)):
                    if idx != french_sub_idx:
                        subtitle_mapping.append(idx)
            else:
                subtitle_mapping = list(range(len(subtitle_streams)))

            # Map all subtitle streams
            for output_idx, input_idx in enumerate(subtitle_mapping):
                cmd.extend(['-map', f'0:s:{input_idx}'])
                cmd.extend(['-c:s', config.SUBTITLE_CODEC])

                # Set first subtitle as default
                if output_idx == 0:
                    cmd.extend(['-disposition:s:0', 'default'])

                # Preserve language metadata for all subtitle tracks
                original_stream = subtitle_streams[input_idx]
                tags = original_stream.get('tags', {})
                language = tags.get('language', '')
                title = tags.get('title', '')

                # Set language metadata if available
                if language:
                    cmd.extend([f'-metadata:s:s:{output_idx}', f'language={language}'])
                    self.logger.debug(f"Subtitle track {output_idx}: language={language}")

                # Set title metadata if available
                if title:
                    cmd.extend([f'-metadata:s:s:{output_idx}', f'title={title}'])
                    self.logger.debug(f"Subtitle track {output_idx}: title={title}")

        # MP4 optimization flags
        cmd.extend(['-movflags', config.MOVFLAGS])

        # Copy metadata
        cmd.extend(['-map_metadata', '0'])

        # Overwrite output file without asking
        cmd.extend(['-y'])

        # Output file
        cmd.append(output_path)

        return cmd

    def parse_progress(self, line: str, duration: Optional[float]) -> Optional[dict]:
        """
        Parse FFmpeg progress output

        Args:
            line: FFmpeg output line
            duration: Total video duration in seconds

        Returns:
            Dictionary with progress info, or None
        """
        # FFmpeg outputs progress like: frame=  123 fps= 45 time=00:00:05.12 ...
        time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
        fps_match = re.search(r'fps=\s*(\d+\.?\d*)', line)
        frame_match = re.search(r'frame=\s*(\d+)', line)

        if time_match:
            hours, minutes, seconds = time_match.groups()
            current_time = int(hours) * 3600 + int(minutes) * 60 + float(seconds)

            progress_info = {
                'current_time': current_time,
                'fps': float(fps_match.group(1)) if fps_match else 0,
                'frame': int(frame_match.group(1)) if frame_match else 0
            }

            if duration and duration > 0:
                progress_info['percentage'] = min(100, (current_time / duration) * 100)
                if progress_info['fps'] > 0:
                    remaining_time = (duration - current_time) / progress_info['fps']
                    progress_info['eta'] = remaining_time
            else:
                progress_info['percentage'] = 0
                progress_info['eta'] = None

            return progress_info

        return None

    def convert_video(self, input_path: str, output_path: Optional[str] = None) -> bool:
        """
        Convert video file to MP4

        Args:
            input_path: Path to input video file
            output_path: Optional output path (auto-generated if None)

        Returns:
            True if conversion successful, False otherwise
        """
        self.logger.info(f"Starting conversion: {input_path}")

        # Validate input
        if not utils.validate_input_file(input_path, self.logger):
            return False

        # Generate output path
        if output_path is None:
            output_path = utils.generate_output_path(input_path)

        self.logger.info(f"Output file: {output_path}")

        # Probe input file
        try:
            probe_data = utils.probe_file(input_path, self.logger)
        except RuntimeError as e:
            self.logger.error(f"Failed to probe file: {e}")
            return False

        # Get video duration for progress tracking
        duration = utils.get_video_duration(probe_data)
        if duration:
            self.logger.info(f"Video duration: {utils.format_duration(duration)}")

        # Get input file size
        input_size = utils.get_file_size(input_path)
        self.logger.info(f"Input file size: {utils.format_file_size(input_size)}")

        # Build FFmpeg command
        cmd = self.build_ffmpeg_command(input_path, output_path, probe_data)

        # Log the command (sanitized)
        cmd_str = ' '.join(cmd)
        self.logger.debug(f"FFmpeg command: {cmd_str}")

        # Run FFmpeg
        self.logger.info("Starting FFmpeg conversion...")
        start_time = time.time()

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            last_progress_time = 0
            for line in process.stdout:
                # Parse progress
                progress = self.parse_progress(line, duration)

                if progress:
                    current_time = time.time()
                    # Update progress every 2 seconds
                    if current_time - last_progress_time >= 2:
                        percentage = progress.get('percentage', 0)
                        fps = progress.get('fps', 0)
                        eta = progress.get('eta')

                        progress_msg = f"Progress: {percentage:.1f}% | FPS: {fps:.1f}"
                        if eta is not None:
                            progress_msg += f" | ETA: {utils.format_duration(eta)}"

                        self.logger.info(progress_msg)
                        last_progress_time = current_time

                # Log FFmpeg errors
                if 'error' in line.lower() or 'invalid' in line.lower():
                    self.logger.warning(f"FFmpeg: {line.strip()}")

            process.wait()

            if process.returncode != 0:
                self.logger.error(f"FFmpeg failed with return code {process.returncode}")
                return False

        except Exception as e:
            self.logger.error(f"Conversion failed: {e}")
            return False

        # Calculate conversion time
        elapsed_time = time.time() - start_time
        self.logger.info(f"Conversion completed in {utils.format_duration(elapsed_time)}")

        # Check output file
        if not os.path.exists(output_path):
            self.logger.error("Output file was not created")
            return False

        output_size = utils.get_file_size(output_path)
        self.logger.info(f"Output file size: {utils.format_file_size(output_size)}")

        size_ratio = (output_size / input_size) * 100
        self.logger.info(f"Size ratio: {size_ratio:.1f}% of original")

        # Verify output file integrity
        self.logger.info("Verifying output file...")
        try:
            output_probe = utils.probe_file(output_path, self.logger)
            output_duration = utils.get_video_duration(output_probe)

            if output_duration and duration:
                duration_diff = abs(output_duration - duration)
                if duration_diff > 1.0:  # Allow 1 second difference
                    self.logger.warning(
                        f"Duration mismatch: input={utils.format_duration(duration)}, "
                        f"output={utils.format_duration(output_duration)}"
                    )
                else:
                    self.logger.info("Duration verification passed")
        except Exception as e:
            self.logger.warning(f"Could not verify output file: {e}")

        self.logger.info(f"Successfully converted: {output_path}")
        return True

    def convert_batch(
        self,
        input_dir: str,
        output_dir: Optional[str] = None,
        skip_existing: bool = True
    ) -> dict:
        """
        Convert all supported files in directory

        Args:
            input_dir: Input directory path
            output_dir: Output directory path (uses config default if None)
            skip_existing: Skip files that are already converted

        Returns:
            Dictionary with conversion statistics
        """
        self.logger.info(f"Starting batch conversion from: {input_dir}")

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # Find all supported files
        files = utils.list_files_in_directory(input_dir)

        if not files:
            self.logger.warning(f"No supported files found in {input_dir}")
            return {'total': 0, 'success': 0, 'failed': 0, 'skipped': 0}

        self.logger.info(f"Found {len(files)} file(s) to process")

        stats = {'total': len(files), 'success': 0, 'failed': 0, 'skipped': 0}

        for idx, file_path in enumerate(files, 1):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Processing file {idx}/{len(files)}: {Path(file_path).name}")
            self.logger.info(f"{'='*60}")

            # Check if already converted
            if skip_existing and utils.is_already_converted(file_path, output_dir):
                self.logger.info(f"Skipping (already converted): {file_path}")
                stats['skipped'] += 1
                continue

            # Generate output path
            if output_dir:
                input_file = Path(file_path)
                output_name = f"{input_file.stem}{config.OUTPUT_SUFFIX}.mp4"
                output_path = os.path.join(output_dir, output_name)
            else:
                output_path = None

            # Convert
            success = self.convert_video(file_path, output_path)

            if success:
                stats['success'] += 1
            else:
                stats['failed'] += 1

        # Print summary
        self.logger.info(f"\n{'='*60}")
        self.logger.info("BATCH CONVERSION SUMMARY")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Total files: {stats['total']}")
        self.logger.info(f"Successfully converted: {stats['success']}")
        self.logger.info(f"Failed: {stats['failed']}")
        self.logger.info(f"Skipped: {stats['skipped']}")
        self.logger.info(f"{'='*60}")

        return stats


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Convert MKV/AVI videos to QuickTime-compatible MP4 with French audio default'
    )

    # Input/output options
    parser.add_argument(
        '--input', '-i',
        type=str,
        help='Input video file'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output video file (auto-generated if not specified)'
    )
    parser.add_argument(
        '--input-dir',
        type=str,
        help='Input directory for batch conversion'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Output directory for batch conversion'
    )

    # Quality options
    parser.add_argument(
        '--crf',
        type=int,
        help=f'CRF value for quality (18-28, lower=better, default={config.VIDEO_CRF})'
    )
    parser.add_argument(
        '--preset',
        type=str,
        choices=['ultrafast', 'superfast', 'veryfast', 'faster', 'fast', 'medium', 'slow', 'slower', 'veryslow'],
        help=f'Encoding preset (default={config.VIDEO_PRESET})'
    )
    parser.add_argument(
        '--quality',
        type=str,
        choices=['high', 'balanced', 'compressed'],
        help='Quality preset (overrides --crf and --preset)'
    )

    # Batch options
    parser.add_argument(
        '--no-skip-existing',
        action='store_true',
        help='Do not skip already converted files in batch mode'
    )

    # Logging options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        help='Log file path'
    )

    args = parser.parse_args()

    # Setup logging
    logger = utils.setup_logging(args.log_file, args.verbose)

    # Check FFmpeg availability
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("FFmpeg is not installed or not in PATH")
        logger.error("Install FFmpeg: https://ffmpeg.org/download.html")
        sys.exit(1)

    # Apply quality preset if specified
    crf = args.crf
    preset = args.preset

    if args.quality:
        preset_config = config.QUALITY_PRESETS[args.quality]
        crf = preset_config['crf']
        preset = preset_config['preset']
        logger.info(f"Using {args.quality} quality preset (CRF={crf}, preset={preset})")

    # Create converter
    converter = VideoConverter(logger, crf, preset)

    # Batch mode
    if args.input_dir:
        input_dir = args.input_dir
        output_dir = args.output_dir if args.output_dir else config.OUTPUT_DIR
        skip_existing = not args.no_skip_existing

        stats = converter.convert_batch(input_dir, output_dir, skip_existing)

        if stats['failed'] > 0:
            sys.exit(1)

    # Single file mode
    elif args.input:
        success = converter.convert_video(args.input, args.output)

        if not success:
            sys.exit(1)

    else:
        parser.print_help()
        logger.error("\nError: Must specify either --input or --input-dir")
        sys.exit(1)

    logger.info("All done!")


if __name__ == '__main__':
    main()
