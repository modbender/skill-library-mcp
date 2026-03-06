#!/bin/bash
# search_diary.sh - Search diary by tags, date, or content
# Security: Read-only operations, no file modifications, no network access

set -euo pipefail  # Strict mode: exit on error, undefined variables, pipe failures
IFS=$'\n\t'        # Safer word splitting

# Security disclaimer
echo "🔒 Security: This script only reads user diary files, no modifications" >&2

# Security: Validate file paths to prevent arbitrary file access
validate_safe_path() {
    local path="$1"
    local purpose="$2"
    
    # Convert to absolute path
    local abs_path=$(realpath -m "$path" 2>/dev/null || echo "$path")
    
    # Security checks
    if [[ "$abs_path" =~ ^/etc/ ]]; then
        echo "❌ Security error: Cannot access system directory /etc/" >&2
        exit 1
    fi
    
    if [[ "$abs_path" =~ ^/usr/ ]]; then
        echo "❌ Security error: Cannot access system directory /usr/" >&2
        exit 1
    fi
    
    if [[ "$abs_path" =~ ^/bin/|^/sbin/|^/lib/|^/lib64/ ]]; then
        echo "❌ Security error: Cannot access system binaries directory" >&2
        exit 1
    fi
    
    # Ensure it's within user's home or current directory
    local user_home="${HOME:-/tmp}"
    if [[ ! "$abs_path" =~ ^$user_home ]] && [[ ! "$abs_path" =~ ^$(pwd) ]]; then
        echo "⚠️  Warning: $purpose path is outside user directory: $abs_path" >&2
        echo "   Only accessing user home or current directory is allowed for safety." >&2
        exit 1
    fi
    
    echo "$abs_path"
}

# Default configuration with safety
DEFAULT_DIARY="$HOME/diary.md"
DIARY_FILE="${DIARY_FILE:-$DEFAULT_DIARY}"
DIARY_FILE=$(validate_safe_path "$DIARY_FILE" "diary")

# Function to display help
show_help() {
    cat << EOF
Mini Diary Search Tool

Usage: $0 [OPTIONS] [QUERY]

Options:
  --tag TAG          Search by tag (e.g., 📦, 💰, 💻)
  --date DATE        Search by date (YYYY-MM-DD)
  --content TEXT     Search in note content
  --stats            Show tag statistics
  --list-tags        List all used tags
  --help             Show this help message

Examples:
  $0 --tag 📦        # Find all order-related notes
  $0 --date 2024-02-22 # Find notes from specific date
  $0 "client meeting" # Search in content
  $0 --stats         # Show tag usage statistics
EOF
}

# Function to search by tag
search_by_tag() {
    local tag="$1"
    echo "🔍 Searching for tag: $tag"
    echo "======================"
    
    grep -n "$tag" "$DIARY_FILE" | while IFS=: read -r line_num content; do
        # Get date context
        local date_line=$(grep -B10 ":$line_num:" <(cat -n "$DIARY_FILE") | grep "## 📅" | tail -1)
        if [ -n "$date_line" ]; then
            local date_info=$(echo "$date_line" | sed 's/.*## 📅 //')
            echo "📅 $date_info"
        fi
        echo "📝 $content"
        echo "---"
    done
    
    local count=$(grep -c "$tag" "$DIARY_FILE" 2>/dev/null || echo 0)
    echo "📊 Found $count notes with tag: $tag"
}

# Function to search by date
search_by_date() {
    local date="$1"
    echo "🔍 Searching for date: $date"
    echo "======================"
    
    # Find the date section and show notes
    awk -v target_date="$date" '
    /^## 📅 / {
        current_date = substr($0, 7)
        if (current_date ~ target_date) {
            in_target_section = 1
            print "📅 " current_date
            print ""
        } else {
            in_target_section = 0
        }
    }
    /^- / && in_target_section {
        print "📝 " $0
        print "---"
    }
    ' "$DIARY_FILE"
}

# Function to search in content
search_in_content() {
    local query="$1"
    echo "🔍 Searching for: \"$query\""
    echo "======================"
    
    grep -i -n "$query" "$DIARY_FILE" | while IFS=: read -r line_num content; do
        # Get date context
        local date_line=$(grep -B10 ":$line_num:" <(cat -n "$DIARY_FILE") | grep "## 📅" | tail -1)
        if [ -n "$date_line" ]; then
            local date_info=$(echo "$date_line" | sed 's/.*## 📅 //')
            echo "📅 $date_info"
        fi
        echo "📝 $content"
        echo "---"
    done
    
    local count=$(grep -i -c "$query" "$DIARY_FILE" 2>/dev/null || echo 0)
    echo "📊 Found $count notes containing: \"$query\""
}

# Function to show statistics
show_statistics() {
    echo "📊 Diary Statistics"
    echo "=================="
    
    # Count total notes
    local total_notes=$(grep -c "^- " "$DIARY_FILE" 2>/dev/null || echo 0)
    echo "Total notes: $total_notes"
    
    # Count dates
    local total_dates=$(grep -c "## 📅 " "$DIARY_FILE" 2>/dev/null || echo 0)
    echo "Total dates: $total_dates"
    
    # Tag statistics
    echo ""
    echo "🏷️ Tag Statistics:"
    echo "----------------"
    
    # Extract all tags and count them
    grep -o "[🏠💰📦🚚💻🔧🎋📋📅]" "$DIARY_FILE" | sort | uniq -c | sort -rn | while read count tag; do
        case $tag in
            🏠) desc="Family" ;;
            💰) desc="Finance" ;;
            📦) desc="Order" ;;
            🚚) desc="Shipping" ;;
            💻) desc="Tech" ;;
            🔧) desc="Support" ;;
            🎋) desc="Bambu" ;;
            📋) desc="Form" ;;
            📅) desc="Daily" ;;
            *) desc="Unknown" ;;
        esac
        printf "  %-2s %-10s (%s)\n" "$tag" "$count" "$desc"
    done
}

# Function to list all tags
list_tags() {
    echo "🏷️ Available Tags:"
    echo "----------------"
    echo "🏠  Family"
    echo "💰  Finance/Invoice"
    echo "📦  Order/Purchase"
    echo "🚚  Shipping/Delivery"
    echo "💻  Tech/Software"
    echo "🔧  Support/Repair"
    echo "🎋  Bambu/3D Printing"
    echo "📋  Form/Report"
    echo "📅  Daily/Routine"
    echo ""
    echo "Tags are automatically added based on note content."
}

# Main function
main() {
    # Check if diary file exists
    if [ ! -f "$DIARY_FILE" ]; then
        echo "❌ Diary file not found: $DIARY_FILE"
        echo "Create a diary first or set DIARY_FILE environment variable."
        exit 1
    fi
    
    # Parse arguments
    case "$1" in
        --tag)
            if [ -z "$2" ]; then
                echo "❌ Please provide a tag to search for"
                exit 1
            fi
            search_by_tag "$2"
            ;;
        --date)
            if [ -z "$2" ]; then
                echo "❌ Please provide a date (YYYY-MM-DD)"
                exit 1
            fi
            search_by_date "$2"
            ;;
        --content)
            if [ -z "$2" ]; then
                echo "❌ Please provide search text"
                exit 1
            fi
            search_in_content "$2"
            ;;
        --stats)
            show_statistics
            ;;
        --list-tags)
            list_tags
            ;;
        --help|-h)
            show_help
            ;;
        "")
            show_help
            ;;
        *)
            # Default: search in content
            search_in_content "$1"
            ;;
    esac
}

# Run main function
main "$@"