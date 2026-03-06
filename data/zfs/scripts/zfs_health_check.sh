#!/usr/bin/env bash
# ZFS Health Check — summarizes pool and dataset status
# Usage: bash zfs_health_check.sh [pool_name]
# If no pool name given, checks all pools.

set -euo pipefail

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

POOL="${1:-}"

print_header() {
    echo ""
    echo "=========================================="
    echo " $1"
    echo "=========================================="
}

check_pool_status() {
    local pool="$1"
    local state
    state=$(zpool get -H -o value health "$pool")

    case "$state" in
        ONLINE)  echo -e "  State: ${GREEN}${state}${NC}" ;;
        DEGRADED) echo -e "  State: ${YELLOW}${state}${NC} — pool is running with reduced redundancy" ;;
        FAULTED) echo -e "  State: ${RED}${state}${NC} — pool cannot serve I/O" ;;
        *)       echo -e "  State: ${RED}${state}${NC}" ;;
    esac
}

check_pool_capacity() {
    local pool="$1"
    local cap
    cap=$(zpool get -H -o value capacity "$pool" | tr -d '%')

    if [ "$cap" -ge 90 ]; then
        echo -e "  Capacity: ${RED}${cap}%${NC} — CRITICAL: performance severely degraded"
    elif [ "$cap" -ge 80 ]; then
        echo -e "  Capacity: ${YELLOW}${cap}%${NC} — WARNING: approaching performance degradation"
    else
        echo -e "  Capacity: ${GREEN}${cap}%${NC}"
    fi
}

check_pool_errors() {
    local pool="$1"
    local errors
    errors=$(zpool status "$pool" | grep -c "DEGRADED\|FAULTED\|REMOVED\|UNAVAIL" || true)

    if [ "$errors" -gt 0 ]; then
        echo -e "  Devices with issues: ${RED}${errors}${NC}"
        zpool status "$pool" | grep -E "DEGRADED|FAULTED|REMOVED|UNAVAIL" | sed 's/^/    /'
    else
        echo -e "  Device errors: ${GREEN}none${NC}"
    fi
}

check_scrub_status() {
    local pool="$1"
    local scan_line
    scan_line=$(zpool status "$pool" | grep "scan:" || echo "  scan: no scrubs performed")

    if echo "$scan_line" | grep -q "scrub in progress"; then
        echo -e "  Scrub: ${YELLOW}in progress${NC}"
        zpool status "$pool" | grep -A1 "scan:" | sed 's/^/    /'
    elif echo "$scan_line" | grep -q "with 0 errors"; then
        echo -e "  Last scrub: ${GREEN}clean${NC}"
        echo "    $scan_line"
    elif echo "$scan_line" | grep -q "errors"; then
        echo -e "  Last scrub: ${RED}errors found${NC}"
        echo "    $scan_line"
    else
        echo -e "  Scrub: ${YELLOW}no scrubs performed${NC}"
    fi
}

check_io_errors() {
    local pool="$1"
    local total_errors
    total_errors=$(zpool status "$pool" | awk '/READ WRITE CKSUM/{found=1; next} found && /^ /{sum+=$3+$4+$5} END{print sum+0}')

    if [ "$total_errors" -gt 0 ]; then
        echo -e "  I/O errors (read+write+cksum): ${RED}${total_errors}${NC}"
    else
        echo -e "  I/O errors: ${GREEN}0${NC}"
    fi
}

# Determine pools to check
if [ -n "$POOL" ]; then
    pools="$POOL"
else
    pools=$(zpool list -H -o name 2>/dev/null || true)
fi

if [ -z "$pools" ]; then
    echo "No ZFS pools found."
    exit 0
fi

print_header "ZFS Health Check — $(date '+%Y-%m-%d %H:%M:%S')"

for pool in $pools; do
    echo ""
    echo "--- Pool: $pool ---"
    check_pool_status "$pool"
    check_pool_capacity "$pool"
    check_pool_errors "$pool"
    check_io_errors "$pool"
    check_scrub_status "$pool"
done

# Dataset summary
print_header "Dataset Overview"
zpool list -o name,size,alloc,free,frag,cap,health
echo ""
zfs list -o name,used,avail,refer,mountpoint -r ${POOL:-} 2>/dev/null | head -50

# Check for file-backed vdevs (warning)
echo ""
for pool in $pools; do
    file_vdevs=$(zpool status "$pool" | grep -E "^\s+/" | grep -v "/dev/" || true)
    if [ -n "$file_vdevs" ]; then
        echo -e "${YELLOW}WARNING: Pool '$pool' contains file-backed vdevs (not suitable for production):${NC}"
        echo "$file_vdevs" | sed 's/^/  /'
    fi
done

echo ""
echo "Health check complete."
