# Narrative Engine Setup (X / Twitter)

This engine lets the bot enter based on viral narratives, e.g. posts from high-impact accounts like @elonmusk.

## Use official interfaces
X’s filtered stream lets you stream posts matching rules, and supports rules like `from:elonmusk`.  
See X docs for endpoints and examples.

## Setup
1) Put your Bearer token in `.env`:
- X_BEARER_TOKEN=...

2) Add narratives in `config/narratives.yaml` (manual mapping is safest).

3) Run:
```bash
npm run dev -- --mode paper --minutes 10
npm run dev -- --mode live --minutes 30
```
