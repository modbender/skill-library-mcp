#!/bin/bash
# Setup script for FHIR Questionnaire Skill
# Creates virtual environment and installs dependencies

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Setting up FHIR Questionnaire Skill..."

if command -v uv &> /dev/null; then
    echo "Using uv..."
    cd "$SKILL_DIR"

    if [ ! -d ".venv" ]; then
        uv venv
    fi

    uv pip install -r requirements.txt
    echo "✅ Setup complete! Use: .venv/bin/python scripts/validate_questionnaire.py ..."

elif command -v python3 &> /dev/null; then
    echo "Using python3 venv..."
    cd "$SKILL_DIR"

    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi

    .venv/bin/pip install -r requirements.txt
    echo "✅ Setup complete! Use: .venv/bin/python scripts/validate_questionnaire.py ..."

else
    echo "❌ Error: Neither uv nor python3 found."
    exit 1
fi
