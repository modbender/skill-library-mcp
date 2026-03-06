# Changelog

## 1.0.3 - 2026-02-18

- Re-validated `markdown_url` entries loaded from index JSON to ensure only `https://docs.openclaw.ai` is fetchable.
- Added final trusted-host guard before network fetch in `fetch_doc_markdown.py`.
- Added smoke-test scenario with malicious index entry to prevent off-domain regression.
- Added root-execution guard in smoke tests.
- Bumped network script user agent to `docclaw/1.0.3`.

## 1.0.2 - 2026-02-18

- Removed `OPENCLAW_DOCS_LOCAL_PATHS` environment override from local-doc discovery.
- Kept local docs fallback limited to binary-derived and known default install paths.
- Bumped network script user agent to `docclaw/1.0.2`.

## 1.0.1 - 2026-02-18

- Added release/version section to `SKILL.md`.
- Added packaging/submission guidance for deterministic `.skill` archives.
- Standardized Python script user agent to `docclaw/1.0.1`.
- Renamed smoke test labels from `openclaw-docs` to `docclaw`.
- Restricted docs root to `https://docs.openclaw.ai` in network scripts.
- Blocked full URL input in `fetch_doc_markdown.py` (slug/title only).
- Removed custom docs-root environment override guidance from docs.

## 1.0.0 - 2026-02-18

- Initial DocClaw release with:
  - live docs search workflow (`openclaw docs`)
  - docs index refresh script
  - markdown fetch script
  - local docs discovery fallback
  - smoke tests
