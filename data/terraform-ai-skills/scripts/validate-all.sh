#!/bin/bash
# Validate All Modules Script
# Runs terraform validate on all modules and examples

set -e

# Load configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/../config/global.config"

if [ -f "$CONFIG_FILE" ]; then
  source "$CONFIG_FILE"
else
  echo "❌ Configuration file not found: $CONFIG_FILE"
  exit 1
fi

echo "🔍 Starting Validation"
echo ""

TOTAL=0
SUCCESS=0
FAILED=0
FAILED_ITEMS=()

# Function to validate a module
validate_module() {
  local path=$1
  local name=$2
  
  cd "$path"
  
  if terraform init -backend=false >/dev/null 2>&1; then
    if terraform validate >/dev/null 2>&1; then
      echo "  ✅ $name"
      ((SUCCESS++))
    else
      echo "  ❌ $name - validation failed"
      FAILED_ITEMS+=("$name")
      ((FAILED++))
    fi
  else
    echo "  ⚠️  $name - init failed"
    FAILED_ITEMS+=("$name (init)")
    ((FAILED++))
  fi
  
  cd - >/dev/null
  ((TOTAL++))
}

# Validate each repository
for dir in terraform-${PROVIDER_NAME}-*/; do
  repo_name="${dir%/}"
  
  if [[ " ${EXCLUDE_REPOS} " =~ " ${repo_name} " ]]; then
    continue
  fi
  
  if [ ! -d "$dir" ]; then
    continue
  fi
  
  echo "=== $repo_name ==="
  
  # Validate main module
  if [ -f "$dir/versions.tf" ]; then
    validate_module "$dir" "main"
  fi
  
  # Validate examples
  if [ -d "$dir/_examples" ]; then
    for example in "$dir/_examples"/*/ ; do
      if [ -f "$example/versions.tf" ]; then
        example_name=$(basename "$example")
        validate_module "$example" "example:$example_name"
      fi
    done
  fi
  
  echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Validation Results:"
echo "  Total:   $TOTAL"
echo "  ✅ Success: $SUCCESS"
echo "  ❌ Failed:  $FAILED"

if [ ${#FAILED_ITEMS[@]} -gt 0 ]; then
  echo ""
  echo "Failed items:"
  for item in "${FAILED_ITEMS[@]}"; do
    echo "  - $item"
  done
  exit 1
else
  echo ""
  echo "🎉 All validations passed!"
fi
