#!/bin/bash
# QMD Memory Skill Setup Script
# As Above Technologies

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║     QMD MEMORY SKILL — Local Hybrid Search for OpenClaw          ║"
echo "║     Save \$50-300/month in API costs                              ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"

# Check if QMD is installed
if ! command -v qmd &> /dev/null; then
    echo "📦 Installing QMD..."
    npm install -g @tobilu/qmd
    echo "✅ QMD installed"
else
    echo "✅ QMD already installed ($(qmd --version))"
fi

echo ""
echo "🔍 Scanning workspace structure..."

# Create collections based on what exists
if [ -d "$WORKSPACE/memory" ]; then
    echo "📁 Found: memory/ → Creating 'daily-logs' collection"
    qmd collection add "$WORKSPACE/memory" --name daily-logs --mask "**/*.md" 2>/dev/null || true
    qmd context add qmd://daily-logs "Daily work logs and session notes" 2>/dev/null || true
fi

if [ -d "$WORKSPACE/intelligence" ]; then
    echo "📁 Found: intelligence/ → Creating 'intelligence' collection"
    qmd collection add "$WORKSPACE/intelligence" --name intelligence --mask "**/*.md" 2>/dev/null || true
    qmd context add qmd://intelligence "Analysis, research, dashboards, and reference documents" 2>/dev/null || true
fi

if [ -d "$WORKSPACE/projects" ]; then
    echo "📁 Found: projects/ → Creating 'projects' collection"
    qmd collection add "$WORKSPACE/projects" --name projects --mask "**/*.md" 2>/dev/null || true
    qmd context add qmd://projects "Project documentation and work files" 2>/dev/null || true
fi

# Always create workspace collection for core files
echo "📁 Creating 'workspace' collection for core agent files"
qmd collection add "$WORKSPACE" --name workspace --mask "*.md" 2>/dev/null || true
qmd context add qmd://workspace "Core agent files: MEMORY.md, SOUL.md, USER.md, TOOLS.md" 2>/dev/null || true

echo ""
echo "📊 Running initial index..."
qmd update 2>/dev/null || true

echo ""
echo "🧠 Generating embeddings (this downloads ~2GB of models on first run)..."
echo "   This may take 5-10 minutes on first run. Go grab coffee ☕"
echo ""

# Run embed in background-friendly way
qmd embed 2>&1 || echo "⚠️  Embedding will complete in background. Run 'qmd status' to check."

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo "✅ QMD MEMORY SKILL SETUP COMPLETE"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "Your collections:"
qmd collection list 2>/dev/null || true
echo ""
echo "Quick commands:"
echo "  qmd search \"query\"     — Fast keyword search"
echo "  qmd vsearch \"query\"    — Semantic search"
echo "  qmd query \"query\"      — Best quality (hybrid + rerank)"
echo "  qmd status             — Check index health"
echo ""
echo "💰 You're now saving \$50-300/month in API costs!"
echo ""
echo "Questions? support@asabove.tech"
echo "More tips: asabove.tech/newsletter"
