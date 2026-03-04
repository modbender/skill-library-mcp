# Model Switchboard v3.0 — Safe AI Model Configuration for OpenClaw

> ⛔ **HARD RULE: NEVER edit `openclaw.json` model fields directly.**
> Always use this skill's commands. No exceptions. Ever.

## Why This Exists

Editing `openclaw.json` directly for model changes is the #1 cause of OpenClaw gateway crashes. Wrong model type in wrong slot = instant death. No backup = hours rebuilding. This skill eliminates that entirely.

## How It Works

1. **Validates** model format and role compatibility before any change
2. **Auto-backs up** config before every modification (30 rolling backups)
3. **Uses OpenClaw CLI** (`openclaw models set`) — never raw JSON
4. **Blocks unsafe assignments** (image-gen model as primary LLM = blocked)
5. **Instant rollback** if anything goes wrong
6. **Canvas UI** for visual model management

## Quick Reference

```bash
SWITCHBOARD="$SKILL_DIR/scripts/switchboard.sh"

# View current setup
$SWITCHBOARD status

# Change models
$SWITCHBOARD set-primary "anthropic/claude-opus-4-6"
$SWITCHBOARD set-image "google/gemini-3-pro-preview"
$SWITCHBOARD add-fallback "openai/gpt-5.2"
$SWITCHBOARD remove-fallback "openai/gpt-5.2"
$SWITCHBOARD add-image-fallback "openai/gpt-5.1"

# Preview before applying
$SWITCHBOARD dry-run set-primary "openai/gpt-5.2"

# Discovery & recommendations
$SWITCHBOARD discover          # List all available models
$SWITCHBOARD recommend         # Get optimal suggestions

# Redundancy (3-deep failover)
$SWITCHBOARD redundancy        # Assess current redundancy
$SWITCHBOARD redundancy-deploy # Preview optimal config
$SWITCHBOARD redundancy-apply  # Apply optimal config
$SWITCHBOARD redundancy-apply 4  # Custom depth

# Backup & restore
$SWITCHBOARD backup            # Manual backup
$SWITCHBOARD list-backups      # Show all backups
$SWITCHBOARD restore latest    # Undo last change

# Import/Export (portable model configs)
$SWITCHBOARD export config.json
$SWITCHBOARD import config.json

# Cron model validation
$SWITCHBOARD validate-cron-models  # Check cron jobs use valid models

# Diagnostics
$SWITCHBOARD health            # Gateway + provider status
$SWITCHBOARD validate <model> <role>  # Test compatibility
```

## Model Roles

| Role | Purpose | Config Key |
|------|---------|-----------|
| **Primary** | Main LLM for all conversations | `agents.defaults.model.primary` |
| **Fallback** | Ordered backup LLMs | `agents.defaults.model.fallbacks` |
| **Image** | Vision/image processing | `agents.defaults.imageModel.primary` |
| **Image Fallback** | Backup vision models | `agents.defaults.imageModel.fallbacks` |
| **Heartbeat** | Low-cost polling model | `agents.defaults.heartbeat.model` |
| **Coding** | Sub-agent code generation | Spawn-time model param |

## Validation Rules

The validation engine (`scripts/validate.py`) enforces:

- **Format**: Must be `provider/model-name` (e.g., `anthropic/claude-opus-4-6`)
- **Capability match**: LLM roles require `llm` + `tools` capabilities
- **Image roles**: Require `vision` capability
- **Hard blocks**: Image-generation-only models (DALL-E, Stability) blocked from ALL LLM roles
- **Registry warnings**: Unknown models get a caution warning but are allowed (for OpenRouter/new models)

## Known Providers

- `anthropic` — Claude family (Opus, Sonnet, Haiku)
- `openai` — GPT family
- `openai-codex` — Codex OAuth models
- `google` — Gemini family
- `opencode` — Zen proxy (routes to various models)
- `zai` — GLM family
- `xai` — Grok family
- `openrouter` — Multi-provider gateway
- `groq`, `cerebras` — Fast inference

## Canvas UI

To show the visual dashboard:
```bash
# Get UI data
DATA=$($SWITCHBOARD ui)

# Present via canvas
# The UI reads window.__switchboardData JSON
```

The Canvas UI at `ui/index.html` shows:
- Primary LLM and Image model with color coding
- Fallback chains (ordered)
- Provider auth status (green/red indicators)
- Model allowlist
- Config issues with severity levels
- Backup count

## For Agents: Operating Protocol

When a user asks to change model assignments:

1. **Read this SKILL.md first**
2. **Show current status**: `$SWITCHBOARD status`
3. **Preview the change**: `$SWITCHBOARD dry-run <action> <model>`
4. **Confirm with user** before applying
5. **Apply**: `$SWITCHBOARD <action> <model>`
6. **Verify**: Check gateway health after change

**NEVER:**
- Edit `openclaw.json` directly for model fields
- Skip the dry-run for primary model changes
- Apply without user confirmation
- Ignore validation failures

## Troubleshooting

**Gateway won't start:**
```bash
$SWITCHBOARD restore latest
openclaw gateway restart
# Or: openclaw doctor --fix
```

**"Model is not allowed" error:**
Model isn't in the allowlist. Add it or clear the list:
```bash
openclaw config set 'agents.defaults.models."provider/model"' '{"alias":"Name"}'
# Or clear: openclaw config unset agents.defaults.models
```

**Unknown model warning:**
The model isn't in `model-registry.json`. Add it for future validation:
```bash
# Edit model-registry.json to add the model entry
```

## File Structure

```
model-switchboard/
├── SKILL.md              # This file — agent instructions
├── README.md             # ClawHub publishing readme
├── model-registry.json   # Known model capabilities database
├── scripts/
│   ├── switchboard.sh    # Main CLI tool (bash)
│   └── validate.py       # Validation engine (python3, no deps)
└── ui/
    └── index.html        # Canvas dashboard (single-file, no deps)
```
