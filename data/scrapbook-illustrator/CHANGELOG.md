# Changelog

## [1.3.0] - 2026-02-18
### Changed
- Step 3: image generation now runs in parallel (all images launched simultaneously)
- Explicit instruction for agents to use concurrent exec calls in a single tool-use turn
- Reduces total generation time from N×30s to ~30s regardless of image count

## [1.2.0] - 2026-02-18
### Added
- OpenRouter provider support (auto-detects from available keys, GLM preferred)
- `--provider` flag to override auto-detection
- `--model` flag for OpenRouter model selection (default: `openai/gpt-5-image-mini`)
- Margin guard for OpenRouter prompts — prevents edge clipping (center 80% constraint)
- Per-image cost display (GLM: ¥ pricing, OpenRouter: USD from usage.cost)
- 7 supported languages: zh, en, ja, ko, fr, de, es
- Setup section with dual-provider configuration docs
- Step 0: API key validation before proceeding
### Changed
- `generate.py` synced from glm-image v1.8.0 (372 lines, full feature parity)
- `language` parameter now required (was optional with zh default)
- SKILL.md rewritten to document both providers

## [1.1.0] - 2026-02-17
### Added
- Bundled `scripts/generate.py` from glm-image — no separate skill dependency needed
- `language` input parameter: `zh` (Chinese, default) or `en` (English) — controls text language in generated images
- skill.yml with display_name "Scrapbook-Style Illustration Inserter", attribution, triggers
- README.md
- Formal Inputs section (article, image_count, orientation)
- Step 1 input validation (200-word minimum check)
- glm-image failure handling (continue on single failure, abort only if all fail)
- Anchor-not-found fallback (nearest paragraph break)
- Edge cases section
- Agent Owner, Success Criteria, Configuration sections
- Attribution to ViffyGwaanl
### Fixed
- Removed hardcoded ~/.claude/skills/ path — now invokes glm-image skill by name
- Fixed step numbering mismatch (Workflow list aligned with Step N sections)

## [1.0.0] - 2026-02-01
### Added
- Initial release by ViffyGwaanl
- Scrapbook-style illustration workflow
- references/scrapbook-prompt.md system prompt
