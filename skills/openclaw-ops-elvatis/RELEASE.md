# Release / QA (Human-in-the-loop)

## Goals

- Never publish broken plugins.
- Never cause gateway freezes/crashes for end users.
- GitHub is source control. **ClawHub is distribution** (publish only when the repo is complete + verified working).

## Staging Gateway (where we test first)

- **Gateway profile:** `staging`
- **Machine / host:** this same machine (single-host setup)
- **Profile state dir:** `~/.openclaw-staging/`
- **How to start/use:**
  - `openclaw --profile staging gateway start`
  - Install plugin locally into that profile and verify:
    - `openclaw --profile staging plugins install -l ~/.openclaw/workspace/<plugin-repo>`
    - `openclaw --profile staging gateway restart`
    - `openclaw --profile staging status`

(If you prefer a different staging setup: separate VM/container, different workspace, etc., write it here.)

## Staging smoke tests (mandatory)

For **every** `openclaw-*` repo before rollout:

- Install into staging profile: `openclaw --profile staging plugins install -l ~/.openclaw/workspace/<repo>`
- Restart staging gateway: `openclaw --profile staging gateway restart`
- Health check: `openclaw --profile staging status`
- Run one smoke command/tool call if the plugin exposes one

Document results (and any failures) before asking for GO.

## “Go” checklist (what the human approves)

Before publishing to ClawHub, the human checks:

1) **Repo is complete**
- README includes install/config + tool list
- Plugin loads without crashing the gateway

2) **Tests / sanity checks are green**
- build/typecheck (where applicable)
- unit tests (where applicable)
- smoke test on staging gateway (install + restart + basic tool call)

3) **Risk control**
- No destructive/default-on operations
- Dangerous tools are gated (readOnly/allowlist where relevant)

When all checks pass, human says: **GO: publish**

## Publish flow (after GO)

1) Tag/release in GitHub (if used)
2) Publish to ClawHub (`clawhub publish ...`) **only after** staging is green

