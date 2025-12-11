"""
Utility functions for video conversion
"""

import json
import subprocess
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import config


def setup_logging(log_file: Optional[str] = None, verbose: bool = False) -> logging.Logger:
    """
    Setup logging configuration

    Args:
        log_file: Optional path to log file
        verbose: Enable verbose logging

    Returns:
        Configured logger instance
    """
    log_level = logging.DEBUG if verbose else getattr(logging, config.LOG_LEVEL)

    # Create logger
    logger = logging.getLogger('video_converter')
    logger.setLevel(log_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler
    if log_file:
        os.makedirs(config.LOGS_DIR, exist_ok=True)
        if not os.path.isabs(log_file):
            log_file = os.path.join(config.LOGS_DIR, log_file)

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger


def probe_file(input_path: str, logger: logging.Logger) -> Dict:
    """
    Probe video file to get stream information

    Args:
        input_path: Path to input video file
        logger: Logger instance

    Returns:
        Dictionary containing stream information

    Raises:
        RuntimeError: If ffprobe fails
    """
    logger.debug(f"Probing file: {input_path}")

    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        input_path
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        probe_data = json.loads(result.stdout)
        logger.debug(f"Successfully probed file: {len(probe_data.get('streams', []))} streams found")
        return probe_data
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to probe file: {e.stderr}")
        raise RuntimeError(f"Failed to probe file: {input_path}")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse ffprobe output: {e}")
        raise RuntimeError(f"Invalid probe data for file: {input_path}")


def get_streams_info(probe_data: Dict, logger: logging.Logger) -> Tuple[List[Dict], List[Dict], List[Dict]]:
    """
    Extract video, audio, and subtitle streams from probe data

    Args:
        probe_data: FFprobe output data
        logger: Logger instance

    Returns:
        Tuple of (video_streams, audio_streams, subtitle_streams)
    """
    streams = probe_data.get('streams', [])

    video_streams = []
    audio_streams = []
    subtitle_streams = []

    for stream in streams:
        codec_type = stream.get('codec_type', '')

        if codec_type == 'video':
            video_streams.append(stream)
        elif codec_type == 'audio':
            audio_streams.append(stream)
        elif codec_type == 'subtitle':
            subtitle_streams.append(stream)

    logger.info(f"Found {len(video_streams)} video, {len(audio_streams)} audio, {len(subtitle_streams)} subtitle streams")

    return video_streams, audio_streams, subtitle_streams


def find_french_audio_stream(audio_streams: List[Dict], logger: logging.Logger) -> Optional[int]:
    """
    Find French audio stream index

    Args:
        audio_streams: List of audio stream dictionaries
        logger: Logger instance

    Returns:
        Index of French audio stream, or None if not found
    """
    for idx, stream in enumerate(audio_streams):
        tags = stream.get('tags', {})
        language = tags.get('language', '').lower()
        title = tags.get('title', '').lower()

        logger.debug(f"Audio stream {idx}: language='{language}', title='{title}'")

        # Check if language matches any French language code
        if any(fr_code in language for fr_code in config.FRENCH_LANGUAGE_CODES):
            logger.info(f"Found French audio stream at index {idx} (language: {language})")
            return idx

        # Also check title field for French indicators
        if any(fr_code in title for fr_code in config.FRENCH_LANGUAGE_CODES):
            logger.info(f"Found French audio stream at index {idx} (title: {title})")
            return idx

    logger.warning("No French audio stream found")
    return None


def find_french_subtitle_stream(subtitle_streams: List[Dict], logger: logging.Logger) -> Optional[int]:
    """
    Find French subtitle stream index

    Args:
        subtitle_streams: List of subtitle stream dictionaries
        logger: Logger instance

    Returns:
        Index of French subtitle stream, or None if not found
    """
    for idx, stream in enumerate(subtitle_streams):
        tags = stream.get('tags', {})
        language = tags.get('language', '').lower()
        title = tags.get('title', '').lower()

        logger.debug(f"Subtitle stream {idx}: language='{language}', title='{title}'")

        # Check if language matches any French language code
        if any(fr_code in language for fr_code in config.FRENCH_LANGUAGE_CODES):
            logger.info(f"Found French subtitle stream at index {idx} (language: {language})")
            return idx

        # Also check title field
        if any(fr_code in title for fr_code in config.FRENCH_LANGUAGE_CODES):
            logger.info(f"Found French subtitle stream at index {idx} (title: {title})")
            return idx

    logger.debug("No French subtitle stream found")
    return None


def get_audio_mapping(audio_streams: List[Dict], logger: logging.Logger) -> List[int]:
    """
    Generate audio stream mapping with French audio first

    Args:
        audio_streams: List of audio stream dictionaries
        logger: Logger instance

    Returns:
        List of audio stream indices in desired order
    """
    if not audio_streams:
        logger.warning("No audio streams found")
        return []

    french_idx = find_french_audio_stream(audio_streams, logger)

    if french_idx is None:
        # No French audio found, keep original order
        logger.info("Using original audio stream order")
        return list(range(len(audio_streams)))

    # Put French audio first, then others
    mapping = [french_idx]
    for idx in range(len(audio_streams)):
        if idx != french_idx:
            mapping.append(idx)

    logger.info(f"Audio mapping order: {mapping} (French audio at position 0)")
    return mapping


def validate_input_file(input_path: str, logger: logging.Logger) -> bool:
    """
    Validate input file exists and has supported format

    Args:
        input_path: Path to input file
        logger: Logger instance

    Returns:
        True if valid, False otherwise
    """
    if not os.path.exists(input_path):
        logger.error(f"Input file does not exist: {input_path}")
        return False

    if not os.path.isfile(input_path):
        logger.error(f"Input path is not a file: {input_path}")
        return False

    file_ext = Path(input_path).suffix.lower()
    if file_ext not in config.SUPPORTED_FORMATS:
        logger.error(f"Unsupported file format: {file_ext}. Supported: {config.SUPPORTED_FORMATS}")
        return False

    logger.debug(f"Input file validation passed: {input_path}")
    return True


def generate_output_path(input_path: str, output_path: Optional[str] = None) -> str:
    """
    Generate output file path

    Args:
        input_path: Path to input file
        output_path: Optional custom output path

    Returns:
        Output file path
    """
    if output_path:
        return output_path

    input_file = Path(input_path)
    output_name = f"{input_file.stem}{config.OUTPUT_SUFFIX}.mp4"

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    return os.path.join(config.OUTPUT_DIR, output_name)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted file size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes

    Args:
        file_path: Path to file

    Returns:
        File size in bytes
    """
    return os.path.getsize(file_path)


def format_duration(seconds: float) -> str:
    """
    Format duration in HH:MM:SS format

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_video_duration(probe_data: Dict) -> Optional[float]:
    """
    Extract video duration from probe data

    Args:
        probe_data: FFprobe output data

    Returns:
        Duration in seconds, or None if not found
    """
    format_data = probe_data.get('format', {})
    duration = format_data.get('duration')

    if duration:
        return float(duration)

    return None


def list_files_in_directory(directory: str, extensions: Optional[List[str]] = None) -> List[str]:
    """
    List files in directory with optional extension filter

    Args:
        directory: Directory path
        extensions: Optional list of file extensions to filter (e.g., ['.mkv', '.avi'])

    Returns:
        List of file paths
    """
    if not os.path.exists(directory):
        return []

    if extensions is None:
        extensions = config.SUPPORTED_FORMATS

    files = []
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            file_ext = Path(file_path).suffix.lower()
            if file_ext in extensions:
                files.append(file_path)

    return sorted(files)


def is_already_converted(input_path: str, output_dir: str = None) -> bool:
    """
    Check if file has already been converted

    Args:
        input_path: Path to input file
        output_dir: Output directory (uses config default if None)

    Returns:
        True if converted file exists, False otherwise
    """
    if output_dir is None:
        output_dir = config.OUTPUT_DIR

    input_file = Path(input_path)
    output_name = f"{input_file.stem}{config.OUTPUT_SUFFIX}.mp4"
    output_path = os.path.join(output_dir, output_name)

    return os.path.exists(output_path)
