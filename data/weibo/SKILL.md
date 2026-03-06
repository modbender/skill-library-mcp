---
name: weibo
description: Use Weibo Open Platform for OAuth2 authentication, timeline retrieval, topic search, and structured social sentiment collection. Trigger this skill when tasks involve Weibo API calls, token setup, endpoint debugging, or Chinese social trend monitoring through the official Weibo API.
metadata: {"openclaw":{"skillKey":"weibo","homepage":"https://open.weibo.com/","requires":{"bins":["bash","curl","python3"],"env":["WEIBO_APP_KEY","WEIBO_APP_SECRET","WEIBO_REDIRECT_URI"]},"primaryEnv":"WEIBO_APP_SECRET"}}
---

# Weibo

Use this skill to collect Weibo signals with reproducible Weibo Open Platform API calls and CLI automation.

## Quick Start

1. Review [references/api_guide.md](references/api_guide.md) for current official endpoints and constraints.
2. Provide credentials through OpenClaw skill config or secure environment injection.
3. Generate an authorization URL:
`bash scripts/weibo_cli.sh oauth-authorize-url`
4. Exchange `code` for a token:
`bash scripts/weibo_cli.sh oauth-access-token --code "<code>"`
5. Call endpoints:
`bash scripts/weibo_cli.sh public-timeline --count 20`

## Primary Interface

Use the Bash CLI first:
- `scripts/weibo_cli.sh`: OAuth2 + direct API command interface, optimized for agentic runs.

Optional companion skill:
- `weibo-brave-search`: separate fallback skill for `site:weibo.com` search through Brave Search API.

## Recommended Workflow

1. Validate provider requirements in [references/api_guide.md](references/api_guide.md).
2. Run `oauth-authorize-url`, open URL, capture `code`.
3. Run `oauth-access-token --code ...` and store token securely.
4. Use endpoint helpers (`public-timeline`, `user-timeline`, `search-topics`) or `call`.
5. If API access is blocked and you explicitly want a separate commercial fallback, use the `weibo-brave-search` skill instead of this one.

## CLI Command Surface

- `oauth-authorize-url`
- `oauth-access-token --code <code>`
- `oauth-token-info`
- `public-timeline [--count N] [--page N]`
- `user-timeline --uid <uid> [--count N]`
- `search-topics --q <query>`
- `call --method GET --path /2/... --param key=value`

Run `bash scripts/weibo_cli.sh --help` for details.

## Credentials And Secret Handling

Credential classes:

| Variable | Required | Sensitive | Used for |
| --- | --- | --- | --- |
| `WEIBO_APP_KEY` | Yes | No | OAuth client identifier |
| `WEIBO_APP_SECRET` | Yes | Yes | OAuth token exchange |
| `WEIBO_REDIRECT_URI` | Yes | No | OAuth callback |
| `WEIBO_ACCESS_TOKEN` | Optional | Yes | Authenticated API calls after token issuance |

OpenClaw configuration guidance:

1. Set `skills.entries.weibo.apiKey` to a `SecretRef` or plaintext value only for `WEIBO_APP_SECRET`, because this skill declares `WEIBO_APP_SECRET` as its `primaryEnv`.
2. Set `skills.entries.weibo.env.WEIBO_APP_KEY` and `skills.entries.weibo.env.WEIBO_REDIRECT_URI` as regular env config.
3. If you want pre-issued token flows, set `skills.entries.weibo.env.WEIBO_ACCESS_TOKEN` from your external secret manager or deployment environment.

Warnings:

- `WEIBO_APP_SECRET` and `WEIBO_ACCESS_TOKEN` are sensitive and must not be committed.
- OpenClaw's documented `SecretRef` audit path covers `skills.entries.<skillKey>.apiKey`; it does not give the same visibility for arbitrary ad hoc env vars.
- If you inject `WEIBO_ACCESS_TOKEN` through plain environment variables, store it in your external secrets manager or deployment environment and do not treat it as registry-managed unless you have configured it that way intentionally.
- This skill makes network calls to `https://api.weibo.com`.

## Notes

- Prefer JSON output for downstream automation.
- Keep requests minimal and paginated to reduce rate-limit pressure.
- Use the official docs linked in [references/api_guide.md](references/api_guide.md) as source of truth when endpoint behavior conflicts with old SDK examples.
