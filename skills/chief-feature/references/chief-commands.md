# Chief CLI Reference

## Commands

| Command | Description |
|---------|-------------|
| `chief` | Open TUI for the current project (auto-detects PRDs) |
| `chief <prd-name>` | Open TUI for a specific PRD |
| `chief new <prd-name>` | Launch Claude Code in PRD-writer mode |
| `chief update` | Update Chief to latest version |

## TUI Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `s` | Start / resume the implementation loop |
| `p` | Pause the loop |
| `x` | Stop the loop |
| `d` | Diff — show changes for current story |
| `t` | Log — show tool output / reasoning |
| `n` | New story (add a user story on the fly) |
| `l` | List all stories |
| `1-9` | Jump to story by number |
| `q` | Quit |
| `?` | Help |

## PRD File Structure

```
.chief/
└── prds/
    └── <prd-name>/
        ├── prd.md       # Human-readable PRD (commit this)
        ├── prd.json     # Machine-readable PRD with story state (may be gitignored)
        └── progress.md  # Implementation log (commit this when done)
```

## prd.json Story States

Each user story in `prd.json` tracks:
- `passes: true/false` — whether acceptance criteria pass
- `status` — pending / in-progress / complete / failed

## Chief's Workflow Per Story

1. Read the user story + acceptance criteria from `prd.json`
2. Explore codebase context
3. Implement changes
4. Run verification commands (`make test`, `make lint`, `pnpm typecheck`, etc.)
5. Commit if passing
6. Update `prd.json` + `progress.md`
7. Move to next story

## Official Resources

- **Website:** https://chiefloop.com/
- **GitHub:** https://github.com/minicodemonkey/chief
