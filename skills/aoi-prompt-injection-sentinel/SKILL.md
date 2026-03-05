# AOI Prompt Injection Sentinel

S-DNA: `AOI-2026-0215-SDNA-PG01`

## What this is
A lightweight, **public-safe** prompt-injection detector that scores input text and outputs:
- `severity` (0–4)
- `action` (allow/log/warn/block)
- `reasons` + matched rule ids

## What this is NOT
- No webhook, no outbound calls, no auto-posting.
- No secret handling.

## Usage
### Analyze text (argument)
```bash
node skill.js analyze --text="..."
```

### Analyze stdin
```bash
echo "..." | node skill.js analyze --stdin=true
```

## Output
JSON to stdout.

## Release governance (public)
We publish AOI skills for free and keep improving them. Every release must pass our Security Gate and include an auditable changelog. We do not ship updates that weaken security or licensing clarity. Repeated violations trigger progressive restrictions (warnings → publish pause → archive).

## Support
- Issues / bugs / requests: https://github.com/edmonddantesj/aoi-skills/issues
- Please include the skill slug: `aoi-prompt-injection-sentinel`

## Links
- ClawHub: https://clawhub.com/skills/aoi-prompt-injection-sentinel

## License
MIT (AOI original).
