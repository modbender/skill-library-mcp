#!/bin/bash
#
# ClawWork Skill - Wrapper para execução via OpenClaw
#

set -e

CLAWWORK_DIR="/home/freedom/.openclaw/workspace/ClawWork"
SKILL_DIR="/home/freedom/.openclaw/workspace/skills/clawwork"

# Ativa o ambiente Python
source "$CLAWWORK_DIR/venv/bin/activate"

# Executa o CLI
python "$SKILL_DIR/cli.py" "$@"
