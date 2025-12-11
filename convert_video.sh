#!/bin/bash
# Single command video converter with French default and all languages preserved

set -e

# Function to convert a single file
convert_file() {
    local INPUT="$1"
    local OUTPUT="$2"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Converting: $(basename "$INPUT")"
    echo "Output: $OUTPUT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Create output directory if needed
    mkdir -p "$(dirname "$OUTPUT")"

    # Build FFmpeg command
    ffmpeg -i "$INPUT" \
      -c:v libx264 \
      -preset medium \
      -crf 23 \
      -pix_fmt yuv420p \
      -c:a aac \
      -b:a 192k \
      -ac 2 \
      -map 0:v:0 \
      -map 0:a \
      -map 0:s? \
      -c:s mov_text \
      -disposition:a:0 default \
      -disposition:s:0 default \
      -map_metadata 0 \
      -movflags +faststart \
      -y \
      "$OUTPUT" 2>&1 | grep -E "time=|Duration:|Error|error" || true

    if [ $? -eq 0 ]; then
        echo "✅ Success: $OUTPUT"
    else
        echo "❌ Failed: $INPUT"
        return 1
    fi
    echo ""
}

# Check arguments
if [ $# -eq 0 ]; then
    echo "Usage: ./convert_video.sh <input_file_or_folder> [output_folder]"
    echo ""
    echo "Examples:"
    echo "  Single file:"
    echo "    ./convert_video.sh video.mkv"
    echo "    ./convert_video.sh video.mkv output.mp4"
    echo ""
    echo "  Process entire folder:"
    echo "    ./convert_video.sh input"
    echo "    ./convert_video.sh input output"
    exit 1
fi

INPUT="$1"
OUTPUT_ARG="$2"

# Check if input is a directory
if [ -d "$INPUT" ]; then
    # Batch mode: process entire folder
    INPUT_DIR="$INPUT"
    OUTPUT_DIR="${OUTPUT_ARG:-output}"

    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║          BATCH CONVERSION MODE                             ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo "Input folder: $INPUT_DIR"
    echo "Output folder: $OUTPUT_DIR"
    echo ""

    # Create output directory
    mkdir -p "$OUTPUT_DIR"

    # Find all .mkv and .avi files
    FILES=($(find "$INPUT_DIR" -maxdepth 1 -type f \( -iname "*.mkv" -o -iname "*.avi" \)))

    if [ ${#FILES[@]} -eq 0 ]; then
        echo "No .mkv or .avi files found in $INPUT_DIR"
        exit 1
    fi

    echo "Found ${#FILES[@]} file(s) to convert"
    echo ""

    SUCCESS=0
    FAILED=0

    # Process each file
    for FILE in "${FILES[@]}"; do
        BASENAME=$(basename "$FILE")
        FILENAME="${BASENAME%.*}"
        OUTPUT_FILE="$OUTPUT_DIR/${FILENAME}_converted.mp4"

        if convert_file "$FILE" "$OUTPUT_FILE"; then
            ((SUCCESS++))
        else
            ((FAILED++))
        fi
    done

    # Summary
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║          BATCH CONVERSION SUMMARY                          ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo "Total files: ${#FILES[@]}"
    echo "✅ Successful: $SUCCESS"
    echo "❌ Failed: $FAILED"
    echo ""
    echo "Output directory: $OUTPUT_DIR"

elif [ -f "$INPUT" ]; then
    # Single file mode
    OUTPUT="${OUTPUT_ARG:-${INPUT%.*}_converted.mp4}"

    if ! convert_file "$INPUT" "$OUTPUT"; then
        exit 1
    fi

    echo "To check all language tracks:"
    echo "  ./check_streams.sh \"$OUTPUT\""

else
    echo "Error: Input not found: $INPUT"
    exit 1
fi
