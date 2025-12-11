# Video Converter Project - Setup Instructions

## Project Overview
Create a Python application that converts `.mkv` and `.avi` video files to `.mp4` format with:
- French language as default audio track
- QuickTime compatibility
- FFmpeg-powered conversion with optimized settings
- Proper audio/subtitle track mapping

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
├── converter.py          # Main conversion script
├── requirements.txt      # Python dependencies
├── config.py            # Configuration settings
├── utils.py             # Helper functions
├── input/               # Input videos folder
├── output/              # Converted videos folder
└── logs/                # Conversion logs
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

Create `requirements.txt`:
```
ffmpeg-python==0.2.0
```

Install:
```bash
pip install -r requirements.txt
```

## Implementation Details

### Core FFmpeg Settings

#### QuickTime Compatibility
- **Video Codec**: H.264 (libx264) - universally compatible
- **Audio Codec**: AAC - QuickTime standard
- **Container**: MP4 with faststart flag for web compatibility
- **Pixel Format**: yuv420p - required for QuickTime

#### French Language Priority
- Detect all audio tracks
- Identify French audio track (language tag: `fre`, `fra`, or `fr`)
- Map French audio as first/default track
- Set disposition flag to `default` for French audio
- Include other audio tracks as alternatives

#### Essential FFmpeg Flags
```bash
ffmpeg -i input.mkv \
  -c:v libx264 \              # H.264 video codec
  -preset medium \            # Encoding speed/quality balance
  -crf 23 \                   # Quality (18-28, lower=better)
  -c:a aac \                  # AAC audio codec
  -b:a 192k \                 # Audio bitrate
  -ac 2 \                     # Stereo audio
  -pix_fmt yuv420p \          # QuickTime compatible pixel format
  -movflags +faststart \      # Enable fast start for streaming
  -map 0:v:0 \                # Map video stream
  -map 0:a \                  # Map all audio streams
  -metadata:s:a:0 language=fra \  # Set French as default
  -disposition:a:0 default \  # Mark first audio as default
  output.mp4
```

### Key Features to Implement

1. **Video Stream Detection**
   - Probe input file to detect streams
   - Identify video, audio, and subtitle tracks
   - Parse language metadata

2. **French Audio Prioritization**
   - Search for French audio track (fra/fre/fr)
   - Reorder streams to place French first
   - Maintain other audio tracks as alternatives

3. **Subtitle Handling**
   - Optionally include French subtitles
   - Convert subtitles to mov_text format (QuickTime compatible)
   - Set French subtitles as default if available

4. **Quality Preservation**
   - Use CRF (Constant Rate Factor) for quality
   - Maintain original resolution
   - Preserve aspect ratio

5. **Error Handling**
   - Validate input file exists and is readable
   - Check for corrupted videos
   - Handle missing French audio gracefully
   - Log all operations and errors

6. **Progress Tracking**
   - Display conversion progress percentage
   - Show estimated time remaining
   - Report file size changes

7. **Batch Processing**
   - Support converting multiple files
   - Process entire directories
   - Skip already converted files

### Advanced Considerations

#### Audio Track Mapping Strategy
```python
# Pseudo-logic for audio mapping
1. Scan all audio tracks in input file
2. Find French audio track (check language metadata)
3. If French found:
   - Map French audio as stream 0
   - Map other audio tracks after
4. If French not found:
   - Map all audio tracks in original order
   - Log warning about missing French audio
```

#### Metadata Preservation
- Copy original metadata (title, creation date, etc.)
- Add conversion timestamp
- Preserve chapter markers if present

#### File Naming Convention
```
original_filename_converted.mp4
or
original_filename_[timestamp].mp4
```

### Testing Checklist

- [ ] Convert .mkv file with multiple audio tracks
- [ ] Convert .avi file with single audio track
- [ ] Verify French audio is default in QuickTime Player
- [ ] Test playback on macOS QuickTime
- [ ] Test playback on iOS devices
- [ ] Verify file size is reasonable
- [ ] Check video quality matches source
- [ ] Confirm audio sync is maintained
- [ ] Test with files containing subtitles
- [ ] Batch convert multiple files

## Usage Example

```bash
# Single file conversion
python converter.py --input video.mkv --output converted.mp4

# Batch conversion
python converter.py --input-dir ./input --output-dir ./output

# With custom quality
python converter.py --input video.mkv --crf 20

# Verbose mode with logging
python converter.py --input video.mkv --verbose --log-file conversion.log
```

## Additional Features to Consider

1. **GPU Acceleration** (if available)
   - Use hardware encoders: h264_videotoolbox (macOS), h264_nvenc (NVIDIA)
   - Significantly faster conversion

2. **Dual Audio Setup**
   - Keep original audio + French audio
   - Useful for bilingual content

3. **Subtitle Extraction**
   - Extract subtitles to separate .srt files
   - Embed soft subtitles in MP4

4. **Preset Profiles**
   - High quality (CRF 18)
   - Balanced (CRF 23)
   - Compressed (CRF 28)

5. **Validation**
   - Verify output file integrity
   - Compare duration with source
   - Check for A/V sync issues

6. **Resume Capability**
   - Save conversion state
   - Resume interrupted conversions

## Common Issues and Solutions

### Issue: QuickTime won't play the file
**Solution**: Ensure pixel format is yuv420p and faststart flag is enabled

### Issue: French audio not default
**Solution**: Use `-disposition:a:0 default` flag explicitly

### Issue: File size too large
**Solution**: Adjust CRF value (higher = smaller file) or reduce bitrate

### Issue: Slow conversion
**Solution**: Use faster preset (`-preset faster`) or enable GPU acceleration

### Issue: Audio out of sync
**Solution**: Use `-async 1` flag or ensure consistent frame rate

## Performance Optimization

- Use `-preset faster` or `-preset veryfast` for speed (trade-off: larger files)
- Enable hardware acceleration when available
- Process multiple files in parallel (multiprocessing)
- Use SSD storage for input/output directories

## Command to Start Building

Ask Claude Code:
```
Create a Python video converter that converts .mkv and .avi files to QuickTime-compatible .mp4
with French audio as default. Use ffmpeg-python library. Include progress tracking,
error handling, and batch processing support.
```

## Expected Project Files

1. **converter.py** - Main conversion logic
2. **config.py** - FFmpeg settings and configurations
3. **utils.py** - Stream detection, language parsing, logging
4. **requirements.txt** - Dependencies
5. **README.md** - User documentation
6. **.gitignore** - Exclude output files and logs

## Validation Commands

After conversion, validate the output:
```bash
# Check file info
ffprobe -v quiet -print_format json -show_format -show_streams output.mp4

# Verify default audio track
ffprobe -v quiet -select_streams a:0 -show_entries stream=index,codec_name,codec_type,channels,channel_layout:stream_tags=language -of json output.mp4

# Check QuickTime compatibility
ffmpeg -v error -i output.mp4 -f null -
```

## Success Criteria

✓ Converts .mkv and .avi to .mp4 successfully
✓ QuickTime Player plays files without issues
✓ French audio is selected by default
✓ Video quality is preserved
✓ Conversion completes in reasonable time
✓ Proper error messages for invalid inputs
✓ Logs provide useful debugging information
