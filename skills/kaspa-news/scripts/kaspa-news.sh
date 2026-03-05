#!/usr/bin/env bash
set -euo pipefail

# Kaspa News CLI — uses public kaspa.news API endpoints (no API keys)
API_BASE="https://kaspa.news/api"

LIMIT=10
JSON=false
SINCE=""
SOURCES=false
CMD=""

usage() {
  cat <<'EOF'
kaspa-news — Kaspa ecosystem news from public kaspa.news APIs

USAGE:
  kaspa-news <command> [options]

COMMANDS:
  focused     Curated community tweets (no replies)
  builders    Ecosystem/builder tweets (no replies)
  top         Highest engagement tweets (by views)
  developers  Developer tweets (includes replies)
  videos      Latest YouTube videos
  reddit      Latest Reddit posts
  pulse       Latest AI pulse report

OPTIONS:
  -n, --limit N     Number of items (default: 10)
  --json            Raw JSON output
  --since HOURS     Only items from last N hours
  --sources         Show clickable SOURCE links for pulse references
  -h, --help        Show this help
EOF
  exit 0
}

api_get() {
  local endpoint="$1"
  python3 - "$API_BASE" "$endpoint" <<'PY'
import requests, sys
base = sys.argv[1].rstrip('/')
endpoint = sys.argv[2].lstrip('/')
url = f"{base}/{endpoint}"
r = requests.get(url, timeout=30)
r.raise_for_status()
print(r.text)
PY
}

relative_time() {
  local ts="$1"
  local now epoch diff
  now=$(date +%s)
  epoch=$(date -d "${ts}" +%s 2>/dev/null || echo "$now")
  diff=$(( now - epoch ))
  if (( diff < 60 )); then echo "just now"
  elif (( diff < 3600 )); then echo "$(( diff / 60 ))m"
  elif (( diff < 86400 )); then echo "$(( diff / 3600 ))h"
  else echo "$(( diff / 86400 ))d"
  fi
}

apply_since_filter() {
  local data="$1" field="$2"
  if [[ -z "$SINCE" ]]; then
    echo "$data"
    return
  fi

  local cutoff
  cutoff=$(date -u -d "-${SINCE} hours" +%s 2>/dev/null || date -u +%s)

  echo "$data" | jq --arg field "$field" --argjson cutoff "$cutoff" '
    [ .[]
      | select(
          ((.[ $field ] // "")
            | tostring
            | sub("\\.[0-9]+\\+00:00$"; "Z")
            | sub("\\+00:00$"; "Z")
            | fromdateiso8601? // 0
          ) >= $cutoff
        )
    ]
  '
}

apply_limit() {
  local data="$1"
  echo "$data" | jq --argjson n "$LIMIT" '.[0:$n]'
}

decode_html() {
  local text="$1"
  text="${text//&gt;/>}"
  text="${text//&lt;/<}"
  text="${text//&amp;/&}"
  text="${text//&quot;/\"}"
  echo "$text"
}

strip_tco() {
  local text="$1"
  text=$(echo "$text" | sed -E 's/ ?https:\/\/t\.co\/[a-zA-Z0-9]+//g')
  echo "$text"
}

truncate_text() {
  local text="$1" max="${2:-200}"
  text=$(echo "$text" | tr '\n' ' ' | sed 's/  */ /g')
  if (( ${#text} > max )); then
    echo "${text:0:$max}..."
  else
    echo "$text"
  fi
}

expand_tco_links() {
  local text="$1" entities="$2"
  if [[ -z "$entities" || "$entities" == "null" ]]; then
    echo "$text"
    return
  fi

  # SECURITY: never embed untrusted tweet text/entities into inline code.
  # Pass both values as argv to avoid code injection via crafted payloads.
  local result
  result=$(python3 - "$text" "$entities" <<'PY' 2>/dev/null || true
import json, sys

text = sys.argv[1]
entities_raw = sys.argv[2]

try:
    ent = json.loads(entities_raw) if entities_raw else {}
    if isinstance(ent, str):
        ent = json.loads(ent)
    if not isinstance(ent, dict):
        ent = {}

    urls = ent.get('urls', [])
    if isinstance(urls, list):
        for u in urls:
            if not isinstance(u, dict):
                continue
            tco = u.get('url') or ''
            expanded = (u.get('expanded_url') or u.get('display_url') or '')
            if tco and expanded:
                text = text.replace(tco, expanded)
except Exception:
    pass

print(text)
PY
)

  if [[ -z "$result" ]]; then
    echo "$text"
  else
    echo "$result"
  fi
}

load_tweets() {
  local endpoint="${1:-kaspa-tweets}"
  api_get "$endpoint" | jq '
    [ .tweets[]
      | {
          author_username: (.author.username // "unknown"),
          text: (.text // ""),
          url: (.url // ""),
          is_quote: (.is_quote // false),
          is_reply: (.is_reply // false),
          quoted_tweet_author: (.quoted_tweet_author // ""),
          quoted_tweet_text: (.quoted_tweet_text // ""),
          in_reply_to_user: (.in_reply_to_user // ""),
          entities: (.entities // null),
          created_at: (.createdAt // ""),
          view_count: (.public_metrics.view_count // 0),
          category: (.category // "")
        }
    ]
  '
}

# Format tweets — 📝 tweet, 💬 quote, ↩️ reply
format_tweets() {
  local data="$1" include_views="${2:-false}"
  local count
  count=$(echo "$data" | jq 'length')
  for (( i=0; i<count; i++ )); do
    local user text ts url is_quote is_reply entities rel type_emoji views
    user=$(echo "$data" | jq -r ".[$i].author_username // \"unknown\"")
    text=$(echo "$data" | jq -r ".[$i].text // \"\"")
    ts=$(echo "$data" | jq -r ".[$i].created_at // \"\"")
    url=$(echo "$data" | jq -r ".[$i].url // \"\"")
    is_quote=$(echo "$data" | jq -r ".[$i].is_quote // false")
    is_reply=$(echo "$data" | jq -r ".[$i].is_reply // false")
    entities=$(echo "$data" | jq -c ".[$i].entities // null")
    views=$(echo "$data" | jq -r ".[$i].view_count // 0")
    rel=$(relative_time "$ts")

    if [[ "$is_quote" == "true" ]]; then type_emoji="💬"
    elif [[ "$is_reply" == "true" ]]; then type_emoji="↩️"
    else type_emoji="📝"; fi

    text=$(expand_tco_links "$text" "$entities")
    text=$(strip_tco "$text")
    text=$(decode_html "$text")
    text=$(truncate_text "$text" 300)

    if [[ "$include_views" == "true" ]]; then
      echo "${type_emoji} @${user} (${rel}) — 👁️ ${views}"
    else
      echo "${type_emoji} @${user} (${rel})"
    fi
    echo "${text}"
    if [[ -n "$url" && "$url" != "null" ]]; then
      echo "[SOURCE](${url})"
    fi
    echo ""
  done
}

cmd_focused() {
  local data
  data=$(load_tweets "focused-tweets")
  data=$(apply_since_filter "$data" "created_at")
  data=$(echo "$data" | jq 'sort_by(.created_at) | reverse')
  data=$(apply_limit "$data")

  if $JSON; then echo "$data" | jq .; return; fi
  echo "🎯 Focused Tweets"
  echo ""
  format_tweets "$data" "false"
}

cmd_builders() {
  local data
  data=$(load_tweets "builder-tweets")
  data=$(apply_since_filter "$data" "created_at")
  data=$(echo "$data" | jq 'sort_by(.created_at) | reverse')
  data=$(apply_limit "$data")

  if $JSON; then echo "$data" | jq .; return; fi
  echo "🔨 Ecosystem Tweets"
  echo ""
  format_tweets "$data" "false"
}

cmd_top() {
  local data
  data=$(load_tweets "kaspa-tweets")
  data=$(apply_since_filter "$data" "created_at")
  data=$(echo "$data" | jq 'sort_by(.view_count) | reverse')
  data=$(apply_limit "$data")

  if $JSON; then echo "$data" | jq .; return; fi
  echo "🔥 Top Tweets"
  echo ""
  format_tweets "$data" "true"
}

cmd_developers() {
  local data
  data=$(load_tweets "developer-tweets")
  data=$(apply_since_filter "$data" "created_at")
  data=$(echo "$data" | jq 'sort_by(.created_at) | reverse')
  data=$(apply_limit "$data")

  if $JSON; then echo "$data" | jq .; return; fi
  echo "💻 Developer Tweets"
  echo ""
  format_tweets "$data" "false"
}

cmd_videos() {
  local data
  data=$(api_get "kaspa-videos" | jq '
    [ .videos[]
      | {
          video_id: (.id // ""),
          title: (.title // ""),
          channel_title: (.channelTitle // ""),
          published_at: (.publishedAt // ""),
          view_count: (.viewCount // 0),
          like_count: (.likeCount // 0)
        }
    ]
    | sort_by(.published_at)
    | reverse
  ')
  data=$(apply_since_filter "$data" "published_at")
  data=$(apply_limit "$data")

  if $JSON; then echo "$data" | jq .; return; fi
  echo "📺 Kaspa Videos"
  echo ""
  local count
  count=$(echo "$data" | jq 'length')
  for (( i=0; i<count; i++ )); do
    local vid title channel views likes ts rel
    vid=$(echo "$data" | jq -r ".[$i].video_id // \"\"")
    title=$(echo "$data" | jq -r ".[$i].title // \"\"")
    channel=$(echo "$data" | jq -r ".[$i].channel_title // \"\"")
    views=$(echo "$data" | jq -r ".[$i].view_count // 0")
    likes=$(echo "$data" | jq -r ".[$i].like_count // 0")
    ts=$(echo "$data" | jq -r ".[$i].published_at // \"\"")
    rel=$(relative_time "$ts")
    echo "📺 ${title}"
    echo "  📡 ${channel} | 👁️ ${views} | ❤️ ${likes} | ${rel}"
    echo "  🔗 https://youtube.com/watch?v=${vid}"
    echo ""
  done
}

cmd_reddit() {
  local data
  data=$(api_get "reddit-posts" | jq '
    [ .posts[]
      | {
          id: (.id // ""),
          title: (.title // ""),
          author: (.author // ""),
          score: (.score // 0),
          created_at: (.created_at // "")
        }
    ]
    | sort_by(.created_at)
    | reverse
  ')
  data=$(apply_since_filter "$data" "created_at")
  data=$(apply_limit "$data")

  if $JSON; then echo "$data" | jq .; return; fi
  echo "🟠 Kaspa Reddit"
  echo ""
  local count
  count=$(echo "$data" | jq 'length')
  for (( i=0; i<count; i++ )); do
    local rid title author score ts rel
    rid=$(echo "$data" | jq -r ".[$i].id // \"\"")
    title=$(echo "$data" | jq -r ".[$i].title // \"\"")
    author=$(echo "$data" | jq -r ".[$i].author // \"\"")
    score=$(echo "$data" | jq -r ".[$i].score // 0")
    ts=$(echo "$data" | jq -r ".[$i].created_at // \"\"")
    rel=$(relative_time "$ts")
    echo "🟠 ${title}"
    echo "  👤 u/${author} | ⬆️ ${score} | ${rel}"
    echo "  🔗 https://reddit.com/r/kaspa/comments/${rid}"
    echo ""
  done
}

cmd_pulse() {
  local raw report rid ts model title summary rel
  raw=$(api_get "reports")
  report=$(echo "$raw" | jq '.report // {}')

  if $JSON; then echo "$report" | jq .; return; fi

  # --since support
  if [[ -n "$SINCE" ]]; then
    local cutoff epoch
    cutoff=$(date -u -d "-${SINCE} hours" +%s 2>/dev/null || date -u +%s)
    ts=$(echo "$report" | jq -r '.created_at // ""')
    epoch=$(date -d "${ts}" +%s 2>/dev/null || echo 0)
    if (( epoch < cutoff )); then
      echo "📊 Kaspa Pulse"
      echo ""
      echo "No reports in the last ${SINCE}h."
      return
    fi
  fi

  rid=$(echo "$report" | jq -r '.id // ""')
  ts=$(echo "$report" | jq -r '.created_at // ""')
  rel=$(relative_time "$ts")

  # executive_summary may be a JSON string payload or plain text
  local es parsed
  es=$(echo "$report" | jq -r '.executive_summary // ""')
  parsed=$(python3 - "$es" <<'PY'
import json, sys
s = sys.argv[1]
out = {"title": "Untitled", "summary": s}
try:
    obj = json.loads(s)
    if isinstance(obj, dict):
        out["title"] = obj.get("report_title") or "Untitled"
        out["summary"] = obj.get("executive_summary") or s
except Exception:
    pass
print(json.dumps(out))
PY
)
  title=$(echo "$parsed" | jq -r '.title // "Untitled"')
  summary=$(echo "$parsed" | jq -r '.summary // ""')

  echo "📊 Kaspa Pulse"
  echo ""
  echo "[REPORT HERE](https://kaspa.news/pulse/${rid})"
  echo ""
  echo "📊 ${title}"
  echo "  🕐 ${rel}"
  echo ""

  if [[ -n "$summary" && "$summary" != "null" ]]; then
    local short_summary
    short_summary="${summary:0:500}"
    if (( ${#summary} > 500 )); then
      short_summary="${short_summary}..."
    fi
    if $SOURCES; then
      short_summary=$(echo "$short_summary" | sed -E 's/@([a-zA-Z0-9_]+) \[source\]\(([0-9]+)\)/@\1 [SOURCE](https:\/\/x.com\/\1\/status\/\2)/g')
    else
      short_summary=$(echo "$short_summary" | sed -E 's/ - @[a-zA-Z0-9_]+ \[source\]\([0-9]+\)//g')
    fi
    echo "  ${short_summary}"
    echo ""
  fi
}

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    focused|builders|top|developers|videos|reddit|pulse)
      CMD="$1"; shift ;;
    -n|--limit)
      LIMIT="$2"; shift 2 ;;
    --json)
      JSON=true; shift ;;
    --sources)
      SOURCES=true; shift ;;
    --since)
      SINCE="$2"; shift 2 ;;
    -h|--help)
      usage ;;
    *)
      echo "Unknown: $1. Run with --help"; exit 1 ;;
  esac
done

if [[ -z "$CMD" ]]; then
  usage
fi

"cmd_${CMD}"
