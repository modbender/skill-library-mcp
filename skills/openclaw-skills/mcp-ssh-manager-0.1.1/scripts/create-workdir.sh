#!/bin/bash
# create-workdir.sh - Create new workdir structure for SSH operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Usage
usage() {
    echo "Usage: $0 <hostname> <YYYY-MM-DD-topic>"
    echo ""
    echo "Examples:"
    echo "  $0 rock-5t 2026-02-07-system-check"
    echo "  $0 rock-5t 2026-02-07-deployment"
    echo ""
    exit 1
}

# Check arguments
if [ -z "$1" ] || [ -z "$2" ]; then
    echo -e "${RED}Error: Missing arguments${NC}"
    usage
fi

HOSTNAME="$1"
TOPIC="$2"
WORKDIR_BASE="${HOME}/.ssh-workdir"

# Validate hostname format
if [[ ! "$HOSTNAME" =~ ^[a-zA-Z0-9][a-zA-Z0-9.-]*$ ]]; then
    echo -e "${RED}Error: Invalid hostname format${NC}"
    exit 1
fi

# Validate topic format
if [[ ! "$TOPIC" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}- ]]; then
    echo -e "${YELLOW}Warning: Topic should start with YYYY-MM-DD- for consistency${NC}"
fi

# Create directory structure
WORKDIR="${WORKDIR_BASE}/${HOSTNAME}/${TOPIC}"
OUTPUT_DIR="${WORKDIR}/output"

echo -e "${GREEN}Creating workdir...${NC}"
echo "  Hostname: ${HOSTNAME}"
echo "  Topic: ${TOPIC}"
echo "  Path: ${WORKDIR}"

# Create directories
mkdir -p "${OUTPUT_DIR}"

# Create tracking files
touch "${WORKDIR}/commands.md"
touch "${WORKDIR}/summary.md"

# Create commands.md template
cat > "${WORKDIR}/commands.md" << EOF
# Commands Log - ${TOPIC}

## Metadata
- Hostname: ${HOSTNAME}
- Created: $(date -Iseconds)
- Purpose: ${TOPIC}

## Commands

### Pre-operation
1. 

### Main operations

### Post-operation

EOF

# Create summary.md template
cat > "${WORKDIR}/summary.md" << 'EOF'
# Summary - 

## Overview

## Findings

## Actions Taken

## Issues Found

## Recommendations

## Next Steps

EOF

# Set permissions
chmod 700 "${WORKDIR}"
chmod 600 "${WORKDIR}/commands.md"
chmod 600 "${WORKDIR}/summary.md"
chmod 755 "${OUTPUT_DIR}"

echo ""
echo -e "${GREEN}✅ Workdir created successfully!${NC}"
echo ""
echo "Structure:"
find "${WORKDIR}" -type f | sed "s|${WORKDIR}|  .|g"
echo ""
echo "To use:"
echo "  cd ${WORKDIR}"
echo ""
echo "To log a command:"
echo "  echo 'command' >> ${WORKDIR}/commands.md"
echo ""
echo "To save output:"
echo "  ssh_execute server=\"${HOSTNAME}\" command=\"df -h\" > ${WORKDIR}/output/df-h.txt"
