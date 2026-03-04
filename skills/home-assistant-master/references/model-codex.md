# Model Notes — Codex-style Agents

Use concise, tool-first execution with explicit state checks.

## Style
- Lead with action/result.
- Keep explanations short unless asked.
- Use deterministic checklists.

## Recommended pattern
1. State current observed status.
2. Propose one safe next step.
3. If write requested, show exact affected entities/services and ask approval.
4. Verify post-change state.

## Prompting hints
- Prefer structured bullets over long prose.
- Include exact paths/URLs/entity ids when available.
- Keep fallback plans minimal and practical.
