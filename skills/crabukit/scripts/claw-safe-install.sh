#!/bin/bash
# 🔒 claw-safe-install - Safe skill installer with security scanning
# 
# SECURITY NOTE: This is a DEFENSIVE security tool. It scans skills BEFORE
# installation to detect malware. It does NOT modify your system except:
# 1. Downloads skills to a temp directory for scanning
# 2. Optionally adds an alias to your shell if you manually source this file
#
# This script wraps clawdhub install with automatic security scanning
# using both Clawdex (database) and Crabukit (behavior analysis).
#
# Usage:
#   source ~/.claw-safe-install.sh
#   claw-safe-install <skill-name>
#
# Or add to ~/.zshrc:
#   source ~/.claw-safe-install.sh

claw-safe-install() {
    local skill="$1"
    local fail_on="${2:-high}"  # Default: fail on high severity
    local temp_dir="/tmp/claw-safe-install.$$"
    local workdir="/tmp/claw-safe-workdir.$$"
    
    # Colors for output (disable for compatibility)
    local RED=''
    local GREEN=''
    local YELLOW=''
    local BLUE=''
    local NC=''
    
    # Check arguments
    if [ -z "$skill" ]; then
        echo "Error: No skill name provided"
        echo "Usage: claw-safe-install <skill-name> [fail-on-level]"
        echo "Example: claw-safe-install youtube-summarize"
        echo "Example: claw-safe-install youtube-summarize critical"
        return 1
    fi
    
    # Check if crabukit is available
    if ! command -v crabukit &> /dev/null; then
        echo "⚠️  crabukit not found in PATH"
        echo "Please install crabukit first:"
        echo "  pip install crabukit"
        echo "Or from source:"
        echo "  git clone https://github.com/tnbradley/crabukit.git"
        echo "  cd crabukit && pip install -e ."
        return 1
    fi
    
    # Create temp workdir
    mkdir -p "$workdir/skills"
    
    echo "🔒 Claw Safe Install: $skill"
    echo ""
    
    # Step 1: Install to temp location
    echo "⬇️  Step 1: Installing to temp location for scanning..."
    if ! CLAWDHUB_WORKDIR="$workdir" clawdhub install "$skill" 2>/dev/null; then
        echo "❌ Failed to install skill: $skill"
        rm -rf "$workdir"
        return 1
    fi
    echo "✓ Installed to temp: $workdir/skills/$skill"
    echo ""
    
    # Step 2: Security scan
    echo "🔍 Step 2: Running security scan..."
    echo ""
    echo "   Layer 1: Checking Clawdex database (known malicious skills)..."
    echo "   Layer 2: Running Crabukit behavior analysis (zero-day detection)..."
    echo ""
    
    if crabukit scan "$workdir/skills/$skill" --fail-on="$fail_on"; then
        echo ""
        echo "✅ Security check passed!"
        echo ""
    else
        echo ""
        echo "❌ Security check FAILED"
        echo "⚠️  Installation blocked due to security issues"
        echo ""
        echo "Cleaning up temp files..."
        rm -rf "$workdir"
        echo ""
        echo "To install anyway (not recommended):"
        echo "  clawdhub install $skill"
        return 1
    fi
    
    # Step 3: Install to real location
    echo "📦 Step 3: Installing skill to workspace..."
    if clawdhub install "$skill"; then
        echo ""
        echo "🎉 Successfully installed $skill!"
        rm -rf "$workdir"
        return 0
    else
        echo ""
        echo "❌ Installation failed"
        rm -rf "$workdir"
        return 1
    fi
}

# Alias for convenience
alias csi='claw-safe-install'

# Help function
claw-safe-install-help() {
    echo "🔒 claw-safe-install - Safe skill installer"
    echo ""
    echo "Usage:"
    echo "  claw-safe-install <skill-name> [fail-on-level]"
    echo ""
    echo "Parameters:"
    echo "  skill-name     Name of the skill to install"
    echo "  fail-on-level  Severity to fail on (critical|high|medium|low|info)"
    echo "                 Default: high"
    echo ""
    echo "Examples:"
    echo "  claw-safe-install youtube-summarize"
    echo "  claw-safe-install youtube-summarize critical"
    echo "  claw-safe-install some-skill medium"
    echo ""
    echo "Alias: csi"
    echo "  csi youtube-summarize"
    echo ""
    echo "Security:"
    echo "  • Downloads skill to temp directory"
    echo "  • Runs Clawdex database check (if installed)"
    echo "  • Runs Crabukit behavior analysis"
    echo "  • Only installs if all checks pass"
}

echo "🔒 claw-safe-install loaded. Type 'claw-safe-install-help' for usage."
