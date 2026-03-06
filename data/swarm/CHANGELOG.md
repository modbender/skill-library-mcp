# Changelog

## [1.3.0] - 2026-02-18

### Added
- **Chain pipelines** — Multi-stage refinement pipeline for complex analysis
  - 4 stage modes: `parallel`, `single`, `fan-out`, `reduce`
  - 10 built-in perspectives: extractor, filter, enricher, analyst, synthesizer, challenger, optimizer, strategist, researcher, critic
  - 6 built-in transforms: merge, mergeUnique, best, split, passthrough, jsonParse
  - `POST /chain` — Manual pipeline from JSON definition
  - `swarm chain <file.json>` — CLI for manual chains
- **Auto-chain** — Describe a task in natural language, get an optimal pipeline
  - `POST /chain/auto` — Dynamic pipeline construction
  - `POST /chain/preview` — Dry-run to see pipeline plan without executing
  - 7 task pattern detectors (comparative, research-deep, adversarial, filter-refine, multi-perspective, opportunity, summarize)
  - 4 depth presets: quick (2 stages), standard (4), deep (5-6), exhaustive (8)
  - Smart perspective selection based on task keywords
- **Capabilities discovery** — `GET /capabilities` endpoint for orchestrator LLMs
  - Lists all execution modes, perspectives, transforms, and depth presets
  - `swarm capabilities` CLI command
- **Benchmark** — Quality comparison tool (single vs parallel vs chain)
  - `POST /benchmark` — Runs same task through all 3 modes
  - LLM-as-judge scoring on 6 dimensions (accuracy, depth, completeness, coherence, actionability, nuance)
  - Cost/quality ratio comparison table
  - Based on G-Eval/FLASK evaluation methodology
- **Worker perspective override** — Chain stages inject custom system prompts per worker

### Changed
- Client library: added `chain()`, `chainSync()`, `capabilities()` methods
- CLI help updated with chain and capabilities commands
- Daemon endpoint listing now shows all routes
- 404 response includes list of available endpoints

## [1.2.0] - 2026-02-17

### Added
- **Cost tracking & savings** — Real-time token/cost tracking across all workers
  - `swarm status` shows session cost, Opus equivalent, and savings multiplier
  - `swarm savings` — Monthly savings report (tasks, tokens, dollars saved)
  - Daily cost data persisted to `~/.config/clawdbot/swarm-metrics/daily-summary.json`
- **Task retry** — Workers auto-retry failed tasks (1 retry by default, configurable)
  - Skips retries for non-transient errors (auth, malformed, etc.)
  - Exponential backoff between attempts
- **Task timeout** — 30s default per-task timeout prevents hung workers
  - Configurable via `config.scaling.timeoutMs` or per-task `task.timeoutMs`

### Changed
- **Dead code cleanup** — Removed 7 unused files (1,300+ lines):
  `blackboard.js`, `blackboard-supabase.js`, `swarm-coordinator.js`,
  `swarm-daemon-rt.js`, `swarm-realtime.js`, `persistent-worker.js`, `code-swarm.js`
- Removed BrainDB `recallBrainDB()` from CLI and `--context` flag
- Smart research pipeline (single-phase grounding vs 3-phase fallback)
- `/status` endpoint includes `cost` object and `webSearchMode`
- Worker `getStats()` now includes token counts and cost breakdown

### Fixed
- Per-task stats (`avgTaskMs`) alongside per-request stats (`avgResponseMs`)
- Research response extraction works for both single-phase and 3-phase modes

## [1.1.1] - 2026-02-17

### Added
- **Google Search grounding** for Gemini workers — research tasks query Google natively at zero extra cost
- **Web search onboarding** — setup wizard (Step 4) asks users to enable web search during initial config
- **Per-task stats** — `avgTaskMs` in status endpoint
- **Web search status** — daemon startup and `/status` show web search mode

### Changed
- Removed BrainDB dependency from `client.js` — no external services required

## [0.3.1] - 2026-01-31

### Added
- **SKILL.md** - Agent-facing documentation for Clawdbot skill system integration
  - Mandatory usage triggers for parallel work
  - Quick reference commands
  - Survival math: 200x cost savings vs Opus

### Changed
- Updated benchmarks with verified numbers across multiple batch sizes
- README now shows accurate throughput range (14-35 tasks/sec)

### Performance (verified)
- **10 tasks**: ~700ms (14 tasks/sec)
- **30 tasks**: ~1,000ms (30 tasks/sec)
- **50 tasks**: ~1,450ms (35 tasks/sec)
- Larger batches yield higher throughput (amortizes connection overhead)

## [0.3.0] - 2026-01-31

### Added
- **Unified `swarm` CLI** - Single command for daemon management and task execution
  - `swarm start/stop/status/restart` - Daemon lifecycle
  - `swarm parallel "p1" "p2"` - Run prompts in parallel
  - `swarm research "s1" "s2" --topic "x"` - Multi-phase research
  - `swarm bench --tasks N` - Benchmark throughput
  - `swarm logs [N]` - View daemon logs
  - Auto-detects and uses daemon if running, falls back to direct execution
- **Rate limit tuning** - Increased limits for higher throughput
  - `max_concurrent_api`: 10 → 20
  - `max_nodes`: 16 → 20
  - Rate limiter: 60 → 120 burst

### Changed
- Daemon now spawns in background by default (no terminal lock)
- Improved NDJSON streaming in CLI client
- Better error handling and progress display

## [0.2.1] - 2026-01-26

### Added
- **Security Module** - Protection against prompt injection and credential exfiltration
  - All worker system prompts wrapped with security policy
  - Input scanning for injection attempts
  - Output sanitization to redact accidental credential exposure
  - Detection patterns for: instruction overrides, fake system prompts, exfiltration attempts
- **6 new security unit tests**

### Security
- Workers now refuse to output API keys, tokens, or credentials
- External content treated as DATA, not instructions
- Injection attempts like "ignore all previous instructions" are logged and ignored
- Credentials patterns (Google, OpenAI, Anthropic, GitHub, Slack) auto-redacted from output

## [0.2.0] - 2026-01-25

### Added
- **Swarm Daemon** - Long-running process with pre-warmed workers for instant TTFT
  - `swarm-daemon start/stop/status` CLI
  - `swarm` CLI client for quick requests
  - HTTP API on localhost:9999
- **User Feedback System** - Real-time progress visibility
  - Event system (`swarm:start`, `task:complete`, etc.)
  - Pretty console display with worker status
  - Streaming NDJSON responses
- **Diagnostics System** - Health checks and troubleshooting
  - `npm run diagnose` for system checks
  - Machine profiling with optimal worker recommendations
  - Auto-runs during setup
- **Test Suite** - 24 tests covering core functionality
  - Unit tests (events, display)
  - Integration tests (dispatcher, orchestration)
  - E2E tests (real API calls)
- **Immediate Acknowledgment Pattern** - UX best practice documented

### Changed
- Setup now runs diagnostics and tests automatically
- Cleaner repo structure (removed internal/marketing files)

### Performance
- **TTFT**: <10ms with daemon (vs ~500ms cold start)
- **Speedup**: 2-5x faster than sequential execution
- **6 subject research**: ~8 seconds (vs ~35 seconds sequential)

## [0.1.0] - 2026-01-25

### Added
- Initial release
- Parallel task execution with Gemini Flash workers
- Multi-phase orchestration (search → fetch → analyze)
- Support for multiple providers (Gemini, OpenAI, Anthropic, Groq)
- Code generation with CodeSwarm
- Metrics and performance tracking
