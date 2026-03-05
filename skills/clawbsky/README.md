# clawbsky 🦞🦋

Advanced, professional Bluesky CLI for power users and automation. 

## 🚀 Key Features

- ✅ **Rich Media** — Post images (up to 4) and videos with automatic metadata detection.
- ✅ **Growth Tools** — Clean up non-mutual follows and auto-follow niche communities.
- ✅ **Thread Engine** — Create long-form threads automatically from multiple text blocks.
- ✅ **Smart UX** — Handle auto-completion (`@user` -> `user.bsky.social`) and rich-text facet detection.
- ✅ **Moderation** — Comprehensive block, mute, and notification management.
- ✅ **Discovery** — Deep search for posts, hashtags, and users.

## 📦 Quick Start

1. Install dependencies:
   ```bash
   npm install
   ```
2. Configure your account:
   ```bash
   npx tsx scripts/cli.ts login
   ```
3. Run the CLI:
   ```bash
   npx tsx scripts/cli.ts --help
   ```

## 🛠 Commands

### Growth & Maintenance
- `unfollow-non-mutuals [-n 50]` — Identify and unfollow accounts that don't follow you back.
- `follow-all <query> [-n 20]` — Search for users by keyword and follow them automatically.
- `follow-domain [-n 50]` — Follow users who share your same handle domain (great for community building).

### Posting & Media
- `post "Text" [images/video...]` — Create a post with optional media.
- `thread "Part 1" "Part 2" ...` — Create a multi-post thread.
- `quote <uri> "My thoughts"` — Quote-post another user.
- `reply <uri> "Great post!"` — Reply to a post.

### Reading & Search
- `home [-n 20]` — View your timeline.
- `mentions [-n 10]` — Check your notifications.
- `search "query"` — Search for posts or hashtags.
- `user <handle>` — Inspect a profile's metadata.

## 🛡 Safety & Ethics

Clawbsky is designed for **responsible automation**. 
- **Confirmation Prompts**: Large batch operations (>100 follows/unfollows) require manual confirmation.
- **Rate Limiting**: Built-in 1s delay between follows to prevent API spam flags.
- **Best Practice**: Use this tool for periodic maintenance, not for aggressive aggressive "follow/unfollow" tactics.

## ⚙️ Advanced
- `--json`: Raw data for piping.
- `--plain`: No emojis or formatting for headless logs.
- `--dry-run`: Preview changes without executing.

---
Built for the AT Protocol community. 🦞
