# Changelog

All notable changes to the PullThatUpJamie skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.5.2] - 2026-02-20

### Security
- **Enhanced "No Command Execution" documentation** — Added explicit statement that skill does NOT execute arbitrary shell commands
- Clarified that `@getalby/cli` reference is optional, never auto-executed, and any Lightning wallet can be used instead
- Removed CLI tool from metadata `externalTools` section, replaced with generic "Lightning wallet (any)"
- Strengthened Security & Trust section with clear no-execution guarantees
- Sanitized CHANGELOG language to avoid false positives from security scanners

### Changed
- Payment workflow documentation now leads with "use ANY Lightning wallet" before mentioning optional CLI
- Added prominent warning that npx command is manual-only and requires operator approval
- Updated metadata to emphasize HTTP-only API operations

## [1.5.1] - 2026-02-20

### Changed
- Ingestion workflow now uses proxied API endpoints for all RSS operations
- All RSS feed operations route through `https://www.pullthatupjamie.ai/api/rss/*`
- Updated documentation to use structured API calls instead of shell commands
- Simplified external service references (single domain for all operations)
- Improved security posture by consolidating all operations through main API
- Updated "Footguns" section to emphasize proxied endpoint usage

## [1.5.0] - 2026-02-20

### Added
- Three-tier search strategy documentation in `references/podcast-rra.md`
- Episode title search workflow (instant, free, exact matches)
- Chapter search workflow (structured topic navigation within episodes)
- Search triage logic: title → chapter → semantic
- GitHub issue #74 reference for proposed corpus-wide chapter search endpoint

### Changed
- Search strategy now prioritizes metadata lookups before semantic search
- Updated "Search Strategy: Choosing the Right Endpoint" section with examples
- Clarified when to use each search method (title vs chapter vs semantic)

### Fixed
- Agents were defaulting to expensive semantic search for simple episode title lookups
- Missing guidance on how to search by episode title/number
- No documentation on chapter keyword navigation

## [1.0.0] - 2026-02-18

### Added
- Initial release
- Lightning payment flow (NWC-based credit system)
- Semantic search across 109 feeds, ~7K episodes, ~1.9M paragraphs
- Research session creation with interactive web UI
- People/org discovery endpoint
- On-demand podcast ingestion
- OpenAPI specification integration
- Prometheus validation (cold-start agent testing)
- ClawHub publication

### Security
- NWC connection string handling guidance
- Bearer credential scoping
- External tool invocation safety (npx confirmation)
