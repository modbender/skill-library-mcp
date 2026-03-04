#!/bin/bash
# Pollinations Chat Completions
# Usage: ./chat.sh "message" [--model model] [--temp N] [--max N] [--system "prompt"] [--json] [--seed N]

PROMPT="$1"
shift || true

# Defaults
MODEL="${MODEL:-openai}"
TEMPERATURE="${TEMPERATURE:-}"
MAX_TOKENS="${MAX_TOKENS:-}"
TOP_P="${TOP_P:-}"
SEED="${SEED:-}"
SYSTEM_PROMPT="${SYSTEM_PROMPT:-}"
JSON_MODE=""
REASONING_EFFORT=""
THINKING_BUDGET=""

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      MODEL="$2"
      shift 2
      ;;
    --temp|--temperature)
      TEMPERATURE="$2"
      shift 2
      ;;
    --max|--max-tokens)
      MAX_TOKENS="$2"
      shift 2
      ;;
    --top-p)
      TOP_P="$2"
      shift 2
      ;;
    --seed)
      SEED="$2"
      shift 2
      ;;
    --system)
      SYSTEM_PROMPT="$2"
      shift 2
      ;;
    --json)
      JSON_MODE="true"
      shift
      ;;
    --reasoning-effort)
      REASONING_EFFORT="$2"
      shift 2
      ;;
    --thinking-budget)
      THINKING_BUDGET="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

if [[ -z "$PROMPT" ]]; then
  echo "Usage: chat.sh \"message\" [options]"
  echo ""
  echo "Options:"
  echo "  --model MODEL          Model (default: openai)"
  echo "  --temp N               Temperature 0-2 (default: 1)"
  echo "  --max-tokens N         Max response tokens"
  echo "  --top-p N              Nucleus sampling 0-1"
  echo "  --seed N               Seed for reproducibility (-1 = random)"
  echo "  --system \"PROMPT\"      System prompt"
  echo "  --json                 Force JSON response format"
  echo "  --reasoning-effort LVL For o1/o3/R1: high/medium/low/minimal/none"
  echo "  --thinking-budget N    Token budget for reasoning models"
  exit 1
fi

# Build messages array
if [[ -n "$SYSTEM_PROMPT" ]]; then
  MESSAGES=$(jq -n -c \
    --arg system "$SYSTEM_PROMPT" \
    --arg prompt "$PROMPT" \
    '[{role: "system", content: $system}, {role: "user", content: $prompt}]')
else
  MESSAGES=$(jq -n -c \
    --arg prompt "$PROMPT" \
    '[{role: "user", content: $prompt}]')
fi

# Build request body
BODY=$(jq -n -c \
  --arg model "$MODEL" \
  --argjson messages "$MESSAGES" \
  '{model: $model, messages: $messages}')

# Add optional parameters
if [[ -n "$TEMPERATURE" ]]; then
  BODY=$(echo "$BODY" | jq -c --arg v "$TEMPERATURE" '. + {temperature: ($v | tonumber)}')
fi
if [[ -n "$MAX_TOKENS" ]]; then
  BODY=$(echo "$BODY" | jq -c --arg v "$MAX_TOKENS" '. + {max_tokens: ($v | tonumber)}')
fi
if [[ -n "$TOP_P" ]]; then
  BODY=$(echo "$BODY" | jq -c --arg v "$TOP_P" '. + {top_p: ($v | tonumber)}')
fi
if [[ -n "$SEED" ]]; then
  BODY=$(echo "$BODY" | jq -c --arg v "$SEED" '. + {seed: ($v | tonumber)}')
fi
if [[ -n "$JSON_MODE" ]]; then
  BODY=$(echo "$BODY" | jq -c '. + {jsonMode: true}')
fi
if [[ -n "$REASONING_EFFORT" ]]; then
  BODY=$(echo "$BODY" | jq -c --arg v "$REASONING_EFFORT" '. + {reasoning_effort: $v}')
fi
if [[ -n "$THINKING_BUDGET" ]]; then
  BODY=$(echo "$BODY" | jq -c --arg v "$THINKING_BUDGET" '. + {thinking_budget: ($v | tonumber)}')
fi

# Make request
URL="https://gen.pollinations.ai/v1/chat/completions"

RESPONSE=$(curl -s -H "Content-Type: application/json" \
  ${POLLINATIONS_API_KEY:+-H "Authorization: Bearer $POLLINATIONS_API_KEY"} \
  -X POST "$URL" -d "$BODY")

# Extract and output result
RESULT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content // empty')

if [[ -n "$RESULT" ]]; then
  echo "$RESULT"
else
  echo "Error: No response received"
  echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
  exit 1
fi
