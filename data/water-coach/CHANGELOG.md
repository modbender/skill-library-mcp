# Changelog - Water Coach

All notable changes to this skill will be documented in this file.

---

## [1.7.0] - 2026-02-22

### 🐛 Bug Fixes

- **Hour counter not resetting**: Fixed `water dynamic` to properly reset hourly notification counter when hour changes (was causing false "max_per_hour_reached")
- **Analytics sum bug**: Fixed weekly/monthly reports - was looking for non-existent `cumulative_ml` column, now correctly sums `ml_drank` per day
- **Include 0ml days**: Weekly reports now include all days (even with 0ml) for true average calculation
- **Day name mapping**: Fixed Portuguese day names (was mapping 0=Dom, now correctly 0=Seg)

### ✨ Improvements

- **Better weekly report format**: Table format with day names in Portuguese (Seg, Ter, Qua, Qui, Sex, Sáb, Dom)
- **SKILL.md guide**: Added "How to Build Good Weekly/Monthly Reports" section for agents

### 📋 Commands Updated

```bash
# Weekly report now shows correct days and includes all 7 days
analytics week
```

---

## [1.5.1] - 2026-02-19

### 🔒 Security & Privacy

- **Audit auto-capture now opt-in** (default: false)
- Added privacy warning in SKILL.md explaining audit trail implications
- Users must explicitly enable `audit_auto_capture` in config to allow reading session transcripts
- Audit command now shows warning instead of context when disabled

### ⚙️ Configuration

- New config option: `settings.audit_auto_capture` (boolean, default: false)

---

## [1.5.0] - 2026-02-18

### 🚀 Major Features

#### New CLI Architecture (Option C)
- Unified CLI: `water_coach.py <namespace> <command>`
- Namespaces: `water`, `body`, `analytics`
- Better agent clarity on available commands

#### Audit Trail System
- **Two timestamps**: `logged_at` (when user told you) + `drank_at` (when user actually drank)
- **Message ID**: Auto-captures conversation message ID for proof
- **Audit function**: `water audit <message_id>` - retrieves entry + conversation context
- **Cumulative calculated at query time** - not stored (prevents data corruption on edits)

#### Dynamic Scheduling (Coach Mode)
- Per-hour limits instead of per-day (max 2/hour)
- Aggressiveness curve: easier to trigger near cutoff time
- Can re-trigger multiple times per day

### ✨ Improvements

#### Flexible Paths
- No hardcoded paths (e.g., `/home/oriel/`)
- Uses environment variables and relative paths
- Works on any machine with OpenClaw

#### Body Metrics Integration
- `water set_body_weight` logs to both config AND body_metrics.csv
- Auto-calculates BMI

#### User Choice for Goals
- weight × 35 = default suggestion only
- Agent MUST confirm goal with user at setup
- Agent asks to update goal when weight changes

### 📋 Commands Added

```bash
# Water
water status                   # Current progress (calculated)
water log <ml>               # Log intake
water log <ml> --drank-at=<ISO>  # Log with past time
water dynamic                 # Check if extra notification needed
water threshold               # Get expected % for current hour
water set_body_weight <kg>   # Update weight + logs to body_metrics
water audit <message_id>     # Get entry + conversation context

# Body
body log --weight=80 --height=1.75
body latest
body history 30

# Analytics
analytics week
analytics month
```

### 🔧 Technical Changes

- 21 unit tests (was ~13)
- CSV format: `logged_at,drank_at,date,slot,ml_drank,goal_at_time,message_id`
- Auto-captures message_id from session transcript
- `.gitignore` in data folder to protect user data

---

## [1.2.0] - 2026-02-16

### Initial Release
- Basic water tracking
- Daily cron reminders
- Unit conversion (L, ml, oz, glasses)
- Body metrics logging
- Dynamic scheduling (basic)
