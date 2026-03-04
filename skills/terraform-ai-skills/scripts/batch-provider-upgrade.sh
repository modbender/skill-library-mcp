#!/bin/bash
# Batch Provider Upgrade Script
# Updates provider version across all Terraform modules

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

echo "🚀 Starting Provider Upgrade"
echo "Provider: ${PROVIDER_NAME}"
echo "Target Version: >= ${PROVIDER_MIN_VERSION}"
echo "Terraform Version: >= ${TERRAFORM_MIN_VERSION}"
echo ""

# Find all matching repositories
REPOS=()
for dir in terraform-${PROVIDER_NAME}-*/; do
  repo_name="${dir%/}"
  # Check if in exclude list
  if [[ " ${EXCLUDE_REPOS} " =~ " ${repo_name} " ]]; then
    echo "⏭️  Skipping $repo_name (excluded)"
    continue
  fi
  if [ -d "$dir" ] && [ -f "$dir/versions.tf" ]; then
    REPOS+=("$repo_name")
  fi
done

echo "Found ${#REPOS[@]} repositories to update"
echo ""

# Process each repository
SUCCESS_COUNT=0
FAIL_COUNT=0

for repo in "${REPOS[@]}"; do
  echo "=== Processing $repo ==="
  cd "$repo"
  
  # Update main versions.tf
  if [ -f "versions.tf" ]; then
    sed -i.bak "s/version = \">=.*\"/version = \">= ${PROVIDER_MIN_VERSION}\"/g" versions.tf
    sed -i.bak "s/required_version = \">=.*\"/required_version = \">= ${TERRAFORM_MIN_VERSION}\"/g" versions.tf
    rm -f versions.tf.bak
    echo "  ✅ Updated main versions.tf"
  fi
  
  # Update example versions.tf files
  if [ -d "_examples" ]; then
    example_count=0
    for vfile in $(find _examples -name "versions.tf" -type f); do
      sed -i.bak "s/version = \">=.*\"/version = \">= ${PROVIDER_MIN_VERSION}\"/g" "$vfile"
      sed -i.bak "s/required_version = \">=.*\"/required_version = \">= ${TERRAFORM_MIN_VERSION}\"/g" "$vfile"
      rm -f "${vfile}.bak"
      ((example_count++))
    done
    echo "  ✅ Updated $example_count example files"
  fi
  
  # Validate if enabled
  if [ "$RUN_TERRAFORM_VALIDATE" = true ]; then
    if terraform init -backend=false >/dev/null 2>&1 && terraform validate >/dev/null 2>&1; then
      echo "  ✅ Validation passed"
    else
      echo "  ⚠️  Validation failed (continuing anyway)"
    fi
  fi
  
  # Commit changes
  git add versions.tf _examples/ 2>/dev/null || true
  if git diff --staged --quiet; then
    echo "  ⏭️  No changes to commit"
  else
    git commit -m "⬆️ upgrade: update provider to >= ${PROVIDER_MIN_VERSION}" >/dev/null
    echo "  ✅ Changes committed"
    ((SUCCESS_COUNT++))
  fi
  
  cd ..
  echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Upgrade Complete!"
echo "   Successfully updated: $SUCCESS_COUNT"
echo "   Skipped/Failed: $FAIL_COUNT"
echo ""
echo "Next steps:"
echo "1. Review changes with: git diff"
echo "2. Push changes: git push origin ${DEFAULT_BRANCH}"
echo "3. Create releases"
