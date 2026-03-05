# Skill: Repo Audit Preflight

## Purpose
Prevent hallucinations during repo audits.

## Checklist
- curl -I https://github.com
- export GIT_TERMINAL_PROMPT=0
- git ls-remote <repo>
- clone only if ls-remote succeeds
