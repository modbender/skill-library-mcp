# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [0.1.1] - 2026-02-09
### Added
- Add `SKILL.md` to the public repository so the package can be distributed and indexed explicitly as a Skill.
- Add bilingual (Chinese/English) Skill description emphasizing automation workflow and model-agnostic design.

### Notes
- No runtime behavior changes; this is a distribution/documentation release.

## [0.1.0] - 2026-02-09
### Added
- Initial public CLI package structure with `pyproject.toml` and console entrypoint `ppt-ooxml-tool`.
- Core PPT OOXML workflow commands:
  - `help`, `unpack`, `collect`, `apply`, `normalize`, `validate`, `repack`.
- Interop-focused commands:
  - `workflow` for one-command end-to-end pipeline.
  - `runfile` for JSON job-spec execution.
- Machine-readable output mode:
  - Global `--json` flag for structured integration responses.
- Bilingual help output:
  - `help --lang zh|en|both`.
- Language-to-font presets:
  - `en -> Calibri`
  - `ja -> Yu Gothic`
  - `zh-cn -> Microsoft YaHei`
  - `zh-tw -> Microsoft JhengHei`
  - `ko -> Malgun Gothic`
  - `ar -> Tahoma`
- Packaging and repository assets:
  - `README.md`, `LICENSE`, example glossary and job files.
  - GitHub Actions smoke-test workflow.

### Notes
- The CLI is model-agnostic: translation text generation is provided by the caller/toolchain.
