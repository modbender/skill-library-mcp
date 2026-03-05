#!/bin/bash
# ------------------------------------------------------------------
# OpenClaw Model Manager Wrapper
# This script is a safe entrypoint for the model management skill.
# ------------------------------------------------------------------

# Ensure we are running with Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not found."
    exit 1
fi

# Delegate to the main Python logic
python3 skills/model-manager/manage_models.py "$@"
