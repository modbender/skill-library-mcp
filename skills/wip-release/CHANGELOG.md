# Changelog







## 1.2.4 (2026-02-21)

Align description across all sources

## 1.2.3 (2026-02-21)

Fix npm bin entry: remove ./ prefix so npx wip-release works globally

## 1.2.2 (2026-02-21)

Fix ClawHub display name and slug detection. Harden command injection fix.

## 1.2.0 (2026-02-21)

Add ClawHub publish as step 9 in release pipeline. Fix command injection by replacing execSync with execFileSync argument arrays. Declare required binaries and secrets in SKILL.md metadata.

## 1.1.1 (2026-02-21)

Fix npm bin entry: rename cli.mjs to cli.js

## 1.1.0 (2026-02-21)

Rich release notes, agent-driven install prompt, REFERENCE.md

## 1.0.0 (2026-02-21)

Initial release. Local release pipeline tool.

- `release()` ... full pipeline: bump, changelog, skill sync, commit, tag, publish
- `detectCurrentVersion()` ... read version from package.json
- `syncSkillVersion()` ... update SKILL.md frontmatter
- `updateChangelog()` ... prepend version entry
- `publishNpm()` ... npm publish via 1Password
- `publishGitHubPackages()` ... GitHub Packages publish
- `createGitHubRelease()` ... gh release create

CLI: `wip-release patch|minor|major [--notes --dry-run --no-publish]`
