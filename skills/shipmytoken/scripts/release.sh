#!/bin/bash
set -euo pipefail

# Release script for shipmytoken-skill
# Usage: ./scripts/release.sh <patch|minor|major> "changelog message"

BUMP_TYPE="${1:?Usage: ./scripts/release.sh <patch|minor|major> \"changelog message\"}"
CHANGELOG_MSG="${2:?Usage: ./scripts/release.sh <patch|minor|major> \"changelog message\"}"

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$SCRIPT_DIR"

# Parse current version
CURRENT=$(node -p "require('./package.json').version")
IFS='.' read -r MAJ MIN PAT <<< "$CURRENT"

# Bump version
case "$BUMP_TYPE" in
  patch) PAT=$((PAT + 1)) ;;
  minor) MIN=$((MIN + 1)); PAT=0 ;;
  major) MAJ=$((MAJ + 1)); MIN=0; PAT=0 ;;
  *) echo "Invalid bump type: $BUMP_TYPE (use patch, minor, or major)"; exit 1 ;;
esac
NEW_VERSION="$MAJ.$MIN.$PAT"

echo "Bumping $CURRENT → $NEW_VERSION"

# 1. Update package.json
node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json','utf-8'));
pkg.version = '$NEW_VERSION';
fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
"

# 2. Update SKILL.md metadata
sed -i '' "s/\"version\":\"$CURRENT\"/\"version\":\"$NEW_VERSION\"/" SKILL.md

# 3. Update CHANGELOG.md
DATE=$(date +%Y-%m-%d)
sed -i '' "s/^## \[$CURRENT\]/## [$NEW_VERSION] - $DATE\n\n$CHANGELOG_MSG\n\n## [$CURRENT]/" CHANGELOG.md

# 4. Commit and tag
git add package.json SKILL.md CHANGELOG.md
git commit -m "v$NEW_VERSION: $(echo "$CHANGELOG_MSG" | head -1)"
git tag -a "v$NEW_VERSION" -m "v$NEW_VERSION"
git push && git push --tags

# 5. Create GitHub release
TOKEN=$(security find-generic-password -a 'new-ground' -s 'github-token-newground' -w)
BODY=$(echo "$CHANGELOG_MSG" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))")
curl -sf -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/new-ground/shipmytoken-skill/releases" \
  -d "{\"tag_name\":\"v$NEW_VERSION\",\"name\":\"v$NEW_VERSION\",\"body\":$BODY}" \
  | python3 -c "import sys,json; print('GitHub release:', json.load(sys.stdin)['html_url'])"

echo "Done! v$NEW_VERSION released."
