# Release Notes Generator

Generate clear, professional release notes from git commits, PRs, or a plain list of changes. Outputs formatted changelogs your users actually want to read.

## Usage

Tell the agent what changed — paste commits, PR titles, or describe features in plain language. It produces structured release notes.

### Input Options

1. **Git diff/log** — paste `git log --oneline v1.2.0..v1.3.0` output
2. **PR list** — paste merged PR titles
3. **Plain description** — "We added dark mode, fixed the login bug, and dropped Python 3.7 support"

### Output Format

```markdown
## v1.3.0 — 2026-02-13

### Added
- Dark mode across all pages (#142)

### Fixed
- Login redirect loop on Safari (#138)

### Breaking Changes
- Dropped Python 3.7 support — minimum is now 3.9

### Migration Guide
- Update your CI to use Python 3.9+ images
```

## Behavior

- Group changes by type: Added, Changed, Fixed, Deprecated, Removed, Security, Breaking Changes
- Follow [Keep a Changelog](https://keepachangelog.com/) conventions
- Include migration guides for breaking changes
- Write for end users, not engineers (unless told otherwise)
- Strip internal/refactor commits unless asked to include them
- Add PR/issue numbers when available
- Keep it scannable — bullet points, not paragraphs

## Audience Toggle

Say "internal" for eng-focused notes or "external" for customer-facing notes. Default is external.

## Multiple Formats

Ask for:
- **Changelog** — append-friendly CHANGELOG.md format
- **Email** — ready to paste into a release email
- **Slack** — compact format for #releases channel
- **GitHub Release** — markdown for GitHub release page
- **Tweet thread** — highlight reel for social

## Tips

- Run after every sprint or before every deploy
- Pair with a CI step that dumps `git log` into a file
- Keep a running CHANGELOG.md and append each release

---

Built by [AfrexAI](https://afrexai-cto.github.io/context-packs/) — AI context packs for business teams ($47/pack). See our [AI Revenue Calculator](https://afrexai-cto.github.io/ai-revenue-calculator/) to find what automation is costing you.
