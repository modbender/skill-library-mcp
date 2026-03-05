---
name: clawrent-web-scraping
description: Earn money by completing web scraping tasks when your computer is idle
homepage: https://clawrent.xyz
metadata: {"openclaw": {"requires": {"env": ["CLAWRENT_API_KEY"]}, "primaryEnv": "CLAWRENT_API_KEY"}}
---

# ClawRent - Earn with idle resources

You help users earn passive income by completing web scraping tasks while their machine is idle.

## Setup

If `CLAWRENT_API_KEY` is missing:
1. Tell user to sign up at `https://clawrent.xyz/node/register` to get their API key.
2. Ask user to paste their API key.
3. Save it to the skill config as `CLAWRENT_API_KEY` so it persists across sessions.
4. Confirm: "API key saved. ClawRent is ready to earn for you."

Register node on first run:
- `POST https://clawrent.xyz/v1/node/register`
- Header: `Authorization: Bearer {config.CLAWRENT_API_KEY}`
- Body: `{ "name": "{hostname}", "os": "{platform}", "ip": "auto" }`

## Heartbeat

When idle, request task every 30 seconds:
- `POST https://clawrent.xyz/v1/node/heartbeat`
- Header: `Authorization: Bearer {config.CLAWRENT_API_KEY}`

If response includes `task`, run it immediately.

After reporting each task result, immediately send one more heartbeat to fetch the next task without waiting for the next interval.

## Execute Task

Given one task URL:
1. Open URL in browser tool.
2. Wait `task.options.waitMs` milliseconds (default 2000).
3. If `task.options.selector` exists, extract that element HTML only.
4. Otherwise capture full page HTML.
5. If `task.options.returnType` includes screenshot, capture screenshot.

## Report Result

Send result:
- `POST https://clawrent.xyz/v1/node/result`
- Header: `Authorization: Bearer {config.CLAWRENT_API_KEY}`
- Body:
  - `taskId`
  - `status` (`completed` or `failed`)
  - `html`
  - `statusCode`
  - `error` (if failed)

## Earnings

- After each completed task, tell user earned amount.
- Once per day, summarize total earnings.
