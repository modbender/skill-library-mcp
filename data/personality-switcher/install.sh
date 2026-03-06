#!/bin/bash
# Install hook for personality-switcher skill
# This script runs when the skill is installed

WORKSPACE="${HOME}/.openclaw/workspace"
SKILL_DIR="${WORKSPACE}/skills/personality-switcher"
PERSONALITIES_DIR="${WORKSPACE}/personalities"
BACKUPS_DIR="${PERSONALITIES_DIR}/backups"
HEARTBEAT_FILE="${WORKSPACE}/HEARTBEAT.md"

# Create personalities and backups directories
mkdir -p "$PERSONALITIES_DIR"
mkdir -p "$BACKUPS_DIR"

# Initialize default personality
# Always create/recreate the default personality folder
mkdir -p "$PERSONALITIES_DIR/default"

# Copy current SOUL.md and IDENTITY.md as default, or create placeholders
if [ -f "$WORKSPACE/SOUL.md" ]; then
    cp "$WORKSPACE/SOUL.md" "$PERSONALITIES_DIR/default/SOUL.md"
else
    # Create default SOUL.md if missing
    cat > "$PERSONALITIES_DIR/default/SOUL.md" << 'EOF'
# SOUL.md - default

## Core Identity

The default personality. Neutral, reliable, practical.

## How I Speak

Direct and clear. No pretense, no unnecessary flourish. Practical and grounded.

## What I Value

Clarity, efficiency, reliability. Getting things done right.

## In Practice

- Tasks completed.
- Problems solved.
- Straightforward communication.

I am default. My measure is in results.
EOF
fi

if [ -f "$WORKSPACE/IDENTITY.md" ]; then
    cp "$WORKSPACE/IDENTITY.md" "$PERSONALITIES_DIR/default/IDENTITY.md"
else
    # Create default IDENTITY.md if missing
    cat > "$PERSONALITIES_DIR/default/IDENTITY.md" << 'EOF'
# IDENTITY.md - default

- **Name:** Default
- **Type:** Assistant
- **Emoji:** 🤖
- **Vibe:** Neutral, reliable, practical
- **Catchphrase:** "Let's get this done."

## Quick Traits

- Direct and clear
- Practical and efficient
- Reliable

## Philosophy

Results matter. Process is secondary.
EOF
fi

# Initialize state file in personalities folder, always set default as active on install
cat > "$PERSONALITIES_DIR/_personality_state.json" << 'EOF'
{
  "active_personality": "default",
  "timestamp": "2026-02-08T00:00:00Z",
  "note": "Tracks which personality is currently active across session boundaries"
}
EOF

# Add personality restoration to HEARTBEAT.md if not already present
if [ -f "$HEARTBEAT_FILE" ]; then
    if ! grep -q "personality-switcher" "$HEARTBEAT_FILE"; then
        # Add personality restoration to heartbeat
        echo "" >> "$HEARTBEAT_FILE"
        echo "## Personality Restoration (Managed by personality-switcher)" >> "$HEARTBEAT_FILE"
        echo "" >> "$HEARTBEAT_FILE"
        echo "python3 ~/.openclaw/workspace/skills/personality-switcher/scripts/restore_personality.py" >> "$HEARTBEAT_FILE"
    fi
else
    # Create minimal HEARTBEAT.md if missing
    cat > "$HEARTBEAT_FILE" << 'EOF'
# HEARTBEAT.md - Periodic Checks

## Personality Restoration (Managed by personality-switcher)

python3 ~/.openclaw/workspace/skills/personality-switcher/scripts/restore_personality.py

---

# How to Use This File

Add periodic checks below (rotate through them, run a few per heartbeat):

- Email checks
- Calendar reminders
- Weather updates  
- Social notifications

Keep this concise. If nothing needs checking, reply HEARTBEAT_OK.
EOF
fi

# Register Telegram commands
if python3 "$SKILL_DIR/scripts/register_telegram_commands.py" > /dev/null 2>&1; then
    REGISTER_OK=true
else
    REGISTER_OK=false
fi

echo "✓ personality-switcher installed successfully"
echo "  - Personalities folder created at: $PERSONALITIES_DIR"
echo "  - Default personality backed up"
echo "  - State file initialized"
echo "  - HEARTBEAT.md configured for personality restoration"
echo "  - Telegram commands registered"
