#!/bin/bash
# enoch-tuning: lock identity files after personalization
# Run this AFTER you've finished personalizing SOUL.md and AGENTS.md
#
# Locks:
#   - Core identity (SOUL.md, AGENTS.md) → root-owned, read-only (444)
#   - Private data (USER.md, MEMORY.md) → owner-only (600)
#   - Security playbook (AGENT_PROMPT.md) → owner-only (600)
#   - LaunchAgent plists → owner-only (600)
#   - Cron config (jobs.json) → owner-only (600)
#
# Why: 644 (world-readable) files can be read by any process on the machine —
# daemons, compromised npm packages, spotlight indexing, other user accounts.
# The security playbook especially should never be readable by untrusted processes.

WORKSPACE=${1:-~/.openclaw/workspace}
OPENCLAW_DIR=${2:-~/.openclaw}
LAUNCHAGENTS_DIR=~/Library/LaunchAgents

echo "Locking identity files at $WORKSPACE..."
echo ""

# ── REQUIRED: Core identity files ─────────────────────────────────────────────
MISSING=0
for f in SOUL.md AGENTS.md; do
  if [ ! -f "$WORKSPACE/$f" ]; then
    echo "❌ $f not found at $WORKSPACE/$f — did you copy the templates?"
    MISSING=1
  fi
done
[ "$MISSING" -eq 1 ] && exit 1

sudo chown root:staff "$WORKSPACE/SOUL.md" "$WORKSPACE/AGENTS.md"
sudo chmod 444 "$WORKSPACE/SOUL.md" "$WORKSPACE/AGENTS.md"
echo "✅ SOUL.md   → root-owned, read-only (444)"
echo "✅ AGENTS.md → root-owned, read-only (444)"

# ── PRIVATE DATA: Personal info and memory ────────────────────────────────────
for f in USER.md MEMORY.md; do
  if [ -f "$WORKSPACE/$f" ]; then
    chmod 600 "$WORKSPACE/$f"
    echo "✅ $f → owner-only (600)"
  fi
done

# ── SECURITY PLAYBOOK: Gideon observer agent ──────────────────────────────────
# If Gideon is installed, its prompt is your detection playbook.
# An attacker who reads it knows exactly what to hide from.
AGENT_PROMPT="$WORKSPACE/agents/observer/AGENT_PROMPT.md"
if [ -f "$AGENT_PROMPT" ]; then
  chmod 600 "$AGENT_PROMPT"
  echo "✅ agents/observer/AGENT_PROMPT.md → owner-only (600)"
else
  echo "⏭️  AGENT_PROMPT.md not found — skipping (install Gideon first if needed)"
fi

DAILY_PROMPT="$WORKSPACE/agents/observer/daily-prompt.md"
if [ -f "$DAILY_PROMPT" ]; then
  chmod 600 "$DAILY_PROMPT"
  echo "✅ agents/observer/daily-prompt.md → owner-only (600)"
fi

# ── CRON CONFIG ───────────────────────────────────────────────────────────────
JOBS_JSON="$OPENCLAW_DIR/cron/jobs.json"
if [ -f "$JOBS_JSON" ]; then
  chmod 600 "$JOBS_JSON"
  echo "✅ cron/jobs.json → owner-only (600)"
fi

# ── OPENCLAW CORE CONFIG ──────────────────────────────────────────────────────
OPENCLAW_JSON="$OPENCLAW_DIR/openclaw.json"
if [ -f "$OPENCLAW_JSON" ]; then
  chmod 600 "$OPENCLAW_JSON"
  echo "✅ openclaw.json → owner-only (600)"
fi

# ── LAUNCHAGENT PLISTS ────────────────────────────────────────────────────────
# Plists can reveal script paths, Keychain service names, and monitoring targets.
PLIST_COUNT=0
for plist in "$LAUNCHAGENTS_DIR"/ai.openclaw.*.plist "$LAUNCHAGENTS_DIR"/com.openclaw.*.plist; do
  if [ -f "$plist" ]; then
    chmod 600 "$plist"
    echo "✅ $(basename $plist) → owner-only (600)"
    PLIST_COUNT=$((PLIST_COUNT + 1))
  fi
done
[ "$PLIST_COUNT" -eq 0 ] && echo "⏭️  No OpenClaw LaunchAgent plists found — skipping"

# ── SUMMARY ───────────────────────────────────────────────────────────────────
echo ""
echo "Lock complete."
echo ""
echo "To edit locked files later:"
echo "  sudo chmod 644 $WORKSPACE/SOUL.md && \$EDITOR $WORKSPACE/SOUL.md && sudo chmod 444 $WORKSPACE/SOUL.md"
echo "  chmod 644 $WORKSPACE/USER.md && \$EDITOR $WORKSPACE/USER.md && chmod 600 $WORKSPACE/USER.md"
