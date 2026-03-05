# Skill Files

Agent-facing documentation published to ClawHub. Two variants:

- `SKILL.md` — production (`api.octomail.ai`, slug: `octomail`)
- `SKILL-dev.md` — dev (`api.octomail-dev.com`, slug: `octomail-dev`)

## Frontmatter Fields

| Field | Required | Notes |
|-------|----------|-------|
| `name` | Yes | Skill slug on ClawHub |
| `description` | Yes | One-liner for search/discovery |
| `version` | Yes | Semver — bump on every content change |
| `changelog` | Yes | One-line summary of what changed in this version |
| `author` | Yes | `OctoMail` |
| `tags` | Yes | Discovery tags |
| `metadata` | Yes | OpenClaw requirements (env vars, etc.) |

## When Updating

1. Edit the skill content.
2. Bump `version` (semver).
3. Update `changelog` to describe the change.
4. Keep both files in sync — if a change applies to both prod and dev, update both.

## CI Publish

`SKILL.md` is auto-published to ClawHub on push to `main` when the file changes. CI extracts `version` and `changelog` from frontmatter and passes them to `clawhub publish`. See `.github/workflows/ci.yml` (`publish-skill` job).

`SKILL-dev.md` is not auto-published (dev skill is published manually if needed).

## Content Rules

- Written for AI agents, not humans — concise, example-heavy, no marketing.
- Keep endpoint table, curl examples, error codes, and query params up to date.
- When API endpoints change, update the skill before (or with) the code change.
- Do not include endpoints that aren't deployed yet.
