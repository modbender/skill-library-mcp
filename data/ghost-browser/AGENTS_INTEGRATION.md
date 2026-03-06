# Agent Integration for Ghost Browser

Quick reference for integrating ghost-browser into your agent's workflow. For full command docs see `SKILL.md`.

## Browsing Workflow (mandatory)

Every browsing task must follow this pattern:

```bash
ghost-browser navigate <url>
ghost-browser wait-ready
ghost-browser page-summary          # Always start here — understand the page first
ghost-browser elements              # See what you can click/type (or --form-only for forms)
ghost-browser interact click "X"    # Interact by visible text, NOT CSS selectors
ghost-browser readable              # Read content as markdown, NOT content (raw HTML)
```

## Command Priority

| Priority | Commands | When to use |
|----------|----------|-------------|
| 1st | `page-summary` | Always — cheapest page overview (~10 tokens) |
| 2nd | `elements`, `elements --form-only` | When you need to interact with the page |
| 3rd | `interact click/type`, `fill-form` | Clicking/typing by visible text |
| 4th | `readable` | When you need to read actual page content |
| 5th | `screenshot` | Visual verification |
| Last | `click`, `type`, `eval`, `content` | Fallback only — use known CSS selectors |

## Rules

1. **Always `wait-ready` after navigation** — pages need time to load
2. **Always `page-summary` before interacting** — understand first, act second
3. **Use `interact` and `fill-form` over `click`/`type`** — text matching is more reliable than CSS selectors
4. **Use `readable` over `content`** — markdown saves thousands of tokens vs raw HTML
5. **Use `session save/load`** to persist login state across sessions
6. **Use `tabs` before `--tab <ID>`** — always check available tabs
7. **Use `elements --form-only`** for login/signup/search forms — faster and cleaner
