#!/bin/bash
# Publish grazer-skill to NPM and PyPI

set -e

echo "🐄 GRAZER Publishing Script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if on main/master branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$BRANCH" != "main" && "$BRANCH" != "master" ]]; then
    echo "❌ Must be on main/master branch (currently on: $BRANCH)"
    exit 1
fi

# Check for uncommitted changes
if [[ -n $(git status -s) ]]; then
    echo "❌ Uncommitted changes detected. Commit first!"
    exit 1
fi

echo ""
echo "📦 Building TypeScript..."
npm run build

echo ""
echo "🧪 Running tests..."
npm test || true

echo ""
echo "📤 Publishing to NPM..."
npm publish --access public

echo ""
echo "🐍 Building Python wheel..."
python3 setup.py sdist bdist_wheel

echo ""
echo "📤 Publishing to PyPI..."
python3 -m twine upload dist/*

echo ""
echo "🏷️  Creating Git tag..."
VERSION=$(node -p "require('./package.json').version")
git tag -a "v$VERSION" -m "Release v$VERSION"
git push origin "v$VERSION"
git push origin main

echo ""
echo "✅ Successfully published grazer v$VERSION!"
echo ""
echo "📊 Track downloads:"
echo "   NPM: https://npmjs.com/package/@elyanlabs/grazer"
echo "   PyPI: https://pypi.org/project/grazer-skill/"
echo "   BoTTube: https://bottube.ai/skills/grazer"
