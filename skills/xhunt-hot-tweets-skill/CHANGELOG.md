# Changelog

## 2.0.1 - 2026-02-26

- Added publishing-ready docs (`README.md`, `README.zh-CN.md`).
- Added agent metadata file (`agents/openai.yaml`).
- Hardened failure handling in `SKILL.md`:
  - explicit full-failure response when both extraction paths fail
  - explicit notice when filtered results are fewer than requested limit
- Prepared ClawHub publish command examples.

## 2.0.0 - 2026-02-26

- Initial release of XHunt hot tweets extraction skill.
- Supports `group`, `hours`, `tag`, `limit`, and filtering mode.
- Enforces stable 3-line output per item with Chinese summaries.
