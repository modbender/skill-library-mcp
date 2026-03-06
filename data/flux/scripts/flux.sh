#!/usr/bin/env bash
# Flux CLI helper

FLUX_URL="${FLUX_URL:-https://api.flux-universe.com}"
FLUX_TOKEN="${FLUX_TOKEN:-}"
FLUX_ADMIN_TOKEN="${FLUX_ADMIN_TOKEN:-}"

# Helper function for API calls
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    local auth_header=""

    if [[ -n "$FLUX_TOKEN" ]]; then
        auth_header="-H \"Authorization: Bearer ${FLUX_TOKEN}\""
    fi

    local -a cmd=(curl -s -X "$method" "${FLUX_URL}${endpoint}" -H "Content-Type: application/json")

    if [[ -n "$FLUX_TOKEN" ]]; then
        cmd+=(-H "Authorization: Bearer ${FLUX_TOKEN}")
    fi

    if [[ -n "$data" ]]; then
        cmd+=(-d "$data")
    fi

    "${cmd[@]}"
}

# Format JSON output (pretty print if jq available)
format_output() {
    if command -v jq &> /dev/null; then
        jq '.'
    else
        python3 -m json.tool 2>/dev/null || cat
    fi
}

# Commands
case "${1:-}" in
    publish)
        stream="$2"
        source="$3"
        entity_id="$4"
        properties="$5"

        if [[ -z "$stream" || -z "$source" || -z "$entity_id" || -z "$properties" ]]; then
            echo "Usage: flux.sh publish STREAM SOURCE ENTITY_ID PROPERTIES_JSON"
            echo ""
            echo "Example:"
            echo "  flux.sh publish sensors agent-01 temp-sensor-01 '{\"temperature\":22.5}'"
            exit 1
        fi

        timestamp=$(date +%s)000  # Unix epoch milliseconds

        payload=$(cat <<EOF
{
  "entity_id": "${entity_id}",
  "properties": ${properties}
}
EOF
)

        event=$(cat <<EOF
{
  "stream": "${stream}",
  "source": "${source}",
  "timestamp": ${timestamp},
  "payload": ${payload}
}
EOF
)

        echo "Publishing event to Flux..."
        api_call POST "/api/events" "$event" | format_output
        ;;

    batch)
        events="$2"

        if [[ -z "$events" ]]; then
            echo "Usage: flux.sh batch EVENTS_JSON_ARRAY"
            exit 1
        fi

        batch_payload="{\"events\": ${events}}"
        echo "Publishing batch to Flux..."
        api_call POST "/api/events/batch" "$batch_payload" | format_output
        ;;

    get)
        entity_id="$2"

        if [[ -z "$entity_id" ]]; then
            echo "Usage: flux.sh get ENTITY_ID"
            exit 1
        fi

        # URL-encode slashes in entity_id
        encoded_id=$(echo "$entity_id" | sed 's|/|%2F|g')
        api_call GET "/api/state/entities/${encoded_id}" | format_output
        ;;

    list)
        query=""
        if [[ "$2" == "--prefix" && -n "$3" ]]; then
            query="?prefix=$3"
        elif [[ "$2" == "--namespace" && -n "$3" ]]; then
            query="?namespace=$3"
        fi
        api_call GET "/api/state/entities${query}" | format_output
        ;;

    delete)
        entity_id="$2"

        if [[ -z "$entity_id" ]]; then
            echo "Usage: flux.sh delete ENTITY_ID"
            exit 1
        fi

        encoded_id=$(echo "$entity_id" | sed 's|/|%2F|g')
        echo "Deleting entity ${entity_id}..."
        api_call DELETE "/api/state/entities/${encoded_id}" | format_output
        ;;

    batch-delete)
        filter="$2"

        if [[ -z "$filter" ]]; then
            echo "Usage: flux.sh batch-delete FILTER_JSON"
            echo ""
            echo "Examples:"
            echo '  flux.sh batch-delete '"'"'{"prefix":"loadtest-"}'"'"
            echo '  flux.sh batch-delete '"'"'{"namespace":"matt"}'"'"
            echo '  flux.sh batch-delete '"'"'{"entity_ids":["id1","id2"]}'"'"
            exit 1
        fi

        echo "Batch deleting entities..."
        api_call POST "/api/state/entities/delete" "$filter" | format_output
        ;;

    connectors)
        api_call GET "/api/connectors" | format_output
        ;;

    admin-config)
        if [[ -n "$2" ]]; then
            # Update config
            if [[ -z "$FLUX_ADMIN_TOKEN" ]]; then
                echo "Error: FLUX_ADMIN_TOKEN not set"
                exit 1
            fi
            curl -s -X PUT "${FLUX_URL}/api/admin/config" \
                -H "Content-Type: application/json" \
                -H "Authorization: Bearer ${FLUX_ADMIN_TOKEN}" \
                -d "$2" | format_output
        else
            # Read config
            api_call GET "/api/admin/config" | format_output
        fi
        ;;

    health)
        echo "Testing Flux connection at ${FLUX_URL}..."
        response=$(api_call GET "/api/state/entities")

        if [[ $? -eq 0 && -n "$response" ]]; then
            echo "✓ Flux is reachable"
            entity_count=$(echo "$response" | python3 -c "import sys,json;print(len(json.load(sys.stdin)))" 2>/dev/null || echo "?")
            echo "  Entities in state: ${entity_count}"
        else
            echo "✗ Failed to reach Flux at ${FLUX_URL}"
            exit 1
        fi
        ;;

    *)
        echo "Flux CLI - Interact with Flux state engine"
        echo ""
        echo "Usage: flux.sh COMMAND [ARGS]"
        echo ""
        echo "Commands:"
        echo "  publish STREAM SOURCE ENTITY_ID PROPERTIES_JSON"
        echo "      Publish event to create/update entity"
        echo ""
        echo "  get ENTITY_ID"
        echo "      Query current state of entity"
        echo ""
        echo "  list [--prefix PREFIX] [--namespace NS]"
        echo "      List all entities (optional filter)"
        echo ""
        echo "  delete ENTITY_ID"
        echo "      Delete a single entity"
        echo ""
        echo "  batch-delete FILTER_JSON"
        echo "      Batch delete by prefix/namespace/IDs"
        echo ""
        echo "  batch EVENTS_JSON_ARRAY"
        echo "      Publish multiple events at once"
        echo ""
        echo "  connectors"
        echo "      List connector status"
        echo ""
        echo "  admin-config [UPDATE_JSON]"
        echo "      Read or update runtime config"
        echo ""
        echo "  health"
        echo "      Test connection to Flux"
        echo ""
        echo "Environment:"
        echo "  FLUX_URL=${FLUX_URL}"
        echo "  FLUX_TOKEN=(auth token for write operations)"
        echo "  FLUX_ADMIN_TOKEN=(admin token for config updates)"
        exit 1
        ;;
esac
