#!/bin/bash
# TruthSea Verifier — OpenClaw Skill Installer
# Installs the TruthSea MCP server for use with OpenClaw/ClawHub

set -e

echo "🌊 Installing TruthSea Verifier skill v2.5.0..."

# Install the MCP server globally
npm install -g truthsea-mcp-server

# Copy MCP config
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"
echo ""
echo "✅ TruthSea MCP server installed!"
echo ""
echo "To configure, add the following to your MCP settings:"
echo ""
cat "$SKILL_DIR/mcp-config.json"
echo ""
echo "Set DEPLOYER_PRIVATE_KEY to enable write operations."
echo "Set TRUTH_DAG_ADDRESS and TRUTH_STAKING_ADDRESS to enable V2 DAG tools."
echo "Without these, the server runs in read-only mode."
echo ""
echo "Available commands:"
echo ""
echo "  Truth Verification (V1):"
echo "  /verify <claim>        — Submit a claim for truth verification"
echo "  /truth query <search>  — Search verified truth quanta"
echo "  /dispute <id> <claim>  — Challenge a quantum with counter-evidence"
echo ""
echo "  Dependency Graph (V2):"
echo "  /edge create <src> <tgt> — Create a dependency edge between quanta"
echo "  /edge dispute <edgeId>   — Challenge a dependency edge"
echo "  /dag explore <quantumId> — Navigate the dependency graph"
echo "  /dag score <quantumId>   — Get the propagated chain score"
echo "  /dag weak-links <qId>    — Find weak foundations"
echo "  /dag flag <edgeId>       — Flag weak edge for 100 TRUTH bounty"
echo ""
echo "  Bounties (CrowdedSea):"
echo "  /bounty list           — List available truth bounties"
echo "  /bounty claim <id>     — Claim a bounty for investigation"
echo ""
echo "🌊 TruthSea: Where truth meets the chain."
