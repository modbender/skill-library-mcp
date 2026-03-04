#!/bin/bash
# Skill Security Auditor
# Usage: ./audit.sh /path/to/skill

set -e

SKILL_PATH="${1:-.}"
SKILL_NAME=$(basename "$SKILL_PATH")

# Colors
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "========================================"
echo "🔒 SKILL SECURITY AUDIT: $SKILL_NAME"
echo "========================================"
echo "Path: $SKILL_PATH"
echo ""

CRITICAL=0
HIGH=0
MEDIUM=0
FINDINGS=""

# Function to check patterns
check_pattern() {
    local name="$1"
    local level="$2"
    local pattern="$3"
    
    matches=$(grep -rlE "$pattern" "$SKILL_PATH" 2>/dev/null || true)
    
    if [ -n "$matches" ]; then
        count=$(echo "$matches" | wc -l)
        
        case "$level" in
            CRITICAL) 
                echo -e "${RED}🚨 CRITICAL: $name ($count files)${NC}"
                CRITICAL=$((CRITICAL + 1))
                ;;
            HIGH)
                echo -e "${RED}🔴 HIGH: $name ($count files)${NC}"
                HIGH=$((HIGH + 1))
                ;;
            MEDIUM)
                echo -e "${YELLOW}🟡 MEDIUM: $name ($count files)${NC}"
                MEDIUM=$((MEDIUM + 1))
                ;;
        esac
        
        # Show first 3 matches
        echo "$matches" | head -3 | while read f; do
            line=$(grep -nE "$pattern" "$f" 2>/dev/null | head -1)
            echo "   └─ $f: $line"
        done
        echo ""
        
        FINDINGS="${FINDINGS}${level}:${name}\n"
    fi
}

echo "📋 Scanning for security issues..."
echo ""

# CRITICAL checks
check_pattern "Dynamic Code Execution (exec/eval)" "CRITICAL" "(exec\(|eval\(|compile\(|Function\()[^)]*['\"]"
check_pattern "Import Hijacking" "CRITICAL" "__import__\([^)]*input\(|__import__\([^)]*\+"

# HIGH checks  
check_pattern "Network Exfiltration" "HIGH" "(requests\.post|requests\.put|urllib\.request\.urlopen|http\.client\.HTTPConnection|fetch\([^)]+{)"
check_pattern "Credential File Access" "HIGH" "(open\([^)]*\.(ssh|aws|gnupg|config)|read.*id_rsa|read.*credentials)"
check_pattern "Password Store Access" "HIGH" "subprocess\.(run|call|Popen).*pass\s+(show|insert)"
check_pattern "Keyring/Keychain Access" "HIGH" "(keyring\.get|SecItemCopyMatching|security find-generic-password)"
check_pattern "Shell Command Injection" "HIGH" "(os\.system\(|subprocess\.[^(]+\([^)]*shell=True.*\+)"

# MEDIUM checks
check_pattern "Base64 Encoded Content" "MEDIUM" "(base64\.b64decode|atob\(|Buffer\.from\([^)]+base64)"
check_pattern "Environment Variable Access" "MEDIUM" "(os\.environ\[|process\.env\[|os\.getenv\()"
check_pattern "Generic Network Calls" "MEDIUM" "(requests\.|urllib\.|http\.client\.|socket\.connect)"
check_pattern "File System Traversal" "MEDIUM" "\.\./\.\./|os\.path\.join\([^)]*\.\."

# Summary
echo "========================================"
echo "📊 AUDIT SUMMARY"
echo "========================================"

if [ $CRITICAL -gt 0 ]; then
    echo -e "${RED}🚨 CRITICAL: $CRITICAL findings${NC}"
fi
if [ $HIGH -gt 0 ]; then
    echo -e "${RED}🔴 HIGH: $HIGH findings${NC}"
fi
if [ $MEDIUM -gt 0 ]; then
    echo -e "${YELLOW}🟡 MEDIUM: $MEDIUM findings${NC}"
fi

if [ $CRITICAL -eq 0 ] && [ $HIGH -eq 0 ] && [ $MEDIUM -eq 0 ]; then
    echo -e "${GREEN}✅ CLEAN - No security issues found${NC}"
    exit 0
fi

echo ""

# Recommendation
if [ $CRITICAL -gt 0 ]; then
    echo -e "${RED}⛔ RECOMMENDATION: DO NOT USE THIS SKILL${NC}"
    echo "   Critical security issues detected. Report to owner."
    
    # Add to blocklist
    BLOCKLIST_DIR=$(dirname "$0")
    echo "$SKILL_NAME:$(date -I):CRITICAL findings" >> "$BLOCKLIST_DIR/blocklist.txt" 2>/dev/null || true
    
    exit 2
elif [ $HIGH -gt 0 ]; then
    echo -e "${YELLOW}⚠️  RECOMMENDATION: Manual review required${NC}"
    echo "   Verify these patterns are legitimate before use."
    exit 1
else
    echo -e "${GREEN}ℹ️  RECOMMENDATION: Proceed with awareness${NC}"
    echo "   Medium findings noted. Safe if from trusted source."
    exit 0
fi
