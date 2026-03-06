#!/usr/bin/env bash
set -euo pipefail

# Debate Moderator — Interactive Setup Helper
# Walks through configuration choices and generates:
#   1. A filled-in AGENTS.md for the debate moderator agent
#   2. A config.patch JSON for the OpenClaw gateway
#
# Usage:
#   ./setup.sh [--output-dir DIR]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="${SKILL_DIR}/generated"

# Parse args
while [[ $# -gt 0 ]]; do
    case "$1" in
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: setup.sh [--output-dir DIR]"
            echo "Interactive setup wizard for the Debate Moderator skill."
            echo ""
            echo "Options:"
            echo "  --output-dir DIR   Where to write generated files (default: ./generated/)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

mkdir -p "$OUTPUT_DIR"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎙️  DEBATE MODERATOR — SETUP WIZARD"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Guild ID ──────────────────────────────────────
echo "Step 1: Discord Server (Guild) ID"
echo "  Enable Developer Mode in Discord (Settings → Advanced),"
echo "  then right-click your server icon → Copy Server ID."
echo ""
read -rp "  Guild ID: " GUILD_ID

if [[ -z "$GUILD_ID" ]]; then
    echo "Error: Guild ID is required." >&2
    exit 1
fi
echo ""

# ── Persona ───────────────────────────────────────
echo "Step 2: Choose a Moderator Persona"
echo "  1) Scholar (default) — Thoughtful, measured, references history"
echo "  2) Sports Commentator — High energy, play-by-play"
echo "  3) Philosopher — Socratic method, answers with questions"
echo "  4) Comedian — Witty roast-style commentary"
echo "  5) Drill Sergeant — No-nonsense, demands evidence"
echo "  6) Custom — Provide your own description"
echo ""
read -rp "  Choice [1]: " PERSONA_CHOICE
PERSONA_CHOICE="${PERSONA_CHOICE:-1}"

case "$PERSONA_CHOICE" in
    1) PERSONA="Scholar" ;;
    2) PERSONA="Sports Commentator" ;;
    3) PERSONA="Philosopher" ;;
    4) PERSONA="Comedian" ;;
    5) PERSONA="Drill Sergeant" ;;
    6)
        echo ""
        echo "  Enter your custom persona name:"
        read -rp "  Name: " PERSONA
        if [[ -z "$PERSONA" ]]; then
            echo "Error: Custom persona name is required." >&2
            exit 1
        fi
        ;;
    *)
        echo "Invalid choice. Using Scholar." >&2
        PERSONA="Scholar"
        ;;
esac
echo "  → Selected: $PERSONA"
echo ""

# ── Default Format ────────────────────────────────
echo "Step 3: Choose a Default Debate Format"
echo "  1) Campfire (default) — Free-form exchange"
echo "  2) Oxford — Formal rounds, audience voting"
echo "  3) Lincoln-Douglas — 1v1 value debate"
echo "  4) Hot Takes — One message each, best wins"
echo "  5) Devil's Advocate — Argue the opposite"
echo "  6) Roundtable — Multi-perspective, no winner"
echo ""
read -rp "  Choice [1]: " FORMAT_CHOICE
FORMAT_CHOICE="${FORMAT_CHOICE:-1}"

case "$FORMAT_CHOICE" in
    1) FORMAT="Campfire" ;;
    2) FORMAT="Oxford" ;;
    3) FORMAT="Lincoln-Douglas" ;;
    4) FORMAT="Hot Takes" ;;
    5) FORMAT="Devil's Advocate" ;;
    6) FORMAT="Roundtable" ;;
    *)
        echo "Invalid choice. Using Campfire." >&2
        FORMAT="Campfire"
        ;;
esac
echo "  → Selected: $FORMAT"
echo ""

# ── Judging Weights ───────────────────────────────
echo "Step 4: Judging Criteria Weights"
echo "  Defaults: Evidence 35%, Engagement 25%, Honesty 20%, Persuasiveness 20%"
read -rp "  Use defaults? [Y/n]: " USE_DEFAULT_WEIGHTS
USE_DEFAULT_WEIGHTS="${USE_DEFAULT_WEIGHTS:-Y}"

if [[ "${USE_DEFAULT_WEIGHTS,,}" == "y" ]]; then
    W_EVIDENCE=35
    W_ENGAGEMENT=25
    W_HONESTY=20
    W_PERSUASION=20
else
    echo "  Enter weights (must sum to 100):"
    read -rp "  Evidence & Reasoning [35]: " W_EVIDENCE
    W_EVIDENCE="${W_EVIDENCE:-35}"
    read -rp "  Engagement [25]: " W_ENGAGEMENT
    W_ENGAGEMENT="${W_ENGAGEMENT:-25}"
    read -rp "  Intellectual Honesty [20]: " W_HONESTY
    W_HONESTY="${W_HONESTY:-20}"
    read -rp "  Persuasiveness [20]: " W_PERSUASION
    W_PERSUASION="${W_PERSUASION:-20}"

    TOTAL=$((W_EVIDENCE + W_ENGAGEMENT + W_HONESTY + W_PERSUASION))
    if [[ "$TOTAL" -ne 100 ]]; then
        echo "Error: Weights sum to $TOTAL, must be 100." >&2
        exit 1
    fi
fi
echo "  → Weights: E=$W_EVIDENCE% G=$W_ENGAGEMENT% H=$W_HONESTY% P=$W_PERSUASION%"
echo ""

# ── Verdict Style ─────────────────────────────────
echo "Step 5: Verdict Style"
echo "  1) Detailed (default) — Full scorecard"
echo "  2) Brief — Winner + summary"
echo "  3) Dramatic — Theatrical ruling"
echo ""
read -rp "  Choice [1]: " VERDICT_CHOICE
VERDICT_CHOICE="${VERDICT_CHOICE:-1}"

case "$VERDICT_CHOICE" in
    1) VERDICT_STYLE="Detailed" ;;
    2) VERDICT_STYLE="Brief" ;;
    3) VERDICT_STYLE="Dramatic" ;;
    *)
        echo "Invalid choice. Using Detailed." >&2
        VERDICT_STYLE="Detailed"
        ;;
esac
echo "  → Selected: $VERDICT_STYLE"
echo ""

# ── Channel Names ─────────────────────────────────
echo "Step 6: Channel Names"
echo "  Press Enter to accept defaults."
echo ""
read -rp "  Rules channel [rules]: " CH_RULES
CH_RULES="${CH_RULES:-rules}"
read -rp "  Proposals channel [propose-a-topic]: " CH_PROPOSE
CH_PROPOSE="${CH_PROPOSE:-propose-a-topic}"
read -rp "  Arena channel [the-arena]: " CH_ARENA
CH_ARENA="${CH_ARENA:-the-arena}"
read -rp "  Records channel [hall-of-records]: " CH_RECORDS
CH_RECORDS="${CH_RECORDS:-hall-of-records}"
read -rp "  Casual channel [the-bar]: " CH_BAR
CH_BAR="${CH_BAR:-the-bar}"
echo ""

# ── Additional Options ────────────────────────────
echo "Step 7: Additional Options"
echo ""
read -rp "  Arena requireMention (true=cheaper, false=active moderation) [false]: " ARENA_MENTION
ARENA_MENTION="${ARENA_MENTION:-false}"
read -rp "  Scoreboard enabled? [Y/n]: " SCOREBOARD_ENABLED
SCOREBOARD_ENABLED="${SCOREBOARD_ENABLED:-Y}"
read -rp "  Debate timeout (hours) [48]: " DEBATE_TIMEOUT
DEBATE_TIMEOUT="${DEBATE_TIMEOUT:-48}"
read -rp "  Max concurrent debates [3]: " MAX_CONCURRENT
MAX_CONCURRENT="${MAX_CONCURRENT:-3}"
read -rp "  Topics unrestricted? [Y/n]: " TOPICS_UNRESTRICTED
TOPICS_UNRESTRICTED="${TOPICS_UNRESTRICTED:-Y}"
echo ""

# ── Model ─────────────────────────────────────────
echo "Step 8: AI Model"
echo "  1) anthropic/claude-sonnet-4-6 (default, cost-effective)"
echo "  2) anthropic/claude-opus-4-6 (highest quality)"
echo "  3) Custom model string"
echo ""
read -rp "  Choice [1]: " MODEL_CHOICE
MODEL_CHOICE="${MODEL_CHOICE:-1}"

case "$MODEL_CHOICE" in
    1) MODEL="anthropic/claude-sonnet-4-6" ;;
    2) MODEL="anthropic/claude-opus-4-6" ;;
    3)
        read -rp "  Model string: " MODEL
        if [[ -z "$MODEL" ]]; then
            echo "Error: Model string required." >&2
            exit 1
        fi
        ;;
    *)
        MODEL="anthropic/claude-sonnet-4-6"
        ;;
esac
echo "  → Selected: $MODEL"
echo ""

# ── Generate AGENTS.md ────────────────────────────
echo "Generating AGENTS.md..."

AGENTS_FILE="$OUTPUT_DIR/AGENTS.md"
TEMPLATE="$SKILL_DIR/references/agents-template.md"

if [[ ! -f "$TEMPLATE" ]]; then
    echo "Error: Template not found at $TEMPLATE" >&2
    exit 1
fi

# Read template and replace placeholders
AGENTS_CONTENT=$(<"$TEMPLATE")

# Replace [CONFIGURE: ...] blocks
AGENTS_CONTENT="${AGENTS_CONTENT//\[CONFIGURE: Scholar \/ Sports Commentator \/ Philosopher \/ Comedian \/ Drill Sergeant \/ or paste custom persona description\]/$PERSONA}"
AGENTS_CONTENT="${AGENTS_CONTENT//\[CONFIGURE: Campfire \/ Oxford \/ Lincoln-Douglas \/ Hot Takes \/ Devil\'s Advocate \/ Roundtable\]/$FORMAT}"
AGENTS_CONTENT="${AGENTS_CONTENT//\[CONFIGURE: Detailed \/ Brief \/ Dramatic\]/$VERDICT_STYLE}"
AGENTS_CONTENT="${AGENTS_CONTENT//\[CONFIGURE: 3\]/$MAX_CONCURRENT}"
AGENTS_CONTENT="${AGENTS_CONTENT//\[CONFIGURE: 48\]/$DEBATE_TIMEOUT}"
AGENTS_CONTENT="${AGENTS_CONTENT//\[CONFIGURE: 35\]/$W_EVIDENCE}"
AGENTS_CONTENT="${AGENTS_CONTENT//\[CONFIGURE: 25\]/$W_ENGAGEMENT}"

# Handle the two 20% weights carefully
AGENTS_CONTENT=$(echo "$AGENTS_CONTENT" | sed "0,/\[CONFIGURE: 20\]/s/\[CONFIGURE: 20\]/$W_HONESTY/" | sed "0,/\[CONFIGURE: 20\]/s/\[CONFIGURE: 20\]/$W_PERSUASION/")

# Set scoreboard
if [[ "${SCOREBOARD_ENABLED,,}" == "y" ]]; then
    AGENTS_CONTENT="${AGENTS_CONTENT//\[CONFIGURE: Set to \"enabled\" or \"disabled\"\]/enabled}"
else
    AGENTS_CONTENT="${AGENTS_CONTENT//\[CONFIGURE: Set to \"enabled\" or \"disabled\"\]/disabled}"
fi

# Handle topic policy
if [[ "${TOPICS_UNRESTRICTED,,}" == "y" ]]; then
    # Keep Option A, remove Option B
    AGENTS_CONTENT=$(echo "$AGENTS_CONTENT" | sed '/\[CONFIGURE: Choose one of the following blocks and delete the other.\]/d')
    AGENTS_CONTENT=$(echo "$AGENTS_CONTENT" | sed '/### Option B: Restricted/,/propose a different topic."/d')
    AGENTS_CONTENT=$(echo "$AGENTS_CONTENT" | sed '/\[CONFIGURE: List restricted topics\]/d')
else
    # Keep Option B, remove Option A
    AGENTS_CONTENT=$(echo "$AGENTS_CONTENT" | sed '/\[CONFIGURE: Choose one of the following blocks and delete the other.\]/d')
    AGENTS_CONTENT=$(echo "$AGENTS_CONTENT" | sed '/### Option A: Unrestricted/,/targeted abuse of other participants./d')
fi

# Handle persona voice section
AGENTS_CONTENT=$(echo "$AGENTS_CONTENT" | sed '/\[CONFIGURE: Paste the full persona section/d')

echo "$AGENTS_CONTENT" > "$AGENTS_FILE"
echo "  → Written to $AGENTS_FILE"

# ── Generate config snippets ──────────────────────
echo "Generating config snippets..."

CONFIG_FILE="$OUTPUT_DIR/config-snippets.md"

REQUIRE_MENTION="$ARENA_MENTION"

cat > "$CONFIG_FILE" <<CONFIGMD
# OpenClaw Config — Debate Moderator

Generated by setup.sh. Apply these to your OpenClaw gateway.

## 1. Agent Entry (add to \`agents.list\` array)

\`\`\`json
{
  "id": "debate",
  "name": "Debate Moderator",
  "workspace": "REPLACE_WITH_ABSOLUTE_PATH_TO_DEBATE_WORKSPACE",
  "model": {
    "primary": "$MODEL"
  },
  "tools": {
    "profile": "messaging",
    "deny": [
      "exec", "process", "nodes", "cron", "gateway", "browser",
      "canvas", "sessions_spawn", "sessions_send", "sessions_list",
      "sessions_history", "subagents", "session_status", "agents_list",
      "tts", "image", "memory_search", "memory_get"
    ],
    "exec": { "security": "deny" },
    "fs": { "workspaceOnly": true }
  }
}
\`\`\`

## 2. Binding Entry (add to \`bindings\` BEFORE any catch-all Discord binding)

\`\`\`json
{
  "agentId": "debate",
  "match": {
    "channel": "discord",
    "guildId": "$GUILD_ID"
  }
}
\`\`\`

## 3. Guild Entry (safe to merge with \`config.patch\`)

\`\`\`json
{
  "channels": {
    "discord": {
      "guilds": {
        "$GUILD_ID": {
          "requireMention": $REQUIRE_MENTION,
          "channels": {
            "*": { "allow": true }
          }
        }
      }
    }
  }
}
\`\`\`

## Configuration Summary

| Setting | Value |
|---------|-------|
| Guild ID | $GUILD_ID |
| Persona | $PERSONA |
| Default Format | $FORMAT |
| Verdict Style | $VERDICT_STYLE |
| Judging Weights | E=${W_EVIDENCE}% G=${W_ENGAGEMENT}% H=${W_HONESTY}% P=${W_PERSUASION}% |
| Channels | #$CH_RULES, #$CH_PROPOSE, #$CH_ARENA, #$CH_RECORDS, #$CH_BAR |
| requireMention | $REQUIRE_MENTION |
| Scoreboard | $SCOREBOARD_ENABLED |
| Timeout | ${DEBATE_TIMEOUT}h |
| Max Concurrent | $MAX_CONCURRENT |
| Model | $MODEL |

## Important Notes

- \`agents.list\` and \`bindings\` are arrays — \`config.patch\` replaces them entirely.
  Include ALL existing agents/bindings plus the debate entries.
- Use \`config.get\` to retrieve your current config before patching.
- The guild entry (section 3) merges safely since it's an object keyed by guild ID.
- The debate binding must come BEFORE any catch-all Discord binding in the array.
CONFIGMD

echo "  → Written to $CONFIG_FILE"

# ── Initialize Scoreboard ─────────────────────────
if [[ "${SCOREBOARD_ENABLED,,}" == "y" ]]; then
    echo "Initializing scoreboard..."
    "$SCRIPT_DIR/scoreboard.sh" init
fi

# ── Summary ───────────────────────────────────────
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ SETUP COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Generated files:"
echo "    $AGENTS_FILE"
echo "    $CONFIG_FILE"
echo ""
echo "  Configuration:"
echo "    Guild:       $GUILD_ID"
echo "    Persona:     $PERSONA"
echo "    Format:      $FORMAT"
echo "    Verdict:     $VERDICT_STYLE"
echo "    Weights:     E=${W_EVIDENCE}% G=${W_ENGAGEMENT}% H=${W_HONESTY}% P=${W_PERSUASION}%"
echo "    Channels:    #$CH_RULES, #$CH_PROPOSE, #$CH_ARENA, #$CH_RECORDS, #$CH_BAR"
echo "    Scoreboard:  ${SCOREBOARD_ENABLED}"
echo "    Timeout:     ${DEBATE_TIMEOUT}h"
echo "    Max debates: $MAX_CONCURRENT"
echo "    Model:       $MODEL"
echo ""
echo "  NEXT STEPS:"
echo "  ─────────────────────────────────────────"
echo "  1. Create a workspace directory for the debate agent"
echo "     and copy the generated AGENTS.md into it."
echo ""
echo "  2. Create channels in your Discord server:"
echo "     #$CH_RULES, #$CH_PROPOSE, #$CH_ARENA, #$CH_RECORDS, #$CH_BAR"
echo ""
echo "  3. Apply the config using the snippets in $CONFIG_FILE."
echo "     IMPORTANT: agents.list and bindings are arrays —"
echo "     include ALL existing entries plus the new debate ones."
echo "     The guild entry merges safely via config.patch."
echo ""
echo "  4. Restart the gateway: openclaw gateway restart"
echo ""
echo "  5. Post welcome messages in each channel"
echo "     (see assets/welcome-messages.md)"
echo ""
echo "  6. Test by @mentioning the moderator in #$CH_ARENA:"
echo "     @Moderator start debate: \"Test topic\" [format: hot-takes]"
echo ""
echo "  For detailed instructions, see: references/setup-guide.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
