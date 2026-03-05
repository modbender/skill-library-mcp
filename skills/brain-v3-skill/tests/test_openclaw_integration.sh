#!/usr/bin/env bash
#
# ClawBrain OpenClaw Integration Test
# Restarts OpenClaw and verifies ClawBrain skill is loaded
#
# Usage:
#   ./test_openclaw_integration.sh           # Test with auto-detected platform
#   ./test_openclaw_integration.sh openclaw  # Force OpenClaw
#   ./test_openclaw_integration.sh clawdbot  # Force ClawdBot
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_step() { echo -e "${CYAN}▶ $1${NC}"; }

echo ""
echo "========================================"
echo "  ClawBrain OpenClaw Integration Test"
echo "========================================"
echo ""

# Detect or use specified platform
PLATFORM="${1:-auto}"

if [ "$PLATFORM" = "auto" ]; then
    if [ -d "$HOME/.openclaw" ]; then
        PLATFORM="openclaw"
    elif [ -d "$HOME/.clawdbot" ]; then
        PLATFORM="clawdbot"
    else
        log_error "No OpenClaw or ClawdBot installation detected!"
        log_info "Looking for ~/.openclaw or ~/.clawdbot directories"
        exit 1
    fi
fi

# Set paths based on platform
case "$PLATFORM" in
    openclaw)
        SERVICE_NAME="openclaw"
        CONFIG_DIR="$HOME/.openclaw"
        SKILLS_DIR="$HOME/.openclaw/skills"
        HOOKS_DIR="$HOME/.openclaw/hooks"
        LOG_FILE="$HOME/.openclaw/logs/openclaw.log"
        ;;
    clawdbot)
        SERVICE_NAME="clawdbot"
        CONFIG_DIR="$HOME/.clawdbot"
        SKILLS_DIR="$HOME/.clawdbot/skills"
        HOOKS_DIR="$HOME/.clawdbot/hooks"
        LOG_FILE="$HOME/.clawdbot/logs/clawdbot.log"
        ;;
    *)
        log_error "Unknown platform: $PLATFORM"
        log_info "Use 'openclaw' or 'clawdbot'"
        exit 1
        ;;
esac

log_info "Platform: $PLATFORM"
log_info "Config: $CONFIG_DIR"
echo ""

# ============================================================================
# Pre-flight checks
# ============================================================================
log_step "Step 1: Pre-flight checks"

# Check if service exists
if ! systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
    log_warning "Service '$SERVICE_NAME' not found as systemd service"
    log_info "Checking for process..."
    if pgrep -f "$SERVICE_NAME" > /dev/null; then
        log_info "Found running $SERVICE_NAME process"
    else
        log_error "No $SERVICE_NAME service or process found"
        exit 1
    fi
fi

# Check ClawBrain installation
CLAWBRAIN_SKILL="$SKILLS_DIR/clawbrain"
if [ -d "$CLAWBRAIN_SKILL" ]; then
    log_success "ClawBrain skill found at: $CLAWBRAIN_SKILL"
else
    log_warning "ClawBrain skill not found at $CLAWBRAIN_SKILL"
    log_info "Checking pip installation..."
    if python3 -c "import clawbrain" 2>/dev/null; then
        log_success "ClawBrain installed via pip"
    else
        log_error "ClawBrain not installed!"
        log_info "Install with: pip install clawbrain[all]"
        exit 1
    fi
fi

# Check hook installation
CLAWBRAIN_HOOK="$HOOKS_DIR/clawbrain-startup"
if [ -d "$CLAWBRAIN_HOOK" ]; then
    log_success "ClawBrain hook found at: $CLAWBRAIN_HOOK"
else
    log_warning "ClawBrain hook not installed at $HOOKS_DIR"
    log_info "Run 'clawbrain setup' to install hooks"
fi

echo ""

# ============================================================================
# Restart service
# ============================================================================
log_step "Step 2: Restarting $SERVICE_NAME service"

# Check if we can use systemctl
if command -v systemctl &> /dev/null && systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
    log_info "Stopping $SERVICE_NAME..."
    sudo systemctl stop "$SERVICE_NAME" 2>/dev/null || true
    sleep 2
    
    log_info "Starting $SERVICE_NAME..."
    sudo systemctl start "$SERVICE_NAME"
    sleep 3
    
    # Check status
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_success "$SERVICE_NAME is running"
    else
        log_error "$SERVICE_NAME failed to start"
        log_info "Check logs with: journalctl -u $SERVICE_NAME -n 50"
        exit 1
    fi
else
    log_warning "systemctl not available or service not registered"
    log_info "Attempting process restart..."
    
    # Kill existing process
    pkill -f "$SERVICE_NAME" 2>/dev/null || true
    sleep 2
    
    # Try to start (this is platform-specific)
    log_warning "Manual restart required - cannot auto-start without systemd"
    log_info "Please start $SERVICE_NAME manually and re-run this script with --check-only"
fi

echo ""

# ============================================================================
# Verify ClawBrain is loaded
# ============================================================================
log_step "Step 3: Verifying ClawBrain is loaded"

# Wait for service to fully initialize
log_info "Waiting for service to initialize..."
sleep 5

# Check logs for ClawBrain
if [ -f "$LOG_FILE" ]; then
    log_info "Checking logs at: $LOG_FILE"
    
    # Look for ClawBrain-related log entries (last 100 lines)
    if tail -100 "$LOG_FILE" 2>/dev/null | grep -qi "clawbrain\|brain"; then
        log_success "Found ClawBrain references in logs"
        echo ""
        log_info "Recent ClawBrain log entries:"
        tail -100 "$LOG_FILE" | grep -i "clawbrain\|brain" | tail -10 | while read line; do
            echo "   $line"
        done
    else
        log_warning "No ClawBrain references found in recent logs"
    fi
else
    log_warning "Log file not found at $LOG_FILE"
fi

# Check if hook was triggered (look for startup hook)
if [ -f "$HOOKS_DIR/clawbrain-startup/handler.js" ]; then
    log_info "Checking if startup hook is registered..."
    
    # Try to find hook registration in config
    if [ -f "$CONFIG_DIR/config.json" ] || [ -f "$CONFIG_DIR/config.yaml" ]; then
        log_success "Config file found"
    fi
fi

echo ""

# ============================================================================
# Test ClawBrain functionality
# ============================================================================
log_step "Step 4: Testing ClawBrain functionality"

# Create a test script
TEST_SCRIPT=$(mktemp)
cat > "$TEST_SCRIPT" << 'PYTHON_TEST'
#!/usr/bin/env python3
import sys
import os

# Add skill path if needed
skill_path = os.path.expanduser("~/.openclaw/skills/clawbrain")
if os.path.exists(skill_path) and skill_path not in sys.path:
    sys.path.insert(0, skill_path)

try:
    from clawbrain import Brain
    print("✅ ClawBrain imported successfully")
    
    # Initialize Brain
    brain = Brain()
    print(f"✅ Brain initialized with {brain.storage_backend} storage")
    
    # Check encryption
    if brain._cipher:
        print("✅ Encryption is enabled")
    else:
        print("⚠️  Encryption not available")
    
    # Health check
    health = brain.health_check()
    storage_ok = health.get("sqlite") or health.get("postgresql")
    if storage_ok:
        print("✅ Storage backend is healthy")
    else:
        print("❌ Storage backend issue")
        sys.exit(1)
    
    # Test remember/recall
    test_memory = brain.remember(
        agent_id="integration-test",
        memory_type="test",
        content="Integration test at " + __import__('datetime').datetime.now().isoformat(),
        key="test_key"
    )
    print(f"✅ Memory stored: {test_memory.id[:8]}...")
    
    # Recall
    memories = brain.recall(agent_id="integration-test", memory_type="test")
    if memories:
        print(f"✅ Memory recalled: {len(memories)} items")
    else:
        print("❌ Failed to recall memory")
        sys.exit(1)
    
    brain.close()
    print("\n🎉 All ClawBrain tests passed!")
    sys.exit(0)
    
except ImportError as e:
    print(f"❌ Failed to import ClawBrain: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
PYTHON_TEST

python3 "$TEST_SCRIPT"
TEST_RESULT=$?
rm -f "$TEST_SCRIPT"

echo ""

# ============================================================================
# Summary
# ============================================================================
echo "========================================"
echo "  Summary"
echo "========================================"

if [ $TEST_RESULT -eq 0 ]; then
    log_success "ClawBrain is properly integrated with $PLATFORM!"
    echo ""
    log_info "ClawBrain is ready to use."
    log_info "Skills directory: $SKILLS_DIR/clawbrain"
    log_info "Hooks directory: $HOOKS_DIR/clawbrain-startup"
    echo ""
    exit 0
else
    log_error "ClawBrain integration test failed!"
    echo ""
    log_info "Troubleshooting steps:"
    echo "  1. Check if ClawBrain is installed: pip show clawbrain"
    echo "  2. Run setup: clawbrain setup"
    echo "  3. Check service logs: journalctl -u $SERVICE_NAME -n 50"
    echo "  4. Verify hooks: ls -la $HOOKS_DIR/"
    echo ""
    exit 1
fi
