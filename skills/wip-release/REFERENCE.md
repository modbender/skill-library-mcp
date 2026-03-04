###### WIP Computer
# wip-release ... Reference

Detailed usage, pipeline steps, flags, auth, and module API.

## Usage

Run from inside any repo:

```bash
wip-release patch                    # 1.0.0 -> 1.0.1
wip-release minor                    # 1.0.0 -> 1.1.0
wip-release major                    # 1.0.0 -> 2.0.0

wip-release patch --notes="fix auth config"   # with changelog note
wip-release minor --dry-run                    # preview, no changes
wip-release patch --no-publish                 # bump + tag only
```

## What It Does

```
  wip-grok: 1.0.0 -> 1.0.1 (patch)
  ────────────────────────────────────────
  ✓ package.json -> 1.0.1
  ✓ SKILL.md -> 1.0.1
  ✓ CHANGELOG.md updated
  ✓ Committed and tagged v1.0.1
  ✓ Pushed to remote
  ✓ Published to npm
  ✓ Published to GitHub Packages
  ✓ GitHub release v1.0.1 created
  ✓ Published to ClawHub

  Done. wip-grok v1.0.1 released.
```

## Pipeline Steps

1. **Bump `package.json`** ... patch, minor, or major
2. **Sync `SKILL.md`** ... updates version in YAML frontmatter (if file exists)
3. **Update `CHANGELOG.md`** ... prepends new version entry with date and notes
4. **Git commit + tag** ... commits changed files, creates `vX.Y.Z` tag
5. **Push** ... pushes commit and tag to remote
6. **npm publish** ... publishes to npmjs.com (auth via 1Password)
7. **GitHub Packages** ... publishes to npm.pkg.github.com
8. **GitHub release** ... creates release with changelog notes
9. **ClawHub publish** ... publishes skill to ClawHub (if SKILL.md exists)

## Flags

| Flag | What |
|------|------|
| `--notes="text"` | Changelog entry text |
| `--dry-run` | Show what would happen, change nothing |
| `--no-publish` | Bump + tag only, skip npm and GitHub release |

## Auth

npm token is fetched from 1Password at publish time. No `.npmrc` files stored. No credentials in repos.

Requires:
- `op` CLI installed and configured
- 1Password SA token at `~/.openclaw/secrets/op-sa-token`
- "npm Token" item in "Agent Secrets" vault
- `gh` CLI authenticated (for GitHub Packages and releases)
- `clawhub` CLI authenticated (for ClawHub skill publishing)

## As a Module

```javascript
import { release, detectCurrentVersion, bumpSemver } from '@wipcomputer/wip-release';

const current = detectCurrentVersion('/path/to/repo');
const next = bumpSemver(current, 'minor');
console.log(`${current} -> ${next}`);

await release({
  repoPath: '/path/to/repo',
  level: 'patch',
  notes: 'fix auth',
  dryRun: false,
  noPublish: false,
});
```

## Exports

| Function | What |
|----------|------|
| `release({ repoPath, level, notes, dryRun, noPublish })` | Full pipeline |
| `detectCurrentVersion(repoPath)` | Read version from package.json |
| `bumpSemver(version, level)` | Bump a semver string |
| `syncSkillVersion(repoPath, newVersion)` | Update SKILL.md frontmatter |
| `updateChangelog(repoPath, newVersion, notes)` | Prepend to CHANGELOG.md |
| `publishNpm(repoPath)` | Publish to npmjs.com |
| `publishGitHubPackages(repoPath)` | Publish to npm.pkg.github.com |
| `createGitHubRelease(repoPath, newVersion, notes, currentVersion)` | Create GitHub release with rich notes |
| `buildReleaseNotes(repoPath, currentVersion, newVersion, notes)` | Generate detailed release notes |
| `publishClawHub(repoPath, newVersion, notes)` | Publish skill to ClawHub |
