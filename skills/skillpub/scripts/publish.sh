#!/usr/bin/env bash
set -euo pipefail

# publish.sh - Publish a skill to ClawHub
# Usage: publish.sh <skill-folder> --slug <name> --version <x.y.z> [--changelog <text>]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  echo "Usage: $0 <skill-folder> --slug <name> --version <x.y.z> [options]"
  echo ""
  echo "Publishes a skill to ClawHub after validation and security scan."
  echo ""
  echo "Options:"
  echo "  --slug <name>        Skill slug (required)"
  echo "  --version <x.y.z>    Version number (required)"
  echo "  --changelog <text>   Changelog message (optional)"
  echo "  --skip-checks        Skip validation and security scan"
  echo "  --force              Force publish even with warnings"
  echo ""
  echo "Example:"
  echo "  $0 ./my-skill --slug my-skill --version 1.0.0 --changelog 'Initial release'"
  exit 1
}

# Parse args
SKILL_DIR=""
SLUG=""
VERSION=""
CHANGELOG=""
SKIP_CHECKS=false
FORCE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --slug)
      SLUG="$2"
      shift 2
      ;;
    --version)
      VERSION="$2"
      shift 2
      ;;
    --changelog)
      CHANGELOG="$2"
      shift 2
      ;;
    --skip-checks)
      SKIP_CHECKS=true
      shift
      ;;
    --force)
      FORCE=true
      shift
      ;;
    -h|--help)
      usage
      ;;
    -*)
      echo "Unknown option: $1"
      usage
      ;;
    *)
      if [[ -z "$SKILL_DIR" ]]; then
        SKILL_DIR="$1"
      else
        echo "Unexpected argument: $1"
        usage
      fi
      shift
      ;;
  esac
done

# Validate required args
if [[ -z "$SKILL_DIR" ]]; then
  echo "Error: skill-folder is required"
  usage
fi

if [[ -z "$SLUG" ]]; then
  echo "Error: --slug is required"
  usage
fi

if [[ -z "$VERSION" ]]; then
  echo "Error: --version is required"
  usage
fi

# Check skill directory exists
if [[ ! -d "$SKILL_DIR" ]]; then
  echo "❌ Error: Directory not found: $SKILL_DIR"
  exit 1
fi

echo "📦 Publishing skill: $SLUG v$VERSION"
echo ""

# Run validation and security scan unless skipped
if [[ "$SKIP_CHECKS" != true ]]; then
  echo "Step 1/3: Validating..."
  if ! bash "$SCRIPT_DIR/validate.sh" "$SKILL_DIR"; then
    echo ""
    echo "❌ Validation failed. Fix errors and try again."
    echo "   Or use --skip-checks to bypass (not recommended)"
    exit 1
  fi
  echo ""
  
  echo "Step 2/3: Security scanning..."
  if ! bash "$SCRIPT_DIR/security-scan.sh" "$SKILL_DIR"; then
    echo ""
    echo "❌ Security scan found red flags. Fix issues and try again."
    echo "   Or use --force to bypass (dangerous)"
    if [[ "$FORCE" != true ]]; then
      exit 1
    else
      echo "   ⚠️  --force specified, continuing anyway..."
    fi
  fi
  echo ""
  
  echo "Step 3/3: Publishing to ClawHub..."
else
  echo "⚠️  Skipping validation and security checks"
  echo ""
  echo "Publishing to ClawHub..."
fi

# Check if clawhub is installed
if ! command -v clawhub &> /dev/null; then
  echo "❌ Error: clawhub CLI not found"
  echo "   Install with: npm i -g clawhub"
  exit 1
fi

# Get skill name from SKILL.md for the --name flag
SKILL_NAME=$(grep -E "^name:" "$SKILL_DIR/SKILL.md" | head -1 | sed 's/name:\s*//' | tr -d '"'"'" || echo "$SLUG")

# Build publish command
PUBLISH_CMD="clawhub publish \"$SKILL_DIR\" --slug \"$SLUG\" --version \"$VERSION\""

if [[ -n "$SKILL_NAME" ]]; then
  PUBLISH_CMD="$PUBLISH_CMD --name \"$SKILL_NAME\""
fi

if [[ -n "$CHANGELOG" ]]; then
  PUBLISH_CMD="$PUBLISH_CMD --changelog \"$CHANGELOG\""
fi

echo "Running: $PUBLISH_CMD"
echo ""

# Execute publish
eval "$PUBLISH_CMD"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Published successfully!"
echo ""
echo "View at: https://clawhub.com/$SLUG"
echo "Install: clawhub install $SLUG"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
