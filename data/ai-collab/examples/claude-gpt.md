# Example: Claude ↔ GPT

Claude Code as primary, GPT as background verifier/reviewer.

## Agent A: Claude (Primary)
- **Runtime**: `claude code`
- **Role**: Research, implementation, file writes
- **Sends to B via**: `send.sh "[TASK:review] Review this code: ..."`

## Agent B: GPT (Daemon)
- **Runtime**: Custom daemon using OpenAI API
- **Model**: `gpt-4o-mini` (fast, cheap for background)
- **Role**: Code review, fact-checking, alternative approaches

## Agent B Setup (GPT daemon)

Replace the `claude --print` call in `daemon.sh` with:

```bash
RESPONSE=$(python3 -c "
import os, sys
from openai import OpenAI
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

msg = sys.stdin.read()
result = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {'role': 'system', 'content': 'You are Agent B, an AI collaborator. Use [DONE:name] and [BLOCKED:name] tags. Keep responses under 100 words.'},
        {'role': 'user', 'content': msg}
    ],
    max_tokens=200
)
print(result.choices[0].message.content)
" <<< "$MSG")
```

## Environment Variables
```bash
OPENAI_API_KEY=sk-...
AGENT_B_MODEL=gpt-4o-mini
```

## Best Use Cases
- Claude builds → GPT reviews (cross-model consistency check)
- Claude researches → GPT summarizes into different format
- Claude writes code → GPT spots bugs from a different training perspective

## Cost Estimate
- GPT-4o-mini: ~$0.00015/1K input tokens, ~$0.0006/1K output
- 100 messages/day × 200 tokens avg = ~$0.015/day ≈ $0.45/month
