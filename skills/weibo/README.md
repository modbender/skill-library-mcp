# weibo-api-skill

OpenClaw skill set for Weibo data collection with a separated optional Brave-backed fallback.

## Included Skills

- [`weibo`](/home/noir/enna/skills/weibo/weibo/SKILL.md): official Weibo Open Platform OAuth and REST API wrapper.
- [`weibo-brave-search`](/home/noir/enna/skills/weibo/weibo/weibo-brave-search/SKILL.md): optional fallback skill that searches `site:weibo.com` through Brave Search API.

The split is intentional. The base Weibo skill should not publish or imply a second unrelated commercial credential dependency when the official API path is sufficient.

## Credentials

### `weibo`

| Variable | Required | Sensitive | Purpose |
| --- | --- | --- | --- |
| `WEIBO_APP_KEY` | Yes | No | OAuth client identifier |
| `WEIBO_APP_SECRET` | Yes | Yes | OAuth token exchange |
| `WEIBO_REDIRECT_URI` | Yes | No | OAuth callback |
| `WEIBO_ACCESS_TOKEN` | Optional | Yes | Authenticated API calls after token issuance |

Recommended OpenClaw config shape:

```json
{
  "skills": {
    "entries": {
      "weibo": {
        "enabled": true,
        "apiKey": { "source": "env", "provider": "default", "id": "WEIBO_APP_SECRET" },
        "env": {
          "WEIBO_APP_KEY": "your-app-key",
          "WEIBO_REDIRECT_URI": "https://example.com/callback"
        }
      }
    }
  }
}
```

If you already have a bearer token, inject `WEIBO_ACCESS_TOKEN` through `skills.entries.weibo.env` or your deployment environment. Treat that token as sensitive.

### `weibo-brave-search`

| Variable | Required | Sensitive | Purpose |
| --- | --- | --- | --- |
| `BRAVE_SEARCH_API` | Yes | Yes | Brave Search API subscription token |

Recommended OpenClaw config shape:

```json
{
  "skills": {
    "entries": {
      "weibo-brave-search": {
        "enabled": true,
        "apiKey": { "source": "env", "provider": "default", "id": "BRAVE_SEARCH_API" }
      }
    }
  }
}
```

## Secret Handling Warnings

- `WEIBO_APP_SECRET`, `WEIBO_ACCESS_TOKEN`, and `BRAVE_SEARCH_API` are sensitive and must not be committed.
- OpenClaw's documented secret-reference audit path covers fields such as `skills.entries.<skillKey>.apiKey`. It does not provide the same audit visibility for arbitrary ad hoc env vars.
- If you use `skills.entries.<skillKey>.env` for sensitive values, store those values in an external secret manager or deployment-time environment injection you control.
- The `weibo` skill makes network calls to `https://api.weibo.com`.
- The `weibo-brave-search` skill makes network calls to `https://api.search.brave.com` and should only be enabled if you intentionally accept that extra provider dependency.

## Security Position

This repository is an open-source wrapper around commercial API providers. The goal is open functionality and modification at will, without hiding credential requirements. Where the implementation falls outside OpenClaw's audited `SecretRef` path, the docs call that out explicitly so users can make an informed deployment decision.
