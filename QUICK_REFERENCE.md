# Quick Reference Card

## Convert Videos - ONE COMMAND

### Process Entire Input Folder
```bash
./convert_video.sh input
```

### Single File
```bash
./convert_video.sh video.mkv
```

### Custom Output Folder
```bash
./convert_video.sh input output
```

## Advanced (Python Script)

### High Quality
```bash
./convert.sh --input video.mkv --quality high
```

### With Logging
```bash
./convert.sh --input video.mkv --verbose --log-file logs/conversion.log
```

## Check Converted File

### Verify all language tracks
```bash
./check_streams.sh output/video_converted.mp4
```

### Quick check default audio language
```bash
ffprobe -v quiet -select_streams a:0 -show_entries stream_tags=language -of default=noprint_wrappers=1:nokey=1 output/video.mp4
```

## QuickTime Language Selection

1. Open MP4 in QuickTime Player
2. **Présentation** → **Langues** (switch audio)
3. **Présentation** → **Sous-titres** (switch subtitles)

## What You Get

✅ French audio as default (when available)
✅ All other audio tracks preserved and selectable
✅ All subtitles included with proper labels
✅ QuickTime/iOS/macOS compatible
✅ Fast start enabled for streaming

## Quality Settings

| Preset | CRF | Use Case |
|--------|-----|----------|
| high | 18 | Best quality, larger files |
| balanced | 23 | Good quality (default) |
| compressed | 28 | Smaller files |

## File Locations

- **Input**: Place videos in `input/` folder
- **Output**: Converted videos in `output/` folder
- **Logs**: Conversion logs in `logs/` folder

## Common Commands

```bash
# Convert single file with custom CRF
./convert.sh --input video.mkv --crf 20

# Batch convert with faster encoding
./convert.sh --input-dir input --preset faster

# Force re-convert (don't skip existing)
./convert.sh --input-dir input --no-skip-existing

# Get help
./convert.sh --help
```

## Troubleshooting

**Check FFmpeg:**
```bash
ffmpeg -version
```

**Check Python environment:**
```bash
source venv/bin/activate
pip list
```

**View detailed logs:**
```bash
./convert.sh --input video.mkv --verbose
```
