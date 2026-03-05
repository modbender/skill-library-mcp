# Changelog

All notable changes to HabitFlow skill will be documented in this file.

## [1.5.4] - 2026-02-09

### Fixed
- Add explicit persona ID validation instructions in SKILL.md to prevent path traversal via `activePersona` config field

## [1.5.3] - 2026-02-09

### Changed
- Weekly check-in moved to Monday 8am (configurable)
- Calculate weekly stats using calendar weeks (Mon-Sun)

## [1.5.2] - 2026-02-06

### Fixed
- Fix path traversal vulnerability in persona switching: added explicit ID validation against allowed list
- Fix command injection in `examples/utils.sh`: replaced `eval` with direct command execution using array arguments
- Softened imperative language in SKILL.md to avoid prompt injection classification by security scanners

## [1.5.0] - 2026-02-06

### Changed - Security & Transparency Improvements

#### Cron Message Refactoring
- Replaced multi-paragraph AI instructions in cron `--message` with minimal one-line invocations
- Created `scripts/run_reminder.ts` - deterministic wrapper that checks completion and outputs JSON
- Created `scripts/run_coaching.ts` - deterministic wrapper for coaching analysis output
- Removed Portuguese-language conditional logic from cron messages
- Removed embedded tool-use directives (Read tool, JSON parsing) from cron messages

#### Opt-in Cron Job Creation
- `init_skill.ts` no longer auto-creates coaching cron jobs on install
- Users must explicitly run `sync_reminders.ts sync-coaching` to enable coaching
- Updated SKILL.md documentation to reflect opt-in behavior

#### Asset Management
- Moved persona PNGs to Git LFS (reduces high-entropy file count)
- Removed `heatmap_whatsapp.png` sample image from repo root
- Fixed broken image reference in README.md

#### Documentation
- Added "Handling Automated Task Output" section to SKILL.md
- Documented JSON output format for `run_reminder.ts` and `run_coaching.ts`

## [1.4.1] - 2026-02-04

### Changed
- Fix: `get_stats` now includes data through today
- Feat: skip reminders when habit already completed today

## [1.4.0] - 2026-01-29

### Changed - Agent Skills Specification Compliance

#### Frontmatter Compliance
- ✅ Fixed metadata format to single-line JSON (critical parser requirement)
- ✅ Added `license: MIT` field
- ✅ Added `compatibility` field documenting Node.js 18+ requirement
- ✅ Added `user-invocable: true` explicitly
- ✅ Added `metadata.moltbot.install` for UI install button integration
- ✅ Added `metadata.moltbot.requires.bins` for dependency checking
- ✅ Kept `homepage` field (valid molt.bot field, displays in macOS Skills UI)

#### Documentation Structure & Progressive Disclosure
- ✅ Reduced SKILL.md from 749 lines to 426 lines (43% reduction)
- ✅ Achieved <500 line target per agentskills.io recommendation
- ✅ Implemented progressive disclosure pattern

#### New Reference Files
- ✅ Created `references/EXAMPLES.md` (191 lines) - 10 conversation examples
- ✅ Created `references/COMMANDS.md` (151 lines) - Complete scripts reference
- ✅ Created `references/REMINDERS.md` (81 lines) - Reminder technical documentation
- ✅ Created `references/DATA.md` (59 lines) - Data storage reference

#### Enhanced Reference Files
- ✅ Enhanced `references/atomic-habits-coaching.md` with coaching guidelines by streak level
- ✅ Added example responses for different scenarios

#### SKILL.md Optimizations
- ✅ Moved detailed conversation examples to EXAMPLES.md
- ✅ Moved technical reminder implementation to REMINDERS.md
- ✅ Moved complete command reference to COMMANDS.md
- ✅ Moved data storage details to DATA.md
- ✅ Moved coaching guidelines to atomic-habits-coaching.md
- ✅ Condensed first-time setup section
- ✅ Added cross-references throughout
- ✅ Removed redundant sections

#### Compliance Status
- ✅ Fully compliant with agentskills.io specification
- ✅ Fully compliant with molt.bot/docs/tools/skills specification
- ✅ Install button integration enabled in molt.bot UI
- ✅ All content preserved (reorganized, not removed)
- ✅ Functionality unchanged

## [1.2.0] - 2026-01-28

### Added - Canvas Dashboard UI (Phase 3)

#### Visualization Components
- ✅ **Streak Chart** - Bar chart showing current vs longest streak with quality indicators
- ✅ **Completion Heatmap** - GitHub-style calendar grid showing daily completions (90 days)
- ✅ **Weekly Trends** - Line chart showing completion rate over time (8 weeks)
- ✅ **Multi-Habit Dashboard** - Overview showing all active habits with mini indicators

#### Canvas Dashboard CLI
- `assets/canvas-dashboard.ts` - Main entry point script with Commander.js interface
- Four subcommands: `streak`, `heatmap`, `trends`, `dashboard`
- Theme support: light/dark mode
- PNG output format
- Configurable date ranges and periods

#### Data Aggregation Layer
- `assets/utils/data-aggregator.ts` - Loads and transforms habit data for visualizations
- Reuses existing infrastructure (storage, streak calculation, daily completion logic)
- Aggregation functions for streak data, heatmap data, weekly trends, multi-habit data

#### Chart Rendering
- `assets/utils/chart-renderer.ts` - Canvas drawing utilities using @napi-rs/canvas
- Bar chart, line chart, and heatmap rendering functions
- Grid lines and axis labels
- Customizable color schemes

#### Color Schemes
- `assets/utils/color-schemes.ts` - Unified color palettes
- Quality colors (perfect, excellent, good, fair)
- Status colors (completed, partial, missed, skipped)
- Category colors (health, fitness, mindfulness, productivity, social, learning, other)

#### Testing
- `examples/test-canvas.sh` - Automated test script for all visualizations
- Handles test data generation if no habits exist
- Validates all four visualization types

#### Documentation
- Updated `SKILL.md` with Canvas visualization commands
- Updated `README.md` features list and directory structure
- Added Canvas Dashboard section to Quick Start

### Dependencies Added
- `@napi-rs/canvas` v0.1.44 - Native Canvas API for Node.js

### Technical Notes
- Canvas-first strategy for future compatibility with clawdbot Mac app
- Static visualizations (non-interactive) in Phase 3
- Graceful degradation: works in Claude Code, clawdbot apps
- WhatsApp reminders use text summaries (no image support)

## [1.0.0] - 2026-01-28

### Added - MVP Release (Phase 1)

#### Core Features
- ✅ Habit creation and management (CRUD operations)
- ✅ Natural language logging with chrono-node date parsing
- ✅ String similarity matching for habit names
- ✅ Streak calculation with 1-day forgiveness mechanism
- ✅ Smart reminders via clawdbot cron jobs → WhatsApp delivery
- ✅ Basic statistics (completion rate, trends, best day of week)
- ✅ Flex persona (default neutral professional tone)

#### Scripts
- `manage_habit.ts` - Create, update, archive, delete habits
- `log_habit.ts` - Record single or bulk completions
- `view_habits.ts` - Query and list habits (JSON, markdown, text)
- `calculate_streaks.ts` - Compute streaks with forgiveness
- `get_stats.ts` - Generate completion statistics
- `parse_natural_language.ts` - Parse natural language to structured data
- `sync_reminders.ts` - Sync habit reminders to cron jobs

#### Data Storage
- JSON-based storage in `~/clawd/habit-flow-data/`
- JSONL format for logs (one file per habit per year)
- Config file for user settings (timezone, persona, userId)

#### Documentation
- `SKILL.md` - Complete skill documentation
- `README.md` - Project overview and architecture
- `QUICKSTART.md` - 5-minute getting started guide
- `references/personas.md` - All persona definitions
- `references/atomic-habits-coaching.md` - 9 coaching techniques
- `references/data-schema.md` - Data structure reference

#### Examples
- `examples/demo.sh` - Full demonstration script
- `examples/utils.sh` - Utility functions for shell usage

#### Core Algorithms
- Streak calculation directly ported from original TypeScript codebase
- Daily completion logic (last log per day)
- Forgiveness mechanism (1 missed day allowed)
- Quality grading (perfect, excellent, good, fair)

### Technical Details

**Dependencies:**
- chrono-node: ^2.7.0 (natural language date parsing)
- string-similarity: ^4.0.4 (fuzzy habit name matching)
- zod: ^3.22.0 (validation)
- commander: ^11.0.0 (CLI interface)
- tsx: ^4.0.0 (TypeScript execution)
- typescript: ^5.3.0

**Architecture:**
- TypeScript/JavaScript (Node.js native)
- Reuses original HabitFlow streak calculation algorithm
- No database required (JSON/JSONL storage)
- CLI-first design for skill integration

## [1.1.0] - 2026-01-28

### Added - Phase 2: Multi-Persona Support

#### Personas
- ✅ **Coach Blaze** - Energetic sports coach with high-energy motivational style 🔥
- ✅ **Luna** - Gentle therapist with compassionate, reflective guidance 💜
- ✅ **Ava** - Curious productivity nerd focused on experiments and data 🤓
- ✅ **Max** - Chill buddy with laid-back, no-pressure vibes 😎
- ✅ **Sofi** - Zen minimalist with serene, mindful presence 🌸
- ✅ **The Monk** - Wise philosopher with intentional, profound wisdom 🧘

#### Features
- Dynamic persona loading from `config.json`
- Persona-specific communication styles (tone, vocabulary, response patterns)
- Smooth persona switching with style transitions
- Updated SKILL.md with all 6 persona definitions
- First-time setup now offers persona selection

#### Documentation Updates
- Updated README.md with all personas
- Updated roadmap (Phase 2 complete, Phase 3 in progress)
- Added persona switching instructions
- Enhanced first-time setup flow

## [1.1.1] - 2026-01-28

### Changed - SKILL.md Optimization

#### Performance
- Split persona definitions into separate files (`references/personas/{id}.md`)
- Reduced SKILL.md from 685 lines → ~515 lines
- Implemented lazy loading: only active persona loads into context
- Saves ~140 lines (~600 tokens) per skill activation

#### Structure
- Created `references/personas/` directory with 6 individual persona files:
  - `flex.md` - Professional, data-driven (default)
  - `coach-blaze.md` - Energetic sports coach 🔥
  - `luna.md` - Gentle therapist 💜
  - `ava.md` - Curious productivity nerd 🤓
  - `max.md` - Chill buddy 😎
  - `the-monk.md` - Wise minimalist 🧘
- Updated SKILL.md with dynamic persona loading logic
- Updated documentation to reflect new structure (README.md, references/personas.md)

#### Benefits
- **Context efficiency:** Agent only loads the active persona, not all 6
- **Maintainability:** Update personas independently without touching SKILL.md
- **Scalability:** Can add more personas without bloating main skill file

## [1.3.0] - 2026-01-29

### Added - Proactive Coaching Automation (Phase 3) ✅

#### Core Features
- ✅ **Milestone Celebrations** - Auto-celebrate streak milestones (7, 14, 21, 30, 100 days)
- ✅ **Risk Warnings** - Predict and warn before streaks break based on historical patterns
- ✅ **Weekly Check-ins** - Automated weekly summary with insights and coaching (Sunday 7pm)
- ✅ **Pattern Insights** - Proactively share data-driven observations
- ✅ **Image Attachments** - Canvas visualizations automatically included in messages
  - Milestone messages include streak charts
  - Risk warnings include heatmaps
  - Weekly check-ins include trends + heatmaps
  - Agent-based delivery using Read tool for images

#### Pattern Analysis
- `src/pattern-analyzer.ts` - Risk assessment, milestone detection, pattern insights
- Risk scoring algorithm (0-100 scale):
  - Missed yesterday: +40 risk
  - Tomorrow is weak day: +30 risk
  - Weekend approaching: +20 risk
  - Declining trend: +10 risk
- Pattern detection: day-of-week patterns, improvement/decline trends, consistency

#### Coaching Engine
- `src/coaching-engine.ts` - Message generation with persona integration
- `src/message-templates.ts` - Persona-specific templates for all 6 personas
- Message types: milestone, risk, weekly, insight
- Priority assignment: high (milestone, risk), medium (weekly), low (insight)

#### Proactive Coaching Script
- `scripts/proactive_coaching.ts` - CLI tool for generating messages
- Options: `--check-milestones`, `--check-risks`, `--weekly-checkin`, `--detect-insights`
- Support for `--habit-id` filtering and `--send` flag
- `--format json` for structured output with image paths
- Dry run mode (default) for testing

#### Cron Integration
- Updated `scripts/sync_reminders.ts` with `sync-coaching` command
- Daily checks (8am): milestones + risks
- Weekly check-in (Sunday 7pm): progress summary with trends
- Pattern insights (Wednesday 10am): mid-week reflection
- Cron messages instruct agent to parse JSON and display images
- Uses `--message` + `--deliver` approach for image support

#### Setup & Maintenance Tools
- `scripts/init_skill.ts` - Version-aware initialization and updates
- `scripts/check_cron_jobs.ts` - Health check with auto-repair (`--auto-fix`)
- Version tracking in `~/.clawd/habit-flow-data/.skill-version`
- Automatic cron job updates on skill version changes

#### Documentation
- `references/proactive-coaching.md` - Complete architecture documentation
- Updated `SKILL.md` with proactive coaching section
- Updated `README.md` features list
- Examples and testing instructions

#### Technical Notes
- Reuses existing infrastructure (personas, streak calculation, Canvas dashboards)
- No new dependencies required
- All analysis happens locally (privacy-first)
- Non-intrusive design (only high-value messages)

## [Unreleased] - Future Phases

### Phase 4 - Advanced Analytics (Planned)
- [ ] Time-of-day optimization (requires logTime data collection)
- [ ] Habit correlation analysis
- [ ] Adaptive technique learning (A/B testing)
- [ ] Predictive ML models for streak forecasting

### Phase 3 - Social Features (Planned)
- [ ] Multi-user support
- [ ] Accountability partners
- [ ] Group challenges
- [ ] Shared streaks

### Phase 4 - Advanced Features (Planned)
- [ ] Custom frequency patterns (e.g., 3x/week, every other day)
- [ ] Habit dependencies (do X before Y)
- [ ] Time-of-day analytics
- [ ] Predictive streak warnings

---

## Version History

### v1.0.0 (2026-01-28)
Initial MVP release with core habit tracking, natural language processing, streak calculation with forgiveness, reminders, and Flex persona coaching.
