#!/usr/bin/env bash
set -euo pipefail

# Meeting Notes Summarizer
# Reads transcript from stdin, outputs structured summary

if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "Error: ANTHROPIC_API_KEY environment variable not set" >&2
  exit 1
fi

# Read stdin
TRANSCRIPT=$(cat)

if [ -z "$TRANSCRIPT" ]; then
  echo "Error: No input. Pipe a meeting transcript via stdin." >&2
  echo "Usage: cat transcript.txt | ./summarize.sh" >&2
  exit 1
fi

# Escape for JSON
ESCAPED=$(printf '%s' "$TRANSCRIPT" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')

PROMPT="You are a meeting notes summarizer. Given the following raw meeting transcript, produce a structured summary in markdown with exactly these sections:\n\n## Summary\n(Exactly 3 sentences capturing the essence of the meeting)\n\n## Key Decisions\n(Bulleted list of decisions made)\n\n## Action Items\n(Bulleted list, each with: task, owner in **bold**, and deadline if mentioned)\n\n## Follow-up Dates\n(Bulleted list of any dates, deadlines, or scheduled follow-ups mentioned)\n\nBe concise and precise. Only include what was actually discussed.\n\nTRANSCRIPT:\n"

# Build full message content as proper JSON string
FULL_CONTENT=$(python3 -c "
import sys, json
prompt = '''$PROMPT'''
transcript = json.loads($ESCAPED)
print(json.dumps(prompt + transcript))
")

RESPONSE=$(curl -s https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d "{
    \"model\": \"claude-sonnet-4-20250514\",
    \"max_tokens\": 1500,
    \"messages\": [{
      \"role\": \"user\",
      \"content\": $FULL_CONTENT
    }]
  }" 2>/dev/null)

# Extract text from response
echo "$RESPONSE" | python3 -c "
import sys, json
try:
    r = json.load(sys.stdin)
    if 'content' in r and len(r['content']) > 0:
        print(r['content'][0]['text'])
    elif 'error' in r:
        print(f\"API Error: {r['error']['message']}\", file=sys.stderr)
        sys.exit(1)
    else:
        print('Unexpected response format', file=sys.stderr)
        sys.exit(1)
except Exception as e:
    print(f'Parse error: {e}', file=sys.stderr)
    sys.exit(1)
"
