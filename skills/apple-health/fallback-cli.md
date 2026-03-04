# Fallback CLI Paths (Validated on GitHub)

Use these if MCP startup is blocked by runtime issues.

## 1) `healthkit-sync` (published skill)

GitHub source:
- https://raw.githubusercontent.com/openclaw/skills/main/skills/mneves75/healthkit-sync/SKILL.md

What it gives:
- Local CLI command flow (`healthsync discover`, `healthsync scan`, `healthsync fetch`)
- Secure pairing and local-network sync patterns
- Detailed query examples for steps, heart rate, sleep, and workouts

## 2) `apple-watch` (published skill)

GitHub source:
- https://raw.githubusercontent.com/openclaw/skills/main/skills/lainnet-42/apple-watch/SKILL.md

What it gives:
- End-to-end Health Auto Export setup from iPhone to local server
- Persistent server operations and troubleshooting checklist
- Query and dashboard workflow for agent consumption

## Fallback Decision Rule

- Prefer MCP path when `@neiltron/apple-health-mcp` starts cleanly.
- If MCP fails because of runtime/native module issues, switch to a validated CLI workflow above.
- Keep the same privacy guardrails: local data first, bounded queries, explicit freshness.
