---
name: WIP.release
version: 1.2.4
description: One-command release pipeline. Bumps version, updates changelog + SKILL.md, publishes to npm + GitHub.
homepage: https://github.com/wipcomputer/wip-release
metadata:
  category: dev-tools
  capabilities:
    - version-bump
    - changelog-update
    - skill-sync
    - npm-publish
    - github-release
  dependencies: []
  interface: CLI
  requires:
    binaries: [git, npm, gh, op, clawhub]
    secrets:
      - path: ~/.openclaw/secrets/op-sa-token
        description: 1Password service account token
      - vault: Agent Secrets
        item: npm Token
        description: npm publish token
openclaw:
  emoji: "🚀"
  install:
    env: []
author:
  name: Parker Todd Brooks
---

# wip-release

Local release pipeline. One command bumps version, updates all docs, publishes everywhere.

## When to Use This Skill

**Use wip-release for:**
- Releasing a new version of any @wipcomputer package
- After merging a PR to main and you need to publish
- Bumping version + changelog + SKILL.md in one step

**Use --dry-run for:**
- Previewing what a release would do before committing

**Use --no-publish for:**
- Bumping version and tagging without publishing to registries

### Do NOT Use For

- Pre-release / alpha versions (not yet supported)
- Repos without a package.json

## API Reference

### CLI

```bash
wip-release patch --notes="fix X"    # full pipeline
wip-release minor --dry-run          # preview only
wip-release major --no-publish       # bump + tag only
```

### Module

```javascript
import { release, detectCurrentVersion, bumpSemver, syncSkillVersion } from '@wipcomputer/wip-release';

await release({ repoPath: '.', level: 'patch', notes: 'fix', dryRun: false, noPublish: false });
```

## Troubleshooting

### "Could not fetch npm token from 1Password"
Check that `~/.openclaw/secrets/op-sa-token` exists and `op` CLI is installed.

### "Push failed"
Branch protection may prevent direct pushes. Make sure you're on main after merging a PR.

### SKILL.md not updated
Only updates if the file has a YAML frontmatter `version:` field between `---` markers.
