#!/bin/bash
# Memory Migration Script
# Initializes and migrates memory structure

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/config.json"

# Default values
MEMORY_PATH="./memory"
VERSION="1.0.0"

# Load config if exists
if [[ -f "$CONFIG_FILE" ]]; then
    MEMORY_PATH=$(jq -r '.memory.base_path // "./memory"' "$CONFIG_FILE")
    VERSION=$(jq -r '.migration.version // "1.0.0"' "$CONFIG_FILE")
fi

# Functions
init_structure() {
    echo "🏗️  Initializing memory structure..."
    
    # Create directories
    mkdir -p "$MEMORY_PATH"/{semantic,episodic,procedural,working,index}
    mkdir -p "$MEMORY_PATH/semantic/knowledge"
    mkdir -p "$MEMORY_PATH/episodic/events"
    mkdir -p "$MEMORY_PATH/procedural/scripts"
    mkdir -p "$MEMORY_PATH/working/session"
    mkdir -p "$MEMORY_PATH/index/search"
    
    # Create semantic memory files
    cat > "$MEMORY_PATH/semantic/facts.md" << 'EOF'
# Facts

## Personal Information
- Name: 
- Preferences: 

## Important Dates
- 

## Key Facts
- 
EOF

    cat > "$MEMORY_PATH/semantic/concepts.md" << 'EOF'
# Concepts

## Key Concepts
- 

## Learned Knowledge
- 
EOF

    # Create procedural memory files
    cat > "$MEMORY_PATH/procedural/skills.md" << 'EOF'
# Skills

## Technical Skills
- 

## Soft Skills
- 

## Learning Progress
- 
EOF

    cat > "$MEMORY_PATH/procedural/workflows.md" << 'EOF'
# Workflows

## Common Procedures
1. 

## Automation Scripts
- 
EOF

    # Create working memory files
    cat > "$MEMORY_PATH/working/current.md" << 'EOF'
# Current Context

## Active Tasks
- 

## Recent Context
- 

## Pending Items
- 
EOF

    # Create index files
    cat > "$MEMORY_PATH/index/tags.json" << 'EOF'
{
    "tags": [],
    "last_updated": ""
}
EOF

    cat > "$MEMORY_PATH/index/timeline.json" << 'EOF'
{
    "events": [],
    "last_updated": ""
}
EOF

    # Create version file
    cat > "$MEMORY_PATH/.version" << EOF
$VERSION
EOF

    echo "✅ Memory structure initialized at: $MEMORY_PATH"
}

create_daily() {
    local date_str="${1:-$(date +%Y-%m-%d)}"
    local file_path="$MEMORY_PATH/episodic/${date_str}.md"
    
    if [[ -f "$file_path" ]]; then
        echo "⚠️  Daily file already exists: $file_path"
        return 0
    fi
    
    cat > "$file_path" << EOF
# ${date_str}

## Events
- 

## Conversations
- 

## Decisions
- 

## Learnings
- 
EOF

    echo "✅ Created daily memory: $file_path"
}

migrate() {
    local from_version="$1"
    echo "🔄 Migrating from version $from_version to $VERSION..."
    
    # Check current version
    if [[ -f "$MEMORY_PATH/.version" ]]; then
        local current=$(cat "$MEMORY_PATH/.version")
        if [[ "$current" == "$VERSION" ]]; then
            echo "✅ Already at version $VERSION"
            return 0
        fi
        echo "📋 Current version: $current"
    fi
    
    # Perform migration steps
    # (Add specific migration logic here for future versions)
    
    # Update version
    echo "$VERSION" > "$MEMORY_PATH/.version"
    echo "✅ Migration complete!"
}

# Main command handler
case "${1:-init}" in
    init)
        init_structure
        ;;
    daily)
        create_daily "$2"
        ;;
    migrate)
        migrate "$2"
        ;;
    *)
        echo "Usage: $0 {init|daily [DATE]|migrate [FROM_VERSION]}"
        echo ""
        echo "Commands:"
        echo "  init              Initialize memory structure"
        echo "  daily [DATE]      Create daily memory file (default: today)"
        echo "  migrate [VERSION] Migrate from specified version"
        exit 1
        ;;
esac
