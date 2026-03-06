---
name: zenn_github
description: Publish Zenn articles by managing Markdown in a GitHub-connected repository (push/PR -> merge) and previewing with Zenn CLI.
---

# Zenn: GitHub Push/PR Publishing

## Overview
Zenn publishes by syncing a GitHub repository. Articles/books are Markdown files placed in specific directories, and Zenn CLI helps you preview and scaffold content locally.

This skill defines an operational workflow that is both fast and safe:
- Draft in PRs (`published: false`)
- Review with local preview (`zenn preview`)
- Publish by flipping `published: true` once the PR is ready

## Inputs to collect
- **Repo path** (local clone) and **GitHub remote**
- **Publishing branch** (the branch connected to Zenn)
- **Article metadata**: title, emoji, type (`tech` or `idea`), topics, published
- **Slug / filename** for the Markdown file (kebab-case recommended)
- **Assets** (images) location strategy (recommended: `images/<slug>/...`)

## File placement rules (Zenn)
- Articles must be placed under `articles/` as individual `.md` files.
- (Optional) Books are placed under `books/`.

Recommended repo layout:
```
.
├─ articles/
│  └─ 20260216-openclaw-to-zenn.md
├─ books/                # optional
└─ images/               # optional, recommended
   └─ openclaw-to-zenn/
      ├─ cover.png
      └─ diagram.png
```

## Zenn CLI usage (local)
### Install / init (one-time per repo)
If Zenn CLI is not set up yet in the repo:
```bash
npm init --yes
npm install zenn-cli
npx zenn init
```

### Preview locally
```bash
npx zenn preview
```

### Create new content
```bash
npx zenn new:article
npx zenn new:book
```

### List existing content
```bash
npx zenn list:articles
npx zenn list:books
```

## Article template (copy/paste)
Create `articles/<slug>.md`:

```md
---
title: "記事タイトル"
emoji: "🧩"
type: "tech" # tech or idea
topics: ["ruby", "rails", "ai"]
published: false
---

## TL;DR
- ...
- ...
- ...

## 背景
...

## 実装 / 検証
...

## 学び
...

## 参考
- ...
```

Notes:
- Title is in front matter, so body headings should generally start at `##`.
- Keep topics to a small, consistent set for series-building.

## Standard workflow (recommended)
### 1) Draft in a feature branch
1. Create or edit `articles/<slug>.md` (keep `published: false`)
2. Add images (if any) under `images/<slug>/...`
3. Preview locally:
   ```bash
   npx zenn preview
   ```

### 2) Open a PR
```bash
git checkout -b article/<slug>
git add articles/<slug>.md images/<slug>/
git commit -m "Add draft: <title>"
git push -u origin article/<slug>
```
Open a PR into the Zenn publishing branch.

### 3) Publish safely
Option A (safest): publish in a second tiny PR/commit
1. Merge the draft PR (still `published: false`)
2. Flip to `published: true` and merge a small PR

Option B (fast): publish in the same PR
- Keep `published: false` during writing/review
- Flip to `true` right before merging

## Quality gate checklist (minimum)
Before setting `published: true`, verify:
- No confidential info (customer names, internal URLs, unreleased metrics)
- Code blocks are runnable or clearly labeled as pseudo-code
- Images render and paths are correct
- Links are correct
- Spelling / headings / formatting are acceptable

## Troubleshooting
- Preview differs from Zenn web or CLI shows update notice:
  ```bash
  npm install zenn-cli@latest
  ```
- Images not showing:
  - Ensure they are committed and pushed
  - Ensure references look like `/images/<slug>/...` (not `./images/...`)
- Article not appearing:
  - File is under `articles/`
  - `published: true`
  - The branch synced to Zenn is the one being updated

## When does this not work?
- Skipping PR review (direct publish) increases risk of accidental leaks.
- Relying on UI/browser automation instead of GitHub sync is brittle to UI changes.
- Mixing multiple articles in one file or placing files outside `articles/` will not publish as expected.
