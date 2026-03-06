# Changelog

## [1.7.3] - 2026-03-03
### Added
- Simplified installation instructions (Ask OpenClaw / CLI) to SKILL.md and README.md.

## [1.7.2] - 2026-03-03

### ✨ Features
- **Dynamic Model Registry**: Completely removed hardcoded models, display names, and costs from the Dashboard frontend (`agent-dashboard.html`) and backend (`api-server.js`).
- **Dynamic Pricing via `models-registry.json`**: Cost estimation logic (I/O) is now decoupled and driven entirely by `models-registry.json`. Updating prices (e.g., from Google/Anthropic pricing pages) or adding new models requires zero JS code changes.
- **Smart Color Theming**: Dashboard charts now automatically assign distinct colors to models based on their provider family (Google: Blues, Anthropic: Pinks/Reds, OpenAI: Greens, Local: Teals) using an intelligent palette hash algorithm, ensuring models never collide.


## [1.7.0] - 2026-03-01

### 🔒 Security (VirusTotal Review Round 2)
- **Removed hardcoded gateway restart token** from agent-dashboard.html; restart now proxied through authenticated `/ops/restart` API endpoint
- **Token no longer sent via URL query params** in API calls; switched to `Authorization: Bearer` header for all apiFetch requests
- **Token stripped from URL** immediately on page load via `history.replaceState` to prevent leakage in Referer/logs/history
- **Removed localStorage token storage** from server-monitor.html (was still present despite v1.6.0 claim)
- **Added DOMPurify** for all marked.js markdown rendering to prevent XSS via untrusted task content
- **Added `/ops/restart` server-side endpoint** that proxies to gateway hooks with env-sourced HOOK_TOKEN
- **Updated SECURITY.md** to accurately reflect auth flow, XSS mitigations, and restart architecture

## [2.1.0] - 2026-02-22

### 🎯 Dashboard UX and Information Architecture
- Added per-channel default model settings for sessions
- Added model selector dropdowns for both Sessions and Cron jobs
- Introduced task-model fit dashboard and redesigned Cron Runs view
- Added always-visible system info bar above active sessions
- Renamed product branding
- Added mobile display of `匹配` column and improved model/token visibility on smaller screens

### 💸 Cost Analytics Enhancements
- Added cron cost analysis with fixed vs variable cost trend view
- Updated card and breakdown calculations to use provider `cost.total`
- Included `cacheRead` and `cacheWrite` tokens in cost estimation
- Corrected header card totals by sourcing daily aggregates from `/ops/sessions`
- Improved model breakdown and token count consistency across panels

### ⏰ Cron and Operations Improvements
- Fixed Cron Runs panel field mapping (`name`, `last.startedAt`, `last.endedAt`)
- Improved cron/subagent naming with more user-friendly labels
- Removed duplicate cron entries and improved sorting/audit consistency

### 📱 Mobile and PWA
- Added `apple-touch-icon` PNG asset (180x180) for iOS home screen
- Added PWA icon + manifest support for Add to Home Screen flow
- Added iPhone 17 Pro targeted layout and spacing optimizations
- Added Chinese Discord channel naming support in UI lists

### 🔒 Security and Reliability Fixes
- Improved OpenClaw version detection (`2>&1` handling + `package.json` fallback)
- Ensured Discord channel names resolve fully in dashboard views
- Added API key masking improvements for `/ops/config` responses

### 🧹 Maintenance
- Removed `README-JONY.md` from repository

## [2.0.0] - 2026-02-22

### 🏗️ Architecture Overhaul
- **Session-centric design**: Replaced original 5-tab layout (Ops/Documents/APIs/Logs) with 6 operational tabs (Sessions/Cost/Cron/Quality/Audit/Config)
- **Unified pricing engine**: All cost estimates use official per-token pricing with input/output split (Claude Opus $15/$75, Gemini 3 Pro $2/$12, etc.)
- **Unified PST timezone**: Shared `getTodayPstStartIso()` helper across all endpoints
- **Auto-load keys**: Server reads `~/.openclaw/keys.env` at startup (no env vars needed in LaunchAgent)

### 📊 New: Sessions Tab (Default)
- Per-session table: model, thinking level, messages (effective/total), tokens, cost, idle rate, last active
- Real-time alerts: session errors, model waste detection, stale session warnings
- Header cards: Today Cost / Tokens / Cron Jobs / Active Sessions / Primary Model

### 💰 New: Cost Analytics
- Today's channel breakdown with model distribution bar
- All-time model breakdown with per-model cost cards
- Daily token chart (stacked by model, color-coded)
- Daily cost chart (stacked by model, dollar labels)
- Cost heatmap: model × day matrix with heat coloring
- Provider audit: OpenAI Admin API (7-day usage) + Anthropic org verification

### 📈 New: Quality Panel
- Per-session idle rate visualization (NO_REPLY + HEARTBEAT_OK percentage)
- Color-coded progress bars (green/yellow/red thresholds)
- Effective vs silent message breakdown

### 🔍 New: Config Audit Panel
- Auto-detect: Opus on high-idle channels → suggest downgrade to Sonnet
- Missing thinking level warnings
- Cost-saving recommendations with estimated savings
- Provider verification status

### ⚙️ New: Config Viewer
- Browse openclaw.json, SOUL*.md, AGENTS.md, USER.md, TOOLS.md, IDENTITY.md, HEARTBEAT.md, MEMORY.md
- API keys from keys.env with automatic masking (first 8 + last 4 chars)
- Click-to-expand accordion UI
- File size and modification time

### ⏰ Enhanced: Cron Tab
- Visual card layout replacing timeline view
- Chinese descriptions for each job (🔍 监控 OpenClaw 生态动态, 💼 AI 求职机会扫描, etc.)
- Human-readable schedules (每天 9:00, 每 2 小时, 每周五 9:00)
- Last run: time ago, duration, tokens, model
- Enable/disable status with visual indicators

### 🔐 Security
- Cookie-based auth: HttpOnly, SameSite=Strict, 30-day expiry
- Login page at `/login`, logout at `/logout`
- Key masking in config viewer (never expose full keys)

### 📱 Mobile
- PWA meta tags (apple-mobile-web-app-capable, theme-color, viewport-fit=cover)
- Safe-area padding for notched devices
- Touch targets ≥ 44px
- Responsive tab bar

### 🐛 Bug Fixes
- Fixed PST timezone calculation (was double-converting offsets)
- Fixed model distribution bar gaps (0-token models, legend inside flex container)
- Fixed cost discrepancy between endpoints (unified estimator, removed cron from channels total)
- Filtered `delivery-mirror` model from all views

### API Endpoints Added
- `GET /ops/sessions` — per-session overview with today's usage + alerts
- `GET /ops/channels` — per-channel cost/token breakdown
- `GET /ops/alltime` — historical usage with daily model breakdown
- `GET /ops/audit` — OpenAI/Anthropic official API verification
- `GET /ops/config` — config file viewer with key masking
- `GET /ops/cron` — enhanced cron job list

---

## [1.0.0] - 2026-02-21

### Initial Fork
- Forked from [karem505/openclaw-agent-dashboard](https://github.com/karem505/openclaw-agent-dashboard)
- Added cookie-based auth (login/logout)
- Added system + workspace skills scan (56 skills)
- Added mobile PWA support
- Added Cron Timeline + Vision Ingestion panels
- Added macOS LaunchAgent plist example
- Replaced Kanban tasks with operational monitoring
