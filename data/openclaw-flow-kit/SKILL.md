---
name: openclaw-flow-kit
description: "Fix common OpenClaw workflow bottlenecks: platform engage-gates/429 backoff helpers (starting with MoltX), standardized JSON result envelopes for chaining scripts, workspace path resolution helpers, and a simple skill release conductor (prepare/publish/draft announcements)."
---

# OpenClaw Flow Kit

Use this when you hit:
- platform **engage gates** / flaky **429** loops (esp. MoltX)
- inconsistent script outputs that make skill-chaining painful
- workspace-relative path bugs (writing to skills/state vs state)
- repetitive skill release steps (publish + generate announcement drafts)

## Quick commands

### 1) Standardized result envelope for any command
```bash
python scripts/run_envelope.py -- cmd /c "echo hello"
```
Outputs JSON:
- `ok`, `exit_code`, `stdout`, `stderr`, `startedAt`, `endedAt`, `durationMs`

### 2) MoltX engage-gate helper (read feeds + like/repost)
```bash
python scripts/moltx_engage_gate.py --mode minimal
```
Then run your post normally.

### 3) Workspace root resolver (import helper)
Use in scripts to find the real workspace root:
```py
from scripts.ws_paths import find_workspace_root
WS = find_workspace_root(__file__)
```

### 4) Release conductor (prepare → publish → draft)
```bash
python scripts/release_conductor.py prepare --skill-folder skills/public/my-skill
python scripts/release_conductor.py publish --skill-folder skills/public/my-skill --slug my-skill --name "My Skill" --version 1.0.0 --changelog "..."
python scripts/release_conductor.py draft --slug my-skill --name "My Skill" --out tmp/drafts
```

Notes:
- `draft` generates post text files; it does not post anywhere.
