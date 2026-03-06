#!/bin/bash
# Batch Release Creation Script
# Creates GitHub releases for all modules with updated changelogs

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

echo "🚀 Starting Release Creation"
echo "Organization: ${ORG_NAME}"
echo ""

# Function to process a single repository
process_repo() {
  local repo=$1
  
  echo "=== Processing $repo ==="
  cd "$repo"
  
  # Get current version
  local old_version=$(git describe --tags --abbrev=0 2>/dev/null || echo "0.0.0")
  old_version="${old_version#v}"
  
  # Calculate new version (increment patch)
  IFS='.' read -r major minor patch <<< "$old_version"
  local new_patch=$((patch + 1))
  local new_version="$major.$minor.$new_patch"
  
  # Check if tag already exists
  if git rev-parse "${TAG_PREFIX}${new_version}" >/dev/null 2>&1; then
    echo "  ⏭️  Tag ${TAG_PREFIX}${new_version} already exists"
    cd ..
    return
  fi
  
  # Get recent commits
  local commits=$(git log --oneline --format="- %s" -15 | head -15)
  
  # Update CHANGELOG
  {
    echo "## [${new_version}] - $(date +%Y-%m-%d)"
    echo ""
    echo "### Changes"
    echo "$commits"
    echo ""
    cat CHANGELOG.md
  } > CHANGELOG.md.new
  mv CHANGELOG.md.new CHANGELOG.md
  
  # Commit and tag
  git add CHANGELOG.md
  git commit -m "📝 docs: update CHANGELOG for v${new_version}" -q
  git tag -a "${TAG_PREFIX}${new_version}" -m "Release v${new_version}"
  
  # Push
  git push origin ${DEFAULT_BRANCH} -q
  git push origin "${TAG_PREFIX}${new_version}" -q
  
  # Create GitHub release
  gh release create "${TAG_PREFIX}${new_version}" \
    --repo "${ORG_NAME}/$repo" \
    --title "🚀 Release v${new_version}" \
    --notes "## What's Changed

$commits

### Key Updates
- ⬆️ Updated provider to v${PROVIDER_MIN_VERSION}+
- ✨ Updated examples with latest versions
- 🐛 Fixed workflow configurations
- 📝 Enhanced documentation

**Full Changelog**: https://github.com/${ORG_NAME}/$repo/releases" >/dev/null
  
  echo "  ✅ Released v${new_version}"
  cd ..
}

# Find and process repositories
REPOS=()
for dir in terraform-${PROVIDER_NAME}-*/; do
  repo_name="${dir%/}"
  if [[ " ${EXCLUDE_REPOS} " =~ " ${repo_name} " ]]; then
    continue
  fi
  if [ -d "$dir/.git" ]; then
    REPOS+=("$repo_name")
  fi
done

echo "Found ${#REPOS[@]} repositories for release"
echo ""

# Process each repository
for repo in "${REPOS[@]}"; do
  process_repo "$repo" || echo "  ⚠️  Failed to process $repo"
  echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Releases Complete!"
echo "   Processed: ${#REPOS[@]} repositories"
echo ""
echo "View releases at: https://github.com/${ORG_NAME}"
