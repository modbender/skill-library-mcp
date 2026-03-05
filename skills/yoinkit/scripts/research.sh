#!/bin/bash
# yoinkit research <topic>
# Automated research workflow — combines search and trending across platforms

set -e

TOPIC="$1"
shift 2>/dev/null || true

if [ -z "$TOPIC" ]; then
    echo "Error: Topic required"
    echo "Usage: yoinkit research \"<topic>\" [options]"
    exit 1
fi

if [ -z "$YOINKIT_API_TOKEN" ]; then
    echo "Error: YOINKIT_API_TOKEN not configured"
    exit 1
fi

API_BASE="${YOINKIT_API_URL:-https://yoinkit.ai/api/v1/openclaw}"

# Default parameters
PLATFORMS=("youtube" "tiktok")
TRANSCRIPTS=false

# Parse additional options
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --platforms)
            IFS=',' read -r -a PLATFORMS <<< "$2"
            shift 2
            ;;
        --transcripts)
            TRANSCRIPTS=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Platforms that support search
SEARCH_PLATFORMS=("youtube" "tiktok" "instagram" "reddit" "pinterest")
# Platforms that support trending
TRENDING_PLATFORMS=("youtube" "tiktok")
# Platforms that support transcripts
TRANSCRIPT_PLATFORMS=("youtube" "tiktok" "instagram" "twitter" "facebook")

echo "{"
echo "  \"topic\": \"$TOPIC\","
echo "  \"results\": {"

FIRST_PLATFORM=true

for platform in "${PLATFORMS[@]}"; do
    if [ "$FIRST_PLATFORM" = false ]; then
        echo ","
    fi
    FIRST_PLATFORM=false

    echo "    \"$platform\": {"

    # Search if platform supports it
    if [[ " ${SEARCH_PLATFORMS[@]} " =~ " ${platform} " ]]; then
        ENCODED_QUERY=$(echo "$TOPIC" | jq -sRr @uri)
        SEARCH_RESPONSE=$(curl -s -H "Authorization: Bearer $YOINKIT_API_TOKEN" \
            "$API_BASE/$platform/search?query=$ENCODED_QUERY")

        if echo "$SEARCH_RESPONSE" | jq -e '.success == false' > /dev/null 2>&1; then
            echo "      \"search\": null,"
        else
            echo "      \"search\": $(echo "$SEARCH_RESPONSE" | jq '.data // []'),"
        fi
    else
        echo "      \"search\": null,"
    fi

    # Trending if platform supports it
    if [[ " ${TRENDING_PLATFORMS[@]} " =~ " ${platform} " ]]; then
        if [[ "$platform" == "youtube" ]]; then
            # YouTube trending takes NO parameters
            TRENDING_RESPONSE=$(curl -s -H "Authorization: Bearer $YOINKIT_API_TOKEN" \
                "$API_BASE/youtube/trending")
        else
            # TikTok trending: region (required)
            TRENDING_RESPONSE=$(curl -s -H "Authorization: Bearer $YOINKIT_API_TOKEN" \
                "$API_BASE/tiktok/trending?region=US")
        fi

        if echo "$TRENDING_RESPONSE" | jq -e '.success == false' > /dev/null 2>&1; then
            echo "      \"trending\": null"
        else
            TRENDING_DATA=$(echo "$TRENDING_RESPONSE" | jq '.data // .')

            # Check if we need transcripts
            if [ "$TRANSCRIPTS" = true ] && [[ " ${TRANSCRIPT_PLATFORMS[@]} " =~ " ${platform} " ]]; then
                # Extract URLs based on platform response structure
                if [[ "$platform" == "youtube" ]]; then
                    URLS=$(echo "$TRENDING_DATA" | jq -r '.shorts[0:3]? // .[0:3]? | .[]? | .url // empty' 2>/dev/null)
                elif [[ "$platform" == "tiktok" ]]; then
                    URLS=$(echo "$TRENDING_DATA" | jq -r '.aweme_list[0:3]? // .[0:3]? | .[]? | .video.play_addr.url_list[0]? // empty' 2>/dev/null)
                fi

                TRANSCRIPTS_JSON="["
                FIRST_TRANSCRIPT=true
                for url in $URLS; do
                    if [ -n "$url" ]; then
                        if [ "$FIRST_TRANSCRIPT" = false ]; then
                            TRANSCRIPTS_JSON+=","
                        fi
                        FIRST_TRANSCRIPT=false

                        ENCODED_URL=$(echo "$url" | jq -sRr @uri)
                        TRANSCRIPT_RESPONSE=$(curl -s -H "Authorization: Bearer $YOINKIT_API_TOKEN" \
                            "$API_BASE/$platform/transcript?url=$ENCODED_URL")

                        if echo "$TRANSCRIPT_RESPONSE" | jq -e '.success != false' > /dev/null 2>&1; then
                            TRANSCRIPT_TEXT=$(echo "$TRANSCRIPT_RESPONSE" | jq -r '.data.transcript_only_text // .data.transcript // null')
                            TRANSCRIPTS_JSON+="{\"url\":\"$url\",\"transcript\":$(echo "$TRANSCRIPT_TEXT" | jq -Rs .)}"
                        fi
                    fi
                done
                TRANSCRIPTS_JSON+="]"

                echo "      \"trending\": $TRENDING_DATA,"
                echo "      \"transcripts\": $TRANSCRIPTS_JSON"
            else
                echo "      \"trending\": $TRENDING_DATA"
            fi
        fi
    else
        echo "      \"trending\": null"
    fi

    echo -n "    }"
done

echo ""
echo "  }"
echo "}"
