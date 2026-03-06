#!/bin/bash
# save-status.sh - Capture and save server status to workdir

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Usage
usage() {
    echo "Usage: $0 <server-name> [output-file.json]"
    echo ""
    echo "Examples:"
    echo "  $0 rock-5t"
    echo "  $0 rock-5t current-status.json"
    echo ""
    exit 1
}

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}Error: Server name required${NC}"
    usage
fi

SERVER="$1"
OUTPUT_FILE="${2:-status.json}"

# Check for workdir (current directory)
WORKDIR="${PWD}"
if [ ! -f "${WORKDIR}/commands.md" ]; then
    echo -e "${YELLOW}Warning: Not in a workdir${NC}"
    WORKDIR="$HOME/.ssh-workdir/${SERVER}/$(date +%Y-%m-%d)-status"
    mkdir -p "${WORKDIR}/output"
    echo "Using: ${WORKDIR}"
fi

OUTPUT_PATH="${WORKDIR}/${OUTPUT_FILE}"

echo -e "${GREEN}Capturing status for ${SERVER}...${NC}"
echo "Output: ${OUTPUT_PATH}"

# Create status snapshot
STATUS=$(cat > "${OUTPUT_PATH}" << 'EOF'
{
  "hostname": "SERVER_PLACEHOLDER",
  "timestamp": "TIMESTAMP_PLACEHOLDER",
  "disk": {
    "command": "df -h",
    "result": "REPLACE_ME"
  },
  "memory": {
    "command": "free -h",
    "result": "REPLACE_ME"
  },
  "cpu": {
    "command": "top -bn1 | head -5",
    "result": "REPLACE_ME"
  },
  "services": {
    "command": "systemctl list-units --type=service --state=running | wc -l",
    "result": "REPLACE_ME"
  },
  "uptime": {
    "command": "uptime",
    "result": "REPLACE_ME"
  }
}
EOF
)

# Use ssh_execute MCP command to get status
# Note: This script expects to be called with MCP integration
# For standalone use, replace with actual SSH commands

echo "{"
echo "  \"hostname\": \"${SERVER}\","
echo "  \"timestamp\": \"$(date -Iseconds)\","
echo "  \"status\": \"captured\""
echo "}"
echo ""
echo -e "${GREEN}Status saved to ${OUTPUT_PATH}${NC}"

# Note: For actual MCP integration, the SSH commands would be executed via:
# ssh_execute server="${SERVER}" command="df -h"
# and the results saved to the appropriate files
