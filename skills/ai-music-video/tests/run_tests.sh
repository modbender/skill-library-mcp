#!/usr/bin/env bash
# AI Music Video — Test Runner
# Usage:
#   ./run_tests.sh              # Tier 1 only (free, no API)
#   ./run_tests.sh --cheap      # Tier 1 + 2 (minimal API, ~$0.05)
#   ./run_tests.sh --full       # All tiers (full E2E, ~$0.15+)
#   ./run_tests.sh --e2e-only   # Tier 3 only (E2E pipeline)

set -euo pipefail
cd "$(dirname "$0")"

# API keys must be set in the environment before running tests.
# Example: export SUNO_API_KEY=xxx OPENAI_API_KEY=xxx

TIER="${1:-}"

case "$TIER" in
  --cheap)
    echo "🧪 Running Tier 1 (free) + Tier 2 (cheap API calls)..."
    python3 -m pytest test_dry_run.py test_integration.py -v -s -m "free or cheap" --tb=short
    ;;
  --full)
    echo "🧪 Running ALL tiers (including E2E — costs money!)..."
    python3 -m pytest test_dry_run.py test_integration.py test_e2e.py -v -s --tb=short
    ;;
  --e2e-only)
    echo "🧪 Running Tier 3 only (E2E pipeline)..."
    python3 -m pytest test_e2e.py -v -s --tb=short
    ;;
  *)
    echo "🧪 Running Tier 1 only (free, no API calls)..."
    python3 -m pytest test_dry_run.py -v -s -m "free" --tb=short
    ;;
esac
