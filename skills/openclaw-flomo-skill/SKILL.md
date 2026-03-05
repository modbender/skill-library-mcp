---
name: flomo
description: Read and write flomo memos on macOS. Use when user asks to fetch recent flomo notes, search memo text in local flomo cache, or create/write a new memo to flomo via incoming webhook or URL scheme.
---

# flomo

Use this skill on macOS to read and write flomo content.

## Commands

- Read recent memos (remote API, recommended; auto-expands time window):

```bash
python3 scripts/flomo_tool.py read --remote --limit 20
```

- Search recent memos by keyword (remote API):

```bash
python3 scripts/flomo_tool.py read --remote --limit 100 --query "关键词"
```

- Read by tag (recommended for diary/book/etc):

```bash
python3 scripts/flomo_tool.py read --remote --limit 10 --tag "日记"
```

- List top tags (to see how many memos each tag has):

```bash
python3 scripts/flomo_tool.py read --dump-tags --limit 20
```

- Write memo (auto-resolve incoming webhook from local flomo login state):

```bash
python3 scripts/flomo_tool.py write --content "内容"
```

- Write memo via URL scheme (opens flomo app draft):

```bash
python3 scripts/flomo_tool.py write --content "内容" --url-scheme
```

- One-shot health check (read + write-url-scheme dry flow):

```bash
python3 scripts/flomo_tool.py verify --try-webhook --query "#openclaw"
```

## Behavior Rules

- Prefer webhook write; script can auto-resolve webhook when logged in on this Mac.
- Use URL scheme write only as fallback, because it requires GUI interaction to confirm/save.
- Read path uses remote API first and can auto-expand search window for sparse tags/keywords.
- For tag intent, prefer `--tag`; `--query "#标签"` is also supported.
- Never print full webhook URL in logs; only print masked form.
