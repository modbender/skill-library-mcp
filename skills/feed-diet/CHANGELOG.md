# Changelog

## v0.1.1 — 2026-02-16

### Added
- Discord v2 delivery guidance in `SKILL.md` for OpenClaw v2026.2.14+:
  - Compact first response with key diet insights
  - Component-style quick actions
  - Numbered fallback when components are unavailable
- `discord` and `discord-v2` tags in skill metadata

### Changed
- README: added "OpenClaw Discord v2 Ready" compatibility section.
- Script and metadata versions bumped to `0.1.1`.
- README/sample output version strings updated to `0.1.1`.

### Fixed
- `classify.sh`: replaced hand-built JSON request/payload assembly with `jq -n --arg` construction.
- `classify.sh`: LLM request bodies now built via jq and parsed via jq for safer JSON handling.
- `feed-diet.sh`: fallback category assignment now uses jq JSON merge instead of ad-hoc Python mutation.

## v0.1.0 — 2026-02-15

### 🎉 Initial Release

**Feed Diet** — Audit your information diet across HN and RSS feeds.

#### Features
- **HN Audit:** Analyze any Hacker News user's submitted stories by category
- **OPML/RSS Audit:** Parse OPML files, fetch recent items from each feed, classify them
- **Beautiful Reports:** Markdown tables with ASCII bar charts (█ blocks), emoji, percentages
- **7 content categories:** deep-technical, news, opinion, drama, entertainment, tutorial, meta
- **Surprising Finds:** Automated insights ("62% drama — do you really want that?")
- **Recommendations:** Personalized suggestions based on your diet composition
- **Weekly Digest Mode:** Filter content by your goals, get a curated reading list
- **Batch LLM classification:** 25 items per API call for token efficiency
- **Keyword fallback:** Works without an LLM API key (rule-based classification)
- **Parallel fetching:** Concurrent HN API calls for speed

#### Data Sources
- ✅ Hacker News (username → stories)
- ✅ RSS/Atom feeds via OPML

#### Coming in v0.1.2
- Reddit user history
- YouTube subscription analysis
- Feed-by-feed quality scores for OPML
- Trend analysis (how your diet changed over time)
