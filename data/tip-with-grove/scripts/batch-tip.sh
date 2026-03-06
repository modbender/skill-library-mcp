#!/usr/bin/env bash
#
# batch-tip.sh - Batch tip multiple destinations from a file
#
# Usage:
#   ./batch-tip.sh <input-file> [--network <network>] [--dry-run]
#
# Input file format (CSV or plain text):
#   destination,amount
#   olshansky.info,0.01
#   @username,0.05
#   vitalik.eth,0.10
#
# Or plain text (one per line):
#   olshansky.info 0.01
#   @username 0.05
#   vitalik.eth 0.10
#
# For destination formats, see: grove tip --help
# Full documentation: https://grove.city/docs/skills
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
NETWORK="${DEFAULT_NETWORK:-base}"
DRY_RUN=false
INPUT_FILE=""

# Usage function
usage() {
    cat << EOF
Usage: $0 <input-file> [options]

Batch tip multiple destinations from a file.

Options:
    --network <network>    Network to use (default: base)
    --dry-run              Validate without sending tips
    --help                 Show this help message

Input file formats:
    CSV:   destination,amount
    Text:  destination amount

Examples:
    $0 tips.csv
    $0 tips.txt --network base-sepolia
    $0 tips.csv --dry-run

EOF
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --network)
            NETWORK="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            usage
            ;;
        *)
            if [[ -z "$INPUT_FILE" ]]; then
                INPUT_FILE="$1"
            else
                echo -e "${RED}Error: Unknown argument: $1${NC}" >&2
                usage
            fi
            shift
            ;;
    esac
done

# Validate input file
if [[ -z "$INPUT_FILE" ]]; then
    echo -e "${RED}Error: Input file required${NC}" >&2
    usage
fi

if [[ ! -f "$INPUT_FILE" ]]; then
    echo -e "${RED}Error: File not found: $INPUT_FILE${NC}" >&2
    exit 1
fi

# Check if grove CLI is available
if ! command -v grove &> /dev/null; then
    echo -e "${RED}Error: grove CLI not found${NC}" >&2
    echo "Install with: curl -fsSL https://grove.city/install-cli.sh | bash" >&2
    exit 1
fi

# Arrays to track results
declare -a destinations=()
declare -a amounts=()
declare -a results=()

# Parse input file
echo -e "${BLUE}📋 Parsing input file: $INPUT_FILE${NC}"

line_num=0
while IFS= read -r line || [[ -n "$line" ]]; do
    line_num=$((line_num + 1))

    # Skip empty lines and comments
    [[ -z "$line" ]] && continue
    [[ "$line" =~ ^[[:space:]]*# ]] && continue

    # Parse CSV or space-separated
    if [[ "$line" =~ , ]]; then
        # CSV format
        IFS=',' read -r dest amt <<< "$line"
    else
        # Space-separated format
        read -r dest amt <<< "$line"
    fi

    # Trim whitespace
    dest=$(echo "$dest" | xargs)
    amt=$(echo "$amt" | xargs)

    # Validate
    if [[ -z "$dest" ]] || [[ -z "$amt" ]]; then
        echo -e "${YELLOW}⚠️  Line $line_num: Skipping invalid entry${NC}"
        continue
    fi

    destinations+=("$dest")
    amounts+=("$amt")
done < "$INPUT_FILE"

total_count=${#destinations[@]}

if [[ $total_count -eq 0 ]]; then
    echo -e "${RED}Error: No valid entries found in $INPUT_FILE${NC}" >&2
    exit 1
fi

echo -e "${GREEN}✓ Found $total_count destinations${NC}"
echo ""

# Validate all destinations first
echo -e "${BLUE}🔍 Validating destinations...${NC}"

validation_failed=0
for i in "${!destinations[@]}"; do
    dest="${destinations[$i]}"
    progress=$((i + 1))

    printf "  [%d/%d] Checking %s... " "$progress" "$total_count" "$dest"

    if grove check "$dest" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗ Not tippable${NC}"
        validation_failed=$((validation_failed + 1))
    fi
done

echo ""

if [[ $validation_failed -gt 0 ]]; then
    echo -e "${YELLOW}⚠️  Warning: $validation_failed destination(s) failed validation${NC}"
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Dry run - stop here
if [[ "$DRY_RUN" == "true" ]]; then
    echo -e "${YELLOW}🚫 Dry run mode - no tips will be sent${NC}"
    echo ""
    echo "Would tip:"
    for i in "${!destinations[@]}"; do
        printf "  %s → %s USDC\n" "${destinations[$i]}" "${amounts[$i]}"
    done
    exit 0
fi

# Check balance before starting
echo -e "${BLUE}💰 Checking balance...${NC}"
balance_json=$(grove balance --json)
total_balance=$(echo "$balance_json" | jq -r '.total_balance')

# Calculate total tip amount
total_amount=0
for amt in "${amounts[@]}"; do
    total_amount=$(echo "$total_amount + $amt" | bc -l)
done

echo "  Total balance: $total_balance USDC"
echo "  Total to tip:  $total_amount USDC"
echo ""

if (( $(echo "$total_balance < $total_amount" | bc -l) )); then
    echo -e "${RED}Error: Insufficient balance${NC}" >&2
    echo "Need at least $total_amount USDC, but only have $total_balance USDC" >&2
    exit 1
fi

# Confirm before proceeding
echo -e "${YELLOW}⚠️  About to send $total_count tips (total: $total_amount USDC)${NC}"
read -p "Continue? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""

# Send tips
echo -e "${BLUE}💸 Sending tips...${NC}"

success_count=0
failed_count=0

for i in "${!destinations[@]}"; do
    dest="${destinations[$i]}"
    amt="${amounts[$i]}"
    progress=$((i + 1))

    printf "  [%d/%d] Tipping %s → %s USDC... " "$progress" "$total_count" "$dest" "$amt"

    if grove tip "$dest" "$amt" --network "$NETWORK" --yes > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        results+=("✓ $dest")
        success_count=$((success_count + 1))
    else
        echo -e "${RED}✗ Failed${NC}"
        results+=("✗ $dest")
        failed_count=$((failed_count + 1))
    fi

    # Small delay to avoid rate limiting
    sleep 1
done

echo ""

# Summary report
echo -e "${BLUE}📊 Summary Report${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Total tips:     $total_count"
echo -e "Success:        ${GREEN}$success_count${NC}"
if [[ $failed_count -gt 0 ]]; then
    echo -e "Failed:         ${RED}$failed_count${NC}"
else
    echo "Failed:         0"
fi
echo "Network:        $NETWORK"
echo "Total amount:   $total_amount USDC"
echo ""

# Detailed results
if [[ $failed_count -gt 0 ]]; then
    echo "Results:"
    for result in "${results[@]}"; do
        if [[ "$result" =~ ^✓ ]]; then
            echo -e "  ${GREEN}$result${NC}"
        else
            echo -e "  ${RED}$result${NC}"
        fi
    done
    echo ""
fi

# Check final balance
echo -e "${BLUE}💰 Final balance:${NC}"
grove balance

exit 0
