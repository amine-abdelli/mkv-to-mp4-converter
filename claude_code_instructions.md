# Video Converter Project - Implementation Guide

## Project Overview
A complete Python application that converts `.mkv` and `.avi` video files to `.mp4` format with:
- French language as default audio track (when available)
- All audio tracks and subtitles preserved with proper language metadata
- QuickTime compatibility (macOS/iOS)
- FFmpeg-powered conversion with optimized settings
- Proper audio/subtitle track mapping and reordering
- Real-time progress tracking with ETA
- Comprehensive error handling and validation
- Batch processing support
- Stream verification tools

## Prerequisites

### 1. Install FFmpeg
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Verify installation
ffmpeg -version
```

### 2. Python Environment
Ensure Python 3.8+ is installed:
```bash
python3 --version
```

## Project Setup Instructions

### Step 1: Create Project Structure
```bash
mkdir video-converter
cd video-converter
```

Create the following structure:
```
video-converter/
├── convert.sh           # Convenience wrapper script
├── converter.py         # Main conversion script
├── config.py            # Configuration settings
├── utils.py             # Helper functions
├── check_streams.sh     # Stream verification script
├── requirements.txt     # Python dependencies
├── README.md            # User documentation
├── input/               # Input videos folder (created automatically)
├── output/              # Converted videos folder (created automatically)
├── logs/                # Conversion logs (created automatically)
└── venv/                # Python virtual environment
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

The `requirements.txt` file is minimal (no external Python packages required):
```
# No external dependencies - uses only Python standard library
# FFmpeg must be installed separately on the system
```

The project uses Python's standard library (`subprocess`, `json`, `logging`, etc.) and relies on system-installed FFmpeg.

```bash
pip install -r requirements.txt  # (Currently empty, but included for future dependencies)
```

## Implementation Details

### Core FFmpeg Settings

#### QuickTime Compatibility
- **Video Codec**: H.264 (libx264) - universally compatible
- **Audio Codec**: AAC - QuickTime standard
- **Container**: MP4 with faststart flag for web compatibility
- **Pixel Format**: yuv420p - required for QuickTime

#### French Language Priority (All Languages Preserved)
- Detect all audio tracks using FFprobe
- Identify French audio track (language tags: `fre`, `fra`, `fr`, or `french`)
- Reorder audio streams to place French first
- Set disposition flag to `default` for French audio
- **Include ALL other audio tracks** with their original language metadata
- Same approach for subtitles (French first if available, all others preserved)
- All tracks remain selectable in QuickTime Player menus

#### Essential FFmpeg Flags (As Implemented)
```bash
ffmpeg -i input.mkv \
  -c:v libx264 \                      # H.264 video codec
  -preset medium \                    # Encoding speed/quality balance
  -crf 23 \                           # Quality (18-28, lower=better)
  -pix_fmt yuv420p \                  # QuickTime compatible pixel format
  -c:a aac \                          # AAC audio codec
  -b:a 192k \                         # Audio bitrate
  -ac 2 \                             # Stereo audio
  -map 0:v:0 \                        # Map first video stream
  -map 0:a:2 \                        # Map French audio (example: index 2)
  -map 0:a:0 \                        # Map original audio
  -map 0:a:1 \                        # Map other audio tracks
  -disposition:a:0 default \          # Mark first audio as default
  -metadata:s:a:0 language=fra \      # Preserve French metadata
  -metadata:s:a:0 title="French" \    # Preserve title metadata
  -map 0:s? \                         # Map all subtitle streams (optional)
  -c:s mov_text \                     # QuickTime compatible subtitles
  -movflags +faststart \              # Enable fast start for streaming
  -map_metadata 0 \                   # Copy source metadata
  -y \                                # Overwrite output without asking
  output.mp4
```

### Key Features (✅ = Implemented)

1. **✅ Video Stream Detection**
   - Probe input file using FFprobe (JSON output)
   - Identify video, audio, and subtitle tracks
   - Parse language metadata from tags
   - **Implementation**: `utils.py` - `probe_file()`, `get_streams_info()`

2. **✅ French Audio Prioritization**
   - Search for French audio track (fra/fre/fr/french)
   - Reorder streams to place French first
   - **Maintain ALL other audio tracks** as alternatives
   - Preserve original language metadata for each track
   - **Implementation**: `utils.py` - `find_french_audio_stream()`, `get_audio_mapping()`

3. **✅ Subtitle Handling**
   - Include all subtitles (configurable in `config.py`)
   - Convert subtitles to mov_text format (QuickTime compatible)
   - Set French subtitles as default if available
   - Preserve all subtitle tracks with language metadata
   - **Implementation**: `converter.py` - lines 108-145

4. **✅ Quality Preservation**
   - Use CRF (Constant Rate Factor) for quality (default: 23)
   - Support quality presets: high (18), balanced (23), compressed (28)
   - Maintain original resolution
   - Preserve aspect ratio
   - **Implementation**: `config.py` - `QUALITY_PRESETS`, `converter.py` - VideoConverter class

5. **✅ Error Handling**
   - Validate input file exists and is readable
   - Check for supported formats (.mkv, .avi)
   - Handle missing French audio gracefully (logs warning)
   - Log all operations and errors with configurable levels
   - Verify output file integrity after conversion
   - **Implementation**: `utils.py` - `validate_input_file()`, comprehensive try/catch blocks

6. **✅ Progress Tracking**
   - Display conversion progress percentage
   - Show FPS (frames per second)
   - Show estimated time remaining (ETA)
   - Report file size changes (input vs output)
   - Duration verification
   - **Implementation**: `converter.py` - `parse_progress()` method (lines 161-198)

7. **✅ Batch Processing**
   - Support converting multiple files
   - Process entire directories
   - Skip already converted files (configurable)
   - Display batch conversion summary
   - **Implementation**: `converter.py` - `convert_batch()` method (lines 328-398)

### Implementation Details

#### Audio Track Mapping Strategy (As Implemented)
The implementation in `utils.py` follows this logic:
```python
def get_audio_mapping(audio_streams, logger):
    """Generate audio stream mapping with French audio first"""
    1. Scan all audio tracks in input file using FFprobe
    2. Call find_french_audio_stream() to detect French track
    3. If French found:
       - Create mapping list with French index first: [french_idx]
       - Append all other audio indices: [french_idx, 0, 1, 2, ...]
       - Skip the French index when adding others
    4. If French not found:
       - Map all audio tracks in original order: [0, 1, 2, ...]
       - Log warning about missing French audio
    5. Return mapping list for use in FFmpeg -map commands
```

#### Metadata Preservation (✅ Implemented)
- Copy original metadata: `-map_metadata 0`
- Preserve language tags for each audio/subtitle stream
- Preserve track titles when available
- Maintain video metadata (resolution, frame rate, etc.)
- File creation date and other container metadata preserved

#### File Naming Convention (✅ Implemented)
```
input/Movie.mkv  →  output/Movie_converted.mp4
```
- Configurable suffix in `config.py`: `OUTPUT_SUFFIX = '_converted'`
- Default output directory: `output/`
- Can be overridden with `--output` or `--output-dir` flags

### Testing Checklist

- [✅] Convert .mkv file with multiple audio tracks
- [✅] Convert .avi file with single audio track
- [✅] Verify French audio is default in QuickTime Player
- [✅] Test playback on macOS QuickTime
- [✅] Verify file size is reasonable (compression ratio logged)
- [✅] Check video quality matches source (CRF-based quality)
- [✅] Confirm audio sync is maintained
- [✅] Test with files containing subtitles
- [✅] Batch convert multiple files
- [✅] Verify all language tracks are accessible in QuickTime menus
- [✅] Test stream verification with check_streams.sh
- [ ] Test playback on iOS devices (device-dependent)
- [ ] Test GPU acceleration on macOS (optional)

## Usage Examples (As Implemented)

### Using the Wrapper Script (Recommended)
```bash
# Single file conversion
./convert.sh --input video.mkv

# Batch conversion (convert entire input folder)
./convert.sh --input-dir input

# With custom quality preset
./convert.sh --input video.mkv --quality high

# Verbose mode with logging
./convert.sh --input video.mkv --verbose --log-file logs/conversion.log

# Verify converted file
./check_streams.sh output/video_converted.mp4
```

### Direct Python Usage
```bash
# Single file conversion
python converter.py --input video.mkv --output converted.mp4

# Batch conversion with custom settings
python converter.py --input-dir ./input --output-dir ./output --crf 20 --preset faster

# Force re-convert existing files
python converter.py --input-dir input --no-skip-existing
```

## Additional Features

### ✅ Implemented Features

1. **✅ GPU Acceleration** (configurable)
   - Configurable in `config.py`: `USE_GPU_ACCELERATION = True/False`
   - macOS hardware encoder: `h264_videotoolbox`
   - Significantly faster conversion with slight quality trade-off

2. **✅ All Audio Tracks Preserved**
   - Keep ALL original audio tracks
   - French reordered to first position
   - All tracks selectable in QuickTime Player
   - Language metadata preserved

3. **✅ Subtitle Support**
   - Embed all subtitles in MP4
   - Convert to mov_text format (QuickTime compatible)
   - French subtitles prioritized when available
   - Configurable: `INCLUDE_SUBTITLES` in `config.py`

4. **✅ Preset Profiles**
   - High quality (CRF 18, preset slow)
   - Balanced (CRF 23, preset medium) - default
   - Compressed (CRF 28, preset fast)
   - Configurable via `--quality` flag

5. **✅ Validation**
   - Verify output file integrity with FFprobe
   - Compare duration with source (warns if >1s difference)
   - Check for file creation
   - Report file size changes
   - Stream verification script: `check_streams.sh`

6. **✅ Convenience Scripts**
   - `convert.sh` - Wrapper to activate venv and run converter
   - `check_streams.sh` - Verify all streams in converted files

### 🔮 Future Enhancements

1. **Resume Capability**
   - Save conversion state
   - Resume interrupted conversions

2. **Web Interface**
   - Browser-based upload and conversion
   - Real-time progress monitoring

3. **Parallel Processing**
   - Convert multiple files simultaneously
   - Utilize multi-core CPUs

## Common Issues and Solutions

### Issue: QuickTime won't play the file
**Solution**: The converter automatically uses correct settings (yuv420p, faststart)
```bash
# Verify with check_streams.sh
./check_streams.sh output/video_converted.mp4

# If issues persist, try high quality preset
./convert.sh --input video.mkv --quality high
```

### Issue: French audio not default
**Solution**: Verify with the stream checker
```bash
./check_streams.sh output/video_converted.mp4
```
The converter automatically:
- Detects French audio (fra/fre/fr/french language codes)
- Reorders streams to place French first
- Sets disposition flag to default
- Logs warning if no French audio found

### Issue: File size too large
**Solution**: Use compressed preset or adjust CRF
```bash
# Smaller file size
./convert.sh --input video.mkv --quality compressed

# Or custom CRF (higher = smaller)
./convert.sh --input video.mkv --crf 28
```

### Issue: Slow conversion
**Solution**: Use faster preset or enable GPU acceleration
```bash
# Faster encoding
./convert.sh --input video.mkv --preset faster

# Enable GPU acceleration (edit config.py)
USE_GPU_ACCELERATION = True
```

### Issue: Audio out of sync
**Solution**: This is rare and usually indicates source file issues
```bash
# Try slower, more careful encoding
./convert.sh --input video.mkv --preset slow
```

### Issue: "FFmpeg is not installed"
**Solution**: Install FFmpeg first
```bash
# macOS
brew install ffmpeg

# Verify installation
ffmpeg -version
```

## Performance Tips (✅ Implemented)

- **Faster presets**: Use `--preset faster` or `--preset veryfast` (trade-off: larger files)
- **GPU acceleration**: Enable in `config.py` with `USE_GPU_ACCELERATION = True`
- **Batch processing**: Converts files sequentially with automatic skip of existing files
- **SSD storage**: Recommended for input/output directories
- **Quality presets**: Use `--quality compressed` for faster, smaller files

## Project Architecture

### Core Files (✅ Implemented)

1. **convert.sh** - Bash wrapper script
   - Activates Python virtual environment
   - Passes all arguments to converter.py
   - Ensures consistent Python environment

2. **converter.py** - Main conversion logic
   - `VideoConverter` class with conversion methods
   - FFmpeg command building with stream mapping
   - Progress parsing and display
   - Batch processing with statistics
   - Command-line argument parsing

3. **config.py** - All FFmpeg settings and configurations
   - Video codec, CRF, preset, pixel format
   - Audio codec, bitrate, channels
   - Quality presets (high/balanced/compressed)
   - GPU acceleration settings
   - Subtitle configuration
   - File naming and directories
   - Language codes for French detection

4. **utils.py** - Helper functions
   - Stream detection with FFprobe
   - Language parsing and French audio detection
   - Audio/subtitle mapping logic
   - File validation
   - Logging setup
   - Duration formatting and file size utilities

5. **check_streams.sh** - Stream verification script
   - Uses FFprobe to display all streams
   - Shows video, audio, and subtitle tracks
   - Displays language codes and default tracks
   - Useful for verifying conversion results

6. **requirements.txt** - Python dependencies
   - Currently minimal (only standard library used)
   - FFmpeg required as system dependency

7. **README.md** - Comprehensive user documentation
   - Installation instructions
   - Usage examples
   - Troubleshooting guide
   - Technical details

8. **.gitignore** - Git exclusions
   - Output files and logs
   - Python cache and virtual environment
   - OS-specific files

## Validation Commands

After conversion, validate the output:

### Using the Stream Checker (Recommended)
```bash
./check_streams.sh output/video_converted.mp4
```

### Manual FFprobe Commands
```bash
# Check all file info
ffprobe -v quiet -print_format json -show_format -show_streams output/video_converted.mp4

# Verify default audio track
ffprobe -v quiet -select_streams a:0 -show_entries stream=index,codec_name:stream_tags=language output/video_converted.mp4

# Check QuickTime compatibility
ffmpeg -v error -i output/video_converted.mp4 -f null -

# Test playback
open -a "QuickTime Player" output/video_converted.mp4
```

## Success Criteria (✅ All Achieved)

✅ Converts .mkv and .avi to .mp4 successfully
✅ QuickTime Player plays files without issues
✅ French audio is selected by default (when available)
✅ **All audio tracks and subtitles are preserved**
✅ **All tracks are selectable in QuickTime menus**
✅ Video quality is preserved with configurable CRF
✅ Conversion completes in reasonable time with progress tracking
✅ Proper error messages for invalid inputs
✅ Comprehensive logging with configurable verbosity
✅ Batch processing with statistics
✅ Stream verification tool included
✅ Convenience wrapper script for ease of use

## How to Use This Project

### For End Users
1. Place video files in `input/` folder
2. Run: `./convert.sh --input-dir input`
3. Find converted files in `output/` folder
4. Verify with: `./check_streams.sh output/filename_converted.mp4`

### For Developers
- **converter.py**: Main logic, modify FFmpeg command building in `build_ffmpeg_command()`
- **config.py**: Adjust default settings, quality presets, codecs
- **utils.py**: Add new stream detection logic or helper functions
- **convert.sh**: Modify to add pre/post-processing hooks

## Project Status

**Status**: ✅ **Complete and Production-Ready**

All core features have been implemented and tested:
- ✅ French audio prioritization with all languages preserved
- ✅ QuickTime compatibility
- ✅ Batch processing
- ✅ Progress tracking
- ✅ Error handling
- ✅ Stream verification tools
- ✅ Comprehensive documentation

The project successfully converts MKV/AVI files to QuickTime-compatible MP4 format while preserving all audio tracks and subtitles, with French set as the default language when available.
