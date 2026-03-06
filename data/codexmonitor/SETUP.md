# CodexMonitor - Setup Instructions

## Prerequisites

### Required Software

- **macOS** — This tool is macOS-only
- **Codex CLI or VS Code Extension** — Must be installed and producing session logs
  - Codex creates session files in `~/.codex/sessions/`

### Installation

Install via Homebrew:

```bash
brew tap cocoanetics/tap
brew install codexmonitor
```

This installs the `codexmonitor` binary to your PATH.

## Configuration

### Sessions Directory

By default, CodexMonitor reads from `~/.codex/sessions/`.

If your sessions are stored elsewhere, set one of these environment variables:

- **`CODEX_SESSIONS_DIR`** — Absolute path to sessions directory (preferred)
  ```bash
  export CODEX_SESSIONS_DIR="/path/to/sessions"
  ```

- **`CODEX_HOME`** — CodexMonitor will use `$CODEX_HOME/sessions`
  ```bash
  export CODEX_HOME="/path/to/codex"
  ```

### Session Structure

Sessions are organized by date:
```
~/.codex/sessions/
├── YYYY/
│   ├── MM/
│   │   ├── DD/
│   │   │   ├── session-id-1.jsonl
│   │   │   ├── session-id-2.jsonl
│   │   │   └── ...
```

## Verification

Verify installation:
```bash
codexmonitor --version
```

Check that sessions are detected:
```bash
codexmonitor list $(date +%Y/%m/%d)
```
