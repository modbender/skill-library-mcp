#!/bin/bash
# bomb-dog-sniff - OpenClaw Skill Wrapper
# Version: 1.2.0 - Hardened Edition
# Usage: openclaw skill bomb-dog-sniff <command> [args]

set -o pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Check if node is available
command -v node >/dev/null 2>&1 || {
    echo "Error: Node.js is required but not installed." >&2
    exit 1
}

show_help() {
    cat << EOF
Bomb-Dog-Sniff v1.2.0 - Security scanner for OpenClaw skills

Commands:
  scan <path>           Scan a skill directory for malicious patterns
  safe-install <source> Download, scan, and safely install a skill
  audit <name>          Audit an already-installed skill
  batch <file>          Scan multiple skills from a list file
  version               Show version information

Options for safe-install:
  --threshold N         Set risk threshold (default: 39)
  --dry-run             Scan only, don't install
  --verbose             Show detailed findings

Examples:
  openclaw skill bomb-dog-sniff scan ./suspicious-skill
  openclaw skill bomb-dog-sniff safe-install cool-skill
  openclaw skill bomb-dog-sniff audit bird
  openclaw skill bomb-dog-sniff batch skills-to-check.txt

Risk Thresholds:
  0-19   SAFE         ✅ Auto-install allowed
  20-39  LOW          ⚠️  Manual review recommended
  40-69  SUSPICIOUS   🚫 Blocked by default
  70-100 MALICIOUS    ☠️  Never install

Exit Codes:
  0      Success / Safe (below threshold)
  1      Error / Invalid arguments
  2      Risky detected (above threshold)

EOF
}

show_version() {
    echo "Bomb-Dog-Sniff v1.2.0"
    echo "Security scanner for OpenClaw skills"
    echo ""
    echo "Node version: $(node --version 2>/dev/null || echo 'unknown')"
}

# Parse command
cmd="${1:-}"
shift || true

case "$cmd" in
    scan)
        node "$SKILL_DIR/scan.js" "$@"
        exit $?
        ;;
    safe-install|install-safe)
        node "$SKILL_DIR/safe-download.js" --install "$@"
        exit $?
        ;;
    audit)
        SKILL_NAME="${1:-}"
        if [ -z "$SKILL_NAME" ]; then
            echo "Error: No skill name specified" >&2
            echo "Usage: audit <skill-name>" >&2
            exit 1
        fi
        shift
        SKILLS_DIR="${OPENCLAW_SKILLS_DIR:-$HOME/.openclaw/workspace/skills}"
        
        if [ ! -d "$SKILLS_DIR/$SKILL_NAME" ]; then
            echo "Error: Skill not found: $SKILLS_DIR/$SKILL_NAME" >&2
            exit 1
        fi
        
        node "$SKILL_DIR/scan.js" "$SKILLS_DIR/$SKILL_NAME" "$@"
        exit $?
        ;;
    batch)
        LIST_FILE="${1:-}"
        if [ -z "$LIST_FILE" ]; then
            echo "Error: No list file specified" >&2
            echo "Usage: batch <file-with-skill-list>" >&2
            exit 1
        fi
        
        if [ ! -f "$LIST_FILE" ]; then
            echo "Error: List file not found: $LIST_FILE" >&2
            exit 1
        fi
        
        SKILLS_DIR="${OPENCLAW_SKILLS_DIR:-$HOME/.openclaw/workspace/skills}"
        OVERALL_RISKY=0
        
        echo "🔍 Batch scanning skills from: $LIST_FILE"
        echo ""
        
        while IFS= read -r skill || [ -n "$skill" ]; do
            # Skip empty lines and comments
            [ -z "$skill" ] && continue
            [[ "$skill" =~ ^[[:space:]]*# ]] && continue
            
            # Trim whitespace
            skill="$(echo "$skill" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
            [ -z "$skill" ] && continue
            
            echo "═══════════════════════════════════════════════════"
            echo "📦 Scanning: $skill"
            echo "═══════════════════════════════════════════════════"
            
            # Determine path
            if [ -d "$skill" ]; then
                # Local path
                SKILL_PATH="$skill"
            elif [ -d "$SKILLS_DIR/$skill" ]; then
                # Installed skill
                SKILL_PATH="$SKILLS_DIR/$skill"
            else
                echo "⚠️  Warning: Skill not found: $skill"
                echo ""
                continue
            fi
            
            # Run scan and capture results
            SCAN_OUTPUT=$(node "$SKILL_DIR/scan.js" --json "$SKILL_PATH" 2>&1)
            SCAN_EXIT=$?
            
            # Parse JSON output
            RISK_SCORE=$(echo "$SCAN_OUTPUT" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{const j=JSON.parse(d);console.log(j.riskScore||0)}catch{console.log(0)}})" 2>/dev/null || echo "0")
            RISK_LEVEL=$(echo "$SCAN_OUTPUT" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{const j=JSON.parse(d);console.log(j.riskLevel||'UNKNOWN')}catch{console.log('UNKNOWN')}})" 2>/dev/null || echo "UNKNOWN")
            FINDINGS=$(echo "$SCAN_OUTPUT" | node -e "let d='';process.stdin.on('data',c=>d+=c);process.stdin.on('end',()=>{try{const j=JSON.parse(d);console.log(j.stats?.totalFindings||0)}catch{console.log(0)}})" 2>/dev/null || echo "0")
            
            # Display summary
            echo "   Risk Score: ${RISK_SCORE}/100"
            echo "   Risk Level: ${RISK_LEVEL}"
            echo "   Findings: ${FINDINGS}"
            
            # Risk indicator
            if [ "$RISK_SCORE" -ge 70 ]; then
                echo "   ☠️  MALICIOUS - Do not use!"
                OVERALL_RISKY=1
            elif [ "$RISK_SCORE" -ge 40 ]; then
                echo "   🚫 SUSPICIOUS - Review required"
                OVERALL_RISKY=1
            elif [ "$RISK_SCORE" -ge 20 ]; then
                echo "   ⚠️  LOW RISK - Review recommended"
            else
                echo "   ✅ SAFE"
            fi
            
            echo ""
            
            # Track overall risk
            if [ "$SCAN_EXIT" -eq 2 ]; then
                OVERALL_RISKY=1
            fi
        done < "$LIST_FILE"
        
        echo "═══════════════════════════════════════════════════"
        echo "Batch scan complete"
        echo "═══════════════════════════════════════════════════"
        
        if [ "$OVERALL_RISKY" -eq 1 ]; then
            exit 2
        else
            exit 0
        fi
        ;;
    version|--version|-v)
        show_version
        exit 0
        ;;
    help|--help|-h|'')
        show_help
        exit 0
        ;;
    *)
        echo "Error: Unknown command: $cmd" >&2
        show_help >&2
        exit 1
        ;;
esac
