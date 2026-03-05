#!/usr/bin/env bash
# fetch-docs.sh - 抓取项目文档喂给 LLM
# Usage: ./fetch-docs.sh <project|url> [version]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY="$SCRIPT_DIR/docs-registry.json"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/docs-feeder"
MAX_SIZE=500000  # 500KB warning threshold

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[docs]${NC} $*" >&2; }
warn() { echo -e "${YELLOW}[warn]${NC} $*" >&2; }
error() { echo -e "${RED}[error]${NC} $*" >&2; exit 1; }
success() { echo -e "${GREEN}[ok]${NC} $*" >&2; }

usage() {
    cat <<EOF
Usage: $(basename "$0") <project|url> [options]

Examples:
  $(basename "$0") nextjs              # 按项目名抓取
  $(basename "$0") https://hono.dev    # 按 URL 抓取
  $(basename "$0") react --raw         # 只输出内容，不加元信息
  $(basename "$0") --list              # 列出所有支持的项目

Options:
  --raw         只输出文档内容
  --save        保存到文件而不是输出
  --list        列出支持的项目
  --refresh     忽略缓存重新抓取
  --help        显示帮助
EOF
}

# Check dependencies
check_deps() {
    for cmd in curl jq; do
        command -v "$cmd" &>/dev/null || error "需要安装 $cmd"
    done
}

# Get project config from registry
get_config() {
    local project="$1"
    jq -r --arg p "$project" '.[$p] // empty' "$REGISTRY"
}

# List all projects
list_projects() {
    echo "支持的项目："
    jq -r 'keys[]' "$REGISTRY" | sort | column
}

# Try to fetch LLM-friendly docs
fetch_llms_txt() {
    local base_url="$1"
    local llms_path="${2:-/llms-full.txt}"
    
    # Try llms-full.txt first
    local url="${base_url}${llms_path}"
    log "尝试 $url"
    
    local content
    if content=$(curl -sfL --max-time 30 "$url" 2>/dev/null); then
        if [[ -n "$content" && ${#content} -gt 100 ]]; then
            echo "$content"
            return 0
        fi
    fi
    
    # Try llms.txt
    if [[ "$llms_path" == "/llms-full.txt" ]]; then
        url="${base_url}/llms.txt"
        log "尝试 $url"
        if content=$(curl -sfL --max-time 30 "$url" 2>/dev/null); then
            if [[ -n "$content" && ${#content} -gt 100 ]]; then
                echo "$content"
                return 0
            fi
        fi
    fi
    
    return 1
}

# Fetch GitHub README as fallback
fetch_github_readme() {
    local repo="$1"
    local url="https://raw.githubusercontent.com/${repo}/main/README.md"
    
    log "Fallback: GitHub README ($repo)"
    
    local content
    if content=$(curl -sfL --max-time 30 "$url" 2>/dev/null); then
        echo "$content"
        return 0
    fi
    
    # Try master branch
    url="https://raw.githubusercontent.com/${repo}/master/README.md"
    if content=$(curl -sfL --max-time 30 "$url" 2>/dev/null); then
        echo "$content"
        return 0
    fi
    
    return 1
}

# Fetch local docs
fetch_local() {
    local path="$1"
    
    if [[ -d "$path" ]]; then
        log "读取本地文档: $path"
        find "$path" -name "*.md" -type f -exec cat {} \; 2>/dev/null
        return 0
    elif [[ -f "$path" ]]; then
        cat "$path"
        return 0
    fi
    
    return 1
}

# Main fetch logic
fetch_docs() {
    local input="$1"
    local raw="${2:-false}"
    local refresh="${3:-false}"
    
    local content=""
    local source=""
    local project_name=""
    
    # Check if input is URL
    if [[ "$input" =~ ^https?:// ]]; then
        project_name=$(echo "$input" | sed -E 's|https?://([^/]+).*|\1|' | sed 's/^www\.//' | sed 's/\..*$//')
        
        if content=$(fetch_llms_txt "$input"); then
            source="$input/llms*.txt"
        else
            error "无法从 $input 抓取文档"
        fi
    else
        # Lookup in registry
        project_name="$input"
        local config
        config=$(get_config "$input")
        
        if [[ -z "$config" ]]; then
            # Try common patterns
            warn "项目 '$input' 不在 registry 中，尝试常见模式..."
            
            local base_url="https://docs.${input}.com"
            if content=$(fetch_llms_txt "$base_url"); then
                source="$base_url (guessed)"
            else
                base_url="https://${input}.dev"
                if content=$(fetch_llms_txt "$base_url"); then
                    source="$base_url (guessed)"
                else
                    error "找不到 '$input' 的文档。使用 --list 查看支持的项目。"
                fi
            fi
        else
            local base_url llms_path github_repo local_path
            base_url=$(echo "$config" | jq -r '.url // empty')
            llms_path=$(echo "$config" | jq -r '.llms // "/llms-full.txt"')
            github_repo=$(echo "$config" | jq -r '.github // empty')
            local_path=$(echo "$config" | jq -r '.local // empty')
            
            # Try local first
            if [[ -n "$local_path" ]] && content=$(fetch_local "$local_path"); then
                source="local: $local_path"
            # Then try llms.txt
            elif [[ -n "$base_url" ]] && content=$(fetch_llms_txt "$base_url" "$llms_path"); then
                source="$base_url$llms_path"
            # Finally try GitHub
            elif [[ -n "$github_repo" ]] && content=$(fetch_github_readme "$github_repo"); then
                source="github: $github_repo"
            else
                error "无法抓取 '$input' 的文档"
            fi
        fi
    fi
    
    # Check size
    local size=${#content}
    if [[ $size -gt $MAX_SIZE ]]; then
        warn "文档较大 ($(numfmt --to=iec $size))，可能需要裁剪"
    fi
    
    # Output
    if [[ "$raw" == "true" ]]; then
        echo "$content"
    else
        cat <<EOF
# Documentation: $project_name

**Source:** $source
**Size:** $(numfmt --to=iec $size)
**Fetched:** $(date -Iseconds)

---

$content
EOF
    fi
    
    success "已抓取 $project_name 文档 ($(numfmt --to=iec $size))"
}

# Parse arguments
main() {
    check_deps
    
    local input=""
    local raw=false
    local save=false
    local refresh=false
    
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --help|-h)
                usage
                exit 0
                ;;
            --list|-l)
                list_projects
                exit 0
                ;;
            --raw)
                raw=true
                shift
                ;;
            --save)
                save=true
                shift
                ;;
            --refresh)
                refresh=true
                shift
                ;;
            -*)
                error "未知选项: $1"
                ;;
            *)
                input="$1"
                shift
                ;;
        esac
    done
    
    [[ -z "$input" ]] && { usage; exit 1; }
    
    if [[ "$save" == "true" ]]; then
        local outfile="/tmp/docs-${input//[^a-zA-Z0-9]/-}.md"
        fetch_docs "$input" "$raw" "$refresh" > "$outfile"
        success "已保存到 $outfile"
    else
        fetch_docs "$input" "$raw" "$refresh"
    fi
}

main "$@"
