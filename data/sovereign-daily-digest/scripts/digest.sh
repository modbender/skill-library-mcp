#!/usr/bin/env bash
# ============================================================================
# Daily Digest — Compilation Script
# Version: 1.0.0
# Description: Gathers data from multiple sources and compiles a daily digest.
# Usage: bash digest.sh [--config PATH] [--format markdown|html|both] [--output DIR]
# ============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="${HOME}/.openclaw/daily-digest"
CONFIG_FILE="${CONFIG_DIR}/config.yaml"
OUTPUT_DIR="${CONFIG_DIR}/output"
OUTPUT_FORMAT="markdown"
TODAY=$(date +%Y-%m-%d)
DAY_OF_WEEK=$(date +%A)
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S %Z")
LOCATION="New York"
UNITS="imperial"
TEMP_DIR=$(mktemp -d)
DIGEST_FILE=""
OFFLINE_MODE=false

# Counters for the final summary
COUNT_EVENTS=0
COUNT_TASKS=0
COUNT_NEWS=0
COUNT_EMAILS=0
WARNINGS=""

# ---------------------------------------------------------------------------
# Argument Parsing
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --location)
            LOCATION="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: digest.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --config PATH     Path to config.yaml (default: ~/.openclaw/daily-digest/config.yaml)"
            echo "  --format FORMAT   Output format: markdown, html, or both (default: markdown)"
            echo "  --output DIR      Output directory (default: ~/.openclaw/daily-digest/output)"
            echo "  --location CITY   Weather location (default: New York)"
            echo "  -h, --help        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log() {
    echo "[digest] $(date +%H:%M:%S) $*" >&2
}

warn() {
    WARNINGS="${WARNINGS}\n- $*"
    log "WARNING: $*"
}

cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

check_connectivity() {
    if ! curl -s --max-time 3 "https://wttr.in/?format=3" > /dev/null 2>&1; then
        OFFLINE_MODE=true
        warn "No internet connectivity detected. Running in offline mode."
    fi
}

# ---------------------------------------------------------------------------
# Config Handling
# ---------------------------------------------------------------------------
ensure_config() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        log "Config not found. Creating default at $CONFIG_FILE"
        mkdir -p "$(dirname "$CONFIG_FILE")"
        cp "${SKILL_DIR}/SKILL.md" /dev/null 2>/dev/null || true
        # Write a minimal default config
        cat > "$CONFIG_FILE" << 'YAML'
general:
  timezone: "America/New_York"
  output_format: "markdown"
  output_dir: "~/.openclaw/daily-digest/output"
  archive: true
  max_archive_days: 30

sections:
  weather:
    enabled: true
    location: "New York"
    units: "imperial"
  calendar:
    enabled: true
    sources: []
  tasks:
    enabled: true
    sources:
      - type: "todotxt"
        path: "~/todo.txt"
  news:
    enabled: true
    feeds:
      - name: "Hacker News"
        url: "https://hnrss.org/frontpage"
        max_items: 5
  quote:
    enabled: true
    source: "zenquotes"
YAML
        echo "DEFAULT_CONFIG_CREATED"
    fi
}

# Simple YAML value reader (no dependencies required)
yaml_get() {
    local file="$1"
    local key="$2"
    local default="${3:-}"
    # Handles simple key: value pairs — not nested. For nested, use dot notation search.
    local value
    value=$(grep -E "^\s*${key}:" "$file" 2>/dev/null | head -1 | sed 's/.*:\s*//' | sed 's/^"//' | sed 's/"$//' | sed "s/^'//" | sed "s/'$//" | tr -d '\r')
    if [[ -z "$value" ]]; then
        echo "$default"
    else
        echo "$value"
    fi
}

# ---------------------------------------------------------------------------
# Section: Weather
# ---------------------------------------------------------------------------
fetch_weather() {
    log "Fetching weather for ${LOCATION}..."
    local weather_file="${TEMP_DIR}/weather.txt"

    if [[ "$OFFLINE_MODE" == true ]]; then
        echo "Weather data unavailable (offline mode)." > "$weather_file"
        return
    fi

    local encoded_location
    encoded_location=$(echo "$LOCATION" | sed 's/ /+/g')

    # Fetch compact weather
    local current
    current=$(curl -s --max-time 10 "wttr.in/${encoded_location}?format=%C+|+%t+|+Humidity:+%h+|+Wind:+%w" 2>/dev/null || echo "")

    # Fetch one-line summary
    local summary
    summary=$(curl -s --max-time 10 "wttr.in/${encoded_location}?format=4" 2>/dev/null || echo "")

    # Fetch feels-like temperature
    local feels_like
    feels_like=$(curl -s --max-time 10 "wttr.in/${encoded_location}?format=Feels+like:+%f" 2>/dev/null || echo "")

    if [[ -n "$current" ]]; then
        {
            echo "**${LOCATION}**: ${current}"
            [[ -n "$feels_like" ]] && echo "${feels_like}"
            echo ""
            [[ -n "$summary" ]] && echo "_${summary}_"
        } > "$weather_file"
    else
        echo "Weather data unavailable. Check your location setting or network." > "$weather_file"
        warn "Could not fetch weather data for ${LOCATION}."
    fi
}

# ---------------------------------------------------------------------------
# Section: Calendar (iCal parsing)
# ---------------------------------------------------------------------------
fetch_calendar() {
    log "Processing calendar sources..."
    local cal_file="${TEMP_DIR}/calendar.txt"
    local has_events=false

    echo "| Time | Event | Calendar |" > "$cal_file"
    echo "|------|-------|----------|" >> "$cal_file"

    # Parse ICS files — look for VEVENT blocks with today's date
    # This is a simplified parser for common iCal formats.
    parse_ics() {
        local ics_content="$1"
        local cal_name="$2"
        local in_event=false
        local summary=""
        local dtstart=""

        while IFS= read -r line; do
            line=$(echo "$line" | tr -d '\r')
            case "$line" in
                BEGIN:VEVENT)
                    in_event=true
                    summary=""
                    dtstart=""
                    ;;
                END:VEVENT)
                    if [[ "$in_event" == true && -n "$summary" && "$dtstart" == *"${TODAY//-/}"* ]]; then
                        # Extract time portion
                        local time_part
                        time_part=$(echo "$dtstart" | grep -oE 'T[0-9]{4}' | sed 's/T//' | sed 's/\(..\)/\1:/')
                        [[ -z "$time_part" ]] && time_part="All day"
                        echo "| ${time_part} | ${summary} | ${cal_name} |" >> "$cal_file"
                        COUNT_EVENTS=$((COUNT_EVENTS + 1))
                        has_events=true
                    fi
                    in_event=false
                    ;;
                SUMMARY:*)
                    [[ "$in_event" == true ]] && summary="${line#SUMMARY:}"
                    ;;
                DTSTART*)
                    [[ "$in_event" == true ]] && dtstart="$line"
                    ;;
            esac
        done <<< "$ics_content"
    }

    # Check for local .ics files in common locations
    for ics_path in ~/calendars/*.ics ~/.local/share/calendars/**/*.ics; do
        if [[ -f "$ics_path" ]]; then
            local name
            name=$(basename "$ics_path" .ics)
            parse_ics "$(cat "$ics_path")" "$name"
        fi
    done

    if [[ "$has_events" == false ]]; then
        echo "" > "$cal_file"
        echo "No calendar events found for today. Configure iCal sources in your config." > "$cal_file"
    fi
}

# ---------------------------------------------------------------------------
# Section: Tasks
# ---------------------------------------------------------------------------
fetch_tasks() {
    log "Processing task sources..."
    local tasks_file="${TEMP_DIR}/tasks.txt"
    local overdue_file="${TEMP_DIR}/tasks_overdue.txt"
    local today_file="${TEMP_DIR}/tasks_today.txt"
    local other_file="${TEMP_DIR}/tasks_other.txt"

    : > "$tasks_file"
    : > "$overdue_file"
    : > "$today_file"
    : > "$other_file"

    # todo.txt format
    local todotxt_path="${HOME}/todo.txt"
    if [[ -f "$todotxt_path" ]]; then
        while IFS= read -r line; do
            [[ -z "$line" || "$line" == x\ * ]] && continue
            COUNT_TASKS=$((COUNT_TASKS + 1))

            # Check for due dates
            local due_date
            due_date=$(echo "$line" | grep -oE 'due:[0-9]{4}-[0-9]{2}-[0-9]{2}' | sed 's/due://')

            if [[ -n "$due_date" ]]; then
                if [[ "$due_date" < "$TODAY" ]]; then
                    echo "- **OVERDUE** ${line}" >> "$overdue_file"
                elif [[ "$due_date" == "$TODAY" ]]; then
                    echo "- ${line}" >> "$today_file"
                else
                    echo "- ${line}" >> "$other_file"
                fi
            else
                echo "- ${line}" >> "$other_file"
            fi
        done < "$todotxt_path"
    fi

    # Markdown task lists
    local md_tasks_path="${HOME}/tasks.md"
    if [[ -f "$md_tasks_path" ]]; then
        grep -E '^\s*- \[ \]' "$md_tasks_path" 2>/dev/null | while IFS= read -r line; do
            COUNT_TASKS=$((COUNT_TASKS + 1))
            echo "${line}" >> "$other_file"
        done
    fi

    # GitHub issues (if gh CLI is available)
    if command -v gh &> /dev/null; then
        local gh_issues
        gh_issues=$(gh issue list --assignee @me --state open --limit 10 --json title,url,updatedAt 2>/dev/null || echo "")
        if [[ -n "$gh_issues" && "$gh_issues" != "[]" ]]; then
            echo "$gh_issues" | python3 -c "
import sys, json
try:
    issues = json.load(sys.stdin)
    for i in issues:
        print(f\"- [{i['title']}]({i['url']})\")
except:
    pass
" >> "$other_file" 2>/dev/null || true
        fi
    fi

    # Compile into the tasks file
    {
        if [[ -s "$overdue_file" ]]; then
            echo "### Overdue"
            echo ""
            cat "$overdue_file"
            echo ""
        fi
        if [[ -s "$today_file" ]]; then
            echo "### Due Today"
            echo ""
            cat "$today_file"
            echo ""
        fi
        if [[ -s "$other_file" ]]; then
            echo "### Upcoming"
            echo ""
            cat "$other_file"
            echo ""
        fi
        if [[ ! -s "$overdue_file" && ! -s "$today_file" && ! -s "$other_file" ]]; then
            echo "No tasks found. Configure task sources in your config or create ~/todo.txt."
        fi
    } > "$tasks_file"
}

# ---------------------------------------------------------------------------
# Section: News (RSS)
# ---------------------------------------------------------------------------
fetch_news() {
    log "Fetching news feeds..."
    local news_file="${TEMP_DIR}/news.txt"
    : > "$news_file"

    if [[ "$OFFLINE_MODE" == true ]]; then
        echo "News feeds unavailable (offline mode)." > "$news_file"
        return
    fi

    fetch_rss_feed() {
        local name="$1"
        local url="$2"
        local max_items="${3:-5}"

        local feed_xml
        feed_xml=$(curl -s --max-time 15 "$url" 2>/dev/null || echo "")

        if [[ -z "$feed_xml" ]]; then
            warn "Could not fetch RSS feed: ${name} (${url})"
            return
        fi

        echo "### ${name}" >> "$news_file"
        echo "" >> "$news_file"

        # Extract titles and links from RSS/Atom XML
        # This handles both <item><title>...</title><link>...</link></item>
        # and <entry><title>...</title><link href="..."/></entry> formats.
        echo "$feed_xml" | python3 -c "
import sys
import xml.etree.ElementTree as ET

try:
    content = sys.stdin.read()
    root = ET.fromstring(content)
    count = 0
    max_items = ${max_items}

    # Try RSS format
    for item in root.iter('item'):
        if count >= max_items:
            break
        title_el = item.find('title')
        link_el = item.find('link')
        desc_el = item.find('description')
        title = title_el.text.strip() if title_el is not None and title_el.text else 'Untitled'
        link = link_el.text.strip() if link_el is not None and link_el.text else ''
        desc = ''
        if desc_el is not None and desc_el.text:
            desc = desc_el.text.strip()[:120].replace('\n', ' ')
            # Strip HTML tags
            import re
            desc = re.sub(r'<[^>]+>', '', desc)
        if link:
            print(f'{count+1}. [{title}]({link})')
        else:
            print(f'{count+1}. {title}')
        if desc:
            print(f'   _{desc}_')
        count += 1

    # Try Atom format if no RSS items found
    if count == 0:
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        for entry in root.findall('.//atom:entry', ns):
            if count >= max_items:
                break
            title_el = entry.find('atom:title', ns)
            link_el = entry.find('atom:link', ns)
            title = title_el.text.strip() if title_el is not None and title_el.text else 'Untitled'
            link = link_el.get('href', '') if link_el is not None else ''
            if link:
                print(f'{count+1}. [{title}]({link})')
            else:
                print(f'{count+1}. {title}')
            count += 1

    if count == 0:
        print('No recent items.')
except Exception as e:
    print(f'Could not parse feed: {e}')
" >> "$news_file" 2>/dev/null

        echo "" >> "$news_file"

        # Count items we added
        local item_count
        item_count=$(grep -cE '^\d+\.' "$news_file" 2>/dev/null || echo "0")
        COUNT_NEWS=$((COUNT_NEWS + item_count))
    }

    # Default feeds
    fetch_rss_feed "Hacker News" "https://hnrss.org/frontpage" 5
    fetch_rss_feed "TechCrunch" "https://techcrunch.com/feed/" 3
}

# ---------------------------------------------------------------------------
# Section: Quote of the Day
# ---------------------------------------------------------------------------
fetch_quote() {
    log "Fetching quote of the day..."
    local quote_file="${TEMP_DIR}/quote.txt"

    if [[ "$OFFLINE_MODE" == true ]]; then
        # Fallback Stoic quotes for offline mode
        local stoic_quotes=(
            "The happiness of your life depends upon the quality of your thoughts.|Marcus Aurelius"
            "Waste no more time arguing about what a good man should be. Be one.|Marcus Aurelius"
            "He who fears death will never do anything worthy of a living man.|Seneca"
            "The best revenge is not to be like your enemy.|Marcus Aurelius"
            "Difficulties strengthen the mind, as labor does the body.|Seneca"
            "You have power over your mind, not outside events. Realize this, and you will find strength.|Marcus Aurelius"
            "It is not that we have a short time to live, but that we waste a great deal of it.|Seneca"
        )
        local idx=$((RANDOM % ${#stoic_quotes[@]}))
        local entry="${stoic_quotes[$idx]}"
        local text="${entry%%|*}"
        local author="${entry##*|}"
        echo "> \"${text}\" -- _${author}_" > "$quote_file"
        return
    fi

    local quote_json
    quote_json=$(curl -s --max-time 10 "https://zenquotes.io/api/today" 2>/dev/null || echo "")

    if [[ -n "$quote_json" && "$quote_json" != *"error"* ]]; then
        echo "$quote_json" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if isinstance(data, list) and len(data) > 0:
        q = data[0].get('q', '')
        a = data[0].get('a', 'Unknown')
        print(f'> \"{q}\" -- _{a}_')
    else:
        print('> \"The only way to do great work is to love what you do.\" -- _Steve Jobs_')
except:
    print('> \"The only way to do great work is to love what you do.\" -- _Steve Jobs_')
" > "$quote_file" 2>/dev/null
    else
        echo '> "The only way to do great work is to love what you do." -- _Steve Jobs_' > "$quote_file"
    fi
}

# ---------------------------------------------------------------------------
# Compile the Digest
# ---------------------------------------------------------------------------
compile_markdown() {
    log "Compiling Markdown digest..."
    local output_file="${OUTPUT_DIR}/digest-${TODAY}.md"
    mkdir -p "$OUTPUT_DIR"

    {
        echo "# Daily Digest -- ${DAY_OF_WEEK}, $(date +'%B %d, %Y')"
        echo ""

        # Quote
        if [[ -f "${TEMP_DIR}/quote.txt" ]]; then
            cat "${TEMP_DIR}/quote.txt"
            echo ""
        fi

        echo "---"
        echo ""

        # Weather
        if [[ -f "${TEMP_DIR}/weather.txt" && -s "${TEMP_DIR}/weather.txt" ]]; then
            echo "## Weather"
            echo ""
            cat "${TEMP_DIR}/weather.txt"
            echo ""
            echo "---"
            echo ""
        fi

        # Calendar
        if [[ -f "${TEMP_DIR}/calendar.txt" && -s "${TEMP_DIR}/calendar.txt" ]]; then
            echo "## Calendar"
            echo ""
            cat "${TEMP_DIR}/calendar.txt"
            echo ""
            echo "---"
            echo ""
        fi

        # Tasks
        if [[ -f "${TEMP_DIR}/tasks.txt" && -s "${TEMP_DIR}/tasks.txt" ]]; then
            echo "## Tasks"
            echo ""
            cat "${TEMP_DIR}/tasks.txt"
            echo ""
            echo "---"
            echo ""
        fi

        # News
        if [[ -f "${TEMP_DIR}/news.txt" && -s "${TEMP_DIR}/news.txt" ]]; then
            echo "## News"
            echo ""
            cat "${TEMP_DIR}/news.txt"
            echo ""
            echo "---"
            echo ""
        fi

        # Warnings
        if [[ -n "$WARNINGS" ]]; then
            echo "## Notices"
            echo ""
            echo -e "$WARNINGS"
            echo ""
            echo "---"
            echo ""
        fi

        # Footer
        echo "*Generated at ${TIMESTAMP} by Daily Digest v1.0.0*"
        echo ""
        echo "*Events: ${COUNT_EVENTS} | Tasks: ${COUNT_TASKS} | News items: ${COUNT_NEWS}*"

    } > "$output_file"

    DIGEST_FILE="$output_file"
    log "Markdown digest saved to ${output_file}"
}

compile_html() {
    log "Compiling HTML digest..."
    local md_file="${OUTPUT_DIR}/digest-${TODAY}.md"
    local html_file="${OUTPUT_DIR}/digest-${TODAY}.html"

    # If markdown file doesn't exist yet, compile it first
    [[ ! -f "$md_file" ]] && compile_markdown

    # Convert markdown to HTML with inline styles
    python3 -c "
import re, html as html_mod

def md_to_html(md_text):
    lines = md_text.split('\n')
    out = []
    in_table = False
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Headings
        if stripped.startswith('# '):
            if in_list: out.append('</ul>'); in_list = False
            out.append(f'<h1>{stripped[2:]}</h1>')
        elif stripped.startswith('## '):
            if in_list: out.append('</ul>'); in_list = False
            out.append(f'<h2>{stripped[3:]}</h2>')
        elif stripped.startswith('### '):
            if in_list: out.append('</ul>'); in_list = False
            out.append(f'<h3>{stripped[4:]}</h3>')
        elif stripped.startswith('> '):
            out.append(f'<blockquote>{stripped[2:]}</blockquote>')
        elif stripped.startswith('---'):
            out.append('<hr>')
        elif stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list: out.append('<ul>'); in_list = True
            out.append(f'<li>{stripped[2:]}</li>')
        elif stripped.startswith('|') and '|' in stripped[1:]:
            if '---' in stripped:
                continue
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            if not in_table:
                out.append('<table><tr>' + ''.join(f'<th>{c}</th>' for c in cells) + '</tr>')
                in_table = True
            else:
                out.append('<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>')
        elif stripped == '' and in_table:
            out.append('</table>')
            in_table = False
        elif stripped.startswith('*') and stripped.endswith('*') and not stripped.startswith('**'):
            out.append(f'<p><em>{stripped[1:-1]}</em></p>')
        elif stripped:
            if in_list: out.append('</ul>'); in_list = False
            # Inline formatting
            s = stripped
            s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
            s = re.sub(r'_(.+?)_', r'<em>\1</em>', s)
            s = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href=\"\2\" target=\"_blank\">\1</a>', s)
            out.append(f'<p>{s}</p>')

    if in_list: out.append('</ul>')
    if in_table: out.append('</table>')
    return '\n'.join(out)

with open('${md_file}', 'r') as f:
    md = f.read()

body = md_to_html(md)

html = '''<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"UTF-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
<title>Daily Digest - $(date +'%B %d, %Y')</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         background: #f0f2f5; color: #333; line-height: 1.6; }
  .header { background: #1a1a2e; color: white; padding: 2rem; text-align: center; }
  .header h1 { font-size: 1.8rem; font-weight: 300; }
  .container { max-width: 700px; margin: 0 auto; padding: 1rem; }
  .card { background: white; border-radius: 8px; padding: 1.5rem; margin: 1rem 0;
           box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
  h2 { color: #0f3460; border-bottom: 2px solid #0f3460; padding-bottom: 0.5rem;
       margin-bottom: 1rem; font-size: 1.3rem; }
  h3 { color: #16213e; margin: 0.8rem 0 0.4rem; }
  blockquote { border-left: 4px solid #0f3460; padding: 0.8rem 1rem;
               background: #f8f9fa; margin: 1rem 0; font-style: italic; }
  table { width: 100%%; border-collapse: collapse; margin: 0.5rem 0; }
  th, td { padding: 0.5rem 0.8rem; text-align: left; border-bottom: 1px solid #eee; }
  th { background: #f8f9fa; font-weight: 600; color: #0f3460; }
  ul { padding-left: 1.5rem; margin: 0.5rem 0; }
  li { margin: 0.3rem 0; }
  a { color: #0f3460; text-decoration: none; }
  a:hover { text-decoration: underline; }
  hr { border: none; border-top: 1px solid #e0e0e0; margin: 1.5rem 0; }
  .footer { text-align: center; color: #888; font-size: 0.85rem; padding: 2rem 0; }
  strong { color: #c0392b; }
  em { color: #555; }
  @media (max-width: 600px) { .container { padding: 0.5rem; }
    .card { padding: 1rem; } .header h1 { font-size: 1.4rem; } }
</style>
</head>
<body>
<div class=\"header\"><h1>Daily Digest</h1></div>
<div class=\"container\"><div class=\"card\">
''' + body + '''
</div></div>
<div class=\"footer\">Generated by Daily Digest v1.0.0</div>
</body></html>'''

with open('${html_file}', 'w') as f:
    f.write(html)
" 2>/dev/null

    if [[ -f "$html_file" ]]; then
        log "HTML digest saved to ${html_file}"
    else
        warn "Failed to generate HTML output. Python3 may not be available."
    fi
}

# ---------------------------------------------------------------------------
# Archive Management
# ---------------------------------------------------------------------------
cleanup_archives() {
    local max_days=30
    log "Cleaning up archives older than ${max_days} days..."
    find "$OUTPUT_DIR" -name "digest-*.md" -mtime +"$max_days" -delete 2>/dev/null || true
    find "$OUTPUT_DIR" -name "digest-*.html" -mtime +"$max_days" -delete 2>/dev/null || true
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    log "=== Daily Digest — ${TODAY} ==="

    ensure_config
    check_connectivity

    mkdir -p "$OUTPUT_DIR"

    # Gather all sections (run in sequence to avoid race conditions on counters)
    fetch_weather
    fetch_calendar
    fetch_tasks
    fetch_news
    fetch_quote

    # Compile output
    case "$OUTPUT_FORMAT" in
        markdown)
            compile_markdown
            ;;
        html)
            compile_markdown  # HTML depends on MD
            compile_html
            ;;
        both)
            compile_markdown
            compile_html
            ;;
        *)
            warn "Unknown format '${OUTPUT_FORMAT}'. Defaulting to markdown."
            compile_markdown
            ;;
    esac

    cleanup_archives

    # Print the digest to stdout
    if [[ -n "$DIGEST_FILE" && -f "$DIGEST_FILE" ]]; then
        echo ""
        cat "$DIGEST_FILE"
    fi

    log ""
    log "=== Digest Complete ==="
    log "Events: ${COUNT_EVENTS} | Tasks: ${COUNT_TASKS} | News: ${COUNT_NEWS}"
    [[ -n "$WARNINGS" ]] && log "Warnings:${WARNINGS}"
    log "Output: ${OUTPUT_DIR}/digest-${TODAY}.md"
}

main "$@"
