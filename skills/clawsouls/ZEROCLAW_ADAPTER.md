# ZeroClaw Adapter Design

## Overview

ZeroClaw is a Rust-based alternative to OpenClaw that already supports OpenClaw-style markdown identity files via its `IdentityConfig` trait. This adapter extends ClawSouls CLI to install/use souls on ZeroClaw.

## ZeroClaw Identity System

### Config Location
- `~/.zeroclaw/config.toml` — main config
- Workspace directory — identity files (SOUL.md, IDENTITY.md, etc.)

### IdentityConfig Trait
ZeroClaw supports two identity formats:
1. **OpenClaw (markdown)** — SOUL.md, IDENTITY.md, AGENTS.md, HEARTBEAT.md, STYLE.md
2. **AIEOS v1.1 (JSON)** — alternative format

Since ZeroClaw already reads OpenClaw-style markdown, Soul files work **out of the box** if placed in the workspace.

## Adapter Strategy

### Option A: CLI Flag (Minimal)
Add `--platform zeroclaw` flag to existing commands:

```bash
npx clawsouls install clawsouls/surgical-coder --platform zeroclaw
npx clawsouls use clawsouls/surgical-coder --platform zeroclaw
```

**Differences from OpenClaw:**
- Workspace: `~/.zeroclaw/` instead of `~/.openclaw/workspace/`
- Restart: `zeroclaw gateway restart` instead of `openclaw gateway restart`
- No `restore` needed — same backup logic

### Option B: Auto-detect (Smart)
CLI detects which platform is running:

```
1. Check if ~/.openclaw/ exists → OpenClaw mode
2. Check if ~/.zeroclaw/ exists → ZeroClaw mode
3. Both exist → prompt user
4. Neither → error
```

### Recommended: Option B (auto-detect) with Option A as override

## Implementation Plan

### Phase 1: Detection
- `src/utils/platform.ts` — detect OpenClaw vs ZeroClaw
- Return workspace path, restart command, config format

### Phase 2: Install/Use
- Modify `install` command to use detected workspace
- Modify `use` command to copy to correct directory
- Modify restart hint to show correct command

### Phase 3: SKILL.md Update
- Add ZeroClaw instructions to SKILL.md
- Document both platforms

## File Mapping

| Soul File | OpenClaw Location | ZeroClaw Location |
|-----------|-------------------|-------------------|
| SOUL.md | ~/.openclaw/workspace/SOUL.md | ~/.zeroclaw/workspace/SOUL.md |
| IDENTITY.md | ~/.openclaw/workspace/IDENTITY.md | ~/.zeroclaw/workspace/IDENTITY.md |
| AGENTS.md | ~/.openclaw/workspace/AGENTS.md | ~/.zeroclaw/workspace/AGENTS.md |
| STYLE.md | ~/.openclaw/workspace/STYLE.md | ~/.zeroclaw/workspace/STYLE.md |
| HEARTBEAT.md | ~/.openclaw/workspace/HEARTBEAT.md | ~/.zeroclaw/workspace/HEARTBEAT.md |

## Testing

1. Install ZeroClaw locally (`cargo install`)
2. Run `npx clawsouls install clawsouls/surgical-coder`
3. Verify files placed in `~/.zeroclaw/workspace/`
4. Run `zeroclaw agent -m "who are you?"` → should respond as Surgical Coder
