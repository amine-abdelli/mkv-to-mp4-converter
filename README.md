# Video Converter

Convert `.mkv` and `.avi` video files to QuickTime-compatible `.mp4` format with French audio as the default track.

## Features

- **QuickTime Compatible**: H.264 video, AAC audio, proper pixel format
- **French Audio Priority**: Automatically detects and sets French audio as default
- **Quality Preservation**: Configurable CRF settings for optimal quality
- **Batch Processing**: Convert entire directories of videos
- **Progress Tracking**: Real-time conversion progress with ETA
- **Subtitle Support**: Includes French subtitles when available
- **Error Handling**: Comprehensive validation and error reporting
- **Fast Start**: MP4 files optimized for streaming

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

### Single File Conversion

Convert a single video file:
```bash
python converter.py --input video.mkv
```

Specify output path:
```bash
python converter.py --input video.mkv --output converted.mp4
```

### Batch Conversion

Convert all videos in a directory:
```bash
python converter.py --input-dir ./input --output-dir ./output
```

Place your video files in the `input/` directory and run:
```bash
python converter.py --input-dir input
```

### Quality Settings

Use a quality preset:
```bash
python converter.py --input video.mkv --quality high
```

Available presets:
- `high` - Best quality, larger files (CRF 18)
- `balanced` - Good quality, reasonable size (CRF 23, default)
- `compressed` - Smaller files (CRF 28)

Custom CRF value (18-28, lower = better quality):
```bash
python converter.py --input video.mkv --crf 20
```

Custom encoding preset:
```bash
python converter.py --input video.mkv --preset faster
```

### Logging

Enable verbose output:
```bash
python converter.py --input video.mkv --verbose
```

Save logs to file:
```bash
python converter.py --input video.mkv --log-file conversion.log
```

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

### French Audio Priority

The converter automatically:
1. Probes the input file to detect all audio tracks
2. Identifies French audio tracks (language codes: `fra`, `fre`, `fr`)
3. Reorders audio streams to place French first
4. Sets the French track as default with proper disposition flags
5. Includes all other audio tracks as alternatives

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
python converter.py --input movie.mkv

# Verify French audio is default
ffprobe -v quiet -select_streams a:0 -show_entries stream_tags=language output/movie_converted.mp4
```

### High-Quality Conversion
```bash
# Convert with maximum quality
python converter.py --input video.mkv --quality high
```

### Batch Conversion with Logging
```bash
# Convert all videos in input/ directory with detailed logs
python converter.py --input-dir input --output-dir output --verbose --log-file logs/conversion.log
```

### Custom Settings
```bash
# Custom CRF and faster encoding
python converter.py --input video.mkv --crf 20 --preset faster
```

## Validation

After conversion, validate the output:

**Check file information:**
```bash
ffprobe -v quiet -print_format json -show_format -show_streams output/video_converted.mp4
```

**Verify default audio track:**
```bash
ffprobe -v quiet -select_streams a:0 -show_entries stream=index,codec_name:stream_tags=language output/video_converted.mp4
```

**Test QuickTime compatibility:**
```bash
ffmpeg -v error -i output/video_converted.mp4 -f null -
```

**Play in QuickTime Player (macOS):**
```bash
open -a "QuickTime Player" output/video_converted.mp4
```

## Project Structure

```
video-converter/
├── converter.py          # Main conversion script
├── config.py            # Configuration settings
├── utils.py             # Helper functions
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── VIDEO_CONVERTER_PROJECT.md  # Setup instructions
├── input/              # Place input videos here
├── output/             # Converted videos appear here
└── logs/               # Log files
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
python converter.py --input video.mkv --quality high
```

### Issue: French audio not default
**Solution**: The converter automatically detects French audio. If your file doesn't have French audio:
1. Check available audio tracks: `ffprobe input.mkv`
2. The converter will log a warning if no French audio is found
3. All audio tracks are still included in the output

### Issue: Conversion is slow
**Solution**: Use a faster preset or enable GPU acceleration
```bash
# Faster encoding (lower quality/larger file)
python converter.py --input video.mkv --preset faster

# Enable GPU acceleration (edit config.py)
USE_GPU_ACCELERATION = True
```

### Issue: File size too large
**Solution**: Increase CRF value
```bash
python converter.py --input video.mkv --crf 28
```

### Issue: Audio out of sync
**Solution**: This is rare but if it occurs, the issue is usually with the source file. Try re-encoding with:
```bash
python converter.py --input video.mkv --preset slow
```

## Performance Tips

- **Use SSD storage** for input/output directories
- **Enable GPU acceleration** in [config.py](config.py) (macOS: h264_videotoolbox)
- **Use faster presets** for quick conversions (trade-off: slightly larger files)
- **Batch process** multiple files to maximize efficiency
- **Keep source files on same drive** as output to avoid I/O bottlenecks

## Technical Details

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
  -map 0:a:0 -map 0:a:1 \
  -disposition:a:0 default \
  -metadata:s:a:0 language=fra \
  -movflags +faststart \
  -map_metadata 0 \
  output.mp4
```

### Audio Stream Mapping

1. Probe all audio streams
2. Find French audio (language=fra/fre/fr)
3. Map French audio first: `-map 0:a:X`
4. Set as default: `-disposition:a:0 default`
5. Set French metadata: `-metadata:s:a:0 language=fra`
6. Map remaining audio tracks

## License

This project is provided as-is for personal and educational use.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review FFmpeg documentation: https://ffmpeg.org/documentation.html
3. Check logs with `--verbose` flag for detailed error messages
