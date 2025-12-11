"""
Configuration settings for video converter
"""

import os

# Directories
INPUT_DIR = "input"
OUTPUT_DIR = "output"
LOGS_DIR = "logs"

# Supported input formats
SUPPORTED_FORMATS = ['.mkv', '.avi']

# FFmpeg video settings
VIDEO_CODEC = 'libx264'
VIDEO_PRESET = 'medium'  # Options: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
VIDEO_CRF = 23  # Constant Rate Factor: 18-28 (lower = better quality, larger file)
PIXEL_FORMAT = 'yuv420p'  # Required for QuickTime compatibility

# FFmpeg audio settings
AUDIO_CODEC = 'aac'
AUDIO_BITRATE = '192k'
AUDIO_CHANNELS = 2  # Stereo

# FFmpeg output settings
MOVFLAGS = '+faststart'  # Enable fast start for streaming/web compatibility

# Language codes for French
FRENCH_LANGUAGE_CODES = ['fra', 'fre', 'fr', 'french']

# Quality presets
QUALITY_PRESETS = {
    'high': {'crf': 18, 'preset': 'slow'},
    'balanced': {'crf': 23, 'preset': 'medium'},
    'compressed': {'crf': 28, 'preset': 'fast'}
}

# GPU acceleration (macOS)
# Set to True to use hardware encoding (faster but may reduce quality slightly)
USE_GPU_ACCELERATION = False
GPU_ENCODER = 'h264_videotoolbox'  # macOS hardware encoder

# Subtitle settings
INCLUDE_SUBTITLES = True
SUBTITLE_CODEC = 'mov_text'  # QuickTime compatible subtitle format

# File naming
OUTPUT_SUFFIX = '_converted'

# Logging
LOG_LEVEL = 'INFO'  # Options: DEBUG, INFO, WARNING, ERROR
