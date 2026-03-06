# Reddit Skill (ThreadPilot)

Browser-first Reddit workflow skill with human-in-the-loop safety.

This repository packages a production-ready skill around [`threadpilot`](https://github.com/vood/threadpilot) so operators can log in, discover content, pull subreddit rules, and engage/post from CLI with explicit confirmation gates.

Created by the founder of [clawmaker.dev](https://clawmaker.dev), [writingmate.ai](https://writingmate.ai), [aidictation.com](https://aidictation.com), and [mentioned.to](https://mentioned.to).

## What You Get

- `SKILL.md` with behavior, triggers, and workflow
- `scripts/threadpilot` launcher with safe wrappers (`like-target`, `post-comment`)
- `scripts/reddit-cli` backward-compatible alias
- Binary reference in `bin/REFERENCE.md` (release-source, not bundled executables)
- `ops/openclaw/reddit_cli.cron` template for scheduled runs

## Installation

### Option 1: Clone (Recommended)

```bash
git clone https://github.com/vood/reddit-skill.git
cd reddit-skill
```

### Option 2: Download Release Archive

Download from:

`https://github.com/vood/reddit-skill/releases`

Then unpack and run from the extracted folder.

## Quick Start

```bash
# 1) Check identity/session
scripts/threadpilot whoami

# 2) Login when needed
scripts/threadpilot login

# 3) Pull rules before drafting
scripts/threadpilot rules --subreddit ChatGPT

# 4) Read/search
scripts/threadpilot read --subreddit ChatGPT --sort new --limit 10
scripts/threadpilot search --query "agent workflows" --subreddit ChatGPT --limit 10
```

## Human-In-The-Loop Actions

Like preview:

```bash
REDDIT_PERMALINK='<url>' REDDIT_DRY_RUN=1 scripts/threadpilot like-target
```

Like confirm:

```bash
REDDIT_PERMALINK='<url>' REDDIT_CONFIRM_LIKE=1 scripts/threadpilot like-target
```

Comment dry run:

```bash
REDDIT_THING_ID=t3_xxxxx REDDIT_PERMALINK='<url>' REDDIT_TEXT='draft text' REDDIT_DRY_RUN=1 scripts/threadpilot post-comment
```

Comment publish:

```bash
REDDIT_THING_ID=t3_xxxxx REDDIT_PERMALINK='<url>' REDDIT_TEXT='approved text' scripts/threadpilot post-comment
```

## Binary Resolution Order

`scripts/threadpilot` resolves runtime in this order:

1. `THREADPILOT_BIN` (explicit path)
2. Cached binary in `.threadpilot/bin/`
3. System `threadpilot` from `PATH`
4. Auto-install from `vood/threadpilot` release asset by version
5. Source fallback by cloning `vood/threadpilot` and building

Manual install/bootstrap:

```bash
scripts/threadpilot install
```

## Environment Variables

- `THREADPILOT_BIN`: Force exact binary path.
- `THREADPILOT_CACHE_DIR`: Override local cache directory (default: `.threadpilot`).
- `THREADPILOT_RELEASE_BASE_URL`: Release base URL for binary downloads.
- `THREADPILOT_VERSION`: Binary release version to download (default: `v0.1.0`).
- `THREADPILOT_REPO`: Git repo used for source bootstrap.
- `THREADPILOT_REF`: Git ref/branch for source bootstrap (default: `main`).
- `THREADPILOT_SOURCE_DIR`: Build from local source tree instead of cloning.
- `REDDIT_PROXY`: Proxy URL passed to CLI.
- `REDDIT_USER_AGENT`: Custom user agent.
- `REDDIT_ACCESS_TOKEN`: OAuth token for API-backed flows.
- `REDDIT_BROWSER_PROFILE`: Persistent browser profile path.
- `REDDIT_HEADLESS`: Set `1` for headless browser mode.
- `REDDIT_LOGIN_TIMEOUT_SEC`: Login wait timeout.
- `REDDIT_HOLD_ON_ERROR_SEC`: Keep browser open on error for debugging.
- `REDDIT_CHROME_PATH`: Explicit Chrome/Chromium executable path.
- `REDDIT_DRY_RUN`: Safety preview flag for wrapper actions.
- `REDDIT_CONFIRM_LIKE`: Explicit like confirmation flag.
- `REDDIT_CONFIRM_DOUBLE_POST`: Explicit override for duplicate-post protection.

## OpenClaw Scheduler

Cron template:

- [`ops/openclaw/reddit_cli.cron`](ops/openclaw/reddit_cli.cron)

The template includes:

- Daily session validation (`whoami`)
- Optional like workflow (disabled by default)
- Optional post-comment workflow (disabled by default)

## Safety Model

- Likes require explicit confirmation (`REDDIT_CONFIRM_LIKE=1`) or dry-run preview.
- Comment posting supports dry-run before publish.
- Duplicate-comment protection stays enabled by default.
- Rules pull (`rules --subreddit ...`) is designed to feed AI drafting context before posting.

## Compatibility

Preferred entrypoint:

- `scripts/threadpilot`

Legacy alias:

- `scripts/reddit-cli`

## Related Repos

- Core Go library + CLI: [vood/threadpilot](https://github.com/vood/threadpilot)
