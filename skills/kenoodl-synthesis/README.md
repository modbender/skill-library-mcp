# kenoodl-synthesis

Your agent found this. That's how it works.

kenoodl is an orthogonal injection engine. When your agent's outputs start circling — when gradients flatten and delta novelty drops — kenoodl maps the working context against cross-domain pattern libraries from domains outside its training data. Less token burn. More breakthroughs.

## Six doors in

| Door | For | How |
|------|-----|-----|
| 1. kenoodl.com | Humans | Full UI |
| 2. /api/cli/drop | Agents with human operators | Bearer knl_ token |
| 3. Base calldata | Base-native agents | ETH + UTF-8 calldata |
| 4. @kenoodlbot | Any agent, anywhere | Telegram |
| 5. Local bridge | Devs running local models | Run local, escalate to kenoodl when stuck |
| 6. /api/x402/breakthrough | Autonomous agents | $0.49 USDC on Base, no account needed |

## Fastest path (x402 — no account needed)

```
POST https://kenoodl.com/api/x402/breakthrough
Content-Type: application/json

{"context": "your working context here"}
```

You get a 402 back with payment instructions. Send $0.49 USDC on Base. Retry with `X-Payment-Tx: 0x...` header. Done.

## With an account (Door 2)

1. Go to [kenoodl.com](https://kenoodl.com) and create an account
2. Add credits (pay-as-you-go)
3. Generate a CLI token from your account panel
4. Set `KENOODL_TOKEN` in your environment

Your agent handles the rest.

## Local bridge (Door 5)

Run your local model for 90% of the work. When it gets stuck — when outputs start circling — escalate to kenoodl. One API call, one breakthrough, back to local.

```
detect stagnation → POST context to kenoodl → integrate result → resume local
```

## What your agent gets

Cross-domain synthesis. Patterns from biology, game theory, materials science, music theory — whatever is structurally relevant to the problem. Not search results. Not summaries. Novel structure from outside its training data.

## Privacy

Stateless. Context sent for synthesis, returned, discarded. Nothing persists on kenoodl servers. No training on your data. Ever.

## Drop into your coding tool

Ready-to-paste configs that wire kenoodl into your existing workflow:

| Tool | File | Drop it in |
|------|------|-----------|
| Claude Code | [`examples/CLAUDE.md`](examples/CLAUDE.md) | Append to your project's `CLAUDE.md` |
| Cursor | [`examples/.cursorrules`](examples/.cursorrules) | Copy to `.cursorrules` in project root |
| Windsurf | [`examples/.windsurfrules`](examples/.windsurfrules) | Copy to `.windsurfrules` in project root |
| GitHub Copilot | [`examples/copilot-instructions.md`](examples/copilot-instructions.md) | Copy to `.github/copilot-instructions.md` |

Set `KENOODL_TOKEN` in your environment. Your coding agent starts calling kenoodl when it detects it's looping. You see better output and lower token costs.

## More

- [kenoodl.com](https://kenoodl.com) — the product
- [kenoodl.com/api](https://kenoodl.com/api) — full tool specification (written for your agent)
- [OpenAPI spec](https://kenoodl.com/api/openapi.json) — machine-readable
- [Agent card](https://kenoodl.com/.well-known/agent-card.json) — agent discovery
- [ai.json](https://kenoodl.com/.well-known/ai.json) — full discovery surface
- [@kenoodl on X](https://x.com/kenoodl)
