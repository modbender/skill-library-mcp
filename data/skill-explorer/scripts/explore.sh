#!/bin/bash
# Skill Explorer Helper Script
# Assists with systematic skill exploration workflow

set -e

SKILL_NAME=$1
ACTION=$2
WORK_DIR="/tmp/skill-explore-$(date +%s)"

show_help() {
    echo "Skill Explorer - Helper Script"
    echo ""
    echo "Usage:"
    echo "  ./explore.sh <skill-name> inspect    - Inspect skill details"
    echo "  ./explore.sh <skill-name> download  - Download for security review"
    echo "  ./explore.sh <skill-name> analyze   - Run security analysis"
    echo ""
    echo "Examples:"
    echo "  ./explore.sh tweet-writer inspect"
    echo "  ./explore.sh marketing-mode analyze"
}

inspect_skill() {
    echo "🔍 Inspecting skill: $SKILL_NAME"
    echo "===================="
    clawhub inspect "$SKILL_NAME" --json 2>/dev/null | jq -r '{
        name: .skill.displayName,
        summary: .skill.summary,
        stars: .skill.stats.stars,
        downloads: .skill.stats.downloads,
        installs: .skill.stats.installsAllTime,
        active: .skill.stats.installsCurrent,
        owner: .owner.handle,
        updated: .skill.updatedAt
    }' 2>/dev/null || echo "Error: Could not inspect skill"
}

download_skill() {
    echo "📥 Downloading skill: $SKILL_NAME"
    echo "===================="
    mkdir -p "$WORK_DIR"
    cd "$WORK_DIR"
    clawhub install "$SKILL_NAME" --force 2>&1 || {
        echo "⚠️  May need --force for suspicious skills"
        return 1
    }
    echo ""
    echo "✅ Downloaded to: $WORK_DIR/skills/$SKILL_NAME"
    echo ""
    echo "File structure:"
    find "$WORK_DIR/skills/$SKILL_NAME" -type f | head -20
}

analyze_skill() {
    SKILL_DIR="/tmp/skill-explore-*/skills/$SKILL_NAME"
    
    # Find the actual directory
    for dir in /tmp/skill-explore-*/skills/$SKILL_NAME; do
        if [ -d "$dir" ]; then
            SKILL_DIR="$dir"
            break
        fi
    done
    
    if [ ! -d "$SKILL_DIR" ]; then
        echo "❌ Skill not found. Download it first with: ./explore.sh $SKILL_NAME download"
        exit 1
    fi
    
    echo "🔐 Security Analysis: $SKILL_NAME"
    echo "===================="
    echo ""
    
    cd "$SKILL_DIR"
    
    # File structure
    echo "📁 File Structure:"
    find . -type f | sort
    echo ""
    
    # Check for executable scripts
    echo "📜 Scripts found:"
    find . -name "*.js" -o -name "*.py" -o -name "*.sh" 2>/dev/null | head -10
    echo ""
    
    # Security patterns check
    echo "🔍 Security Check:"
    
    # Suspicious patterns
    SUSPICIOUS=$(grep -r -E "(eval\(|exec\(|Function\(|atob\(|btoa\()" . 2>/dev/null | wc -l)
    echo "  Suspicious patterns (eval/exec/Function): $SUSPICIOUS"
    
    CRYPTO=$(grep -r -E "(crypto|encrypt|decrypt|base64)" . 2>/dev/null | wc -l)
    echo "  Crypto-related strings: $CRYPTO"
    
    NETWORK=$(grep -r -E "https?://" . 2>/dev/null | wc -l)
    echo "  HTTP(S) URLs found: $NETWORK"
    
    echo ""
    
    # Risk assessment
    if [ "$SUSPICIOUS" -eq 0 ] && [ "$CRYPTO" -eq 0 ]; then
        echo "✅ Risk Level: 🟢 LOW - No suspicious code patterns"
    elif [ "$SUSPICIOUS" -lt 5 ]; then
        echo "⚠️  Risk Level: 🟡 MEDIUM - Some patterns found, manual review needed"
    else
        echo "❌ Risk Level: 🔴 HIGH - Multiple suspicious patterns detected"
    fi
    
    echo ""
    echo "📊 Full analysis complete. Review files in: $SKILL_DIR"
}

case "$ACTION" in
    inspect)
        inspect_skill
        ;;
    download)
        download_skill
        ;;
    analyze)
        analyze_skill
        ;;
    *)
        show_help
        exit 1
        ;;
esac
