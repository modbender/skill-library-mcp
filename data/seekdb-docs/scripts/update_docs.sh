#!/bin/bash
# Update seekdb-docs from GitHub repository
# This script downloads the latest documentation and replaces the local copy

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_MD="$(dirname "$0")/../SKILL.md"
TARGET_DIR="$(dirname "$0")/../seekdb-docs"

# Extract version from SKILL.md frontmatter
VERSION=$(grep "^version:" "$SKILL_MD" | cut -d'"' -f2)

REPO_URL="https://github.com/oceanbase/seekdb-doc.git"

BRANCH="$VERSION"
TEMP_DIR="/tmp/seekdb-doc-update"

echo -e "${GREEN}=== seekdb-docs Update Script ===${NC}"
echo "This will update the documentation to version: ${VERSION}"
echo ""

# Create temp directory
echo -e "${YELLOW}[1/5] Creating temporary directory...${NC}"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# Clone repository
echo -e "${YELLOW}[2/5] Cloning repository from GitHub...${NC}"
git clone --depth 1 --branch "$BRANCH" --single-branch "$REPO_URL" "$TEMP_DIR" 2>/dev/null || {
    echo -e "${RED}Error: Failed to clone repository${NC}"
    echo "Please check your internet connection and try again."
    exit 1
}

# Copy only the en-US documentation
echo -e "${YELLOW}[3/5] Copying documentation files...${NC}"
rm -rf "$TARGET_DIR"
mkdir -p "$(dirname "$TARGET_DIR")"
cp -r "$TEMP_DIR/en-US" "$TARGET_DIR"

# Get file count
FILE_COUNT=$(find "$TARGET_DIR" -type f -name "*.md" | wc -l)
DIR_SIZE=$(du -sh "$TARGET_DIR" | cut -f1)

# Cleanup
echo -e "${YELLOW}[4/5] Cleaning up temporary files...${NC}"
rm -rf "$TEMP_DIR"

# Done
echo -e "${GREEN}[5/5] Update complete!${NC}"
echo ""
echo "Summary:"
echo "  - Location: $TARGET_DIR"
echo "  - Version: $VERSION"
echo "  - Files: $FILE_COUNT markdown files"
echo "  - Size: $DIR_SIZE"
echo ""
echo -e "${GREEN}✓ Documentation updated successfully${NC}"
echo -e "You can now use the latest seekdb documentation."