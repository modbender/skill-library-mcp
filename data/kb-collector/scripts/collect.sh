#!/bin/bash
# KB Collector - Save to Obsidian
# Usage: ./collect.sh "content" "tags" [type]
# type: youtube, url, text (default: auto-detect)

CONTENT="$1"
TAGS="$2"
TYPE="$3"

if [ -z "$CONTENT" ]; then
    echo "Usage: collect.sh <URL|text> <tags> [youtube|url|text]"
    exit 1
fi

# Detect type if not specified
if [ -z "$TYPE" ]; then
    if echo "$CONTENT" | grep -qE "(youtube\.com|youtu\.be)"; then
        TYPE="youtube"
    elif echo "$CONTENT" | grep -qE "^https?://"; then
        TYPE="url"
    else
        TYPE="text"
    fi
fi

# Common settings
DATE=$(date +%Y-%m-%d)
VAULT="/Users/george/Documents/Georges/Knowledge"

case "$TYPE" in
    youtube)
        echo "=== YouTube Mode ==="
        URL="$CONTENT"
        
        # Get video title
        TITLE=$(yt-dlp --get-title "$URL" 2>/dev/null | sed 's/[/\\]//g' | cut -c1-50)
        FILENAME="${DATE}-${TITLE}.md"
        OUTPUT="${VAULT}/${FILENAME}"
        
        echo "Downloading audio from YouTube..."
        yt-dlp -f "bestaudio[ext=m4a]" --extract-audio --audio-format m4a -o "/tmp/youtube_audio.%(ext)s" "$URL"
        
        echo "Transcribing with Whisper..."
        whisper /tmp/youtube_audio.m4a --model tiny --output_format txt --output_dir /tmp --language Chinese 2>/dev/null
        
        if [ -f /tmp/youtube_audio.txt ]; then
            TRANSCRIPT=$(cat /tmp/youtube_audio.txt)
            
            cat > "$OUTPUT" << EOF
---
created: $(date +%Y-%m-%dT%H:%M:%S)
source: $URL
tags: [$TAGS]
---

# $TITLE

> TLDR: [Add your TLDR summary here]

---

## Transcript

$TRANSCRIPT

---

*存入: $(date +%Y-%m-%d)*
EOF
            echo "Saved to: $OUTPUT"
        else
            echo "Transcription failed"
            exit 1
        fi
        
        rm -f /tmp/youtube_audio.m4a /tmp/youtube_audio.txt
        ;;
        
    url)
        echo "=== URL Mode ==="
        URL="$CONTENT"
        
        TITLE=$(echo "$URL" | sed 's/.*\///' | cut -c1-50)
        FILENAME="${DATE}-${TITLE}.md"
        OUTPUT="${VAULT}/${FILENAME}"
        
        echo "Fetching content..."
        CONTENT_TEXT=$(web_fetch "$URL" 2>/dev/null | head -200)
        
        cat > "$OUTPUT" << EOF
---
created: $(date +%Y-%m-%dT%H:%M:%S)
source: $URL
tags: [$TAGS]
---

# $TITLE

> TLDR: [Add your TLDR summary here]

---

## Content

$CONTENT_TEXT

---

*存入: $(date +%Y-%m-%d)*
EOF
        echo "Saved to: $OUTPUT"
        ;;
        
    text)
        echo "=== Text Mode ==="
        TEXT_CONTENT="$CONTENT"
        TITLE="Note-$(date +%H%M%S)"
        FILENAME="${DATE}-${TITLE}.md"
        OUTPUT="${VAULT}/${FILENAME}"
        
        cat > "$OUTPUT" << EOF
---
created: $(date +%Y-%m-%dT%H:%M:%S)
tags: [$TAGS]
---

# $TITLE

$TEXT_CONTENT

---

*存入: $(date +%Y-%m-%d)*
EOF
        echo "Saved to: $OUTPUT"
        ;;
        
    *)
        echo "Unknown type: $TYPE"
        exit 1
        ;;
esac

echo "Done!"
