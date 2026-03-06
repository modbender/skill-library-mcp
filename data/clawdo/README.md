# clawdo ClawHub Skill Package

This folder contains the minimal ClawHub skill package for `clawdo`.

## Contents

- **SKILL.md** - ClawHub skill manifest + documentation
- **LICENSE** - MIT license

## Publishing

This folder is automatically published to ClawHub when a GitHub release is created.

### Automatic (via GitHub Actions)

1. Create a GitHub release (e.g., `v1.1.0`)
2. GitHub Actions automatically:
   - Publishes npm package
   - Publishes this `skill/` folder to ClawHub

### Manual (for testing)

```bash
# From repo root
clawhub login
clawhub publish ./skill \
  --slug clawdo \
  --name "clawdo - Task Queue" \
  --version 1.1.0 \
  --changelog "Release notes"
```

## Users Install Via

```bash
# In OpenClaw
clawhub install clawdo

# Or npm directly
npm install -g clawdo
```

## Updating

When CLI changes:
1. Update `skill/SKILL.md` in same commit as code changes
2. Commit atomically: `git commit -m "feat: add feature + update skill docs"`
3. Create release: workflow auto-publishes to npm + ClawHub

## Size

This minimal package (~7 KB) contains only documentation and license.
The actual CLI tool is installed via `npm install -g clawdo`.
