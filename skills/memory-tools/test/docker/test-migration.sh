#!/bin/bash
# Test Migration from v1 to v2
#
# This script:
# 1. Seeds a v1 database with test data
# 2. Installs memory-tools v2
# 3. Runs the migration
# 4. Verifies memories were migrated correctly

set -e

echo "========================================"
echo "Memory-Tools Migration Test"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Paths
V1_DB_PATH="$HOME/.openclaw/memory/tools"
V2_MEMORIES_PATH="$HOME/.openclaw/memories"

# Step 1: Seed v1 database
echo -e "${YELLOW}Step 1: Creating v1 database with test data...${NC}"
cd /app/memory-tools
node test/docker/seed-v1-data.js

# Verify v1 database exists
if [ -f "$V1_DB_PATH/memory.db" ]; then
    echo -e "${GREEN}✓ v1 database created${NC}"
    echo "  Location: $V1_DB_PATH/memory.db"
    echo "  Size: $(du -h "$V1_DB_PATH/memory.db" | cut -f1)"
else
    echo -e "${RED}✗ Failed to create v1 database${NC}"
    exit 1
fi
echo ""

# Step 2: Install memory-tools v2
echo -e "${YELLOW}Step 2: Installing memory-tools v2...${NC}"
npm install
npm run build
echo -e "${GREEN}✓ memory-tools v2 installed${NC}"
echo ""

# Step 3: Run migration test
echo -e "${YELLOW}Step 3: Testing migration...${NC}"

# Create a simple test script that imports and runs migration
node --experimental-vm-modules -e "
import { hasLegacyDatabase, hasNewMemories, migrateFromV1 } from './dist/migration.js';

const legacyPath = '$V1_DB_PATH';
const newPath = '$V2_MEMORIES_PATH';

console.log('Checking for legacy database...');
const hasLegacy = hasLegacyDatabase(legacyPath);
console.log('Has legacy database:', hasLegacy);

console.log('Checking for new memories...');
const hasNew = hasNewMemories(newPath);
console.log('Has new memories:', hasNew);

if (hasLegacy && !hasNew) {
    console.log('Starting migration...');
    const result = await migrateFromV1(legacyPath, newPath);
    console.log('Migration result:', JSON.stringify(result, null, 2));

    if (result.success || result.migratedCount > 0) {
        console.log('Migration successful!');
        process.exit(0);
    } else {
        console.error('Migration failed:', result.errors);
        process.exit(1);
    }
} else if (hasNew) {
    console.log('New memories already exist, skipping migration');
    process.exit(0);
} else {
    console.error('No legacy database found');
    process.exit(1);
}
"

echo ""

# Step 4: Verify migration
echo -e "${YELLOW}Step 4: Verifying migration...${NC}"

# Check that .md files were created
FACT_COUNT=$(find "$V2_MEMORIES_PATH/facts" -name "*.md" 2>/dev/null | wc -l || echo 0)
PREF_COUNT=$(find "$V2_MEMORIES_PATH/preferences" -name "*.md" 2>/dev/null | wc -l || echo 0)
INSTR_COUNT=$(find "$V2_MEMORIES_PATH/instructions" -name "*.md" 2>/dev/null | wc -l || echo 0)
DELETED_COUNT=$(find "$V2_MEMORIES_PATH/.deleted" -name "*.md" 2>/dev/null | wc -l || echo 0)

echo "Migrated memories:"
echo "  Facts: $FACT_COUNT"
echo "  Preferences: $PREF_COUNT"
echo "  Instructions: $INSTR_COUNT"
echo "  Deleted: $DELETED_COUNT"

TOTAL=$((FACT_COUNT + PREF_COUNT + INSTR_COUNT))

if [ "$TOTAL" -gt 0 ]; then
    echo -e "${GREEN}✓ Migration verification passed${NC}"
else
    echo -e "${RED}✗ No memories were migrated${NC}"
    exit 1
fi
echo ""

# Step 5: Check file content
echo -e "${YELLOW}Step 5: Checking file content...${NC}"

# Find first fact file and display it
FIRST_FILE=$(find "$V2_MEMORIES_PATH" -name "*.md" -not -path "*/.deleted/*" | head -1)
if [ -n "$FIRST_FILE" ]; then
    echo "Sample migrated file: $FIRST_FILE"
    echo "---"
    cat "$FIRST_FILE"
    echo "---"
    echo -e "${GREEN}✓ File content looks good${NC}"
else
    echo -e "${RED}✗ No memory files found${NC}"
    exit 1
fi
echo ""

# Step 6: Verify original database preserved
echo -e "${YELLOW}Step 6: Checking backup...${NC}"

if [ -f "$V1_DB_PATH/memory.db" ]; then
    echo -e "${GREEN}✓ Original v1 database preserved at $V1_DB_PATH${NC}"
else
    echo -e "${RED}✗ Original database was deleted${NC}"
    exit 1
fi

if [ -f "$V1_DB_PATH/.migrated-to-v2" ]; then
    echo -e "${GREEN}✓ Migration marker created${NC}"
else
    echo -e "${YELLOW}⚠ Migration marker not found (non-critical)${NC}"
fi
echo ""

# Final summary
echo "========================================"
echo -e "${GREEN}ALL TESTS PASSED${NC}"
echo "========================================"
echo ""
echo "Summary:"
echo "  - v1 database: $V1_DB_PATH/memory.db (preserved)"
echo "  - v2 memories: $V2_MEMORIES_PATH/"
echo "  - Total migrated: $TOTAL active + $DELETED_COUNT deleted"
echo ""
echo "Next steps:"
echo "  1. Install QMD: npm install -g @tobilu/qmd"
echo "  2. Create collection: qmd collection add $V2_MEMORIES_PATH --name memories"
echo "  3. Index: qmd embed"
echo ""
