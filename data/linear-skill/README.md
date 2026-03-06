# Linear Skill (OpenClaw Hub + Claude Code)

Manage Linear issues and projects with the bundled Node CLI (`scripts/linear-cli.js`).

## Security/Runtime Summary

- Runtime: local Node.js script in this repo
- Dependency: `@linear/sdk` (installed under `scripts/`)
- Credential: `LINEAR_API_KEY`
- API scope: Linear GraphQL via official SDK (`https://api.linear.app/graphql`)
- Source: [github.com/MaTriXy/linear-skill](https://github.com/MaTriXy/linear-skill)

## Install

```bash
git clone https://github.com/MaTriXy/linear-skill.git
cd linear-skill/scripts
npm install
```

## Credentials

Create a personal API key in Linear, then set:

```bash
export LINEAR_API_KEY="lin_api_..."
```

## Usage

```bash
node ./scripts/linear-cli.js teams
node ./scripts/linear-cli.js projects
node ./scripts/linear-cli.js issues
node ./scripts/linear-cli.js issue ENG-123
node ./scripts/linear-cli.js createIssue "Title" "Description" "team-id" '{"priority":2}'
node ./scripts/linear-cli.js updateIssue "issue-id" '{"stateId":"state-id"}'
```

## Notes

- The skill package includes the CLI source at `scripts/linear-cli.js`.
- If you use OpenClaw/Grace skill settings, set `skills.entries.linear.apiKey` to map into `LINEAR_API_KEY`.
- `SKILL.md` includes machine-readable metadata for install requirements and credential declaration.
