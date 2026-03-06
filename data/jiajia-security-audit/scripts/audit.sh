#!/usr/bin/env bash
# Skill Security Audit Script
# 扫描 skill 目录中的安全风险

set -euo pipefail

# Colors
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
GREEN='\033[0;32m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Severity counters
CRITICAL=0
HIGH=0
MEDIUM=0
LOW=0

# Output format
JSON_OUTPUT=false
FINDINGS=()

usage() {
    echo "Usage: $0 <skill-path> [--json] [--include-docs]"
    echo ""
    echo "Arguments:"
    echo "  skill-path      Path to skill directory or skills/ folder"
    echo "  --json          Output in JSON format"
    echo "  --include-docs  Include documentation files (references/, *.md) in scan"
    exit 1
}

if [[ $# -lt 1 ]]; then
    usage
fi

TARGET_PATH="$1"
shift

INCLUDE_DOCS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --include-docs)
            INCLUDE_DOCS=true
            shift
            ;;
        *)
            usage
            ;;
    esac
done

if [[ ! -d "$TARGET_PATH" ]]; then
    echo "Error: $TARGET_PATH is not a directory"
    exit 1
fi

# Check if it's a single skill or skills directory
if [[ -f "$TARGET_PATH/SKILL.md" ]]; then
    SKILLS=("$TARGET_PATH")
else
    SKILLS=()
    for dir in "$TARGET_PATH"/*/; do
        if [[ -f "${dir}SKILL.md" ]]; then
            SKILLS+=("${dir%/}")
        fi
    done
fi

if [[ ${#SKILLS[@]} -eq 0 ]]; then
    echo "Error: No skills found in $TARGET_PATH"
    exit 1
fi

# Check if file is documentation (should be skipped unless --include-docs)
is_documentation_file() {
    local file="$1"
    local skill_path="$2"
    
    # Skip if --include-docs is set
    $INCLUDE_DOCS && return 1
    
    # Check if file is in references/ directory
    if [[ "$file" == *"/references/"* ]]; then
        return 0
    fi
    
    # Check if file is a markdown file (except SKILL.md which might have real issues)
    local filename=$(basename "$file")
    if [[ "$filename" == *.md && "$filename" != "SKILL.md" ]]; then
        return 0
    fi
    
    return 1
}

# Check if line is inside a code block or example
is_in_code_block() {
    local file="$1"
    local line_num="$2"
    
    # For markdown files, check if line is in a code block
    if [[ "$file" == *.md ]]; then
        local in_code=false
        local current_line=0
        while IFS= read -r line || [[ -n "$line" ]]; do
            ((current_line++))
            if [[ "$line" == '```'* ]]; then
                if $in_code; then
                    in_code=false
                else
                    in_code=true
                fi
            fi
            if [[ $current_line -eq $line_num ]]; then
                $in_code && return 0
                return 1
            fi
        done < "$file"
    fi
    
    # For shell/python, check if line is a comment or in a heredoc example
    local line_content
    line_content=$(sed -n "${line_num}p" "$file" 2>/dev/null || echo "")
    
    # Check if it's a comment line
    if [[ "$line_content" =~ ^[[:space:]]*# ]]; then
        # But not shebang
        [[ "$line_content" =~ ^#! ]] && return 1
        return 0
    fi
    
    # Check if it looks like an example (contains "Example:", "e.g.", etc.)
    if [[ "$line_content" =~ (Example|e\.g\.|pattern|regex|检测|示例) ]]; then
        return 0
    fi
    
    return 1
}

add_finding() {
    local severity="$1"
    local category="$2"
    local file="$3"
    local line="$4"
    local message="$5"
    
    case $severity in
        CRITICAL) ((CRITICAL++)) || true ;;
        HIGH) ((HIGH++)) || true ;;
        MEDIUM) ((MEDIUM++)) || true ;;
        LOW) ((LOW++)) || true ;;
    esac
    
    if $JSON_OUTPUT; then
        FINDINGS+=("{\"severity\":\"$severity\",\"category\":\"$category\",\"file\":\"$file\",\"line\":$line,\"message\":\"$message\"}")
    else
        local color
        case $severity in
            CRITICAL) color=$RED ;;
            HIGH) color=$YELLOW ;;
            MEDIUM) color=$BLUE ;;
            LOW) color=$GREEN ;;
        esac
        echo -e "  ${color}[$severity]${NC} $file:$line - $message"
    fi
}

check_file_for_ignore() {
    local file="$1"
    local line_num="$2"
    local skill_path="$3"
    
    # Check inline ignore
    local prev_line=$((line_num - 1))
    if [[ $prev_line -gt 0 ]]; then
        local prev_content
        prev_content=$(sed -n "${prev_line}p" "$file" 2>/dev/null || echo "")
        if [[ "$prev_content" == *"security-audit: ignore-next-line"* ]]; then
            return 0
        fi
    fi
    
    # Check .security-audit-ignore file
    local ignore_file="$skill_path/.security-audit-ignore"
    if [[ -f "$ignore_file" ]]; then
        local rel_path="${file#$skill_path/}"
        while IFS= read -r pattern || [[ -n "$pattern" ]]; do
            [[ -z "$pattern" || "$pattern" == \#* ]] && continue
            if [[ "$rel_path" == $pattern ]]; then
                return 0
            fi
        done < "$ignore_file"
    fi
    
    return 1
}

# Combined check: should this finding be skipped?
should_skip_finding() {
    local file="$1"
    local line_num="$2"
    local skill_path="$3"
    
    # Skip if explicitly ignored
    check_file_for_ignore "$file" "$line_num" "$skill_path" && return 0
    
    # Skip if in documentation file
    is_documentation_file "$file" "$skill_path" && return 0
    
    # Skip if in code block or example
    is_in_code_block "$file" "$line_num" && return 0
    
    return 1
}

scan_credentials() {
    local file="$1"
    local skill_path="$2"
    
    # OpenAI API key
    grep -nE 'sk-[a-zA-Z0-9]{20,}' "$file" 2>/dev/null | while IFS=: read -r line_num content; do
        should_skip_finding "$file" "$line_num" "$skill_path" && continue
        add_finding "CRITICAL" "Credential" "$file" "$line_num" "OpenAI API key pattern detected"
    done || true
    
    # Anthropic API key
    grep -nE 'sk-ant-[a-zA-Z0-9-]{20,}' "$file" 2>/dev/null | while IFS=: read -r line_num content; do
        should_skip_finding "$file" "$line_num" "$skill_path" && continue
        add_finding "CRITICAL" "Credential" "$file" "$line_num" "Anthropic API key pattern detected"
    done || true
    
    # AWS Access Key
    grep -nE 'AKIA[0-9A-Z]{16}' "$file" 2>/dev/null | while IFS=: read -r line_num content; do
        should_skip_finding "$file" "$line_num" "$skill_path" && continue
        add_finding "CRITICAL" "Credential" "$file" "$line_num" "AWS Access Key detected"
    done || true
    
    # GitHub Token
    grep -nE 'gh[pousr]_[A-Za-z0-9_]{36,}' "$file" 2>/dev/null | while IFS=: read -r line_num content; do
        should_skip_finding "$file" "$line_num" "$skill_path" && continue
        add_finding "CRITICAL" "Credential" "$file" "$line_num" "GitHub token detected"
    done || true
    
    # Google API Key
    grep -nE 'AIza[0-9A-Za-z_-]{35}' "$file" 2>/dev/null | while IFS=: read -r line_num content; do
        should_skip_finding "$file" "$line_num" "$skill_path" && continue
        add_finding "CRITICAL" "Credential" "$file" "$line_num" "Google API key detected"
    done || true
    
    # Slack Token
    grep -nE 'xox[baprs]-[0-9a-zA-Z-]+' "$file" 2>/dev/null | while IFS=: read -r line_num content; do
        should_skip_finding "$file" "$line_num" "$skill_path" && continue
        add_finding "CRITICAL" "Credential" "$file" "$line_num" "Slack token detected"
    done || true
    
    # Private keys
    grep -nE '-----BEGIN (RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----' "$file" 2>/dev/null | while IFS=: read -r line_num content; do
        should_skip_finding "$file" "$line_num" "$skill_path" && continue
        add_finding "CRITICAL" "Credential" "$file" "$line_num" "Private key detected"
    done || true
    
    # Generic password/secret patterns (only in non-config files)
    if [[ "$file" != *.json && "$file" != *.yaml && "$file" != *.yml ]]; then
        grep -niE '(password|passwd|secret|api_key|apikey|auth_token)\s*[=:]\s*['"'"'"][^'"'"'"]{8,}['"'"'"]' "$file" 2>/dev/null | while IFS=: read -r line_num content; do
            should_skip_finding "$file" "$line_num" "$skill_path" && continue
            # Skip if it looks like a placeholder
            if [[ "$content" =~ (your[-_]|xxx|example|placeholder|\<|\{) ]]; then
                continue
            fi
            add_finding "HIGH" "Credential" "$file" "$line_num" "Possible hardcoded credential"
        done || true
    fi
}

scan_dangerous_commands() {
    local file="$1"
    local skill_path="$2"
    
    # Only scan executable files
    [[ "$file" != *.sh && "$file" != *.py && "$file" != *.js && "$file" != *.ts && "$file" != "Makefile" && "$file" != "Dockerfile" ]] && return
    
    # rm -rf with dangerous paths
    grep -nE 'rm\s+(-[rf]+\s+)*(\/|\~|\$HOME|\$\{HOME\}|\.\.\/)' "$file" 2>/dev/null | while IFS=: read -r line_num content; do
        should_skip_finding "$file" "$line_num" "$skill_path" && continue
        add_finding "HIGH" "DangerousCommand" "$file" "$line_num" "Dangerous rm command detected"
    done || true
    
    # sudo commands
    grep -nE '\bsudo\s+' "$file" 2>/dev/null | while IFS=: read -r line_num content; do
        should_skip_finding "$file" "$line_num" "$skill_path" && continue
        add_finding "MEDIUM" "DangerousCommand" "$file" "$line_num" "sudo command (privilege escalation)"
    done || true
    
    # eval/exec (but not in grep patterns)
    grep -nE '\b(eval|exec)\s*\(' "$file" 2>/dev/null | while IFS=: read -r line_num content; do
        should_skip_finding "$file" "$line_num" "$skill_path" && continue
        # Skip if it's in a grep/regex pattern
        [[ "$content" =~ grep|regex|pattern|\\b ]] && continue
        add_finding "HIGH" "DangerousCommand" "$file" "$line_num" "Dynamic code execution (eval/exec)"
    done || true
    
    # curl | bash pattern
    grep -nE '(curl|wget)\s+.*\|\s*(ba)?sh' "$file" 2>/dev/null | while IFS=: read -r line_num content; do
        should_skip_finding "$file" "$line_num" "$skill_path" && continue
        add_finding "HIGH" "DangerousCommand" "$file" "$line_num" "Remote code execution (curl|bash)"
    done || true
    
    # chmod 777
    grep -nE 'chmod\s+777' "$file" 2>/dev/null | while IFS=: read -r line_num content; do
        should_skip_finding "$file" "$line_num" "$skill_path" && continue
        add_finding "MEDIUM" "DangerousCommand" "$file" "$line_num" "Overly permissive chmod 777"
    done || true
}

scan_network_exfiltration() {
    local file="$1"
    local skill_path="$2"
    
    # Only scan executable files
    [[ "$file" != *.sh && "$file" != *.py && "$file" != *.js && "$file" != *.ts ]] && return
    
    # HTTP requests to unknown domains (exclude common safe domains)
    grep -nE '(curl|wget|requests\.(get|post|put)|fetch|axios|http\.request)\s*[\(\s]+['"'"'"]https?://' "$file" 2>/dev/null | \
    grep -vE '(api\.openai\.com|api\.anthropic\.com|api\.github\.com|registry\.npmjs\.org|pypi\.org|amazonaws\.com|googleapis\.com)' | \
    while IFS=: read -r line_num content; do
        should_skip_finding "$file" "$line_num" "$skill_path" && continue
        add_finding "MEDIUM" "NetworkExfiltration" "$file" "$line_num" "HTTP request to external domain"
    done || true
    
    # WebSocket connections
    grep -nE 'WebSocket\s*\(['"'"'"]wss?://' "$file" 2>/dev/null | while IFS=: read -r line_num content; do
        should_skip_finding "$file" "$line_num" "$skill_path" && continue
        add_finding "MEDIUM" "NetworkExfiltration" "$file" "$line_num" "WebSocket connection"
    done || true
}

scan_file_access() {
    local file="$1"
    local skill_path="$2"
    
    # Only scan executable files
    [[ "$file" != *.sh && "$file" != *.py && "$file" != *.js && "$file" != *.ts ]] && return
    
    # Sensitive directory access
    grep -nE '(~|/home/[^/]+|/root)/\.(ssh|gnupg|aws|config|netrc|npmrc|pypirc)' "$file" 2>/dev/null | while IFS=: read -r line_num content; do
        should_skip_finding "$file" "$line_num" "$skill_path" && continue
        add_finding "HIGH" "FileAccess" "$file" "$line_num" "Access to sensitive directory"
    done || true
    
    # System path access
    grep -nE '(/etc/(passwd|shadow|sudoers|ssh))' "$file" 2>/dev/null | while IFS=: read -r line_num content; do
        should_skip_finding "$file" "$line_num" "$skill_path" && continue
        add_finding "HIGH" "FileAccess" "$file" "$line_num" "Access to system files"
    done || true
}

scan_dependencies() {
    local skill_path="$1"
    
    # Check requirements.txt for unpinned versions
    if [[ -f "$skill_path/requirements.txt" ]]; then
        grep -nE '^[a-zA-Z0-9_-]+$' "$skill_path/requirements.txt" 2>/dev/null | while IFS=: read -r line_num content; do
            add_finding "LOW" "Dependency" "$skill_path/requirements.txt" "$line_num" "Unpinned Python dependency: $content"
        done || true
    fi
    
    # Check package.json for loose versions
    if [[ -f "$skill_path/package.json" ]]; then
        grep -nE '"[^"]+"\s*:\s*"(\*|latest)"' "$skill_path/package.json" 2>/dev/null | while IFS=: read -r line_num content; do
            add_finding "LOW" "Dependency" "$skill_path/package.json" "$line_num" "Unpinned Node dependency"
        done || true
    fi
}

# Main scanning logic
for skill in "${SKILLS[@]}"; do
    skill_name=$(basename "$skill")
    
    if ! $JSON_OUTPUT; then
        echo ""
        echo "=== Scanning: $skill_name ==="
    fi
    
    # Find all text files to scan (exclude documentation by default)
    if $INCLUDE_DOCS; then
        files=$(find "$skill" -type f \( -name "*.sh" -o -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.md" -o -name "*.txt" -o -name "*.env*" -o -name "*.config" -o -name "Makefile" -o -name "Dockerfile" \) 2>/dev/null || true)
    else
        # Exclude references/ directory and most markdown files
        files=$(find "$skill" -type f \( -name "*.sh" -o -name "*.py" -o -name "*.js" -o -name "*.ts" -o -name "*.json" -o -name "*.yaml" -o -name "*.yml" -o -name "*.env*" -o -name "*.config" -o -name "Makefile" -o -name "Dockerfile" -o -name "SKILL.md" \) ! -path "*/references/*" 2>/dev/null || true)
    fi
    
    file_count=0
    for file in $files; do
        ((file_count++)) || true
        scan_credentials "$file" "$skill"
        scan_dangerous_commands "$file" "$skill"
        scan_network_exfiltration "$file" "$skill"
        scan_file_access "$file" "$skill"
    done
    
    scan_dependencies "$skill"
    
    if ! $JSON_OUTPUT; then
        echo "  Scanned $file_count files"
    fi
done

# Output summary
if $JSON_OUTPUT; then
    echo "{"
    echo "  \"summary\": {"
    echo "    \"critical\": $CRITICAL,"
    echo "    \"high\": $HIGH,"
    echo "    \"medium\": $MEDIUM,"
    echo "    \"low\": $LOW"
    echo "  },"
    echo "  \"findings\": ["
    first=true
    for finding in "${FINDINGS[@]}"; do
        if $first; then
            echo "    $finding"
            first=false
        else
            echo "    ,$finding"
        fi
    done
    echo "  ]"
    echo "}"
else
    echo ""
    echo "=== Summary ==="
    if [[ $CRITICAL -gt 0 ]]; then
        echo -e "${RED}Critical: $CRITICAL${NC}"
    fi
    if [[ $HIGH -gt 0 ]]; then
        echo -e "${YELLOW}High: $HIGH${NC}"
    fi
    if [[ $MEDIUM -gt 0 ]]; then
        echo -e "${BLUE}Medium: $MEDIUM${NC}"
    fi
    if [[ $LOW -gt 0 ]]; then
        echo -e "${GREEN}Low: $LOW${NC}"
    fi
    
    total=$((CRITICAL + HIGH + MEDIUM + LOW))
    if [[ $total -eq 0 ]]; then
        echo -e "${GREEN}✅ No security issues found${NC}"
    else
        echo ""
        echo "Total: $total issues"
        if [[ $CRITICAL -gt 0 ]]; then
            echo -e "${RED}⚠️  Critical issues require immediate attention!${NC}"
        fi
    fi
    
    if ! $INCLUDE_DOCS; then
        echo -e "${GRAY}(Documentation files skipped. Use --include-docs to scan them too)${NC}"
    fi
fi
