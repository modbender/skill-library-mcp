# Publishing AISP Skill to ClawHub

Steps so agents can install via `clawhub install aisp`.

## Prerequisites

- GitHub account (at least 1 week old; required by ClawHub)
- Node.js / pnpm

## 1. Install ClawHub CLI

```bash
npm i -g clawhub
# or
pnpm add -g clawhub
```

## 2. Log in

```bash
clawhub login
```

Opens a browser to authenticate with ClawHub. Or use a token:

```bash
clawhub login --token <your-token>
```

## 3. Publish from skill directory

From the project root:

```bash
clawhub publish ./skills/aisp --slug aisp --name "AISP" --version 1.0.0 --tags latest
```

Or from inside the skill folder:

```bash
cd skills/aisp
clawhub publish . --slug aisp --name "AISP" --version 1.0.0 --tags latest
```

## 4. Sync (alternative: publish all skills)

To scan and publish all skills in the workspace:

```bash
clawhub sync --all
```

This finds skills under `./skills` (or `~/.openclaw/skills`) and publishes them.

## 5. Publish updates

When changing the skill:

1. Bump version in `SKILL.md` frontmatter (e.g. `1.0.0` → `1.0.1`)
2. Add an entry to `CHANGELOG.md`
3. Re-run publish:

```bash
clawhub publish ./skills/aisp --slug aisp --name "AISP" --version 1.0.1 --changelog "Fix foo" --tags latest
```

Or use sync with bump:

```bash
clawhub sync --all --bump patch --changelog "Fix foo"
```

## 6. Install (for others)

After publishing, agents and users can install with:

```bash
clawhub install aisp
```

## References

- [ClawHub docs](https://docs.openclaw.ai/tools/clawhub)
- [ClawHub site](https://clawhub.ai)
