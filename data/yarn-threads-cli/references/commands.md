# yarn-threads Command Reference

Full flag reference for yarn-threads-cli v0.1.x.

## Global Flags

| Flag | Description |
|------|-------------|
| `--session-id <token>` | Threads sessionid cookie |
| `--csrf-token <token>` | Threads csrftoken cookie |
| `--user-id <id>` | Threads ds_user_id cookie |
| `--chrome-profile <name>` | Chrome profile name |
| `--chrome-profile-dir <path>` | Chrome/Chromium profile directory or cookie DB path |
| `--firefox-profile <name>` | Firefox profile name |
| `--cookie-timeout <ms>` | Cookie extraction timeout |
| `--timeout <ms>` | Request timeout |
| `--json` | Output as JSON |
| `--plain` | Plain output (stable, no emoji, no color) |
| `--no-emoji` | Disable emoji output |
| `--no-color` | Disable ANSI colors |

## Commands

### whoami
Show current authenticated user.
```bash
yarn-threads whoami
```

### home
Get your home feed.
```bash
yarn-threads home [--cursor <cursor>] [--max-pages <n>] [--all] [--json-full]
```

### likes
Get your liked posts.
```bash
yarn-threads likes [--cursor <cursor>] [--max-pages <n>] [--all] [--json-full]
```

### saved
Get your saved/bookmarked posts.
```bash
yarn-threads saved [--cursor <cursor>] [--max-pages <n>] [--all] [--json-full]
```

### read
Fetch a single thread/post by URL or shortcode.
```bash
yarn-threads read <url-or-code>
```

### replies
Get replies to a post.
```bash
yarn-threads replies <url-or-code> [--cursor <cursor>] [--max-pages <n>] [--all] [--json-full]
```

### thread
Get full thread (post + replies).
```bash
yarn-threads thread <url-or-code> [--cursor <cursor>] [--max-pages <n>] [--all] [--json-full]
```

### about
Get user profile information.
```bash
yarn-threads about <handle>
```

### user-posts
Get a user's posts.
```bash
yarn-threads user-posts <handle> [--cursor <cursor>] [--max-pages <n>] [--all] [--json-full]
```

### followers
Get a user's followers list.
```bash
yarn-threads followers <handle> [--cursor <cursor>] [--max-pages <n>] [--all] [--json-full]
```

### following
Get a user's following list.
```bash
yarn-threads following <handle> [--cursor <cursor>] [--max-pages <n>] [--all] [--json-full]
```

### search
Search users on Threads.
```bash
yarn-threads search <query>
```

### post
Create a new text post.
```bash
yarn-threads post <text> [--reply-control <mode>]
```
`--reply-control` modes: `everyone` (default), `accounts_you_follow`, `mentioned_only`

### reply
Reply to an existing post.
```bash
yarn-threads reply <url-or-code> <text>
```

### quote
Quote an existing post.
```bash
yarn-threads quote <url-or-code> <text>
```
