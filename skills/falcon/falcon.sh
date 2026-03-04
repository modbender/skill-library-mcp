#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# falcon — Twitter/X CLI powered by TwexAPI
###############################################################################

BASE_URL="https://api.twexapi.io"

# ---------------------------------------------------------------------------
# Cleanup trap for temp files
# ---------------------------------------------------------------------------

_tmp_files=()
_cleanup() { [[ ${#_tmp_files[@]} -gt 0 ]] && rm -f "${_tmp_files[@]}" || true; }
trap _cleanup EXIT

_mktemp() {
  local f
  f=$(mktemp)
  chmod 600 "$f"
  _tmp_files+=("$f")
  echo "$f"
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

die()  { echo "error: $*" >&2; exit 1; }
need() { [[ -n "${!1:-}" ]] || die "environment variable $1 is not set"; }

# Input validators
validate_username() {
  [[ "$1" =~ ^[A-Za-z0-9_]{1,15}$ ]] || die "invalid username: $1"
}

validate_count() {
  [[ "$1" =~ ^[0-9]+$ ]] || die "invalid count (must be a positive integer): $1"
}

validate_country() {
  [[ "$1" =~ ^[a-z][a-z-]*$ ]] || die "invalid country slug: $1"
}

validate_path_segment() {
  if [[ "$1" == *"/"* ]] || [[ "$1" == *"?"* ]] || [[ "$1" == *"#"* ]] || [[ "$1" == *"&"* ]]; then
    die "input contains illegal characters: $1"
  fi
}

# Extract tweet ID from a URL or bare ID
tweet_id() {
  local input="$1"
  if [[ "$input" =~ /status/([0-9]+) ]]; then
    echo "${BASH_REMATCH[1]}"
  elif [[ "$input" =~ ^[0-9]+$ ]]; then
    echo "$input"
  else
    die "cannot parse tweet ID from input"
  fi
}

# Authenticated GET request — secrets kept out of process args
api_get() {
  need TWEXAPI_KEY
  local path="$1"
  local hdr_file
  hdr_file=$(_mktemp)
  printf 'Authorization: Bearer %s\n' "$TWEXAPI_KEY" > "$hdr_file"
  printf 'Content-Type: application/json\n' >> "$hdr_file"
  curl -sS --fail-with-body \
    -H @"$hdr_file" \
    "${BASE_URL}${path}" | jq .
}

# Authenticated POST request — secrets kept out of process args
api_post() {
  need TWEXAPI_KEY
  local path="$1"
  local body="$2"
  local hdr_file body_file
  hdr_file=$(_mktemp)
  body_file=$(_mktemp)
  printf 'Authorization: Bearer %s\n' "$TWEXAPI_KEY" > "$hdr_file"
  printf 'Content-Type: application/json\n' >> "$hdr_file"
  printf '%s' "$body" > "$body_file"
  curl -sS --fail-with-body \
    -X POST \
    -H @"$hdr_file" \
    -d @"$body_file" \
    "${BASE_URL}${path}" | jq .
}

# Authenticated DELETE request — secrets kept out of process args
api_delete() {
  need TWEXAPI_KEY
  local path="$1"
  local body="$2"
  local hdr_file body_file
  hdr_file=$(_mktemp)
  body_file=$(_mktemp)
  printf 'Authorization: Bearer %s\n' "$TWEXAPI_KEY" > "$hdr_file"
  printf 'Content-Type: application/json\n' >> "$hdr_file"
  printf '%s' "$body" > "$body_file"
  curl -sS --fail-with-body \
    -X DELETE \
    -H @"$hdr_file" \
    -d @"$body_file" \
    "${BASE_URL}${path}" | jq .
}

require_cookie() {
  need TWITTER_COOKIE
}

# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------

usage() {
cat <<'EOF'
falcon — Twitter/X CLI powered by TwexAPI

READ COMMANDS (require TWEXAPI_KEY):
  falcon check                         Verify API key is configured
  falcon balance                       Check API credit balance
  falcon user <username>               User profile info
  falcon users <u1,u2,...>             Multiple user profiles
  falcon find <keyword> [count]        Search for users (default: 5)
  falcon tweets <username> [count]     User's tweets & replies (default: 20)
  falcon read <id-or-url> [...]        Read one or more tweets by ID/URL
  falcon replies <id-or-url> [count]   Replies to a tweet (default: 20)
  falcon similar <id-or-url>           Similar tweets
  falcon search <query> [count]        Advanced search (default: 10)
  falcon hashtag <tag> [count]         Search by hashtag (default: 20)
  falcon cashtag <tag> [count]         Search by cashtag (default: 20)
  falcon trending [country]            Trending topics (default: worldwide)
  falcon followers <username> [count]  Get followers (default: 20)
  falcon following <username> [count]  Get following (default: 20)
  falcon retweeters <id-or-url> [cnt]  Who retweeted (default: 20)

WRITE COMMANDS (also require TWITTER_COOKIE):
  falcon tweet <text>                  Post a tweet
  falcon reply <id-or-url> <text>      Reply to a tweet
  falcon quote <tweet-url> <text>      Quote tweet
  falcon like <id-or-url>              Like a tweet
  falcon unlike <id-or-url>            Unlike a tweet
  falcon retweet <id-or-url>           Retweet
  falcon bookmark <id-or-url>          Bookmark a tweet
  falcon follow <username>             Follow a user
  falcon unfollow <username>           Unfollow a user

ENVIRONMENT VARIABLES:
  TWEXAPI_KEY       Required. Your TwexAPI bearer token.
  TWITTER_COOKIE    Required for write commands. Your Twitter auth cookie/auth_token.
EOF
}

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

cmd_check() {
  if [[ -n "${TWEXAPI_KEY:-}" ]]; then
    echo "TWEXAPI_KEY: set"
  else
    echo "TWEXAPI_KEY: NOT SET"
  fi
  if [[ -n "${TWITTER_COOKIE:-}" ]]; then
    echo "TWITTER_COOKIE: set"
  else
    echo "TWITTER_COOKIE: not set (needed for write commands)"
  fi
}

cmd_balance() {
  api_get "/balance"
}

cmd_user() {
  [[ $# -ge 1 ]] || die "usage: falcon user <username>"
  validate_username "$1"
  api_get "/twitter/$1/about"
}

cmd_users() {
  [[ $# -ge 1 ]] || die "usage: falcon users <u1,u2,...>"
  # Validate each username
  local IFS=','
  for u in $1; do
    validate_username "$u"
  done
  unset IFS
  # Split comma-separated usernames into JSON array
  local json
  json=$(printf '%s' "$1" | tr ',' '\n' | jq -R . | jq -s .)
  api_post "/twitter/users" "$json"
}

cmd_find() {
  [[ $# -ge 1 ]] || die "usage: falcon find <keyword> [count]"
  local keyword="$1"
  local count="${2:-5}"
  validate_path_segment "$keyword"
  validate_count "$count"
  api_get "/twitter/search-user/${keyword}/${count}"
}

cmd_tweets() {
  [[ $# -ge 1 ]] || die "usage: falcon tweets <username> [count]"
  local username="$1"
  local count="${2:-20}"
  validate_username "$username"
  validate_count "$count"
  api_get "/twitter/${username}/tweets-replies/${count}"
}

cmd_read() {
  [[ $# -ge 1 ]] || die "usage: falcon read <id-or-url> [...]"
  local ids=()
  for arg in "$@"; do
    ids+=("$(tweet_id "$arg")")
  done
  local json
  json=$(printf '%s\n' "${ids[@]}" | jq -R 'tonumber' | jq -s .)
  api_post "/twitter/tweets/lookup" "$json"
}

cmd_replies() {
  [[ $# -ge 1 ]] || die "usage: falcon replies <id-or-url> [count]"
  local id
  id=$(tweet_id "$1")
  local count="${2:-20}"
  validate_count "$count"
  api_get "/twitter/tweets/${id}/replies/${count}"
}

cmd_similar() {
  [[ $# -ge 1 ]] || die "usage: falcon similar <id-or-url>"
  local id
  id=$(tweet_id "$1")
  api_get "/twitter/tweets/${id}/similar"
}

cmd_search() {
  [[ $# -ge 1 ]] || die "usage: falcon search <query> [count]"
  local query="$1"
  local count="${2:-10}"
  validate_count "$count"
  local json
  json=$(jq -n --arg q "$query" --argjson n "$count" \
    '{searchTerms: [$q], maxItems: $n, sortBy: "Latest"}')
  api_post "/twitter/advanced_search" "$json"
}

cmd_hashtag() {
  [[ $# -ge 1 ]] || die "usage: falcon hashtag <tag> [count]"
  local tag="${1#\#}"
  local count="${2:-20}"
  validate_count "$count"
  local json
  json=$(jq -n --arg t "$tag" --argjson n "$count" \
    '{hashtags: [$t], maxItems: $n, sortBy: "Latest"}')
  api_post "/twitter/hashtags" "$json"
}

cmd_cashtag() {
  [[ $# -ge 1 ]] || die "usage: falcon cashtag <tag> [count]"
  local tag="${1#\$}"
  local count="${2:-20}"
  validate_count "$count"
  local json
  json=$(jq -n --arg t "$tag" --argjson n "$count" \
    '{cashtags: [$t], maxItems: $n, sortBy: "Latest"}')
  api_post "/twitter/cashtags" "$json"
}

cmd_trending() {
  local country="${1:-worldwide}"
  validate_country "$country"
  api_get "/twitter/${country}/trending"
}

cmd_followers() {
  [[ $# -ge 1 ]] || die "usage: falcon followers <username> [count]"
  local username="$1"
  local count="${2:-20}"
  validate_username "$username"
  validate_count "$count"
  api_get "/twitter/followers/${username}/${count}"
}

cmd_following() {
  [[ $# -ge 1 ]] || die "usage: falcon following <username> [count]"
  local username="$1"
  local count="${2:-20}"
  validate_username "$username"
  validate_count "$count"
  api_get "/twitter/following/${username}/${count}"
}

cmd_retweeters() {
  [[ $# -ge 1 ]] || die "usage: falcon retweeters <id-or-url> [count]"
  local id
  id=$(tweet_id "$1")
  local count="${2:-20}"
  validate_count "$count"
  api_get "/twitter/tweets/${id}/retweeters/${count}"
}

# --- Write commands ---

cmd_tweet() {
  [[ $# -ge 1 ]] || die "usage: falcon tweet <text>"
  require_cookie
  local json
  json=$(jq -n --arg text "$1" --arg cookie "$TWITTER_COOKIE" \
    '{tweet_content: $text, cookie: $cookie}')
  api_post "/twitter/tweets/create" "$json"
}

cmd_reply() {
  [[ $# -ge 2 ]] || die "usage: falcon reply <id-or-url> <text>"
  require_cookie
  local id
  id=$(tweet_id "$1")
  local json
  json=$(jq -n --arg text "$2" --arg cookie "$TWITTER_COOKIE" --arg rid "$id" \
    '{tweet_content: $text, cookie: $cookie, reply_tweet_id: $rid}')
  api_post "/twitter/tweets/create" "$json"
}

cmd_quote() {
  [[ $# -ge 2 ]] || die "usage: falcon quote <tweet-url> <text>"
  require_cookie
  local json
  json=$(jq -n --arg text "$2" --arg cookie "$TWITTER_COOKIE" --arg url "$1" \
    '{tweet_content: $text, cookie: $cookie, quote_tweet_url: $url}')
  api_post "/twitter/tweets/quote" "$json"
}

cmd_like() {
  [[ $# -ge 1 ]] || die "usage: falcon like <id-or-url>"
  require_cookie
  local id
  id=$(tweet_id "$1")
  local json
  json=$(jq -n --arg cookie "$TWITTER_COOKIE" '{cookie: $cookie}')
  api_post "/twitter/tweets/${id}/like" "$json"
}

cmd_unlike() {
  [[ $# -ge 1 ]] || die "usage: falcon unlike <id-or-url>"
  require_cookie
  local id
  id=$(tweet_id "$1")
  local json
  json=$(jq -n --arg cookie "$TWITTER_COOKIE" '{cookie: $cookie}')
  api_delete "/twitter/tweets/${id}/like" "$json"
}

cmd_retweet() {
  [[ $# -ge 1 ]] || die "usage: falcon retweet <id-or-url>"
  require_cookie
  local id
  id=$(tweet_id "$1")
  local json
  json=$(jq -n --arg cookie "$TWITTER_COOKIE" '{cookie: $cookie}')
  api_post "/twitter/tweets/${id}/retweet" "$json"
}

cmd_bookmark() {
  [[ $# -ge 1 ]] || die "usage: falcon bookmark <id-or-url>"
  require_cookie
  local id
  id=$(tweet_id "$1")
  local json
  json=$(jq -n --arg cookie "$TWITTER_COOKIE" '{cookie: $cookie}')
  api_post "/twitter/tweets/${id}/bookmark" "$json"
}

cmd_follow() {
  [[ $# -ge 1 ]] || die "usage: falcon follow <username>"
  require_cookie
  validate_username "$1"
  local json
  json=$(jq -n --arg u "$1" --arg cookie "$TWITTER_COOKIE" \
    '{username: $u, cookie: $cookie}')
  api_post "/twitter/user/follow" "$json"
}

cmd_unfollow() {
  [[ $# -ge 1 ]] || die "usage: falcon unfollow <username>"
  require_cookie
  validate_username "$1"
  local json
  json=$(jq -n --arg u "$1" --arg cookie "$TWITTER_COOKIE" \
    '{username: $u, cookie: $cookie}')
  api_delete "/twitter/user/follow" "$json"
}

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

cmd="${1:-help}"
shift 2>/dev/null || true

case "$cmd" in
  help|--help|-h)  usage ;;
  check)           cmd_check ;;
  balance)         cmd_balance ;;
  user)            cmd_user "$@" ;;
  users)           cmd_users "$@" ;;
  find)            cmd_find "$@" ;;
  tweets)          cmd_tweets "$@" ;;
  read)            cmd_read "$@" ;;
  replies)         cmd_replies "$@" ;;
  similar)         cmd_similar "$@" ;;
  search)          cmd_search "$@" ;;
  hashtag)         cmd_hashtag "$@" ;;
  cashtag)         cmd_cashtag "$@" ;;
  trending)        cmd_trending "$@" ;;
  followers)       cmd_followers "$@" ;;
  following)       cmd_following "$@" ;;
  retweeters)      cmd_retweeters "$@" ;;
  tweet)           cmd_tweet "$@" ;;
  reply)           cmd_reply "$@" ;;
  quote)           cmd_quote "$@" ;;
  like)            cmd_like "$@" ;;
  unlike)          cmd_unlike "$@" ;;
  retweet)         cmd_retweet "$@" ;;
  bookmark)        cmd_bookmark "$@" ;;
  follow)          cmd_follow "$@" ;;
  unfollow)        cmd_unfollow "$@" ;;
  *)               die "unknown command: $cmd (run 'falcon help')" ;;
esac
