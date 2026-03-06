# Changelog

## 2.0.2 - 2026-02-26

- Updated README docs to focus on user value and installation only.
- Removed ClawHub publishing instructions from README files.
- Aligned skill naming in docs with repository name (`xhunt-hot-tweets-skill`).
- Added clear install guides for both GitHub and ClawHub paths.

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
