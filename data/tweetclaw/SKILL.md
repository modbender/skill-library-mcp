---
name: TweetClaw
description: "Use @xquik/tweetclaw in OpenClaw to search tweets, search tweet replies, post tweets and replies with approval, export followers, look up users, manage media, monitor tweets, send direct messages, deliver webhooks, and run giveaway draws."
homepage: https://github.com/Xquik-dev/tweetclaw
metadata: {"openclaw":{"emoji":"X","requires":{"bins":["openclaw","node","npm"],"env":["XQUIK_API_KEY"]},"primaryEnv":"XQUIK_API_KEY"}}
---

# TweetClaw

Use this skill when a user asks an OpenClaw agent to work with X/Twitter data or reviewed account actions through the official `@xquik/tweetclaw` plugin. TweetClaw is an OpenClaw plugin, not a browser macro. It exposes an agent-safe endpoint catalog through OpenClaw tools.

## Install

```bash
openclaw plugins install npm:@xquik/tweetclaw
openclaw plugins inspect tweetclaw --runtime --json
```

Use the explicit `npm:` source for npm installs. Inspect the runtime after install so the agent only uses tools that OpenClaw reports as available.

Configure one of these sensitive values outside chat:

- `XQUIK_API_KEY` for Xquik account-backed workflows
- `MPP_SIGNING_KEY` for supported read-only pay-per-use workflows

Store keys in OpenClaw plugin config or the local environment. Never paste keys into prompts, logs, issues, or generated files.

## Use TweetClaw For

- Search tweets, scrape tweets, search tweet replies, and collect public conversation context.
- Look up X/Twitter users, export followers, and gather account evidence.
- Download media, upload media for approved posts, and inspect media workflows.
- Monitor tweets, deliver webhooks, and verify public campaign signals.
- Send direct messages only when the user has approved the recipient and text.
- Run giveaway draws from declared criteria and preserve reviewable results.
- Post tweets and post tweet replies after the final text and target account are approved.

## Approval Rules

- Start with read-only calls for source discovery, audience context, reply context, campaign evidence, or result verification.
- Ask for explicit approval before any write-like or account-changing action: post tweet, post reply, delete, follow, unfollow, like, retweet, direct message, media upload, monitor creation, webhook change, giveaway draw, or paid action.
- Confirm the connected account, target tweet or recipient, exact text, media, filters, and cost-bearing action before execution.
- Refuse spam, harassment, deceptive engagement, impersonation, credential collection, platform evasion, mass unsolicited direct messages, bulk follows, or bulk engagement.
- Do not claim TweetClaw schedules posts or replaces a content calendar. Use it as source context or approval-gated execution when the installed plugin supports the requested action.

## OpenClaw Workflow

1. Run `openclaw plugins inspect tweetclaw --runtime --json` and read the available tool names.
2. If OpenClaw hides optional plugin tools, keep the normal tool profile and add `explore` and `tweetclaw` to `tools.alsoAllow`.
3. Call `explore` first when the user asks what TweetClaw can do, which endpoint fits, or what inputs are required.
4. Call `tweetclaw` only after selecting a specific endpoint and validating required inputs.
5. Summarize returned data by source, account, tweet ID, timestamp, and action outcome. Keep private keys and raw tokens out of the response.

## Good Requests

- "Search tweets about our launch and group the top complaints."
- "Find replies to this tweet, then draft 3 responses for review."
- "Export followers for this account and identify developer-tool profiles."
- "Look up this user and summarize recent public posts."
- "Upload this image and post the approved launch tweet."
- "Set up a monitor for this keyword and send webhook events to my endpoint."
- "Run a giveaway draw from replies that match these rules."

## Links

- GitHub: https://github.com/Xquik-dev/tweetclaw
- npm: https://www.npmjs.com/package/@xquik/tweetclaw
- ClawHub: https://clawhub.ai/plugins/@xquik/tweetclaw
- Setup Guide: https://docs.xquik.com/guides/tweetclaw
