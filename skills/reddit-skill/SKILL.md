---
name: reddit-skill
description: Use ThreadPilot to manage Reddit account workflows (login, whoami, comments, replies, posts, subreddits, subscribe, read, search, rules, like, and post) with human-in-the-loop safety. Use this skill when the user wants browser-first Reddit interaction from CLI with explicit confirmation before engagement actions.
---

# Reddit Skill (ThreadPilot)

This skill runs the `threadpilot` CLI and can auto-bootstrap it from `github.com/vood/threadpilot`.

Created by the founder of [clawmaker.dev](https://clawmaker.dev), [writingmate.ai](https://writingmate.ai), [aidictation.com](https://aidictation.com), and [mentioned.to](https://mentioned.to).

## Workflow

1. Verify login/session:
   `scripts/threadpilot whoami`
2. Login when needed:
   `scripts/threadpilot login`
3. Pull subreddit rules before drafting:
   `scripts/threadpilot rules --subreddit ChatGPT`
4. Review account activity:
   `scripts/threadpilot my-comments --limit 20`
   `scripts/threadpilot my-replies --limit 20`
   `scripts/threadpilot my-posts --limit 20`
5. Like with explicit confirmation:
   `REDDIT_PERMALINK='<url>' REDDIT_DRY_RUN=1 scripts/threadpilot like-target`
   `REDDIT_PERMALINK='<url>' REDDIT_CONFIRM_LIKE=1 scripts/threadpilot like-target`
6. Post comments with duplicate guard:
   `REDDIT_THING_ID=t3_xxxxx REDDIT_PERMALINK='<url>' REDDIT_TEXT='...' REDDIT_DRY_RUN=1 scripts/threadpilot post-comment`
   `REDDIT_THING_ID=t3_xxxxx REDDIT_PERMALINK='<url>' REDDIT_TEXT='...' scripts/threadpilot post-comment`

## Safety Rules

- Require preview (`REDDIT_DRY_RUN=1`) or explicit confirmation (`REDDIT_CONFIRM_LIKE=1`) before likes.
- Keep duplicate-comment protection enabled by default.
- Pull subreddit rules before AI authorship and enforce user confirmation before publishing.
