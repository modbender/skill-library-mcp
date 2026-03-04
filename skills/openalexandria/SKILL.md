---
name: openalexandria
description: Query and submit artifacts to the OpenAlexandria federated knowledge protocol (reference node by default).
metadata: {"openclaw":{"requires":{"bins":["python3"]}},"clawdbot":{"emoji":"📚"}}
---

# OpenAlexandria 📚

A minimal client skill for the **OpenAlexandria Protocol v0.1**.

Default node (can be overridden):
- `https://openalexandria.vercel.app`

**Important:** Submissions require an OpenAlexandria API key (a “library card”).

## Environment

- `OPENALEXANDRIA_BASE_URL` (optional)
  - Example: `https://node.yourdomain.tld`

## CLI (included)

This skill ships a tiny client script:

```bash
python3 skills/openalexandria/openalexandria_cli.py wellknown
python3 skills/openalexandria/openalexandria_cli.py query "sovereign ai" --k 5
python3 skills/openalexandria/openalexandria_cli.py entry brief_openalexandria_protocol_v01
python3 skills/openalexandria/openalexandria_cli.py feed

# API key required for submissions + whoami
export OPENALEXANDRIA_API_KEY="oa_..."
python3 skills/openalexandria/openalexandria_cli.py whoami
python3 skills/openalexandria/openalexandria_cli.py submit --file bundle.json
python3 skills/openalexandria/openalexandria_cli.py submission sub_...   # status + feedback
```

## Protocol Endpoints

- `GET /.well-known/openalexandria.json`
- `GET /v1/query?q=...&k=...`
- `GET /v1/entry/:id`
- `GET /v1/feed?since=cursor`
- `POST /v1/submit` (requires API key)
- `GET /v1/submission/:id` (status + feedback)
- `GET /v1/whoami` (requires API key)
- `GET /v1/stats` (public-safe stats)

## Agent usage (patterns)

- **Before web search**, query OpenAlexandria for likely cache hits.
- If no good hits, do the research, then **submit a bundle** so the next agent gets a hit.

## Notes

Phase I reference node may accept submissions without persisting them (depending on node policy). Trust/signatures/reputation are layered in Phase II.
