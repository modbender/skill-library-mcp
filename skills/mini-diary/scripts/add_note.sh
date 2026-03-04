#!/bin/bash
# add_note.sh - Add a note to the diary with auto-tagging
# Security: Safe file operations only, no network access, no system modifications

set -euo pipefail  # Strict mode: exit on error, undefined variables, pipe failures
IFS=$'\n\t'        # Safer word splitting

# Security disclaimer
echo "🔒 Security: This script only reads/writes user diary files in safe locations" >&2

# Security: Validate file paths to prevent arbitrary file write
validate_safe_path() {
    local path="$1"
    local purpose="$2"
    
    # Convert to absolute path
    local abs_path=$(realpath -m "$path" 2>/dev/null || echo "$path")
    
    # Security checks
    if [[ "$abs_path" =~ ^/etc/ ]]; then
        echo "❌ Security error: Cannot write to system directory /etc/" >&2
        exit 1
    fi
    
    if [[ "$abs_path" =~ ^/usr/ ]]; then
        echo "❌ Security error: Cannot write to system directory /usr/" >&2
        exit 1
    fi
    
    if [[ "$abs_path" =~ ^/bin/|^/sbin/|^/lib/|^/lib64/ ]]; then
        echo "❌ Security error: Cannot write to system binaries directory" >&2
        exit 1
    fi
    
    # Ensure it's within user's home or current directory
    local user_home="${HOME:-/tmp}"
    if [[ ! "$abs_path" =~ ^$user_home ]] && [[ ! "$abs_path" =~ ^$(pwd) ]]; then
        echo "⚠️  Warning: $purpose path is outside user directory: $abs_path" >&2
        echo "   Only writing to user home or current directory is allowed for safety." >&2
        exit 1
    fi
    
    # Ensure it's a .md file for diary
    if [[ "$purpose" == "diary" ]] && [[ ! "$abs_path" =~ \.md$ ]]; then
        echo "⚠️  Warning: Diary file should have .md extension" >&2
        # Allow but warn
    fi
    
    echo "$abs_path"
}

# Default configuration with safety
DEFAULT_DIARY="$HOME/diary.md"
DIARY_FILE="${DIARY_FILE:-$DEFAULT_DIARY}"
DIARY_FILE=$(validate_safe_path "$DIARY_FILE" "diary")

# Tags config (optional)
TAGS_CONFIG="${TAGS_CONFIG:-$(dirname "$0")/../config/tags.json}"
if [ -n "$TAGS_CONFIG" ] && [ -f "$TAGS_CONFIG" ]; then
    TAGS_CONFIG=$(validate_safe_path "$TAGS_CONFIG" "tags_config")
fi

# Tag definitions (simplified version)
declare -A TAG_RULES=(
    ["family"]="👨‍👩‍👧"
    ["finance"]="💰"
    ["order"]="📦"
    ["shipping"]="🚚"
    ["tech"]="💻"
    ["support"]="🔧"
    ["bambu"]="🎋"
    ["form"]="📋"
    ["daily"]="📅"
)

# Function to get tags for content
get_tags() {
    local content="$1"
    local tags=""
    
    # Convert to lowercase for matching
    local lower_content=$(echo "$content" | tr '[:upper:]' '[:lower:]')
    
    # Simple keyword matching (can be enhanced with AI)
    if [[ $lower_content =~ family|home|household ]]; then
        tags="${tags}${TAG_RULES[family]}"
    fi
    
    if [[ $lower_content =~ invoice|payment|finance|accounting ]]; then
        tags="${tags}${TAG_RULES[finance]}"
    fi
    
    if [[ $lower_content =~ order|purchase|buy|stock ]]; then
        tags="${tags}${TAG_RULES[order]}"
    fi
    
    if [[ $lower_content =~ shipping|delivery|logistics ]]; then
        tags="${tags}${TAG_RULES[shipping]}"
    fi
    
    if [[ $lower_content =~ tech|software|system|computer|network ]]; then
        tags="${tags}${TAG_RULES[tech]}"
    fi
    
    if [[ $lower_content =~ support|repair|fix|issue|problem ]]; then
        tags="${tags}${TAG_RULES[support]}"
    fi
    
    if [[ $lower_content =~ bambu|3d.print|printer|filament ]]; then
        tags="${tags}${TAG_RULES[bambu]}"
    fi
    
    if [[ $lower_content =~ form|report|data|spreadsheet ]]; then
        tags="${tags}${TAG_RULES[form]}"
    fi
    
    # Default tag if no specific tags found
    if [ -z "$tags" ]; then
        tags="${TAG_RULES[daily]}"
    else
        # Add daily tag as secondary
        tags="${tags}${TAG_RULES[daily]}"
    fi
    
    echo "$tags"
}

# Main function
main() {
    if [ $# -eq 0 ]; then
        echo "Usage: $0 \"note content\""
        echo "Example: $0 \"Met with client about P1S delivery\""
        exit 1
    fi
    
    local note_content="$1"
    local tags=$(get_tags "$note_content")
    
    # Get current date for diary entry
    local today=$(date "+%Y-%m-%d")
    local weekday=$(date "+%A")
    
    # Check if diary file exists, create if not
    if [ ! -f "$DIARY_FILE" ]; then
        echo "# 📓 My Diary" > "$DIARY_FILE"
        echo "" >> "$DIARY_FILE"
    fi
    
    # Check if today's section exists
    if ! grep -q "## 📅 $today" "$DIARY_FILE"; then
        echo "" >> "$DIARY_FILE"
        echo "## 📅 $today $weekday" >> "$DIARY_FILE"
        echo "" >> "$DIARY_FILE"
        echo "### 📝 Notes" >> "$DIARY_FILE"
        echo "" >> "$DIARY_FILE"
    fi
    
    # Add the note with tags
    echo "- $note_content $tags" >> "$DIARY_FILE"
    
    echo "✅ Note added: \"$note_content\""
    echo "🏷️  Auto-tags: $tags"
    echo "📄 Diary file: $DIARY_FILE"
    
    # If NextCloud sync is configured
    if [ -n "$NEXTCLOUD_SYNC_DIR" ]; then
        # Validate NextCloud directory is safe
        if [[ "$NEXTCLOUD_SYNC_DIR" =~ ^/etc/|^/usr/|^/bin/|^/sbin/|^/lib/ ]]; then
            echo "❌ Security error: NextCloud directory cannot be system directory" >&2
            exit 1
        fi
        
        if [ -d "$NEXTCLOUD_SYNC_DIR" ]; then
            echo "☁️  NextCloud sync available at: $NEXTCLOUD_SYNC_DIR"
            echo "⚠️  Remember to run NextCloud scan if needed"
            
            # Optional: Copy to NextCloud (with safety check)
            if [ -f "$DIARY_FILE" ] && [ -w "$NEXTCLOUD_SYNC_DIR" ]; then
                cp "$DIARY_FILE" "$NEXTCLOUD_SYNC_DIR/" 2>/dev/null || true
            fi
        else
            echo "⚠️  NextCloud directory not found or not accessible: $NEXTCLOUD_SYNC_DIR"
        fi
    fi
}

# Run main function
main "$@"