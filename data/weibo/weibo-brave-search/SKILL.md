---
name: weibo-brave-search
description: Search public Weibo pages through Brave Search API when official Weibo API access is unavailable and the user explicitly accepts a separate Brave credential dependency.
metadata: {"openclaw":{"skillKey":"weibo-brave-search","homepage":"https://api.search.brave.com/","requires":{"bins":["python3"],"env":["BRAVE_SEARCH_API"]},"primaryEnv":"BRAVE_SEARCH_API"}}
---

# Weibo Brave Search

Use this skill only when the user explicitly wants a web-search fallback instead of the official Weibo API.

## Purpose

This skill queries Brave Search with `site:weibo.com` filters to discover public Weibo pages when:

1. Weibo app approval is unavailable.
2. OAuth token acquisition is blocked.
3. The user accepts a separate commercial search provider dependency.

## Primary Interface

- `scripts/weibo_search.py`: Brave Search wrapper for `site:weibo.com` queries.

## Usage

Run:
`python3 scripts/weibo_search.py "<keyword>"`

Examples:
`python3 scripts/weibo_search.py "小米"`
`python3 scripts/weibo_search.py "春节" --count 5 --json`

## Credentials And Secret Handling

| Variable | Required | Sensitive | Used for |
| --- | --- | --- | --- |
| `BRAVE_SEARCH_API` | Yes | Yes | Brave Search API subscription token |

OpenClaw configuration guidance:

1. Set `skills.entries.weibo-brave-search.apiKey` to a `SecretRef` or plaintext value for `BRAVE_SEARCH_API`.
2. Do not treat this skill as part of the base Weibo API path; it is a separate provider with its own commercial terms and secret handling obligations.

Warnings:

- `BRAVE_SEARCH_API` is sensitive and must not be committed.
- This skill makes network calls to `https://api.search.brave.com`.
- Use this skill only when fallback search is intentional.
