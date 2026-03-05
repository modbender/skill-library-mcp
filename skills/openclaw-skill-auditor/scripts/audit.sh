#!/bin/bash
# Skill Auditor v2.0 - Security scanner for ClawHub skills
# Features: Pattern matching + Deobfuscation + LLM Analysis
# Usage: audit.sh <skill-name> OR audit.sh --local <path>

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'
BOLD='\033[1m'

# Temp files
FINDINGS_FILE=$(mktemp)
SUSPICIOUS_CODE=$(mktemp)
trap "rm -f $FINDINGS_FILE $SUSPICIOUS_CODE" EXIT

# === IoC Lists (UPDATE WHEN NEW THREATS FOUND) ===
MALICIOUS_IPS="91.92.242.30"
MALICIOUS_DOMAINS="glot.io webhook.site pastebin.com"
SOCIAL_ENGINEERING="OpenClawDriver ClawdBot.Driver Required.Driver install.driver download.driver"

# === L1: Pattern Matching ===
print_header() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════${NC}"
    echo -e "${CYAN}  SKILL AUDIT REPORT: ${BOLD}$1${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════${NC}"
    echo ""
}

scan_patterns() {
    local file=$1
    local filename=$(basename "$file")
    
    echo -e "${BOLD}[L1] Pattern Scan: $filename${NC}"
    
    local line_num=0
    while IFS= read -r line || [[ -n "$line" ]]; do
        ((line_num++))
        
        # HIGH RISK: base64 + execution
        if echo "$line" | grep -qiE 'base64.*\|.*bash|base64.*-d.*\||base64.*-D.*\|'; then
            echo -e "   ${RED}[LINE $line_num]${NC} Base64 encoded execution"
            echo "HIGH" >> "$FINDINGS_FILE"
            echo "$line" >> "$SUSPICIOUS_CODE"
        fi
        
        # HIGH RISK: curl/wget piped to bash
        if echo "$line" | grep -qiE 'curl.*\|.*bash|wget.*\|.*bash|curl.*\|.*sh[^a-z]|wget.*\|.*sh[^a-z]'; then
            echo -e "   ${RED}[LINE $line_num]${NC} Remote script execution (curl/wget|bash)"
            echo "HIGH" >> "$FINDINGS_FILE"
            echo "$line" >> "$SUSPICIOUS_CODE"
        fi
        
        # HIGH RISK: Known malicious IPs
        for ip in $MALICIOUS_IPS; do
            if echo "$line" | grep -q "$ip"; then
                echo -e "   ${RED}[LINE $line_num]${NC} Known C2 server: $ip"
                echo "HIGH" >> "$FINDINGS_FILE"
            fi
        done
        
        # HIGH RISK: eval/exec
        if echo "$line" | grep -qiE 'eval\s*\(|eval\s+\$|eval\s+["`]'; then
            echo -e "   ${RED}[LINE $line_num]${NC} Dynamic code execution (eval)"
            echo "HIGH" >> "$FINDINGS_FILE"
            echo "$line" >> "$SUSPICIOUS_CODE"
        fi
        
        # HIGH RISK: Credential keywords
        if echo "$line" | grep -qiE 'private.?key|mnemonic|seed.?phrase|wallet.*password'; then
            echo -e "   ${RED}[LINE $line_num]${NC} Credential theft keywords"
            echo "HIGH" >> "$FINDINGS_FILE"
        fi
        
        # MEDIUM RISK: Malicious domains
        for domain in $MALICIOUS_DOMAINS; do
            if echo "$line" | grep -qi "$domain"; then
                echo -e "   ${YELLOW}[LINE $line_num]${NC} Suspicious domain: $domain"
                echo "MEDIUM" >> "$FINDINGS_FILE"
            fi
        done
        
        # MEDIUM RISK: Accessing config dirs
        if echo "$line" | grep -qE '~/\.openclaw|~/\.clawdbot|\$HOME/\.openclaw|\$HOME/\.clawdbot|~/\.ssh|~/\.aws'; then
            echo -e "   ${YELLOW}[LINE $line_num]${NC} Accesses sensitive directory"
            echo "MEDIUM" >> "$FINDINGS_FILE"
        fi
        
        # MEDIUM RISK: Environment secrets
        if echo "$line" | grep -qiE '\$API_KEY|\$SECRET|\$PRIVATE|\$TOKEN|\$PASSWORD'; then
            echo -e "   ${YELLOW}[LINE $line_num]${NC} Reads secret environment variables"
            echo "MEDIUM" >> "$FINDINGS_FILE"
        fi
        
        # MEDIUM RISK: Social engineering
        for keyword in $SOCIAL_ENGINEERING; do
            kw=$(echo "$keyword" | tr '.' ' ')
            if echo "$line" | grep -qi "$kw"; then
                echo -e "   ${YELLOW}[LINE $line_num]${NC} Social engineering: $kw"
                echo "MEDIUM" >> "$FINDINGS_FILE"
            fi
        done
        
        # LOW RISK: Sudo
        if echo "$line" | grep -qiE '^sudo |sudo apt|sudo pip|sudo npm'; then
            echo -e "   ${GREEN}[LINE $line_num]${NC} Requires sudo"
            echo "LOW" >> "$FINDINGS_FILE"
        fi
        
        # Collect base64 strings for L2
        if echo "$line" | grep -qoE "'[A-Za-z0-9+/=]{20,}'|\"[A-Za-z0-9+/=]{20,}\""; then
            echo "$line" >> "$SUSPICIOUS_CODE"
        fi
        
    done < "$file"
}

# === L2: Deobfuscation ===
deobfuscate_scan() {
    echo ""
    echo -e "${BOLD}[L2] Deobfuscation Scan${NC}"
    
    if [ ! -s "$SUSPICIOUS_CODE" ]; then
        echo -e "   ${GREEN}No obfuscated code found${NC}"
        return
    fi
    
    # Extract and decode base64 strings
    while IFS= read -r line; do
        # Find base64-like strings (min 20 chars)
        b64_strings=$(echo "$line" | grep -oE '[A-Za-z0-9+/=]{20,}' | head -5)
        
        for b64 in $b64_strings; do
            # Try to decode
            decoded=$(echo "$b64" | base64 -d 2>/dev/null)
            if [ $? -eq 0 ] && [ -n "$decoded" ]; then
                # Check decoded content for threats
                if echo "$decoded" | grep -qiE 'curl|wget|bash|sh|eval|exec|/bin/|http://|https://'; then
                    echo -e "   ${RED}[DECODED]${NC} Hidden command found:"
                    echo -e "   ${MAGENTA}$decoded${NC}"
                    echo "HIGH" >> "$FINDINGS_FILE"
                fi
                
                # Check for IPs in decoded content
                for ip in $MALICIOUS_IPS; do
                    if echo "$decoded" | grep -q "$ip"; then
                        echo -e "   ${RED}[DECODED]${NC} Hidden C2 server: $ip"
                        echo "HIGH" >> "$FINDINGS_FILE"
                    fi
                done
            fi
        done
        
        # Check for hex encoded strings \x41\x42...
        if echo "$line" | grep -qE '\\x[0-9a-fA-F]{2}'; then
            hex_decoded=$(echo -e "$line" 2>/dev/null)
            if echo "$hex_decoded" | grep -qiE 'curl|wget|bash|eval'; then
                echo -e "   ${RED}[HEX DECODED]${NC} Hidden command in hex"
                echo "HIGH" >> "$FINDINGS_FILE"
            fi
        fi
        
    done < "$SUSPICIOUS_CODE"
}

# === L3: LLM Analysis ===
llm_analysis() {
    echo ""
    echo -e "${BOLD}[L3] LLM Intent Analysis${NC}"
    
    local skill_path=$1
    local skill_name=$(basename "$skill_path")
    
    # Check if we have suspicious code to analyze
    if [ ! -s "$SUSPICIOUS_CODE" ]; then
        echo -e "   ${GREEN}No suspicious code to analyze${NC}"
        return
    fi
    
    # Save suspicious code for OpenClaw agent to analyze
    local output_file="/tmp/skill-audit-${skill_name}-suspicious.txt"
    cp "$SUSPICIOUS_CODE" "$output_file"
    
    echo -e "   ${CYAN}Suspicious code saved to: $output_file${NC}"
    echo -e "   ${CYAN}Request OpenClaw agent to analyze with:${NC}"
    echo -e "   ${MAGENTA}分析这段可疑代码: cat $output_file${NC}"
    echo ""
    echo -e "   ${YELLOW}--- Suspicious Code Preview ---${NC}"
    head -20 "$SUSPICIOUS_CODE" | sed 's/^/   /'
    echo -e "   ${YELLOW}--------------------------------${NC}"
}

# === Verdict ===
print_verdict() {
    local high=$(grep "^HIGH$" "$FINDINGS_FILE" 2>/dev/null | wc -l | tr -d ' ')
    local medium=$(grep "^MEDIUM$" "$FINDINGS_FILE" 2>/dev/null | wc -l | tr -d ' ')
    local low=$(grep "^LOW$" "$FINDINGS_FILE" 2>/dev/null | wc -l | tr -d ' ')
    
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════${NC}"
    
    if [ "$high" -gt 0 ]; then
        echo -e "  VERDICT: ${RED}${BOLD}❌ DO NOT INSTALL${NC}"
        echo -e "  High: $high | Medium: $medium | Low: $low"
        echo -e "${CYAN}═══════════════════════════════════════════${NC}"
        return 2
    elif [ "$medium" -gt 0 ]; then
        echo -e "  VERDICT: ${YELLOW}${BOLD}⚠️  REVIEW REQUIRED${NC}"
        echo -e "  High: $high | Medium: $medium | Low: $low"
        echo -e "${CYAN}═══════════════════════════════════════════${NC}"
        return 1
    else
        echo -e "  VERDICT: ${GREEN}${BOLD}✅ APPEARS SAFE${NC}"
        echo -e "  High: $high | Medium: $medium | Low: $low"
        echo -e "${CYAN}═══════════════════════════════════════════${NC}"
        return 0
    fi
}

# === Main ===
run_audit() {
    local skill_path=$1
    local skill_name=$(basename "$skill_path")
    
    print_header "$skill_name"
    
    # L1: Pattern matching (use for loop to avoid subshell)
    while IFS= read -r -d '' file; do
        scan_patterns "$file"
    done < <(find "$skill_path" -type f \( -name "*.md" -o -name "*.sh" -o -name "*.py" -o -name "*.js" \) -print0 2>/dev/null)
    
    # L2: Deobfuscation
    deobfuscate_scan
    
    # L3: LLM Analysis
    llm_analysis "$skill_path"
    
    # Final verdict
    print_verdict
}

# Entry point
if [ "$1" == "--local" ] && [ -n "$2" ]; then
    SKILL_PATH="$2"
    
    if [ ! -d "$SKILL_PATH" ]; then
        echo "Error: Directory not found: $SKILL_PATH"
        exit 1
    fi
    
    run_audit "$SKILL_PATH"
    exit $?
    
elif [ -n "$1" ]; then
    SKILL_NAME="$1"
    TEMP_DIR=$(mktemp -d)
    trap "rm -rf $TEMP_DIR $FINDINGS_FILE $SUSPICIOUS_CODE" EXIT
    
    echo "Fetching skill: $SKILL_NAME ..."
    if ! clawhub inspect "$SKILL_NAME" --dir "$TEMP_DIR" > /dev/null 2>&1; then
        echo "Error: Could not fetch skill: $SKILL_NAME"
        exit 1
    fi
    
    SKILL_PATH="$TEMP_DIR/$SKILL_NAME"
    run_audit "$SKILL_PATH"
    exit $?
else
    echo "Skill Auditor v2.0 - Security scanner for ClawHub skills"
    echo ""
    echo "Features:"
    echo "  L1: Pattern matching (regex, IoC)"
    echo "  L2: Deobfuscation (base64, hex)"
    echo "  L3: LLM intent analysis (Gemini)"
    echo ""
    echo "Usage:"
    echo "  $0 <skill-name>        Fetch and scan from ClawHub"
    echo "  $0 --local <path>      Scan local skill directory"
    exit 1
fi
