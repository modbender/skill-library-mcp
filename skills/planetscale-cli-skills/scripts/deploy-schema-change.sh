#!/bin/bash
set -e

# deploy-schema-change.sh
# Complete schema migration workflow: create deploy request and optionally deploy

show_help() {
  cat << EOF
Usage: $(basename "$0") [OPTIONS]

Create and optionally deploy a schema change via deploy request.

OPTIONS:
  --database <name>       Database name (required)
  --branch <name>         Branch name (required)
  --deploy                Auto-deploy after creating deploy request
  --org <name>            Organization name (optional; alphanumeric, hyphens, underscores, dots only)
  -h, --help              Show this help message

EXAMPLES:
  # Create deploy request only (manual deploy)
  $(basename "$0") --database my-database --branch feature-schema-v2

  # Create and auto-deploy
  $(basename "$0") --database my-database --branch feature-schema-v2 --deploy

  # With organization
  $(basename "$0") --database my-db --branch feature-x --org my-org --deploy

WORKFLOW:
  1. Creates deploy request from branch
  2. Shows deploy request diff
  3. If --deploy flag, deploys immediately
  4. Shows final status

EXIT CODES:
  0   Success
  1   Error (missing args, pscale command failed)
EOF
}

# Validate that a value contains only safe characters for PlanetScale names
validate_safe_name() {
  local value="$1"
  local param="$2"
  if [[ ! "$value" =~ ^[a-zA-Z0-9._-]+$ ]]; then
    echo "❌ Error: $param contains invalid characters. Only alphanumeric, hyphens, underscores, and dots are allowed."
    exit 1
  fi
}

# Parse arguments
DATABASE=""
BRANCH=""
AUTO_DEPLOY=false
ORG=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --database)
      DATABASE="$2"
      shift 2
      ;;
    --branch)
      BRANCH="$2"
      shift 2
      ;;
    --deploy)
      AUTO_DEPLOY=true
      shift
      ;;
    --org)
      ORG="$2"
      shift 2
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      echo "❌ Unknown option: $1"
      echo "Run with --help for usage"
      exit 1
      ;;
  esac
done

# Validate required arguments
if [[ -z "$DATABASE" ]] || [[ -z "$BRANCH" ]]; then
  echo "❌ Error: --database and --branch are required"
  echo "Run with --help for usage"
  exit 1
fi

# Validate inputs to prevent shell injection
validate_safe_name "$DATABASE" "--database"
validate_safe_name "$BRANCH" "--branch"
[[ -n "$ORG" ]] && validate_safe_name "$ORG" "--org"

# Build org args array (safe: no eval, no string interpolation into commands)
ORG_ARGS=()
[[ -n "$ORG" ]] && ORG_ARGS=(--org "$ORG")

echo "🚀 Starting schema migration workflow..."
echo "  Database: $DATABASE"
echo "  Branch: $BRANCH"
[[ -n "$ORG" ]] && echo "  Org: $ORG"
echo ""

# Step 1: Create deploy request
echo "📝 Creating deploy request..."
DR_OUTPUT=$(pscale deploy-request create "$DATABASE" "$BRANCH" "${ORG_ARGS[@]}" --format json)
DR_NUMBER=$(echo "$DR_OUTPUT" | grep -oP '"number":\s*\K\d+' | head -1)

if [[ -z "$DR_NUMBER" ]]; then
  echo "❌ Failed to create deploy request"
  exit 1
fi

echo "✅ Deploy request #$DR_NUMBER created"
echo ""

# Step 2: Show diff
echo "📊 Deploy request diff:"
pscale deploy-request diff "$DATABASE" "$DR_NUMBER" "${ORG_ARGS[@]}" || true
echo ""

# Step 3: Deploy if requested
if [[ "$AUTO_DEPLOY" == true ]]; then
  echo "🚀 Deploying..."
  pscale deploy-request deploy "$DATABASE" "$DR_NUMBER" "${ORG_ARGS[@]}"
  echo "✅ Deployment complete!"
else
  echo "⏸️  Deploy request created but not deployed (use --deploy to auto-deploy)"
  echo ""
  echo "To deploy manually:"
  echo "  pscale deploy-request deploy $DATABASE $DR_NUMBER ${ORG_ARGS[*]}"
fi

echo ""

# Step 4: Show final status
echo "📋 Deploy request status:"
pscale deploy-request show "$DATABASE" "$DR_NUMBER" "${ORG_ARGS[@]}"
