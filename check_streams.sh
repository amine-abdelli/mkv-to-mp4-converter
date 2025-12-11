#!/bin/bash
# Check audio and subtitle streams in a video file

if [ -z "$1" ]; then
    echo "Usage: ./check_streams.sh <video_file>"
    echo "Example: ./check_streams.sh output/video_converted.mp4"
    exit 1
fi

VIDEO_FILE="$1"

if [ ! -f "$VIDEO_FILE" ]; then
    echo "Error: File not found: $VIDEO_FILE"
    exit 1
fi

echo "================================================"
echo "Analyzing: $VIDEO_FILE"
echo "================================================"
echo ""

echo "📹 VIDEO STREAMS:"
echo "----------------"
ffprobe -v quiet -select_streams v -show_entries stream=index,codec_name,width,height -of csv=p=0 "$VIDEO_FILE" | nl -v 0
echo ""

echo "🔊 AUDIO STREAMS:"
echo "----------------"
ffprobe -v quiet -select_streams a -show_entries stream=index,codec_name,channels:stream_tags=language,title -of json "$VIDEO_FILE" | \
    jq -r '.streams[] | "Stream \(.index): \(.codec_name) | Language: \(.tags.language // "unknown") | Title: \(.tags.title // "none") | Channels: \(.channels)"'
echo ""

echo "💬 SUBTITLE STREAMS:"
echo "-------------------"
ffprobe -v quiet -select_streams s -show_entries stream=index,codec_name:stream_tags=language,title -of json "$VIDEO_FILE" | \
    jq -r '.streams[] | "Stream \(.index): \(.codec_name) | Language: \(.tags.language // "unknown") | Title: \(.tags.title // "none")"'
echo ""

echo "📊 DEFAULT TRACKS:"
echo "-----------------"
echo "Default Audio:"
ffprobe -v quiet -select_streams a -show_entries stream=index:stream_disposition=default:stream_tags=language -of json "$VIDEO_FILE" | \
    jq -r '.streams[] | select(.disposition.default == 1) | "  Stream \(.index) - Language: \(.tags.language // "unknown")"'

echo ""
echo "Default Subtitle:"
ffprobe -v quiet -select_streams s -show_entries stream=index:stream_disposition=default:stream_tags=language -of json "$VIDEO_FILE" | \
    jq -r '.streams[] | select(.disposition.default == 1) | "  Stream \(.index) - Language: \(.tags.language // "unknown")"'
echo ""

echo "================================================"
echo "✅ Analysis complete!"
echo "================================================"
