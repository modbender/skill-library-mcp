---
name: prompt-request
description: >
  GitHub Issue → auto-implement → PR → review → auto-merge pipeline.
  Write an Issue with [auto] tag, and the pipeline handles everything:
  task analysis, implementation, testing, PR creation, review, and merge.
  Includes progress comments on Issues and early-exit optimization.
version: 1.0.0
author: ShunsukeHayashi
tags: [github, webhook, automation, pipeline, prompt-request]
---

# Prompt Request Pipeline

Issue を書くだけで、自動実装 → PR → レビュー → マージまで全自動で回るパイプライン。

## Overview

```
[auto] Issue 起票
  → 🚀 実装開始コメント
  → Phase A: タスク分解（Omega-bridge or Issue本文）
  → 📋 分析完了コメント
  → Phase B: 実装 + テスト
  → ✅ 実装完了コメント
  → Phase C: commit → push → PR作成
  → 🔗 PR作成コメント
  → 自動レビュー → 自動マージ → Issue close
```

## Prerequisites

- OpenClaw Gateway running with hooks enabled
- GitHub CLI (`gh`) authenticated
- Git SSH access to target repository
- GitHub Webhook pointing to OpenClaw hooks endpoint

## Setup

### 1. Register GitHub Webhook

On your GitHub repo → Settings → Webhooks → Add webhook:

- **Payload URL**: `https://<your-openclaw-endpoint>/hooks/github`
- **Content type**: `application/json`
- **Secret**: Your OpenClaw hooks token
- **Events**: Select individual events:
  - Issues
  - Pull requests
  - Pull request reviews
  - Check runs
  - Issue comments
  - Push

### 2. Configure OpenClaw hooks

Add this to your `openclaw.json` under `hooks.mappings`:

```json
{
  "match": { "path": "github" },
  "action": "agent",
  "name": "GitHub",
  "sessionKey": "hook:github:{{repository.name}}:{{headers.x-github-event}}:{{issue.number}}{{pull_request.number}}{{check_run.id}}",
  "messageTemplate": "<see templates/messageTemplate.txt>",
  "deliver": true,
  "allowUnsafeExternalContent": true,
  "channel": "telegram",
  "to": "<your-chat-id>",
  "model": "anthropic/claude-opus-4-6",
  "thinking": "high",
  "timeoutSeconds": 900
}
```

### 3. Set working directory

In the messageTemplate, replace the working directory path:
- `WORKDIR` variable: where repositories are cloned (e.g., `C:\Users\you\Dev` or `/home/you/dev`)

### 4. (Optional) Omega-bridge

If you have Miyabi's omega-bridge for SWML-based task decomposition:
- Set the path to `omega-bridge.ts` in the messageTemplate
- If not available, the pipeline falls back to implementing directly from Issue body

## Usage

### Basic: Create an [auto] Issue

```markdown
Title: [auto] Add utility function X

Body:
## Requirements
- Create scripts/x.sh with function do_x()
- Add tests in tests/test-x.sh

## Acceptance Criteria
- Function returns expected output
- Tests pass
```

### Advanced: With agent personality

```markdown
Title: [auto] [content] Write article about Y

Body:
Read agents/content-agent/AGENTS.md and SOUL.md first.
Follow the rules defined there.

## Topic
...

## Output
- File: articles/y.md
- Word count: 6000
```

### Advanced: With skill reference

```markdown
Title: [auto] Generate report with weather data

Body:
Read skills/weather/SKILL.md for API usage.

## Requirements
...
```

## How It Works

### Issue Events (action=opened)

1. **Early exit check**: If action is closed/labeled/etc → 1-line reply, stop
2. **[auto] check**: Title starts with `[auto]` or body contains `<!-- auto-implement -->`
3. **Phase A**: Task decomposition (omega-bridge or direct)
4. **Phase B**: Implementation (branch, code, test)
5. **Phase C**: Integration (commit, push, PR)
6. Progress comments posted at each phase

### PR Events (action=opened/synchronize)

1. Skip bot senders (loop prevention)
2. Diff review for quality/security
3. Auto-merge if ALL conditions met:
   - PR title contains `[auto]` or branch starts with `feature/issue-`
   - Review is LGTM
   - CI checks pass (or empty = pass)
   - No merge conflicts

### Safety Rules

- Never force push
- Never push directly to main
- Never run permission commands (icacls/chmod/chown)
- Max 3 CI fix retries per PR
- Bot sender events are skipped

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `model` | `claude-opus-4-6` | Model for hook sessions |
| `thinking` | `high` | Thinking level |
| `timeoutSeconds` | `900` | Max execution time (15 min) |
| `deliver` | `true` | Send results to chat |
| `channel` | `telegram` | Delivery channel |

## Performance (measured)

| Metric | Before optimization | After optimization |
|--------|--------------------|--------------------|
| close/push events | 8-12 min, ~500 tokens | 3 sec, ~15 tokens |
| [auto] Issue → merged PR | N/A (stuck) | ~5 min |
| Full pipeline (Issue → merge) | N/A | ~5 min |

## Tips

- **Keep Issues small**: 1 Issue = 1 clear deliverable, ≤300 lines of diff
- **Be specific**: The quality of the Issue body directly determines output quality
- **Use templates**: Create Issue templates for recurring task types
- **Reference skills**: Point the agent to relevant SKILL.md files for domain knowledge
- **Reference agent definitions**: Store AGENTS.md/SOUL.md in the repo for consistent behavior
