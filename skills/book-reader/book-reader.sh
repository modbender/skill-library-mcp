#!/bin/bash
# book-reader.sh - Read books from various sources with progress tracking

set -e

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
STATE_FILE="$WORKSPACE/memory/reading-state.json"
BOOKS_DIR="$WORKSPACE/books"

mkdir -p "$BOOKS_DIR"

usage() {
    echo "Usage: book-reader.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  search <query>              Search for books"
    echo "  download <url> [file]       Download a book"
    echo "  read <file> [--pages N]     Read a book (or continue)"
    echo "  status                      Show reading progress"
    echo "  list                        List downloaded books"
    echo ""
    echo "Examples:"
    echo "  book-reader.sh search 'Thinking Fast and Slow'"
    echo "  book-reader.sh download https://example.com/book.epub"
    echo "  book-reader.sh read ~/books/book.epub --pages 50"
    exit 1
}

# Search books via Gutendex (Project Gutenberg API)
search_books() {
    local query="$1"
    echo "🔍 Searching for: $query"
    echo ""
    
    # Search Project Gutenberg
    echo "📚 Project Gutenberg:"
    local encoded_query=$(echo "$query" | sed 's/ /%20/g')
    local results=$(curl -s "https://gutendex.com/books/?search=$encoded_query")
    
    echo "$results" | jq -r '.results[] | "  \(.id) - \(.title) by \(.authors[0].name // "Unknown") [\(.formats."text/html" // "no link")]"' | head -10
    
    echo ""
    echo "💡 To download from Gutenberg:"
    echo "   book-reader.sh download <book-id>"
    echo ""
    echo "💡 For newer/copyrighted books, check Anna's Archive manually:"
    echo "   https://annas-archive.org"
}

# Download a book
download_book() {
    local source="$1"
    local output="$2"
    
    if [[ -z "$output" ]]; then
        output="$BOOKS_DIR/$(basename "$source")"
    fi
    
    echo "⬇️  Downloading to: $output"
    
    if [[ "$source" =~ ^[0-9]+$ ]]; then
        # Gutenberg book ID
        echo "📚 Downloading from Project Gutenberg (ID: $source)..."
        local book_url=$(curl -s "https://gutendex.com/books/$source/" | jq -r '.formats."application/epub+zip" // .formats."text/plain; charset=utf-8"')
        
        if [[ "$book_url" == "null" ]]; then
            echo "❌ Book not found or no EPUB available"
            exit 1
        fi
        
        curl -L -o "$output" "$book_url"
    else
        # Direct URL
        curl -L -o "$output" "$source"
    fi
    
    echo "✅ Downloaded: $output"
    echo ""
    echo "📖 To read: book-reader.sh read $output"
}

# Extract text from various formats
extract_text() {
    local file="$1"
    local ext="${file##*.}"
    
    case "$ext" in
        txt)
            cat "$file"
            ;;
        pdf)
            if command -v pdftotext &> /dev/null; then
                pdftotext "$file" -
            else
                echo "❌ pdftotext not found. Install poppler-utils"
                exit 1
            fi
            ;;
        epub)
            if command -v pandoc &> /dev/null; then
                pandoc "$file" -t plain
            elif python3 -c "import ebooklib" 2>/dev/null; then
                python3 << 'PYEOF'
import sys
from ebooklib import epub
from bs4 import BeautifulSoup

book = epub.read_epub(sys.argv[1])
text = []

for item in book.get_items_of_type(9):  # TYPE_DOCUMENT
    soup = BeautifulSoup(item.get_content(), 'html.parser')
    text.append(soup.get_text())

print('\n\n'.join(text))
PYEOF
            else
                echo "❌ No EPUB parser found. Install pandoc or python3-ebooklib"
                exit 1
            fi
            ;;
        *)
            echo "❌ Unsupported format: $ext"
            exit 1
            ;;
    esac
}

# Read a book with progress tracking
read_book() {
    local file="$1"
    local pages="${2:-50}"
    
    if [[ ! -f "$file" ]]; then
        echo "❌ File not found: $file"
        exit 1
    fi
    
    echo "📖 Reading: $(basename "$file")"
    echo ""
    
    # Extract full text
    local text=$(extract_text "$file")
    local total_chars=$(echo "$text" | wc -c)
    local chars_per_page=3000  # Roughly 1 page
    
    # Load progress
    local offset=0
    if [[ -f "$STATE_FILE" ]]; then
        offset=$(jq -r --arg f "$file" '.currentFile == $f and .offset // 0' "$STATE_FILE" 2>/dev/null || echo 0)
    fi
    
    # Calculate chunk
    local chunk_size=$((pages * chars_per_page))
    local end_offset=$((offset + chunk_size))
    
    if [[ $end_offset -gt $total_chars ]]; then
        end_offset=$total_chars
    fi
    
    # Display chunk
    echo "$text" | tail -c +$((offset + 1)) | head -c $chunk_size
    
    echo ""
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Progress: $end_offset / $total_chars chars ($(( end_offset * 100 / total_chars ))%)"
    
    # Save progress
    mkdir -p "$(dirname "$STATE_FILE")"
    jq -n \
        --arg file "$file" \
        --arg offset "$end_offset" \
        --arg total "$total_chars" \
        --arg timestamp "$(date +%s)" \
        '{currentFile: $file, offset: ($offset | tonumber), totalChars: ($total | tonumber), lastRead: ($timestamp | tonumber)}' \
        > "$STATE_FILE"
    
    if [[ $end_offset -ge $total_chars ]]; then
        echo "🎉 Book finished!"
    else
        echo "💡 Continue: book-reader.sh read '$file' --pages $pages"
    fi
}

# Show reading status
show_status() {
    if [[ ! -f "$STATE_FILE" ]]; then
        echo "📚 No active reading session"
        exit 0
    fi
    
    echo "📖 Current Reading:"
    jq -r '" File: \(.currentFile)\n Progress: \(.offset) / \(.totalChars) chars (\((.offset * 100 / .totalChars) | floor)%)\n Last read: \(.lastRead)"' "$STATE_FILE"
}

# List downloaded books
list_books() {
    echo "📚 Downloaded books:"
    find "$BOOKS_DIR" -type f \( -name "*.epub" -o -name "*.pdf" -o -name "*.txt" \) -exec basename {} \;
}

# Main
case "${1:-}" in
    search)
        search_books "${2:-}"
        ;;
    download)
        download_book "${2:-}" "${3:-}"
        ;;
    read)
        pages=50
        if [[ "$3" == "--pages" ]]; then
            pages="${4:-50}"
        fi
        read_book "${2:-}" "$pages"
        ;;
    status)
        show_status
        ;;
    list)
        list_books
        ;;
    *)
        usage
        ;;
esac
