# Changelog

## [0.2.1] - 2026-03-02

Follow-up security review (see [SECURITY.md](SECURITY.md) addendum):

- Replaced "return raw output" / "return output" with passive phrasing
- Added guidance disclaimer in SKILL.md (not system overrides; platform precedence)
- Added Before installing checklist (7 steps) to README
- Manual install: preview before `--apply`
- Added Script reference section (line numbers for review)

## [0.2.0] - 2026-03-02

Security remediation (see [SECURITY.md](SECURITY.md)):

- Purge: archive by default; `--delete` for immediate removal
- Setup: preview by default; `--apply` to modify workspace
- Instructions: descriptive wording instead of prescriptive prohibitions
- Data handling: audit metadata only; rewrites use `<redacted>` for secrets
- Allowlist: prefer manual purge; path-specific patterns if exec required

---

## [0.1.0] - 2026-03-02

- Initial release: audit script, purge script, setup, verify, optimization-agent.md.
