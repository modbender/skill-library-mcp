#!/bin/bash
# Claude Code Mastery - Configuration
# Edit these values to customize your installation

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================
# Valid model names for subagents (update as Anthropic releases new models)
# Claude Code accepts short names like "sonnet" or full names like "claude-sonnet-4-5"
VALID_MODELS=(
  # Short names (recommended for Claude Code)
  "sonnet"
  "haiku" 
  "opus"
  # Full model names
  "claude-sonnet-4-5"
  "claude-haiku-3-5"
  "claude-opus-4"
  "claude-3-5-sonnet"
  "claude-3-5-haiku"
  "claude-3-opus"
  # Provider-prefixed (for other tools)
  "anthropic/claude-sonnet-4-5"
  "anthropic/claude-haiku-3-5"
  "anthropic/claude-opus-4"
)

# Default model for subagents
DEFAULT_MODEL="sonnet"

# =============================================================================
# INSTALLATION OPTIONS
# =============================================================================
# Starter pack (3 core agents) vs full team (11 agents)
# Options: "starter" or "full"
INSTALL_MODE="starter"

# Core agents (installed with starter pack)
STARTER_AGENTS=(
  "senior-dev"
  "project-manager"
  "junior-dev"
)

# Full team agents (installed with --full-team flag)
FULL_TEAM_AGENTS=(
  "senior-dev"
  "project-manager"
  "junior-dev"
  "frontend-dev"
  "backend-dev"
  "ai-engineer"
  "ml-engineer"
  "data-scientist"
  "data-engineer"
  "product-manager"
  "devops"
)

# =============================================================================
# HEARTBEAT CONFIGURATION
# =============================================================================
# Enable diagnostics in heartbeat tasks (can burn tokens if always on)
# Set to "true" only if you want automatic health checks
HEARTBEAT_DIAGNOSTICS="false"

# =============================================================================
# CLAUDE-MEM CONFIGURATION (Optional)
# =============================================================================
# Claude-mem is OPTIONAL. Most users don't need it.
# It's community-maintained (not official Anthropic software)

# Original repo (we don't fork - user can choose to install or not)
CLAUDE_MEM_REPO="https://github.com/thedotmack/claude-mem.git"

# Pinned commit for security (update after review of new commits)
CLAUDE_MEM_COMMIT="1341e93fcab15b9caf48bc947d8521b4a97515d8"

# Database location
CLAUDE_MEM_DB="$HOME/.claude-mem/claude-mem.db"

# Worker port
CLAUDE_MEM_PORT="37777"
