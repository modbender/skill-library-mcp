---
name: zero2ai-security-audit
description: Security auditing for git commits, repos, and skills before publishing. Run automatically before any `git commit`, `git push`, or `clawhub publish`. Detects hardcoded secrets, API keys, tokens, absolute paths, committed node_modules, .env files, and other sensitive patterns. Use when reviewing code for security issues, pre-publishing skills, or investigating a potential secret exposure.
---

# Security Audit

Run `scripts/audit.py` before every commit, push, or skill publish. No exceptions.

## When to run

| Trigger | Command |
|---|---|
| Before `git commit` | `python3 {skill_dir}/scripts/audit.py --staged` |
| Before `git push` | `python3 {skill_dir}/scripts/audit.py --last-commit` |
| Before `clawhub publish <path>` | `python3 {skill_dir}/scripts/audit.py <skill_path>` |
| Ad-hoc scan any path | `python3 {skill_dir}/scripts/audit.py <path>` |

`{skill_dir}` = `/home/aladdin/.openclaw/workspace/skills/skill-security-audit`

## Exit codes
- `0` = clean
- `1` = HIGH or MEDIUM findings (block publish/push)
- `2` = usage error

## What it detects

| Severity | Pattern |
|---|---|
| 🔴 HIGH | API keys, secrets, passwords, JWT tokens, WooCommerce keys, AWS keys, private key blocks, bearer tokens, `.env` files |
| 🟡 MEDIUM | Absolute `/home/<user>/` paths, `/root/` paths, refresh tokens, `node_modules/` committed |
| 🔵 LOW | Hardcoded IPs, long base64 strings |

## Rules

1. **HIGH findings = hard block.** Never commit or publish with HIGH findings. Rotate any exposed secret immediately.
2. **MEDIUM findings = fix before publish.** Replace absolute paths with relative or env-var defaults. Remove `node_modules/`.
3. **LOW findings = review.** Not blocking but investigate.
4. **False positives:** If a match is a variable name or safe placeholder (not an actual value), document why it's safe in a comment and re-run.

## After finding a real secret

1. **Do NOT push the commit.** If already pushed: rotate the secret immediately, then rewrite history or delete the file from git.
2. Rotate in the provider portal (TikTok Dev, AWS IAM, WooCommerce, etc.)
3. Move to env var: `process.env.SECRET_NAME` or read from a local config file outside the repo.
4. Add the config file path to `.gitignore`.
5. Report to Aladdin immediately with severity and what was exposed.

## Skill publish checklist

Before `clawhub publish`:
- [ ] `audit.py <skill_path>` returns 0 (clean)
- [ ] `node_modules/` not present in skill folder
- [ ] No absolute paths to user home directories
- [ ] No hardcoded business-specific IDs or credentials
- [ ] `package.json` name matches skill folder name
- [ ] SKILL.md description updated if renamed
