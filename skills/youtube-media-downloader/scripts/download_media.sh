#!/bin/bash

# YouTube Media Downloader
# Downloads audio (MP3) or video (MP4) from YouTube URLs

set -e

show_help() {
    echo "YouTube Media Downloader"
    echo ""
    echo "Usage: $0 [OPTIONS] <youtube-url> [output-filename]"
    echo ""
    echo "Options:"
    echo "  -a, --audio     Download as MP3 audio (default)"
    echo "  -v, --video     Download as MP4 video" 
    echo "  -q, --quality   Video quality: best, worst, 720p, 480p, 360p (default: best)"
    echo "  -o, --output    Output directory (default: current directory)"
    echo "  -h, --help      Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'"
    echo "  $0 -v 'https://www.youtube.com/watch?v=dQw4w9WgXcQ' my_video"
    echo "  $0 -a -q 720p 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'"
    echo "  $0 -o ~/Downloads 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'"
}

# Default options
DOWNLOAD_TYPE="audio"
QUALITY="best" 
OUTPUT_DIR="."
VIDEO_URL=""
OUTPUT_FILENAME=""

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
            if [ -z "$VIDEO_URL" ]; then
                VIDEO_URL="$1"
            elif [ -z "$OUTPUT_FILENAME" ]; then
                OUTPUT_FILENAME="$1"
            else
                echo "Too many arguments"
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

if [ -z "$VIDEO_URL" ]; then
    echo "Error: YouTube URL is required"
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

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Set output filename pattern
if [ -n "$OUTPUT_FILENAME" ]; then
    OUTPUT_TEMPLATE="$OUTPUT_DIR/$OUTPUT_FILENAME.%(ext)s"
else
    OUTPUT_TEMPLATE="$OUTPUT_DIR/%(title)s.%(ext)s"
fi

echo "Downloading from: $VIDEO_URL"
echo "Type: $DOWNLOAD_TYPE"
echo "Quality: $QUALITY"
echo "Output: $OUTPUT_DIR"

if [ "$DOWNLOAD_TYPE" = "audio" ]; then
    echo "Extracting audio as MP3..."
    $YT_DLP \
        --extract-audio \
        --audio-format mp3 \
        --audio-quality 0 \
        --output "$OUTPUT_TEMPLATE" \
        "$VIDEO_URL"
    
    echo "Audio download complete!"
    
else
    echo "Downloading video as MP4..."
    
    # Set quality format
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
    
    $YT_DLP \
        --format "$FORMAT" \
        --output "$OUTPUT_TEMPLATE" \
        "$VIDEO_URL"
    
    echo "Video download complete!"
fi

# Show downloaded files
echo ""
echo "Downloaded files:"
find "$OUTPUT_DIR" -name "*" -type f -newer /tmp -ls 2>/dev/null | tail -5 || ls -la "$OUTPUT_DIR" | tail -5