---
name: yarn-threads
description: Interact with Threads (by Meta) via the yarn-threads-cli. Use when the user wants to read their home feed, likes, saved posts, or a specific thread; look up a profile; search users; or post, reply, or quote on Threads. Requires yarn-threads-cli installed (npm install -g yarn-threads-cli). Auth via Chrome/Firefox profile (the user just needs to be logged in) or manual session tokens.
---

# yarn-threads

CLI for Threads (by Meta). Supports reading, browsing, and posting.

## Installation

```bash
npm install -g yarn-threads-cli
```

Verify:
```bash
yarn-threads --version
```

## Auth

Three options (in order of preference):

- **Chrome profile (recommended)**
- **Firefox profile**
- **Manual tokens** (from browser DevTools → Application → Cookies on threads.net)

Refer to the [yarn-threads-cli documentation](https://github.com/jeizzon/yarn-threads-cli) for more information on how to set up authentication.

Verify auth: `yarn-threads whoami`

## Key Commands

```bash
# Browse
yarn-threads home                        # Home feed
yarn-threads likes                       # Your liked posts
yarn-threads saved                       # Your saved/bookmarked posts

# Read
yarn-threads read <url-or-code>          # Single post
yarn-threads thread <url-or-code>        # Post + all replies
yarn-threads replies <url-or-code>       # Replies only

# Profiles
yarn-threads about <handle>              # User profile info
yarn-threads user-posts <handle>         # User's posts
yarn-threads followers <handle>          # User's followers
yarn-threads following <handle>          # Who user follows

# Search
yarn-threads search <query>              # Search users

# Post / Engage
yarn-threads post "text"                 # Create new post
yarn-threads reply <url-or-code> "text"  # Reply to a post
yarn-threads quote <url-or-code> "text"  # Quote a post
```

## Output Flags

- `--json` — structured JSON output (use for parsing media URLs, metadata)
- `--plain` — stable plain text, no emoji/color (good for piping)
- `--json-full` — includes raw API response (debugging)

## Pagination

Feed/list commands support:
- `--all` — fetch all pages
- `--max-pages <n>` — limit pages
- `--cursor <cursor>` — start from a specific page cursor

## Media

When using `--json`, posts include CDN URLs for images and videos in the media fields. Analyze these with the `image` tool for visual context.

## Examples

```bash
# Get last 2 pages of likes as JSON
yarn-threads likes --max-pages 2 --json

# Read a specific thread
yarn-threads read https://www.threads.net/@user/post/abc123

# Post with restricted replies
yarn-threads post "Hello Threads" --reply-control accounts_you_follow

# Get a profile
yarn-threads about zuck
```

See references/commands.md for full flag reference per command.
