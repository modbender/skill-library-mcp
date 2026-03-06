#!/usr/bin/env bash

# Health Check Script
# Returns JSON status of the skill installation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

STATUS="healthy"
ISSUES=()

# Check skill.json
if [ ! -f "$PROJECT_ROOT/skill.json" ]; then
  STATUS="unhealthy"
  ISSUES+=("skill.json not found")
fi

# Check node_modules
if [ ! -d "$PROJECT_ROOT/node_modules" ]; then
  STATUS="unhealthy"
  ISSUES+=("Dependencies not installed (run: npm install)")
fi

# Check .env
if [ ! -f "$PROJECT_ROOT/.env" ]; then
  STATUS="warning"
  ISSUES+=("Environment file not configured (copy .env.example to .env)")
fi

# Check required environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
  source "$PROJECT_ROOT/.env"

  if [ -z "$JWT_SECRET" ] || [ "$JWT_SECRET" = "your_jwt_secret_here" ]; then
    STATUS="warning"
    ISSUES+=("JWT_SECRET not configured in .env")
  fi

  if [ -z "$DASHBOARD_URL" ]; then
    STATUS="warning"
    ISSUES+=("DASHBOARD_URL not configured in .env")
  fi
fi

# Check Node.js
if ! command -v node &> /dev/null; then
  STATUS="unhealthy"
  ISSUES+=("Node.js not installed")
fi

# Check npm
if ! command -v npm &> /dev/null; then
  STATUS="unhealthy"
  ISSUES+=("npm not installed")
fi

# Output JSON status
cat << EOF
{
  "status": "$STATUS",
  "skill": "bloom-identity",
  "version": "2.0.0",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "checks": {
    "skill_json": $([ -f "$PROJECT_ROOT/skill.json" ] && echo "true" || echo "false"),
    "dependencies": $([ -d "$PROJECT_ROOT/node_modules" ] && echo "true" || echo "false"),
    "environment": $([ -f "$PROJECT_ROOT/.env" ] && echo "true" || echo "false"),
    "node": $(command -v node &> /dev/null && echo "true" || echo "false"),
    "npm": $(command -v npm &> /dev/null && echo "true" || echo "false")
  },
  "issues": [$(IFS=,; echo "\"${ISSUES[*]}\"" | sed 's/ /","/g')]
}
EOF

# Exit with appropriate code
if [ "$STATUS" = "unhealthy" ]; then
  exit 1
elif [ "$STATUS" = "warning" ]; then
  exit 2
else
  exit 0
fi
