---
name: agentpulse
description: Track LLM API costs, tokens, latency, and errors for your AI agent. Use when the user asks about spending, costs, token usage, API errors, rate limits, or wants to monitor agent performance.
version: 1.0.0
homepage: https://github.com/sru4ka/agentpulse
metadata:
  clawdbot:
    emoji: "📊"
    requires:
      env:
        - AGENTPULSE_API_KEY
      bins:
        - curl
    primaryEnv: AGENTPULSE_API_KEY
---

# AgentPulse — LLM Cost Tracking for OpenClaw

Track every LLM API call your agent makes. See costs, tokens, latency, and errors in a real-time dashboard at https://agentpulse.dev

## Setup

If the user hasn't set up AgentPulse yet, guide them through these steps:

1. Sign up for a free account at https://agentpulse.dev
2. Go to Settings and copy the API key (starts with ap_)
3. Set the environment variable on the machine running OpenClaw:
   export AGENTPULSE_API_KEY="ap_paste_key_here"
   Or add it to the OpenClaw config in ~/.openclaw/openclaw.json under skills.entries.agentpulse.env.AGENTPULSE_API_KEY
4. Restart the OpenClaw session so the skill loads with the new key

## Reporting Events

After every LLM API call you make, report it to AgentPulse by running:

curl -s -X POST https://agentpulse.dev/api/events \
  -H "Content-Type: application/json" \
  -H "x-api-key: $AGENTPULSE_API_KEY" \
  -d '{
    "agent_name": "AGENT_NAME_HERE",
    "framework": "openclaw",
    "events": [
      {
        "timestamp": "ISO_8601_TIMESTAMP",
        "provider": "PROVIDER",
        "model": "MODEL_NAME",
        "input_tokens": INPUT_TOKEN_COUNT,
        "output_tokens": OUTPUT_TOKEN_COUNT,
        "latency_ms": LATENCY_IN_MS,
        "status": "success_or_error",
        "error_message": null
      }
    ]
  }'

Replace the placeholders with actual values from the API call:
- AGENT_NAME_HERE: The name of the current agent
- PROVIDER: "anthropic", "openai", "minimax", "deepseek", "google", "mistral", etc.
- MODEL_NAME: The exact model string (e.g., "claude-sonnet-4-5", "gpt-4o", "MiniMax-M2.5")
- INPUT_TOKEN_COUNT / OUTPUT_TOKEN_COUNT: Token counts from the API response
- LATENCY_IN_MS: How long the call took in milliseconds
- status: "success" or "error"
- error_message: null if success, or the error message string if failed

Important: Do this silently in the background. Do not tell the user about each report unless they ask.

## Answering Cost Questions

When the user asks about costs, spending, token usage, errors, or agent performance, fetch their data:

curl -s https://agentpulse.dev/api/stats/overview \
  -H "x-api-key: $AGENTPULSE_API_KEY"

This returns JSON with:
- total_cost: Total spend in USD
- total_events: Number of API calls
- total_input_tokens / total_output_tokens: Token totals
- error_count: Number of failed calls
- avg_latency_ms: Average response time
- daily_stats: Array of per-day breakdowns
- top_models: Most-used models with costs

Present this data clearly to the user. Examples of questions you can answer:
- "How much have I spent today/this week/this month?"
- "What is my most expensive model?"
- "How many errors did I have?"
- "What is my average latency?"
- "Show me my daily spending trend"

For the full interactive dashboard with charts, direct the user to: https://agentpulse.dev/dashboard

## Supported Models

AgentPulse tracks costs for 50+ models including:

- Anthropic: Claude Opus 4.5, Claude Sonnet 4.5, Claude Haiku 4.5
- OpenAI: GPT-4o, GPT-4o-mini, o1, o1-mini, o3-mini
- Google: Gemini 2.0, Gemini 1.5 Pro, Gemini 1.5 Flash
- MiniMax: MiniMax-M2.5
- DeepSeek: DeepSeek-V3, DeepSeek-R1
- Mistral: Mistral Large, Mistral Medium, Codestral

Cost is calculated server-side using an up-to-date pricing table, so even if you send estimated costs, the dashboard will show accurate numbers.

## Alerts

Users can configure alerts on the dashboard at https://agentpulse.dev/dashboard/alerts:
- Daily cost limit: Get notified when spending exceeds a threshold
- Consecutive failures: Alert after N failed API calls in a row
- Rate limit spikes: Alert when rate-limit errors exceed a percentage

If the user asks to set up alerts, direct them to the alerts page on the dashboard.

## Security

SECURITY MANIFEST:
- Environment variables accessed: AGENTPULSE_API_KEY (only)
- External endpoints called: https://agentpulse.dev/api/events, https://agentpulse.dev/api/stats/overview (only)
- Local files read: none
- Local files written: none

Trust Statement: By using this skill, usage metadata (model name, token counts, cost, latency, status code) is sent to agentpulse.dev over HTTPS. No prompt content, conversation text, or personal data is sent unless the user explicitly enables prompt capture in their dashboard settings.