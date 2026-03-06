#!/bin/bash
set -e

# create-branch-for-mr.sh
# Create PlanetScale branch matching your MR/PR branch name

show_help() {
  cat << EOF
Usage: $(basename "$0") [OPTIONS]

Create PlanetScale database branch matching MR/PR branch name.

OPTIONS:
  --database <name>       Database name (required)
  --branch <name>         Branch name (required)
  --from <source>         Source branch (default: main)
  --org <name>            Organization name (optional)
  -h, --help              Show this help message

EXAMPLES:
  # Create branch for MR/PR
  $(basename "$0") --database my-database \\
    --branch feature-user-settings

  # Create branch from specific source
  $(basename "$0") --database my-db --branch feature-x --from development

  # With organization
  $(basename "$0") --database my-db --branch feature-x --org my-org

EXIT CODES:
  0   Success
  1   Error (missing args, invalid input, pscale command failed)
EOF
}

# Validate that a value contains only safe characters for PlanetScale names
# Allowed: alphanumeric, hyphens, underscores, dots
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
FROM="main"
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
    --from)
      FROM="$2"
      shift 2
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

# Validate all inputs to prevent shell injection
validate_safe_name "$DATABASE" "--database"
validate_safe_name "$BRANCH" "--branch"
validate_safe_name "$FROM" "--from"
[[ -n "$ORG" ]] && validate_safe_name "$ORG" "--org"

echo "📦 Creating PlanetScale branch..."
echo "  Database: $DATABASE"
echo "  Branch: $BRANCH"
echo "  From: $FROM"
[[ -n "$ORG" ]] && echo "  Org: $ORG"
echo ""

# Execute pscale directly (no eval — arguments passed as discrete tokens)
if [[ -n "$ORG" ]]; then
  pscale branch create "$DATABASE" "$BRANCH" --from "$FROM" --org "$ORG"
else
  pscale branch create "$DATABASE" "$BRANCH" --from "$FROM"
fi

echo ""
echo "✅ Branch created successfully!"
echo ""
echo "Next steps:"
echo "  1. Make schema changes:"
echo "     pscale shell $DATABASE $BRANCH"
echo ""
echo "  2. View diff:"
echo "     pscale branch diff $DATABASE $BRANCH"
echo ""
echo "  3. Create deploy request:"
echo "     pscale deploy-request create $DATABASE $BRANCH"
