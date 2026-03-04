#!/bin/bash
# OpenClaw PII Anonymizer (Ollama phi3:mini)
# OLLAMA_URL defaults to localhost:11434; override for host (10.0.2.2:11434)

OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
MODEL="${MODEL:-phi3:mini}"
MAX_INPUT=10000

if [ ${#1} -gt $MAX_INPUT ]; then
  echo "Error: Input too long (max $MAX_INPUT chars)" >&2
  exit 1
fi

if ! curl -s --max-time 10 --fail "$OLLAMA_URL/v1/models" >/dev/null 2>&1; then
  echo "Error: Ollama unavailable at $OLLAMA_URL" >&2
  exit 1
fi

prompt_anonymize() {
  local input="$1"
  local response
  response=$(curl -s --max-time 30 --fail "$OLLAMA_URL/v1/chat/completions" \
    -H "Content-Type: application/json" \
    -d "{
      \"model\": \"$MODEL\",
      \"messages\": [
        {\"role\": \"system\", \"content\": \"Anonymize PII only: Replace names/emails/paths/IPs/phones/SSNs/URLs/companies with [PERSON], [EMAIL], [PATH], [IP], [PHONE], [SSN], [URL], [ORG]. Keep all else verbatim. No hallucinations, additions, or changes to structure. Output only the cleaned text.\"},
        {\"role\": \"user\", \"content\": \"$input\"}
      ],
      \"stream\": false,
      \"options\": {\"temperature\": 0.1}
    }") || {
    echo "Error: Curl failed" >&2
    exit 1
  }

  echo "$response" | jq -r '.choices[0].message.content // empty' | tr -d '\n\r' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' || {
    echo "Error: jq parse failed" >&2
    exit 1
  }
}

if [ $# -eq 0 ]; then
  echo "Usage: $0 'your raw text'"
  exit 1
fi

prompt_anonymize "$1"
