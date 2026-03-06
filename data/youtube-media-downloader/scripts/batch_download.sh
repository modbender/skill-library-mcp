#!/bin/bash

# YouTube Batch Downloader
# Downloads multiple videos from playlists or URL lists

set -e

show_help() {
    echo "YouTube Batch Downloader"
    echo ""
    echo "Usage: $0 [OPTIONS] <playlist-url-or-file>"
    echo ""
    echo "Options:"
    echo "  -a, --audio         Download as MP3 audio (default)"
    echo "  -v, --video         Download as MP4 video"
    echo "  -q, --quality       Video quality: best, worst, 720p, 480p, 360p (default: best)"
    echo "  -o, --output        Output directory (default: ./downloads)"
    echo "  -s, --start         Start from playlist item number (default: 1)"
    echo "  -e, --end           End at playlist item number (default: all)"
    echo "  -m, --max-downloads Maximum number of downloads (default: unlimited)"
    echo "  -f, --file          Input is a text file with URLs (one per line)"
    echo "  -h, --help          Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 'https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMHjMRrNVBoUoMvzpB'"
    echo "  $0 -v -q 720p 'https://www.youtube.com/playlist?list=PLxxx'"
    echo "  $0 -f urls.txt"
    echo "  $0 -s 5 -e 10 'https://www.youtube.com/playlist?list=PLxxx'"
}

# Default options
DOWNLOAD_TYPE="audio"
QUALITY="best"
OUTPUT_DIR="./downloads"
START_NUM="1"
END_NUM=""
MAX_DOWNLOADS=""
IS_FILE=false
INPUT=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--audio)
            DOWNLOAD_TYPE="audio"
            shift
            ;;
        -v|--video)
            DOWNLOAD_TYPE="video"
            shift
            ;;
        -q|--quality)
            QUALITY="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -s|--start)
            START_NUM="$2"
            shift 2
            ;;
        -e|--end)
            END_NUM="$2"
            shift 2
            ;;
        -m|--max-downloads)
            MAX_DOWNLOADS="$2"
            shift 2
            ;;
        -f|--file)
            IS_FILE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
        *)
            INPUT="$1"
            shift
            ;;
    esac
done

if [ -z "$INPUT" ]; then
    echo "Error: Playlist URL or file path is required"
    show_help
    exit 1
fi

# Check if yt-dlp exists
if ! command -v yt-dlp &> /dev/null; then
    if [ -f "$HOME/yt-dlp" ]; then
        YT_DLP="$HOME/yt-dlp"
    else
        echo "Installing yt-dlp to ~/yt-dlp..."
        curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o "$HOME/yt-dlp"
        chmod +x "$HOME/yt-dlp"
        YT_DLP="$HOME/yt-dlp"
    fi
else
    YT_DLP="yt-dlp"
fi

# Check if ffmpeg exists (needed for MP3 conversion)
if ! command -v ffmpeg &> /dev/null; then
    if [ -f "$HOME/ffmpeg-portable/bin/ffmpeg" ]; then
        FFMPEG_PATH="$HOME/ffmpeg-portable/bin"
        echo "Using existing ffmpeg at $FFMPEG_PATH"
    else
        echo "Installing ffmpeg for audio conversion..."
        mkdir -p "$HOME/ffmpeg-portable"
        cd "$HOME/ffmpeg-portable"
        curl -L https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz -o ffmpeg.tar.xz
        tar -xf ffmpeg.tar.xz --strip-components=1
        rm -f ffmpeg.tar.xz
        cd - > /dev/null
        FFMPEG_PATH="$HOME/ffmpeg-portable/bin"
        echo "ffmpeg installed to $FFMPEG_PATH"
    fi
    export PATH="$FFMPEG_PATH:$PATH"
else
    echo "Using system ffmpeg"
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "Batch downloading..."
echo "Type: $DOWNLOAD_TYPE"
echo "Quality: $QUALITY"
echo "Output: $OUTPUT_DIR"

# Build yt-dlp arguments
YT_ARGS=("--output" "$OUTPUT_DIR/%(playlist_index)s - %(title)s.%(ext)s")

# Set download range
if [ -n "$START_NUM" ] && [ -n "$END_NUM" ]; then
    YT_ARGS+=("--playlist-items" "$START_NUM-$END_NUM")
elif [ -n "$START_NUM" ] && [ "$START_NUM" != "1" ]; then
    YT_ARGS+=("--playlist-items" "$START_NUM-")
elif [ -n "$END_NUM" ]; then
    YT_ARGS+=("--playlist-items" "1-$END_NUM")
fi

# Set max downloads
if [ -n "$MAX_DOWNLOADS" ]; then
    YT_ARGS+=("--max-downloads" "$MAX_DOWNLOADS")
fi

if [ "$DOWNLOAD_TYPE" = "audio" ]; then
    YT_ARGS+=("--extract-audio" "--audio-format" "mp3" "--audio-quality" "0")
else
    # Set video quality
    case $QUALITY in
        "best")
            FORMAT="best[ext=mp4]/best"
            ;;
        "worst")
            FORMAT="worst[ext=mp4]/worst"
            ;;
        "720p")
            FORMAT="best[height<=720][ext=mp4]/best[height<=720]/best[ext=mp4]/best"
            ;;
        "480p")
            FORMAT="best[height<=480][ext=mp4]/best[height<=480]/best[ext=mp4]/best"
            ;;
        "360p")
            FORMAT="best[height<=360][ext=mp4]/best[height<=360]/best[ext=mp4]/best"
            ;;
        *)
            FORMAT="best[ext=mp4]/best"
            ;;
    esac
    YT_ARGS+=("--format" "$FORMAT")
fi

# Handle file input vs URL input
if [ "$IS_FILE" = true ]; then
    if [ ! -f "$INPUT" ]; then
        echo "Error: File '$INPUT' not found"
        exit 1
    fi
    echo "Processing URLs from file: $INPUT"
    YT_ARGS+=("--batch-file" "$INPUT")
    $YT_DLP "${YT_ARGS[@]}"
else
    echo "Processing playlist: $INPUT"
    $YT_DLP "${YT_ARGS[@]}" "$INPUT"
fi

echo ""
echo "Batch download complete!"
echo "Files saved to: $OUTPUT_DIR"
ls -la "$OUTPUT_DIR" | tail -10