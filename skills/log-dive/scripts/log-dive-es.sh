#!/usr/bin/env bash
# log-dive Elasticsearch/OpenSearch backend — queries via curl
# Read-only. Never modifies or deletes logs.
#
# Powered by Anvil AI 🤿
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ─── Validation ─────────────────────────────────────────────────────────────
validate_es() {
  if [[ -z "${ELASTICSEARCH_URL:-}" ]]; then
    jq -n '{"error":"ELASTICSEARCH_URL is not set. Export it: export ELASTICSEARCH_URL=https://es:9200","backend":"elasticsearch","exit_code":1}'
    exit 1
  fi

  # URL scheme validation
  if [[ ! "$ELASTICSEARCH_URL" =~ ^https?:// ]]; then
    jq -n --arg url "$ELASTICSEARCH_URL" \
      '{"error":"ELASTICSEARCH_URL must use http:// or https:// scheme","got":$url,"backend":"elasticsearch","exit_code":1}'
    exit 1
  fi

  if ! command -v curl &>/dev/null; then
    jq -n '{
      "error": "curl is required for Elasticsearch queries but not found.",
      "install": "apt install curl / brew install curl",
      "backend": "elasticsearch",
      "exit_code": 1
    }'
    exit 1
  fi
}

# ─── Helper: build curl auth headers ───────────────────────────────────────
es_curl() {
  local method="$1"
  local path="$2"
  local data="${3:-}"

  local curl_args=(-s -S --max-time 30 -X "$method")
  curl_args+=(-H "Content-Type: application/json")

  if [[ -n "${ELASTICSEARCH_TOKEN:-}" ]]; then
    # Support both "Basic xxx" and "Bearer xxx" and raw token (treated as Bearer)
    if [[ "$ELASTICSEARCH_TOKEN" =~ ^(Basic|Bearer)\ .+ ]]; then
      curl_args+=(-H "Authorization: ${ELASTICSEARCH_TOKEN}")
    else
      curl_args+=(-H "Authorization: Bearer ${ELASTICSEARCH_TOKEN}")
    fi
  fi

  local url="${ELASTICSEARCH_URL%/}${path}"

  if [[ -n "$data" ]]; then
    curl "${curl_args[@]}" -d "$data" "$url" 2>&1
  else
    curl "${curl_args[@]}" "$url" 2>&1
  fi
}

# ─── Build time-filtered query ──────────────────────────────────────────────
# Wraps user query with a time range filter
wrap_query_with_time() {
  local user_query="$1"
  local since="$2"
  local limit="$3"

  local es_since="now-${since}"

  # Try to parse user_query as JSON
  if echo "$user_query" | jq empty 2>/dev/null; then
    # User provided valid JSON — wrap it with time filter and size
    echo "$user_query" | jq \
      --arg since "$es_since" \
      --argjson limit "$limit" \
      '
      # Extract the query part
      .query as $user_q |
      {
        query: {
          bool: {
            must: (if $user_q.bool.must then $user_q.bool.must
                   elif $user_q.match then [$user_q]
                   elif $user_q.match_all then []
                   elif $user_q.bool then [$user_q]
                   else [$user_q] end),
            filter: [
              { range: { "@timestamp": { gte: $since, lte: "now" } } }
            ] + (if $user_q.bool.filter then $user_q.bool.filter else [] end)
          }
        },
        sort: [{"@timestamp": "desc"}],
        size: $limit
      }
      '
  else
    # User provided plain text — build a simple match query
    jq -n \
      --arg q "$user_query" \
      --arg since "$es_since" \
      --argjson limit "$limit" \
      '{
        query: {
          bool: {
            must: [
              { query_string: { query: $q } }
            ],
            filter: [
              { range: { "@timestamp": { gte: $since, lte: "now" } } }
            ]
          }
        },
        sort: [{"@timestamp": "desc"}],
        size: $limit
      }'
  fi
}

# ─── Search ─────────────────────────────────────────────────────────────────
search() {
  validate_es

  local query=""
  local since="1h"
  local limit="200"
  local index="_all"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --query)  query="$2"; shift 2 ;;
      --since)  since="$2"; shift 2 ;;
      --limit)  limit="$2"; shift 2 ;;
      --index)  index="$2"; shift 2 ;;
      *)        shift ;;
    esac
  done

  if [[ -z "$query" ]]; then
    jq -n '{"error":"--query is required for search","backend":"elasticsearch","exit_code":1}'
    exit 1
  fi

  # Build the full query with time range
  local full_query
  full_query=$(wrap_query_with_time "$query" "$since" "$limit")

  local response
  response=$(es_curl POST "/${index}/_search" "$full_query")

  # Check for errors
  local has_error
  has_error=$(echo "$response" | jq -r 'if .error then "yes" else "no" end' 2>/dev/null || echo "parse_error")

  if [[ "$has_error" == "yes" ]]; then
    echo "$response" | jq --arg query "$query" --arg index "$index" '{
      error: "Elasticsearch query failed",
      details: .error,
      query: $query,
      index: $index,
      backend: "elasticsearch",
      exit_code: 1
    }'
    exit 1
  elif [[ "$has_error" == "parse_error" ]]; then
    jq -n --arg resp "$response" \
      '{"error":"Failed to parse Elasticsearch response","details":$resp,"backend":"elasticsearch","exit_code":1}'
    exit 1
  fi

  # Transform ES response into our standard format
  echo "$response" | jq --arg query "$query" --arg index "$index" '{
    backend: "elasticsearch",
    query: $query,
    index: $index,
    total: .hits.total.value // .hits.total // 0,
    count: (.hits.hits | length),
    took_ms: .timed_out // false | if . then "timed_out" else null end // .took,
    entries: [
      .hits.hits[] | {
        timestamp: ._source["@timestamp"] // ._source.timestamp // null,
        index: ._index,
        id: ._id,
        source: ._source
      }
    ]
  }'
}

# ─── List indices ───────────────────────────────────────────────────────────
list_indices() {
  validate_es

  local response
  response=$(es_curl GET "/_cat/indices?format=json&h=index,health,status,docs.count,store.size&s=index")

  # Check for error
  if echo "$response" | jq empty 2>/dev/null; then
    echo "$response" | jq '{
      backend: "elasticsearch",
      indices: [
        .[] | select(.index | startswith(".") | not) | {
          name: .index,
          health: .health,
          status: .status,
          doc_count: (."docs.count" // "0"),
          size: (."store.size" // "0b")
        }
      ],
      count: ([.[] | select(.index | startswith(".") | not)] | length)
    }'
  else
    jq -n --arg resp "$response" \
      '{"error":"Failed to list indices","details":$resp,"backend":"elasticsearch","exit_code":1}'
    exit 1
  fi
}

# ─── Cluster health ────────────────────────────────────────────────────────
cluster_health() {
  validate_es

  local response
  response=$(es_curl GET "/_cluster/health")

  echo "$response" | jq '{
    backend: "elasticsearch",
    cluster: {
      name: .cluster_name,
      status: .status,
      nodes: .number_of_nodes,
      shards: .active_shards,
      pending: .relocating_shards + .initializing_shards + .unassigned_shards
    }
  }'
}

# ─── Main ───────────────────────────────────────────────────────────────────
main() {
  local command="${1:-search}"
  shift || true

  case "$command" in
    search)
      search "$@"
      ;;
    indices)
      list_indices
      ;;
    health)
      cluster_health
      ;;
    *)
      jq -n --arg cmd "$command" \
        '{"error":"Unknown Elasticsearch command: \($cmd)","backend":"elasticsearch","exit_code":1}'
      exit 1
      ;;
  esac
}

main "$@"
