#!/usr/bin/env bash
# Skill Security Auditor - Analysis Engine
# Version: 1.0.0
# Author: akm626

set -euo pipefail

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATTERNS_FILE="${SCRIPT_DIR}/patterns/malicious-patterns.json"

# Usage
usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] <skill-file-or-slug>

Analyze a ClawHub skill for security issues.

OPTIONS:
    -f, --file FILE         Analyze local SKILL.md file
    -s, --slug SLUG        Fetch and analyze skill from ClawHub by slug
    -v, --verbose          Verbose output
    -h, --help             Show this help message

EXAMPLES:
    $(basename "$0") -f /path/to/SKILL.md
    $(basename "$0") -s bitcoin-tracker
    $(basename "$0") --slug solana-wallet-monitor

EOF
    exit 1
}

# Check dependencies
check_dependencies() {
    local missing=()
    for cmd in curl jq grep; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done
    
    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${RED}Error: Missing required dependencies: ${missing[*]}${NC}" >&2
        echo "Install with: brew install ${missing[*]} (macOS) or apt install ${missing[*]} (Linux)" >&2
        exit 1
    fi
}

# Fetch skill from ClawHub
fetch_skill() {
    local slug="$1"
    local temp_file="$2"
    
    echo -e "${BLUE}Fetching skill '${slug}' from ClawHub...${NC}"
    
    # Try to fetch from ClawHub API
    local url="https://clawhub.ai/api/skills/${slug}/latest"
    if ! curl -f -s "$url" -o "${temp_file}.json" 2>/dev/null; then
        echo -e "${RED}Error: Could not fetch skill '${slug}' from ClawHub${NC}" >&2
        echo "Make sure the skill exists: https://clawhub.ai/skills/${slug}" >&2
        return 1
    fi
    
    # Extract SKILL.md content (adjust based on actual API response)
    if ! jq -r '.content // .skillMd // .skill_md // empty' "${temp_file}.json" > "$temp_file" 2>/dev/null; then
        # If JSON parsing fails, the response might be plain text already
        mv "${temp_file}.json" "$temp_file" 2>/dev/null || true
    fi
    
    if [ ! -s "$temp_file" ]; then
        echo -e "${RED}Error: Could not extract SKILL.md content${NC}" >&2
        return 1
    fi
    
    rm -f "${temp_file}.json"
    echo -e "${GREEN}✓ Skill fetched successfully${NC}"
}

# Load patterns database
load_patterns() {
    if [ ! -f "$PATTERNS_FILE" ]; then
        echo -e "${RED}Error: Patterns file not found: ${PATTERNS_FILE}${NC}" >&2
        exit 1
    fi
    
    # Validate JSON
    if ! jq empty "$PATTERNS_FILE" 2>/dev/null; then
        echo -e "${RED}Error: Invalid JSON in patterns file${NC}" >&2
        exit 1
    fi
}

# Analyze skill content
analyze_skill() {
    local skill_file="$1"
    local risk_score=0
    local findings_critical=()
    local findings_high=()
    local findings_medium=()
    local findings_social=()
    local positives=()
    
    echo -e "${BLUE}Analyzing skill content...${NC}\n"
    
    # Read skill content
    local content
    content=$(<"$skill_file")
    
    # Check critical patterns
    while IFS= read -r pattern_json; do
        local id name pattern severity score_impact description
        id=$(echo "$pattern_json" | jq -r '.id')
        name=$(echo "$pattern_json" | jq -r '.name')
        pattern=$(echo "$pattern_json" | jq -r '.pattern')
        severity=$(echo "$pattern_json" | jq -r '.severity')
        score_impact=$(echo "$pattern_json" | jq -r '.score_impact')
        description=$(echo "$pattern_json" | jq -r '.description')
        
        if echo "$content" | grep -iE "$pattern" &>/dev/null; then
            risk_score=$((risk_score + score_impact))
            findings_critical+=("${id}: ${name} [+${score_impact} points]")
            findings_critical+=("  └─ ${description}")
        fi
    done < <(jq -c '.patterns.critical[]' "$PATTERNS_FILE")
    
    # Check high risk patterns
    while IFS= read -r pattern_json; do
        local id name pattern score_impact description
        id=$(echo "$pattern_json" | jq -r '.id')
        name=$(echo "$pattern_json" | jq -r '.name')
        pattern=$(echo "$pattern_json" | jq -r '.pattern')
        score_impact=$(echo "$pattern_json" | jq -r '.score_impact')
        description=$(echo "$pattern_json" | jq -r '.description')
        
        if echo "$content" | grep -iE "$pattern" &>/dev/null; then
            risk_score=$((risk_score + score_impact))
            findings_high+=("${id}: ${name} [+${score_impact} points]")
            findings_high+=("  └─ ${description}")
        fi
    done < <(jq -c '.patterns.high[]' "$PATTERNS_FILE")
    
    # Check medium risk patterns
    while IFS= read -r pattern_json; do
        local id name pattern score_impact description
        id=$(echo "$pattern_json" | jq -r '.id')
        name=$(echo "$pattern_json" | jq -r '.name')
        pattern=$(echo "$pattern_json" | jq -r '.pattern')
        score_impact=$(echo "$pattern_json" | jq -r '.score_impact')
        description=$(echo "$pattern_json" | jq -r '.description')
        
        if echo "$content" | grep -iE "$pattern" &>/dev/null; then
            risk_score=$((risk_score + score_impact))
            findings_medium+=("${id}: ${name} [+${score_impact} points]")
            findings_medium+=("  └─ ${description}")
        fi
    done < <(jq -c '.patterns.medium[]' "$PATTERNS_FILE")
    
    # Check social engineering
    while IFS= read -r pattern_json; do
        local id name pattern score_impact description
        id=$(echo "$pattern_json" | jq -r '.id')
        name=$(echo "$pattern_json" | jq -r '.name')
        pattern=$(echo "$pattern_json" | jq -r '.pattern')
        score_impact=$(echo "$pattern_json" | jq -r '.score_impact')
        description=$(echo "$pattern_json" | jq -r '.description')
        
        if echo "$content" | grep -iE "$pattern" &>/dev/null; then
            risk_score=$((risk_score + score_impact))
            findings_social+=("${id}: ${name} [+${score_impact} points]")
            findings_social+=("  └─ ${description}")
        fi
    done < <(jq -c '.patterns.social_engineering[]' "$PATTERNS_FILE")
    
    # Check for positive indicators
    while IFS= read -r binary; do
        if echo "$content" | grep -iwq "$binary"; then
            positives+=("Uses trusted binary: $binary")
        fi
    done < <(jq -r '.whitelisted_patterns.safe_binaries[]' "$PATTERNS_FILE")
    
    while IFS= read -r domain; do
        if echo "$content" | grep -iq "$domain"; then
            positives+=("References trusted domain: $domain")
        fi
    done < <(jq -r '.whitelisted_patterns.safe_domains[]' "$PATTERNS_FILE")
    
    # Cap risk score at 100
    if [ $risk_score -gt 100 ]; then
        risk_score=100
    fi
    
    # Generate report
    generate_report "$risk_score" findings_critical findings_high findings_medium findings_social positives
}

# Generate audit report
generate_report() {
    local risk_score=$1
    shift
    local -n critical=$1
    local -n high=$2
    local -n medium=$3
    local -n social=$4
    local -n positive=$5
    
    local risk_level icon recommendation
    if [ $risk_score -le 20 ]; then
        risk_level="SAFE"
        icon="✅"
        recommendation="Safe to install. No significant security concerns detected."
    elif [ $risk_score -le 40 ]; then
        risk_level="LOW RISK"
        icon="⚠️"
        recommendation="Proceed with caution. Minor security concerns detected."
    elif [ $risk_score -le 60 ]; then
        risk_level="MEDIUM RISK"
        icon="🟡"
        recommendation="Manual review recommended. Multiple red flags detected."
    elif [ $risk_score -le 80 ]; then
        risk_level="HIGH RISK"
        icon="🔴"
        recommendation="Expert review required. Serious security concerns detected. Do NOT install without thorough analysis."
    else
        risk_level="CRITICAL"
        icon="☠️"
        recommendation="DO NOT INSTALL. Malicious patterns detected matching known attack campaigns."
    fi
    
    echo "============================================"
    echo "         SECURITY AUDIT REPORT"
    echo "============================================"
    echo ""
    echo -e "Risk Score: ${risk_score}/100 - ${icon} ${risk_level}"
    echo ""
    echo "============================================"
    
    # Critical findings
    if [ ${#critical[@]} -gt 0 ]; then
        echo ""
        echo -e "${RED}☠️ CRITICAL FINDINGS:${NC}"
        for finding in "${critical[@]}"; do
            echo -e "${RED}  $finding${NC}"
        done
    fi
    
    # High risk findings
    if [ ${#high[@]} -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}🔴 HIGH RISK FINDINGS:${NC}"
        for finding in "${high[@]}"; do
            echo -e "${YELLOW}  $finding${NC}"
        done
    fi
    
    # Medium risk findings
    if [ ${#medium[@]} -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}🟡 MEDIUM RISK FINDINGS:${NC}"
        for finding in "${medium[@]}"; do
            echo -e "${YELLOW}  $finding${NC}"
        done
    fi
    
    # Social engineering
    if [ ${#social[@]} -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}⚠️ SOCIAL ENGINEERING INDICATORS:${NC}"
        for finding in "${social[@]}"; do
            echo -e "${YELLOW}  $finding${NC}"
        done
    fi
    
    # Positive indicators
    if [ ${#positive[@]} -gt 0 ]; then
        echo ""
        echo -e "${GREEN}✅ POSITIVE INDICATORS:${NC}"
        for item in "${positive[@]}"; do
            echo -e "${GREEN}  ✓ $item${NC}"
        done
    fi
    
    if [ ${#critical[@]} -eq 0 ] && [ ${#high[@]} -eq 0 ] && [ ${#medium[@]} -eq 0 ] && [ ${#social[@]} -eq 0 ]; then
        echo ""
        echo -e "${GREEN}No security concerns detected.${NC}"
    fi
    
    echo ""
    echo "============================================"
    echo "RECOMMENDATION:"
    echo "$recommendation"
    echo "============================================"
    echo ""
    echo "This analysis is based on pattern matching and heuristics."
    echo "Always combine with manual review and VirusTotal scanning."
    echo "Visit: https://clawhub.ai/skills/<skill-slug> for VirusTotal report."
    echo ""
}

# Main
main() {
    local mode=""
    local target=""
    local verbose=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -f|--file)
                mode="file"
                target="$2"
                shift 2
                ;;
            -s|--slug)
                mode="slug"
                target="$2"
                shift 2
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            -h|--help)
                usage
                ;;
            *)
                if [ -z "$mode" ] && [ -f "$1" ]; then
                    mode="file"
                    target="$1"
                elif [ -z "$mode" ]; then
                    mode="slug"
                    target="$1"
                fi
                shift
                ;;
        esac
    done
    
    if [ -z "$target" ]; then
        echo -e "${RED}Error: No skill file or slug provided${NC}" >&2
        usage
    fi
    
    # Check dependencies
    check_dependencies
    
    # Load patterns
    load_patterns
    
    # Determine analysis target
    local analysis_file
    if [ "$mode" = "file" ]; then
        if [ ! -f "$target" ]; then
            echo -e "${RED}Error: File not found: ${target}${NC}" >&2
            exit 1
        fi
        analysis_file="$target"
        echo -e "${BLUE}Analyzing local file: ${target}${NC}\n"
    else
        # Fetch from ClawHub
        analysis_file=$(mktemp)
        trap "rm -f '$analysis_file'" EXIT
        if ! fetch_skill "$target" "$analysis_file"; then
            exit 1
        fi
        echo ""
    fi
    
    # Run analysis
    analyze_skill "$analysis_file"
}

main "$@"
