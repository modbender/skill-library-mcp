# Release Watch (Free-model friendly)

Goal: track Home Assistant and integration changes continuously with low cost.

## Sources to monitor
- Home Assistant release notes: https://www.home-assistant.io/blog/
- Breaking changes section (monthly release posts)
- Core docs changelog pages when available
- Key integration repos used in this environment (HACS/custom integrations)

## Weekly routine
1. Collect new releases/notes.
2. Extract: breaking changes, deprecations, migration actions.
3. Map impact to local setup (integrations, automations, dashboards).
4. Produce a short action memo: `none | low | medium | urgent`.

## Agent behavior
- Use free model for first-pass summarization/classification.
- Escalate to stronger model only for ambiguous/high-risk items.
- Never auto-apply changes; recommend and ask approval.
