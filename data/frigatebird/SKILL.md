---
name: frigatebird
description: Use the frigatebird npm package to interact with X from the CLI with bird-style command parity, posting/reply/article support, and list automation without X API keys.
argument-hint: 'whoami, read https://x.com/user/status/123, tweet "hello", article "Launch notes" "We shipped", add "AI News" @openai @anthropicai'
---

# Frigatebird Skill

Frigatebird is a Playwright-first CLI and npm package (`frigatebird`) that preserves `bird` command ergonomics while running against X via browser session cookies.

## Use This Skill When

- The user asks for `bird`-style CLI workflows on X.
- The user needs posting/reply/article actions from CLI.
- The user needs list automation (`add`, `remove`, `batch`, `lists`).
- The user needs API-key-free browser-cookie operation.

## Package and Install

- npm package: `frigatebird`
- Global install: `npm install -g frigatebird`
- Local use: `npx frigatebird <command>`

## Core Workflow

1. Validate auth/session:
   - `frigatebird check`
   - `frigatebird whoami`
2. Read flows (use JSON when scripting):
   - `frigatebird read <tweet-id-or-url> --json`
   - `frigatebird search "<query>" --json`
   - `frigatebird home --json`
3. Mutation flows:
   - `frigatebird tweet "<text>"`
   - `frigatebird reply <tweet-id-or-url> "<text>"`
   - `frigatebird article "<title>" "<body>"`
4. List automation:
   - `frigatebird add "<List Name>" @handle1 @handle2`
   - `frigatebird remove @handle "<List Name>"`
   - `frigatebird batch accounts.json`
5. For larger reads, use paging controls:
   - `--all`, `--max-pages`, `--cursor`, `-n`

## Feature Coverage

- Posting/mutations: `tweet`, `post`, `reply`, `article`, `like`, `retweet`, `follow`, `unfollow`, `unbookmark`
- Read/timelines: `read`, `replies`, `thread`, `search`, `mentions`, `user-tweets`, `home`, `bookmarks`, `likes`, `list-timeline`, `news`, `about`
- Identity/health: `check`, `whoami`, `query-ids`, `help`
- List automation: `add`, `remove`, `batch`, `lists`, `list`, `refresh`

## Options That Matter Most

- Auth/cookies: `--auth-token`, `--ct0`, `--cookie-source`, `--chrome-profile`, `--firefox-profile`
- Determinism/testing: `--base-url`, `--plain`, `--no-color`
- Pagination: `-n`, `--all`, `--max-pages`, `--cursor`, `--delay`
- Output: `--json`, `--json-full`
- Media posting: `--media`, `--alt`

## Live E2E Notes

- Standard live mutation e2e does not run premium-feature checks by default.
- Premium-feature e2e opt-in:
  - `npm run test:e2e:live -- --list-name <name> --enable-premium-features-e2e --article-cookie-source chrome --article-expected-handle-prefix <prefix>`

## Caveats

- This tool depends on X web UI selectors; selector drift can break flows.
- `query-ids` is retained for command compatibility and does not drive Playwright execution.
- Some GraphQL-specific behavior from original `bird` is represented as compatibility flags in Playwright mode.
