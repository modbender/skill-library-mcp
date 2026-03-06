---
name: github-digest
description: "Generate a structured GitHub repo digest with briefing summary, categorized changes (breaking/major features/minor features/bug fixes), community discussions, and clickable source links. Use when: (1) user asks about a repo's recent activity, releases, PRs, or issues, (2) user wants a daily/weekly GitHub digest or briefing, (3) user asks 'what's new' or 'what happened' on a GitHub repo. NOT for: single PR review (use github skill), code changes (use coding-agent), or CI/issue management (use github skill directly)."
---

# GitHub Digest

Generate structured, link-rich GitHub repo digests with a briefing overview and categorized details.

## Prerequisites

- `gh` CLI authenticated (`gh auth status`)

## Workflow

### 1. Gather Data

Run these `gh` commands in parallel for the target repo (default: `openclaw/openclaw`):

```bash
# Recent releases (last 5)
gh release list --repo OWNER/REPO --limit 5

# Latest release notes
gh release view TAG --repo OWNER/REPO --json body --jq '.body'

# Recently merged PRs (last 30)
gh pr list --repo OWNER/REPO --state merged --limit 30 \
  --json number,title,author,mergedAt,labels \
  --jq '.[] | "[\(.mergedAt[:10])] #\(.number) \(.title) by @\(.author.login) [\([.labels[].name] | join(","))]"'

# Hot open issues (sorted by comments)
gh issue list --repo OWNER/REPO --state open --limit 30 \
  --json number,title,comments,labels \
  | jq -r '[.[] | {n:.number,t:.title,c:.comments,l:[.labels[].name]}] | sort_by(.c) | reverse | .[0:15] | .[] | "[\(.c)] #\(.n) \(.t) [\(.l | join(","))]"'
```

Adjust `--limit` and time range based on user's request (today / this week / this month).

### 2. Output Format

Structure the digest in this exact order:

#### 📋 Briefing（总览）

A 3-5 sentence executive summary covering:
- What version was released and when
- Core themes (2-3 keywords, e.g. "安全加固、Plugin SDK 开放、工具能力扩展")
- Most impactful change in one line
- Community pulse (what people are discussing)
- Any breaking changes warning

#### ⚠️ Breaking Changes

List each breaking change with:
- What changed
- Migration action required
- Link to docs if available

Skip this section if none.

#### 🏗️ 重大更新 (Major Features)

Significant new capabilities, architectural changes, new integrations. Each item:
- **Bold title**：one-line description ([#PR](https://github.com/OWNER/REPO/pull/NUMBER))

#### ✨ 小功能 / 改进 (Minor Features)

Group by sub-category when there are many (e.g. "Telegram", "CLI", "Plugin SDK"). Each item:
- One-line description ([#PR](https://github.com/OWNER/REPO/pull/NUMBER))

#### 🔧 Bug 修复 (Bug Fixes)

Group by area (e.g. "Channel 修复", "核心/安全", "工具/浏览器"). For channel fixes with 5+ items, use a table:

| Channel | 修复内容 | PR |
|---------|---------|-----|
| **Name** | Description | [#N](link) |

For other fixes, use bullet lists grouped by area.

#### 💬 社区热议 (Community Discussions)

Hot issues sorted by engagement. Each item:
- [#N](link) — **Title**：one-line summary of the discussion

### 3. Formatting Rules

- **Every PR/issue/release MUST have a clickable markdown link**
  - PR: `[#123](https://github.com/OWNER/REPO/pull/123)`
  - Issue: `[#123](https://github.com/OWNER/REPO/issues/123)`
  - Release: `[vTAG](https://github.com/OWNER/REPO/releases/tag/vTAG)`
- Use the user's language (detect from their message; default Chinese for Chinese users)
- Bold key terms for scannability
- Omit empty sections silently
- When release notes mention a PR number like `(#12345)`, always convert to a clickable link
- For "Thanks @user" in release notes, link to `https://github.com/user`
