#!/bin/bash
# Subagent Architecture Setup
set -e

echo "Setting up subagent architecture..."

mkdir -p subagents/{devops,hardware-research}/"{knowledge-base,research}"
mkdir -p subagents/_archived

# Copy SPECIALIST.md template
cp templates/SPECIALIST.md subagents/devops/

echo "✓ subagents/ structure created"
echo "✓ Ready to spawn specialists"
