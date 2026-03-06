#!/bin/bash
#
# Perplexity API client for web search and Q&A (Security-Hardened Edition)
#
# Fixes over the original perplexity-bash:
#   1. User input passed via env vars to Python, never interpolated into code
#   2. Strict input validation (model allowlist, numeric ranges, context values)
#   3. API key passed via stdin to curl (not visible in process list)
#   4. Query length limit to prevent denial-of-wallet
#

set -euo pipefail

# Configuration
PERPLEXITY_API_URL="https://api.perplexity.ai/chat/completions"

# Allowed models (allowlist)
ALLOWED_MODELS=("sonar" "sonar-pro" "sonar-reasoning" "sonar-reasoning-pro")

# Defaults
MODEL="sonar"
MAX_TOKENS=4096
TEMPERATURE="0.0"
SEARCH_CONTEXT="medium"
FORMAT="text"
SYSTEM_PROMPT=""
MAX_QUERY_LENGTH=8000

# --- Validation helpers ---

is_allowed_model() {
    local model="$1"
    for m in "${ALLOWED_MODELS[@]}"; do
        if [[ "$model" == "$m" ]]; then
            return 0
        fi
    done
    return 1
}

is_positive_integer() {
    [[ "$1" =~ ^[0-9]+$ ]] && [[ "$1" -gt 0 ]]
}

is_valid_temperature() {
    # Accept 0, 0.0, 0.5, 1, 1.0, etc. — must be between 0.0 and 1.0
    if [[ ! "$1" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
        return 1
    fi
    python3 -c "import sys; t=float(sys.argv[1]); sys.exit(0 if 0.0 <= t <= 1.0 else 1)" "$1" 2>/dev/null
}

is_valid_context() {
    [[ "$1" == "low" || "$1" == "medium" || "$1" == "high" ]]
}

is_valid_format() {
    [[ "$1" == "text" || "$1" == "markdown" || "$1" == "json" ]]
}

# --- Argument parsing ---

while [[ $# -gt 0 ]]; do
    case $1 in
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -t|--max-tokens)
            MAX_TOKENS="$2"
            shift 2
            ;;
        --temperature)
            TEMPERATURE="$2"
            shift 2
            ;;
        -c|--context)
            SEARCH_CONTEXT="$2"
            shift 2
            ;;
        -s|--system)
            SYSTEM_PROMPT="$2"
            shift 2
            ;;
        -f|--format)
            FORMAT="$2"
            shift 2
            ;;
        --list-models)
            echo "Available Perplexity Models:"
            echo ""
            for m in "${ALLOWED_MODELS[@]}"; do
                echo "  $m"
            done
            exit 0
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS] QUERY"
            echo ""
            echo "Options:"
            echo "  -m, --model MODEL        Model (default: sonar)"
            echo "  -t, --max-tokens NUM     Max tokens 1-4096 (default: 4096)"
            echo "  --temperature NUM        Temperature 0.0-1.0 (default: 0.0)"
            echo "  -c, --context SIZE       Search context: low/medium/high (default: medium)"
            echo "  -s, --system PROMPT      System prompt"
            echo "  -f, --format FORMAT      Output: text/markdown/json (default: text)"
            echo "  --list-models            List available models"
            echo "  -h, --help               Show this help"
            echo ""
            echo "Examples:"
            echo "  $0 \"What is the capital of Germany?\""
            echo "  $0 -m sonar-pro -f markdown \"Latest AI news\""
            exit 0
            ;;
        -*)
            echo "Error: Unknown option: $1" >&2
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

# --- Input validation ---

if ! is_allowed_model "$MODEL"; then
    echo "Error: Invalid model '$MODEL'." >&2
    echo "Allowed models: ${ALLOWED_MODELS[*]}" >&2
    exit 1
fi

if ! is_positive_integer "$MAX_TOKENS" || [[ "$MAX_TOKENS" -gt 4096 ]]; then
    echo "Error: --max-tokens must be an integer between 1 and 4096." >&2
    exit 1
fi

if ! is_valid_temperature "$TEMPERATURE"; then
    echo "Error: --temperature must be a number between 0.0 and 1.0." >&2
    exit 1
fi

if ! is_valid_context "$SEARCH_CONTEXT"; then
    echo "Error: --context must be one of: low, medium, high." >&2
    exit 1
fi

if ! is_valid_format "$FORMAT"; then
    echo "Error: --format must be one of: text, markdown, json." >&2
    exit 1
fi

if [[ $# -eq 0 ]]; then
    echo "Error: No query provided." >&2
    echo "Use -h or --help for usage information." >&2
    exit 1
fi

QUERY="$*"

if [[ ${#QUERY} -gt $MAX_QUERY_LENGTH ]]; then
    echo "Error: Query too long (${#QUERY} chars). Maximum is $MAX_QUERY_LENGTH characters." >&2
    exit 1
fi

# --- API key retrieval ---

get_api_key() {
    # 1. Try skill-specific config file
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local config_file="$script_dir/../config.json"

    if [[ -f "$config_file" ]]; then
        local config_key
        # Safe: read file contents via Python without interpolation
        config_key=$(python3 -c "
import json, sys
try:
    with open(sys.argv[1]) as f:
        print(json.load(f).get('apiKey', ''))
except Exception:
    print('')
" "$config_file" 2>/dev/null || echo "")
        if [[ -n "$config_key" ]]; then
            echo "$config_key"
            return
        fi
    fi

    # 2. Try environment variable
    if [[ -n "${PERPLEXITY_API_KEY:-}" ]]; then
        echo "$PERPLEXITY_API_KEY"
        return
    fi

    echo ""
}

API_KEY=$(get_api_key)

if [[ -z "$API_KEY" ]]; then
    echo "Error: No API key found." >&2
    echo "" >&2
    echo "Set one of the following:" >&2
    echo "  1. Create config.json in the skill directory with: {\"apiKey\": \"pplx-...\"}" >&2
    echo "  2. Environment variable: export PERPLEXITY_API_KEY='your-key-here'" >&2
    exit 1
fi

# --- Build JSON body safely ---
# SECURITY: All user-controlled values are passed via environment variables,
# never interpolated into Python source code.

BODY=$(
    PPLX_QUERY="$QUERY" \
    PPLX_SYSTEM_PROMPT="$SYSTEM_PROMPT" \
    PPLX_MODEL="$MODEL" \
    PPLX_MAX_TOKENS="$MAX_TOKENS" \
    PPLX_TEMPERATURE="$TEMPERATURE" \
    PPLX_SEARCH_CONTEXT="$SEARCH_CONTEXT" \
    python3 -c '
import json, os

query = os.environ["PPLX_QUERY"]
system_prompt = os.environ.get("PPLX_SYSTEM_PROMPT", "")
model = os.environ["PPLX_MODEL"]
max_tokens = int(os.environ["PPLX_MAX_TOKENS"])
temperature = float(os.environ["PPLX_TEMPERATURE"])
search_context = os.environ["PPLX_SEARCH_CONTEXT"]

messages = []
if system_prompt:
    messages.append({"role": "system", "content": system_prompt})
messages.append({"role": "user", "content": query})

body = {
    "model": model,
    "messages": messages,
    "max_tokens": max_tokens,
    "temperature": temperature,
    "stream": False,
}

if model.startswith("sonar"):
    body["search_context_size"] = search_context

print(json.dumps(body))
'
)

# --- Make API request ---
# SECURITY: Both the request body and the Authorization header are passed via
# file descriptors / stdin, so neither appears in process listings (ps aux).
# We write curl config to a temp file (mode 600) containing the auth header,
# then pass the body via --data @<fd>.

CURL_CONFIG_FILE=$(mktemp)
chmod 600 "$CURL_CONFIG_FILE"
trap 'rm -f "$CURL_CONFIG_FILE"' EXIT

cat > "$CURL_CONFIG_FILE" <<EOF
-H "Authorization: Bearer $API_KEY"
EOF

RESPONSE=$(
    curl -s -X POST "$PERPLEXITY_API_URL" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -K "$CURL_CONFIG_FILE" \
        --data @- <<< "$BODY"
)

rm -f "$CURL_CONFIG_FILE"

# --- Parse and output response ---

parse_response() {
    local response="$1"
    local format="$2"

    # Check if the response contains valid choices
    if ! echo "$response" | python3 -c "import json, sys; data = json.load(sys.stdin); sys.exit(0 if 'choices' in data else 1)" 2>/dev/null; then
        local error_msg
        error_msg=$(echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get('error', {}).get('message', 'Unknown API error'))
except Exception:
    print('Failed to parse API response')
" 2>/dev/null || echo "Unknown error")
        echo "Error: $error_msg" >&2
        return 1
    fi

    case "$format" in
        json)
            echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
            ;;
        markdown|text)
            local content
            content=$(echo "$response" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(data['choices'][0]['message']['content'])
")
            echo "$content"

            # Extract and display citations
            local citations
            citations=$(echo "$response" | python3 -c "
import json, sys
data = json.load(sys.stdin)
urls = data.get('citations', [])
if urls:
    for i, url in enumerate(urls, 1):
        print(f'{i}. {url}')
" 2>/dev/null || true)

            if [[ -n "$citations" ]]; then
                echo ""
                if [[ "$format" == "markdown" ]]; then
                    echo "### Sources:"
                else
                    echo "Sources:"
                fi
                echo "$citations"
            fi
            ;;
    esac
}

parse_response "$RESPONSE" "$FORMAT"
