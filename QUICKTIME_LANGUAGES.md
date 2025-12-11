# QuickTime Language Selection Guide

## How Language Selection Works

After converting your videos, all audio tracks and subtitles are preserved with their original language metadata. This allows you to select different languages directly in QuickTime Player.

## Accessing Languages in QuickTime Player

### Audio Tracks (Langues)

1. Open the converted MP4 file in QuickTime Player
2. Click **Présentation** in the menu bar (or **View** in English)
3. Select **Langues** (or **Languages**)
4. Choose from all available audio tracks

**Default**: French audio (if available in the source) will be selected by default.

### Subtitles (Sous-titres)

1. Open the converted MP4 file in QuickTime Player
2. Click **Présentation** in the menu bar
3. Select **Sous-titres** (or **Subtitles**)
4. Choose from all available subtitle tracks

**Default**: French subtitles (if available) will be selected by default.

## What the Converter Does

### All Tracks Are Preserved

- ✅ **All audio tracks** from the source file are included
- ✅ **All subtitle tracks** from the source file are included
- ✅ **Language metadata** is preserved for each track
- ✅ **Track titles** are preserved when available
- ✅ French tracks are prioritized as default (when present)

### Track Organization

**Audio tracks are ordered as:**
1. French audio (if present) - **DEFAULT**
2. Original language
3. English
4. Other languages (in original order)

**Subtitle tracks are ordered as:**
1. French subtitles (if present) - **DEFAULT**
2. Original language
3. English
4. Other languages (in original order)

## Example Output

When you convert a file with multiple audio tracks, the result will look like:

```
📹 Video: H.264, 1920x1080
🔊 Audio Tracks:
   1. French (fra) - AAC, Stereo [DEFAULT]
   2. English (eng) - AAC, Stereo
   3. Japanese (jpn) - AAC, Stereo
💬 Subtitles:
   1. French (fra) - mov_text [DEFAULT]
   2. English (eng) - mov_text
   3. Japanese (jpn) - mov_text
```

## Verifying Language Tracks

Use the included script to verify all tracks are properly labeled:

```bash
./check_streams.sh output/your_video_converted.mp4
```

This will show:
- All available video streams
- All audio streams with language codes
- All subtitle streams with language codes
- Which tracks are set as default

## Command Line Verification

You can also use FFmpeg commands directly:

**Check all audio tracks:**
```bash
ffprobe -v quiet -select_streams a -show_entries stream=index:stream_tags=language,title -of json your_video.mp4
```

**Check all subtitle tracks:**
```bash
ffprobe -v quiet -select_streams s -show_entries stream=index:stream_tags=language,title -of json your_video.mp4
```

**Check default audio track:**
```bash
ffprobe -v quiet -select_streams a:0 -show_entries stream_tags=language -of default=noprint_wrappers=1:nokey=1 your_video.mp4
```

## Troubleshooting

### Issue: Not all languages appear in QuickTime menu

**Possible causes:**
1. The source file didn't have language metadata
2. QuickTime Player may need to be restarted
3. The file may need to be fully loaded (let it buffer)

**Solution:**
- Verify tracks exist: `./check_streams.sh your_video.mp4`
- Restart QuickTime Player
- Check Console logs for any QuickTime errors

### Issue: Default language is not French

**Possible causes:**
1. Source file doesn't contain a French audio track
2. French track wasn't properly detected

**Solution:**
- Check source file: `ffprobe -show_streams source.mkv | grep language`
- Run converter with `--verbose` flag to see detection logs
- Manually verify the converted file has French as first track

### Issue: Language labels show codes (fra, eng) instead of names

**This is normal behavior.** QuickTime Player displays:
- Language codes on some versions
- Full language names on others (depends on macOS version)

The language information is correctly embedded; it's just a display preference.

## Technical Details

### Language Codes Used

The converter recognizes these language codes:

**French:**
- `fra` (ISO 639-2)
- `fre` (ISO 639-2 alternative)
- `fr` (ISO 639-1)
- `french` (full name)

**Other common codes:**
- `eng` / `en` - English
- `spa` / `es` - Spanish
- `deu` / `de` - German
- `ita` / `it` - Italian
- `jpn` / `ja` - Japanese
- `kor` / `ko` - Korean

### FFmpeg Metadata Preservation

The converter uses these FFmpeg flags to preserve language info:

```bash
# For each audio track
-metadata:s:a:0 language=fra
-metadata:s:a:0 title="French Audio"

# For each subtitle track
-metadata:s:s:0 language=fra
-metadata:s:s:0 title="French Subtitles"
```

### Disposition Flags

The first track of each type gets the `default` disposition:

```bash
-disposition:a:0 default  # First audio track is default
-disposition:s:0 default  # First subtitle track is default
```

This tells QuickTime Player which track to play automatically.

## Best Practices

1. **Check source file first** - Use `ffprobe` to see what tracks are available
2. **Use verbose logging** - Run converter with `--verbose` to see what's detected
3. **Verify output** - Use `./check_streams.sh` after conversion
4. **Test in QuickTime** - Open the file and check the Présentation menus
5. **Keep original files** - Don't delete source files until you've verified the conversion

## iOS and macOS Compatibility

The converted MP4 files are fully compatible with:
- ✅ QuickTime Player (macOS)
- ✅ QuickTime Player X
- ✅ iOS Video Player (iPhone/iPad)
- ✅ Apple TV
- ✅ Safari browser
- ✅ Most modern video players (VLC, MPlayer, etc.)

All language tracks will be accessible on these platforms.
