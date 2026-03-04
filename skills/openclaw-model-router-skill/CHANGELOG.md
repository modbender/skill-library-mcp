# Changelog

## 2026-02-28

- Scaffolded v1 router core (`parse -> validate -> switch -> verify -> execute`)
- Added retry + fallback behavior
- Added JSONL route logging
- Added sample `router.config.json`
- Added Node test coverage for parser, switch, success and fallback paths
- Added operator runbook
- Added strict config validation (`validateConfig`) to fail fast on malformed `prefixMap`/`retry`.
- Added explicit `FALLBACK_EXECUTION_FAILED` wrapping + failure log when fallback execution also fails.
- Expanded tests for config validation and fallback failure behavior.
