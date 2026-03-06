# Posting Settings Reference

## Posting Method

**Luka posts manually.** The agent never posts.

Luka's workflow:
1. Receives draft via Telegram
2. Reviews, optionally edits
3. Replies APPROVE or REJECT to Manager
4. Copies the draft and posts it to Reddit himself
5. Sends the Reddit URL back via Telegram to confirm

## Postiz (If Enabled Later)

Postiz is installed but currently not used for auto-posting to Reddit. It may be enabled in future for:
- Scheduled posting to less-restricted subs
- Cross-platform posting (when Twitter/X vertical is added)

When Postiz is enabled for a subreddit, that subreddit will be listed here with explicit approval. Do not assume Postiz can be used for Reddit until it appears in this file.

## Timing Guidelines

Luka posts at roughly 10am weekdays (the post cron slot). This is when most of the target subreddits have good morning traffic.

Do not draft content that has a time-sensitive angle (breaking news, today-only relevance) — Luka may not post until the next morning.

## One Post Per Day Maximum

Draft 1-2 posts per day total across all subreddits. Do not draft one post per subreddit — that's spam behavior and burns Luka's account reputation.

## Account Safety Rules

- Never draft the same post for multiple subreddits (cross-posting is banned in most target subs)
- Each draft must be original and custom-tailored to that specific subreddit's culture
- Space posts across subreddits — not more than 2 posts per week in any single subreddit
- If a post gets removed by mods, log it in active-tasks.md immediately and write a lesson signal
