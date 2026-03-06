#!/usr/bin/env bash
# init.sh – Initialize the MMAG 5-layer memory structure
# Usage: bash init.sh [memory-root]
#
# Creates the following directory layout:
#   memory/
#   ├── conversational/   – dialogue threads (per-session files)
#   ├── long-term/        – user biographical facts & preferences
#   ├── episodic/         – timestamped events & scheduled reminders
#   ├── sensory/          – context signals: location, weather, time-of-day
#   └── working/          – ephemeral in-session scratchpad
#       └── snapshots/    – pre-compression backups

set -euo pipefail

ROOT="${1:-memory}"

LAYERS=(
  "conversational"
  "long-term"
  "episodic"
  "sensory"
  "working"
  "working/snapshots"
)

echo "🧠 Initializing MMAG memory structure at: $ROOT"

for layer in "${LAYERS[@]}"; do
  dir="$ROOT/$layer"
  if [ ! -d "$dir" ]; then
    mkdir -p "$dir"
    echo "  ✅ Created $dir"
  else
    echo "  ⏭️  Already exists: $dir"
  fi
done

# Create a README in each layer to explain its purpose
cat > "$ROOT/conversational/README.md" << 'EOF'
# Conversational Memory

Stores dialogue threads and session context.
Each file represents a session: `YYYY-MM-DD-<session-id>.md`

**Purpose:** Maintain coherence across ongoing dialogues.
Resolves references, tracks topic continuity, and enables multi-turn reasoning.
EOF

cat > "$ROOT/long-term/README.md" << 'EOF'
# Long-Term User Memory

Stores user biographical facts, preferences, and personality traits.
Each file is a topic-based profile: `user-profile.md`, `preferences.md`, etc.

**Purpose:** Personalize responses across sessions.
Injected as the highest-priority system message during context assembly.
Encrypted storage is strongly recommended for sensitive data.
EOF

cat > "$ROOT/episodic/README.md" << 'EOF'
# Episodic & Event-Linked Memory

Stores timestamped events, scheduled reminders, and habitual cues.
Each file is a date log: `YYYY-MM-DD.md`

**Purpose:** Enable proactive, time-aware interactions.
Supports trigger-based retrieval (e.g., surface an event before it happens).
EOF

cat > "$ROOT/sensory/README.md" << 'EOF'
# Sensory & Context-Aware Memory

Stores environmental signals: location, weather, time-of-day, device state.
Each file is a context snapshot: `context-<timestamp>.md`

**Purpose:** Ground responses in the user's current environment.
Keeps context sensitive without being intrusive.
EOF

cat > "$ROOT/working/README.md" << 'EOF'
# Short-Term Working Memory

Ephemeral in-session scratchpad for current task goals and reasoning state.
Cleared at the end of each session via `prune.sh`.

**Purpose:** Transient workspace for goal tracking and multi-step reasoning.
Content should not persist beyond the active session.
EOF

echo ""
echo "✅ MMAG memory structure ready."
echo ""
echo "Next steps:"
echo "  Store a memory:   bash store.sh <layer> \"<content>\""
echo "  Build context:    bash context.sh"
echo "  View stats:       bash stats.sh"
