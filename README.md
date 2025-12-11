# Video Converter

Convert `.mkv` and `.avi` video files to QuickTime-compatible `.mp4` format with French audio as the default track.

## Features

- **QuickTime Compatible**: H.264 video, AAC audio, proper pixel format
- **French Audio Priority**: Automatically detects and sets French audio as default
- **All Languages Preserved**: All audio tracks and subtitles are included with proper language labels, selectable in QuickTime Player (Présentation → Langues / Sous-titres)
- **Quality Preservation**: Configurable CRF settings for optimal quality
- **Batch Processing**: Convert entire directories of videos
- **Progress Tracking**: Real-time conversion progress with ETA
- **Subtitle Support**: Includes all subtitles with French prioritized when available
- **Error Handling**: Comprehensive validation and error reporting
- **Fast Start**: MP4 files optimized for streaming
- **Stream Verification**: Included script to check all audio and subtitle tracks

## Requirements

- Python 3.8 or higher
- FFmpeg (must be installed and in PATH)

## Installation

### 1. Install FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### 2. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Quick Start

The easiest way to use the converter is with the included wrapper script:

**Convert all videos in the input folder:**
```bash
./convert.sh --input-dir input
```

**Convert a single file:**
```bash
./convert.sh --input video.mkv
```

### Single File Conversion

Convert a single video file:
```bash
./convert.sh --input video.mkv
```

Or call Python directly:
```bash
python converter.py --input video.mkv
```

Specify output path:
```bash
./convert.sh --input video.mkv --output converted.mp4
```

### Batch Conversion

Convert all videos in a directory:
```bash
./convert.sh --input-dir input --output-dir output
```

Place your video files in the `input/` directory and run:
```bash
./convert.sh --input-dir input
```

### Quality Settings

Use a quality preset:
```bash
./convert.sh --input video.mkv --quality high
```

Available presets:
- `high` - Best quality, larger files (CRF 18)
- `balanced` - Good quality, reasonable size (CRF 23, default)
- `compressed` - Smaller files (CRF 28)

Custom CRF value (18-28, lower = better quality):
```bash
./convert.sh --input video.mkv --crf 20
```

Custom encoding preset:
```bash
./convert.sh --input video.mkv --preset faster
```

### Logging

Enable verbose output:
```bash
./convert.sh --input video.mkv --verbose
```

Save logs to file:
```bash
./convert.sh --input video.mkv --log-file conversion.log
```

### Verify Converted Files

Check all audio and subtitle streams in a converted file:
```bash
./check_streams.sh output/video_converted.mp4
```

This will show:
- All video streams with codec and resolution
- All audio streams with language codes and default track
- All subtitle streams with language codes and default track

## Command-Line Options

```
usage: converter.py [-h] [--input INPUT] [--output OUTPUT]
                    [--input-dir INPUT_DIR] [--output-dir OUTPUT_DIR]
                    [--crf CRF] [--preset PRESET] [--quality QUALITY]
                    [--no-skip-existing] [--verbose] [--log-file LOG_FILE]

options:
  -h, --help            Show this help message and exit
  --input, -i INPUT     Input video file
  --output, -o OUTPUT   Output video file (auto-generated if not specified)
  --input-dir INPUT_DIR Input directory for batch conversion
  --output-dir OUTPUT_DIR Output directory for batch conversion
  --crf CRF             CRF value for quality (18-28, lower=better)
  --preset PRESET       Encoding preset (ultrafast to veryslow)
  --quality QUALITY     Quality preset (high, balanced, compressed)
  --no-skip-existing    Do not skip already converted files
  --verbose, -v         Enable verbose logging
  --log-file LOG_FILE   Log file path
```

## Configuration

Edit [config.py](config.py) to customize default settings:

- **Video Settings**: codec, CRF, preset, pixel format
- **Audio Settings**: codec, bitrate, channels
- **Quality Presets**: define custom quality levels
- **GPU Acceleration**: enable hardware encoding (macOS)
- **Subtitle Settings**: include/exclude subtitles
- **Directories**: default input/output paths

## How It Works

### French Audio Priority with All Languages Available

The converter automatically:
1. Probes the input file to detect all audio tracks and subtitles
2. Identifies French audio/subtitle tracks (language codes: `fra`, `fre`, `fr`)
3. Reorders audio streams to place French first (same for subtitles)
4. Sets the French track as default with proper disposition flags
5. **Includes ALL other audio tracks and subtitles** with their original language metadata preserved
6. All tracks remain selectable in QuickTime Player via **Présentation → Langues** (audio) or **Présentation → Sous-titres** (subtitles)

**Important**: French is set as the default track, but you can easily switch to any other available language using QuickTime's menu. All language labels are preserved from the original file.

### QuickTime Compatibility

Ensures compatibility by using:
- **H.264 (libx264)** video codec
- **AAC** audio codec
- **yuv420p** pixel format (required for QuickTime)
- **faststart** flag for web streaming
- Proper MP4 container structure

### Quality Preservation

- Uses **CRF (Constant Rate Factor)** encoding for consistent quality
- Maintains original resolution and aspect ratio
- Preserves metadata (title, creation date, etc.)
- Copies chapter markers when present

## Examples

### Basic Conversion
```bash
# Convert movie.mkv to output/movie_converted.mp4
./convert.sh --input movie.mkv

# Verify all streams in the converted file
./check_streams.sh output/movie_converted.mp4
```

### High-Quality Conversion
```bash
# Convert with maximum quality
./convert.sh --input video.mkv --quality high
```

### Batch Conversion with Logging
```bash
# Convert all videos in input/ directory with detailed logs
./convert.sh --input-dir input --output-dir output --verbose --log-file logs/conversion.log
```

### Custom Settings
```bash
# Custom CRF and faster encoding
./convert.sh --input video.mkv --crf 20 --preset faster
```

## Validation

After conversion, use the included verification script:

**Check all streams (recommended):**
```bash
./check_streams.sh output/video_converted.mp4
```

**Or use FFprobe directly:**
```bash
# Check file information
ffprobe -v quiet -print_format json -show_format -show_streams output/video_converted.mp4

# Verify default audio track
ffprobe -v quiet -select_streams a:0 -show_entries stream=index,codec_name:stream_tags=language output/video_converted.mp4

# Test QuickTime compatibility
ffmpeg -v error -i output/video_converted.mp4 -f null -
```

**Play in QuickTime Player (macOS):**
```bash
open -a "QuickTime Player" output/video_converted.mp4
```

**Access language selection in QuickTime:**
- **Présentation** → **Langues** (switch audio tracks)
- **Présentation** → **Sous-titres** (switch subtitle tracks)

## Project Structure

```
video-converter/
├── convert.sh           # Convenience wrapper script
├── converter.py         # Main conversion script
├── config.py            # Configuration settings
├── utils.py             # Helper functions
├── check_streams.sh     # Stream verification script
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── VIDEO_CONVERTER_PROJECT.md  # Setup instructions
├── input/               # Place input videos here
├── output/              # Converted videos appear here
├── logs/                # Log files
└── venv/                # Python virtual environment
```

## Troubleshooting

### Issue: "FFmpeg is not installed or not in PATH"
**Solution**: Install FFmpeg and ensure it's in your system PATH
```bash
# Verify installation
ffmpeg -version
```

### Issue: QuickTime won't play the file
**Solution**: The converter already uses the correct settings (yuv420p, faststart). If issues persist, try:
```bash
./convert.sh --input video.mkv --quality high
```

### Issue: French audio not default
**Solution**: The converter automatically detects French audio. Check with:
```bash
./check_streams.sh output/video_converted.mp4
```
If your file doesn't have French audio:
1. Check available audio tracks in source: `ffprobe input.mkv`
2. The converter will log a warning if no French audio is found
3. All audio tracks are still included in the output

### Issue: Conversion is slow
**Solution**: Use a faster preset or enable GPU acceleration
```bash
# Faster encoding (lower quality/larger file)
./convert.sh --input video.mkv --preset faster

# Enable GPU acceleration (edit config.py)
USE_GPU_ACCELERATION = True
```

### Issue: File size too large
**Solution**: Increase CRF value
```bash
./convert.sh --input video.mkv --crf 28
```

### Issue: Audio out of sync
**Solution**: This is rare but if it occurs, the issue is usually with the source file. Try re-encoding with:
```bash
./convert.sh --input video.mkv --preset slow
```

## Performance Tips

- **Use SSD storage** for input/output directories
- **Enable GPU acceleration** in [config.py](config.py) (macOS: h264_videotoolbox)
- **Use faster presets** for quick conversions (trade-off: slightly larger files)
- **Batch process** multiple files to maximize efficiency
- **Keep source files on same drive** as output to avoid I/O bottlenecks

## Technical Details

### How the Wrapper Script Works

The [convert.sh](convert.sh) script:
1. Activates the Python virtual environment (`venv/`)
2. Calls `converter.py` with all passed arguments
3. Ensures consistent Python dependencies

### FFmpeg Command

The converter builds commands like:
```bash
ffmpeg -i input.mkv \
  -c:v libx264 \
  -preset medium \
  -crf 23 \
  -pix_fmt yuv420p \
  -c:a aac \
  -b:a 192k \
  -ac 2 \
  -map 0:v:0 \
  -map 0:a \
  -c:s mov_text \
  -disposition:a:0 default \
  -metadata:s:a:0 language=fra \
  -movflags +faststart \
  -map_metadata 0 \
  output.mp4
```

### Audio Stream Mapping

1. Probe all audio streams using FFprobe
2. Find French audio (language=fra/fre/fr/french)
3. Reorder streams with French audio first
4. Set French as default: `-disposition:a:0 default`
5. Preserve language metadata: `-metadata:s:a:0 language=fra`
6. Map all remaining audio tracks with their metadata

### Stream Verification

The [check_streams.sh](check_streams.sh) script uses FFprobe to display:
- Video codec, resolution, and frame rate
- All audio tracks with language codes and codec info
- All subtitle tracks with language codes
- Which tracks are marked as default

## License

This project is provided as-is for personal and educational use.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review FFmpeg documentation: https://ffmpeg.org/documentation.html
3. Check logs with `--verbose` flag for detailed error messages
