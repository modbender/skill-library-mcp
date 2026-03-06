# Changelog

All notable changes to the BotSee Claude Code Skill are documented here.

## [0.2.5] - 2026-02-24

### Security

- Removed passive API key detection from SKILL.md to eliminate prompt injection vector;
  keys are now retrieved programmatically via /botsee signup-status
- Removed self-update mechanism (cmd_update, download_github_release, install_update)
  to eliminate supply chain risk from unverified GitHub downloads; updates are handled
  via the plugin marketplace

## [0.2.4] - 2026-02-22

### Added

- `results-keyword-opportunities` command: surfaces questions where your brand is missing or ranks poorly in AI responses, with per-provider breakdown, mention rates, rank data, and the exact search keywords each AI used
- `results-source-opportunities` command: returns sources AI cited in responses where your brand was NOT mentioned — ideal targets for content and link-building campaigns
- `BOTSEE_BASE_URL` environment variable override for `botsee.py`, enabling local development and staging environment testing without code changes

### Changed

- Both new opportunity commands accept an `analysis_uuid` argument consistent with other `results-*` commands
- `results-keyword-opportunities` supports `--threshold` (0.0–1.0) and `--rank-threshold` (integer) flags for tunable filtering

## [0.2.3] - 2026-02-20

### Added

- Plugin packaging structure for Claude plugin directory submission

### Fixed

- Clarified setup URL extraction instructions in signup flows to reduce user confusion during onboarding (#5)

## [0.2.2] - 2026-02-19

### Added

- Setup URL caching: signup URL is stored locally so users do not need to re-run the signup command after returning (#3)
- Improved signup error messages with clearer next-step guidance (#3)

### Changed

- Updated README with correct version numbers, pricing information, and homepage content (#4)

## [0.2.1] - 2026-02-18

### Changed

- Simplified USDC payment flow: USDC signup is now a standalone path independent of the credit card flow (#2)
- Streamlined x402 payment steps — fewer round trips required to complete USDC-based signups

## [0.2.0] - 2026-02-17

### Changed

- Full redesign for non-interactive Claude Code agent usage (#1)
- All commands now accept arguments via flags — no interactive prompts or user input required
- Updated CLI to match full API parity across sites, personas, questions, and results endpoints

## [0.1.0] - 2026-02-11

### Added

- Initial release of the BotSee Claude Code Skill
- Commands for signup (credit card and USDC/x402), site creation, analysis, and content generation
- Support for customer types, personas, and question management
- Results commands: competitors, keywords, sources, and raw AI responses
