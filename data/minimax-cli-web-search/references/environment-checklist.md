# Environment Checklist

## 1) Verify CLI

```bash
command -v mcporter
mcporter --help
```

## 2) Verify minimax MCP registration

```bash
mcporter list --json
```

Expected:
- server named `minimax`
- `status: ok`
- tool includes `web_search`

## 3) Verify search call

```bash
mcporter call minimax.web_search query="latest AI news"
```

If auth/config error appears:
- verify API key placement in MCP server config
- verify the server command/transport
- retry after fixing config

## 4) Wrapper smoke test

```bash
scripts/minimax_web_search.sh --preflight
scripts/minimax_web_search.sh --query "OpenClaw GitHub" --count 3
scripts/minimax_web_search.sh --query "nonexistent-query-zzz" --count 3
```

## 5) Publish readiness

- SKILL frontmatter name/description complete
- script executable (`chmod +x`)
- package command succeeds
