---
name: hermes-tweet
description: Use Hermes Tweet when a Hermes Agent workflow needs native X/Twitter search, public reads, authenticated account context, or approval-gated social actions through the hermes-tweet plugin. Covers install, safe tool selection, read/action gating, and workflows for social listening, launch monitoring, support triage, creator research, giveaways, and controlled publishing.
---

# Hermes Tweet

## Overview

Hermes Tweet is a native Hermes Agent plugin for X/Twitter automation through Xquik. Use it when a Hermes workflow needs current social context, account reads, trend checks, or explicit approval-gated actions without treating social access as a generic browser macro.

The plugin exposes a least-privilege tool split:

- `tweet_explore` searches the bundled endpoint catalog and makes no network request.
- `tweet_read` calls catalog-listed read routes after `XQUIK_API_KEY` is configured.
- `tweet_action` calls write-like or private routes only when `HERMES_TWEET_ENABLE_ACTIONS=true`.

## Install

Install and enable the plugin in Hermes Agent:

```bash
hermes plugins install Xquik-dev/hermes-tweet --enable
```

Hermes prompts for `XQUIK_API_KEY` during interactive installation and stores it in the Hermes environment. In non-interactive setups, set the key before calling `tweet_read`.

If Hermes is already running after an environment change, reload the interactive session or restart the gateway/cron runtime before using the plugin.

For Python package installs inside the Hermes virtual environment:

```bash
uv pip install --python ~/.hermes/hermes-agent/venv/bin/python hermes-tweet
hermes plugins enable hermes-tweet
```

## When to Use

Use Hermes Tweet for:

- Social listening with X search, trends, mentions, account profiles, media, and follower context.
- Launch monitoring where Hermes should summarize public signal without taking account-changing actions.
- Support triage where agents read public mentions first, then hand off replies for explicit review.
- Creator or brand research that combines search, profile, follower, media, and trend reads.
- Giveaway or community audits that need tweet, reply, follower, list, draw, and export evidence.
- Controlled publishing sessions where actions are intentionally enabled for posts, replies, DMs, follows, monitors, webhooks, or media changes.

Do not use Hermes Tweet as a generic scheduler, a browser automation macro, or a replacement for human approval on write-like account actions.

## Safe Workflow

1. Start with `tweet_explore` to find the exact catalog path for the task.
2. Use `tweet_read` for public or authenticated read routes.
3. Keep `tweet_action` disabled unless the current session explicitly needs account-changing behavior.
4. Before enabling actions, confirm `HERMES_TWEET_ENABLE_ACTIONS=true` is set in the runtime environment.
5. Never paste API keys into prompts, issue bodies, PR comments, logs, or tool arguments.

## Runtime Notes

Hermes Tweet ships as the `hermes-tweet` Python package and registers through the `hermes_agent.plugins` entry point. It includes a Hermes plugin manifest, bundled skill guidance, slash commands for quick diagnostics, and a generated Xquik endpoint catalog.

For remote gateway profiles, install and configure Hermes Tweet on the remote Hermes host because plugin code executes there. The desktop app or chat surface should not receive the API key unless it is also the local Hermes runtime.

## References

- GitHub: <https://github.com/Xquik-dev/hermes-tweet>
- PyPI: <https://pypi.org/project/hermes-tweet/>
- Hermes Agent: <https://github.com/NousResearch/hermes-agent>
