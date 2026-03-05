# Changelog

All notable changes to AgentMailGuard are documented here.

## [1.4.0] — 2026-02-27

### Added
- 14 new injection detection patterns (roleplay, hypothetical, output manipulation, broader override variants)
- 3 new spaceless patterns for obfuscation-resistant detection
- Benchmarked against 17,980 samples: 98.7% precision, 19.2% recall, 32.1% F1

## [1.3.0] — 2026-02-22

### Changed
- **Removed dead code** — `detect_flags()` removed from `sanitize_core.py` (unused; `sanitize_text()` handles all detection internally).
- **Flag deduplication** — Replaced O(n²) `if f not in flags` list scans with `dict.fromkeys()` across all modules.
- **Contacts cache optimization** — Contacts data normalized to lowercase `set`s on load instead of rebuilding lowercase lists on every `classify_sender()` call.
- **Test fixtures** — Replaced module-level side effects in `conftest.py` with a proper session-scoped `autouse` pytest fixture with cleanup.
- **Package structure** — Added `[tool.setuptools] py-modules` to `pyproject.toml` so `pip install .` works correctly.

### Fixed
- README: corrected base64 blob threshold from ">100 chars" to ">40 chars".

## [1.2.0] — 2026-02-22

### Added
- Recursive HTML entity decoding (defeats nested `&#38;#105;` tricks).
- Full sanitization pipeline applied to all text fields (subject, body, calendar title/description/location).
- Emoji and symbol stripping in fuzzy detection (`normalize_for_detection`).
- Markdown code block detection and stripping (fenced + inline).
- Hex string detection and stripping.
- Data URI detection and stripping.
- Standard markdown hyperlink stripping.
- Spaced-text bypass fix (collapses `i g n o r e` → `ignore`).
- Cross-field injection detection (split payloads across subject + body).
- Reference-style markdown image/link stripping.
- Zalgo text (combining character) stripping for detection.
- Additional LLM delimiter patterns (`<|system|>`, `<|user|>`, `<|assistant|>`).
- Base64 threshold lowered from 100 to 40 characters.

### Changed
- Pipeline reordering: pre-strip detection runs before HTML stripping to catch patterns destroyed by tag removal.
- Fuzzy regex matching for injection patterns.

## [1.0.0] — 2026-02-21

### Added
- Initial release.
- Email sanitization: HTML stripping, invisible unicode removal, NFKC normalization.
- Prompt injection detection (13+ patterns).
- Markdown image exfiltration blocking.
- Base64 blob stripping.
- Sender reputation classification via `contacts.json`.
- Calendar event sanitization (`cal_sanitizer.py`).
- Audit logging with monthly JSONL rotation.
- Body truncation (2000 char cap).
- Shell wrappers for `gog` CLI integration.
- 48 tests covering 11+ attack vectors.
