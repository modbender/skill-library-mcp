#!/bin/bash
# Memory Compression System - Installation Script
# Version: 3.0.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE_DIR="/home/node/.openclaw/workspace"
CONFIG_DIR="$SKILL_DIR/config"
DATA_DIR="$SKILL_DIR/data"
LOGS_DIR="$SKILL_DIR/logs"
BACKUP_DIR="$WORKSPACE_DIR/archive/memory-compression-backup"

# Log function
log() {
    echo -e "${BLUE}[INSTALL]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if running as node user
    if [ "$(whoami)" != "node" ]; then
        warning "Running as user: $(whoami). Recommended: node"
    fi
    
    # Check OpenClaw workspace
    if [ ! -d "$WORKSPACE_DIR" ]; then
        error "OpenClaw workspace not found: $WORKSPACE_DIR"
    fi
    
    # Check required commands
    for cmd in bash node npm jq crc32; do
        if ! command -v $cmd &> /dev/null; then
            warning "Command not found: $cmd (some features may not work)"
        fi
    done
    
    success "Prerequisites check passed"
}

# Backup existing files
backup_existing() {
    log "Backing up existing files..."
    
    mkdir -p "$BACKUP_DIR"
    timestamp=$(date +%Y%m%d_%H%M%S)
    
    # Backup existing memory compression files
    if [ -d "$WORKSPACE_DIR/skills/extreme-context-compression" ]; then
        cp -r "$WORKSPACE_DIR/skills/extreme-context-compression" "$BACKUP_DIR/extreme-context-compression_$timestamp"
        log "Backed up extreme-context-compression"
    fi
    
    if [ -d "$WORKSPACE_DIR/skills/memory-manager" ]; then
        cp -r "$WORKSPACE_DIR/skills/memory-manager" "$BACKUP_DIR/memory-manager_$timestamp"
        log "Backed up memory-manager"
    fi
    
    # Backup existing cron jobs related to memory/compression
    if command -v openclaw &> /dev/null; then
        openclaw cron list --json > "$BACKUP_DIR/cron-jobs_$timestamp.json" 2>/dev/null || true
        log "Backed up cron jobs"
    fi
    
    success "Backup completed: $BACKUP_DIR"
}

# Create directory structure
create_directories() {
    log "Creating directory structure..."
    
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$DATA_DIR/compressed"
    mkdir -p "$DATA_DIR/backups"
    mkdir -p "$DATA_DIR/search"
    mkdir -p "$LOGS_DIR"
    mkdir -p "$SKILL_DIR/test"
    mkdir -p "$SKILL_DIR/examples"
    
    success "Directory structure created"
}

# Create default configuration
create_configuration() {
    log "Creating default configuration..."
    
    # Main configuration
    cat > "$CONFIG_DIR/default.conf" << 'EOF'
# Memory Compression System Configuration
# Version: 3.0.0

# Compression settings
COMPRESSION_ENABLED=true
DEFAULT_FORMAT=ultra
RETENTION_DAYS=30
MAX_COMPRESSED_FILES=100
BACKUP_BEFORE_COMPRESSION=true

# Cron schedule (UTC)
COMPRESSION_SCHEDULE="0 */6 * * *"  # Every 6 hours
CLEANUP_SCHEDULE="0 4 * * *"       # Daily at 04:00
HEALTH_CHECK_SCHEDULE="0 * * * *"  # Hourly

# Search settings
SEARCH_ENABLED=true
SEARCH_INDEX_AUTO_UPDATE=true
SEARCH_HISTORY_SIZE=1000
SEARCH_CACHE_SIZE=100

# Performance settings
MAX_MEMORY_MB=100
MAX_PROCESSING_TIME_SEC=300
COMPRESSION_TIMEOUT_SEC=60
SEARCH_TIMEOUT_SEC=30

# Notification settings
NOTIFY_ON_ERROR=true
NOTIFY_ON_SUCCESS=false
TELEGRAM_NOTIFICATIONS=false
TELEGRAM_CHAT_ID=""

# Logging settings
LOG_LEVEL=info
LOG_RETENTION_DAYS=7
LOG_ROTATION_SIZE_MB=10

# Advanced settings
ENABLE_DEBUG_MODE=false
ENABLE_TEST_MODE=false
AUTO_UPDATE=false
EOF
    
    # Cron schedule file
    cat > "$CONFIG_DIR/cron-schedule" << 'EOF'
# Memory Compression System Cron Schedule
# All times in UTC

# Compression: Every 6 hours
0 */6 * * * cd /home/node/.openclaw/workspace/skills/memory-compression-system && ./scripts/compress.sh --auto

# Cleanup: Daily at 04:00
0 4 * * * cd /home/node/.openclaw/workspace/skills/memory-compression-system && ./scripts/cleanup.sh

# Health Check: Hourly
0 * * * * cd /home/node/.openclaw/workspace/skills/memory-compression-system && ./scripts/health.sh --quick
EOF
    
    success "Configuration files created"
}

# Create basic scripts
create_scripts() {
    log "Creating basic scripts..."
    
    # Make scripts directory executable
    chmod +x "$SKILL_DIR/scripts"/*
    
    # Create basic script templates
    for script in enable.sh disable.sh status.sh health.sh; do
        if [ ! -f "$SKILL_DIR/scripts/$script" ]; then
            cat > "$SKILL_DIR/scripts/$script" << 'EOF'
#!/bin/bash
# Memory Compression System - Basic Script Template
# This file will be replaced during full installation

echo "Script not fully installed yet. Run install.sh first."
exit 1
EOF
            chmod +x "$SKILL_DIR/scripts/$script"
        fi
    done
    
    success "Basic scripts created"
}

# Create package.json
create_package_json() {
    log "Creating package.json..."
    
    cat > "$SKILL_DIR/package.json" << 'EOF'
{
  "name": "memory-compression-system",
  "version": "3.0.0",
  "description": "Integrated memory management and extreme context compression for OpenClaw",
  "main": "scripts/compress.sh",
  "scripts": {
    "test": "./test/run-tests.sh",
    "install": "./scripts/install.sh",
    "start": "./scripts/enable.sh",
    "stop": "./scripts/disable.sh",
    "status": "./scripts/status.sh",
    "health": "./scripts/health.sh"
  },
  "keywords": [
    "memory",
    "compression",
    "automation",
    "openclaw",
    "optimization"
  ],
  "author": "tenx (@Safetbear)",
  "license": "MIT",
  "dependencies": {},
  "devDependencies": {},
  "engines": {
    "node": ">=14.0.0",
    "openclaw": ">=1.0.0"
  }
}
EOF
    
    success "package.json created"
}

# Create README.md
create_readme() {
    log "Creating README.md..."
    
    cat > "$SKILL_DIR/README.md" << 'EOF'
# Memory Compression System

Integrated memory management and extreme context compression for OpenClaw.

## Quick Installation

```bash
# Clone the skill
cd /home/node/.openclaw/workspace/skills
git clone [repository-url] memory-compression-system

# Install
cd memory-compression-system
./scripts/install.sh

# Enable
./scripts/enable.sh
```

## Features

- **Three compression formats**: Base64, Binary, Ultra-Compact
- **Automatic scheduling**: Compression every 6 hours
- **Search functionality**: Unified search across all memory
- **Backup system**: Automatic backups before operations
- **Health monitoring**: Built-in health checks

## Basic Usage

```bash
# Check status
./scripts/status.sh

# Manual compression
./scripts/compress.sh --format ultra

# Search memory
./scripts/search.sh "keyword"

# View logs
./scripts/logs.sh
```

## Configuration

Edit `config/default.conf` to adjust settings:

```bash
# Compression frequency
COMPRESSION_SCHEDULE="0 */6 * * *"  # Every 6 hours

# Retention policy
RETENTION_DAYS=30

# Default format
DEFAULT_FORMAT=ultra
```

## Documentation

Full documentation available in `SKILL.md`.

## Support

For issues and questions:
1. Check `logs/` directory
2. Run `./scripts/health.sh`
3. Review `examples/troubleshooting.md`

## License

MIT License
EOF
    
    success "README.md created"
}

# Create initial data files
create_initial_data() {
    log "Creating initial data files..."
    
    # Create search index
    cat > "$DATA_DIR/search/index.json" << 'EOF'
{
  "version": "3.0.0",
  "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "last_updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "file_count": 0,
  "files": [],
  "statistics": {
    "total_size": 0,
    "average_ratio": 0,
    "formats": {}
  }
}
EOF
    
    # Create compression history
    cat > "$DATA_DIR/compression-history.csv" << 'EOF'
timestamp,format,original_size,compressed_size,ratio,duration_ms,success
EOF
    
    # Create empty log files
    touch "$LOGS_DIR/compression.log"
    touch "$LOGS_DIR/search.log"
    touch "$LOGS_DIR/error.log"
    touch "$LOGS_DIR/performance.log"
    
    success "Initial data files created"
}

# Set up cron job
setup_cron_job() {
    log "Setting up cron job..."
    
    # Check if openclaw command is available
    if command -v openclaw &> /dev/null; then
        log "Creating OpenClaw cron job..."
        
        # Create cron job via OpenClaw API
        cron_job=$(cat << 'EOF'
{
  "name": "Memory Compression System",
  "schedule": {
    "kind": "every",
    "everyMs": 21600000
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Run Memory Compression System: cd /home/node/.openclaw/workspace/skills/memory-compression-system && ./scripts/compress.sh --auto",
    "timeoutSeconds": 300
  },
  "delivery": {
    "mode": "announce"
  }
}
EOF
        )
        
        # Try to create the cron job
        if openclaw cron add --json "$cron_job" &> /dev/null; then
            success "OpenClaw cron job created"
        else
            warning "Failed to create OpenClaw cron job (may need manual setup)"
        fi
    else
        warning "openclaw command not found, skipping cron setup"
        log "Manual cron setup required. Add to crontab:"
        log "0 */6 * * * cd $SKILL_DIR && ./scripts/compress.sh --auto"
    fi
    
    success "Cron setup completed"
}

# Finalize installation
finalize_installation() {
    log "Finalizing installation..."
    
    # Set permissions
    chmod -R 755 "$SKILL_DIR/scripts"
    chmod 644 "$CONFIG_DIR"/*
    chmod 644 "$DATA_DIR"/*
    
    # Create installation marker
    cat > "$SKILL_DIR/.installed" << EOF
Memory Compression System v3.0.0
Installed: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Installation ID: $(uuidgen)
Backup location: $BACKUP_DIR
EOF
    
    # Installation summary
    echo ""
    echo "========================================="
    echo "  MEMORY COMPRESSION SYSTEM INSTALLED"
    echo "========================================="
    echo ""
    echo "📁 Skill directory: $SKILL_DIR"
    echo "📁 Configuration: $CONFIG_DIR"
    echo "📁 Data: $DATA_DIR"
    echo "📁 Logs: $LOGS_DIR"
    echo "📁 Backup: $BACKUP_DIR"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Review configuration: $CONFIG_DIR/default.conf"
    echo "2. Enable the system: ./scripts/enable.sh"
    echo "3. Check status: ./scripts/status.sh"
    echo "4. Test compression: ./scripts/compress.sh --test"
    echo ""
    echo "📚 Documentation: $SKILL_DIR/SKILL.md"
    echo ""
    
    success "Installation completed successfully!"
}

# Main installation process
main() {
    echo ""
    echo "========================================="
    echo "  Memory Compression System v3.0.0"
    echo "  Installation Script"
    echo "========================================="
    echo ""
    
    check_prerequisites
    backup_existing
    create_directories
    create_configuration
    create_scripts
    create_package_json
    create_readme
    create_initial_data
    setup_cron_job
    finalize_installation
}

# Run main function
main "$@"