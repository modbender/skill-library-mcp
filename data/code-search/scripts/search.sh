#!/usr/bin/env bash
# Code Search Skill — 统一入口脚本
# 用法: bash search.sh <command> [options]
# 子命令: grep, glob, tree, check

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 默认忽略目录
IGNORE_DIRS=".git,.svn,.hg,node_modules,bower_components,__pycache__,.pytest_cache,.mypy_cache,.venv,venv,env,vendor,dist,build,target,out,.DS_Store,Thumbs.db"

# ============================================================
# 依赖检查
# ============================================================
cmd_check() {
    local status="OK"
    local count=0
    local total=3

    echo "[DEPENDENCY CHECK]"

    if command -v rg &>/dev/null; then
        echo "rg (ripgrep):    ✅ installed ($(rg --version | head -1 | awk '{print $2}'))"
        count=$((count + 1))
    else
        echo "rg (ripgrep):    ❌ not found"
        echo "  Install: curl -LO https://github.com/BurntSushi/ripgrep/releases/download/14.1.1/ripgrep-14.1.1-x86_64-unknown-linux-musl.tar.gz"
        status="PARTIAL"
    fi

    if command -v fd &>/dev/null; then
        echo "fd (fd-find):    ✅ installed ($(fd --version | awk '{print $2}'))"
        count=$((count + 1))
    else
        echo "fd (fd-find):    ❌ not found"
        echo "  Install: curl -LO https://github.com/sharkdp/fd/releases/download/v10.2.0/fd-v10.2.0-x86_64-unknown-linux-musl.tar.gz"
        status="PARTIAL"
    fi

    if command -v tree &>/dev/null; then
        echo "tree:            ✅ installed ($(tree --version | head -1 | awk '{print $2}'))"
        count=$((count + 1))
    else
        echo "tree:            ❌ not found"
        echo "  Install: yum install -y tree  (or: apt install tree)"
        status="PARTIAL"
    fi

    if [ "$count" -eq 0 ]; then
        status="MISSING"
    elif [ "$count" -eq "$total" ]; then
        status="OK"
    fi

    echo "---"
    echo "[STATUS: $status] $count/$total dependencies available"
}

# ============================================================
# grep — 内容搜索
# ============================================================
cmd_grep() {
    if ! command -v rg &>/dev/null; then
        echo "[ERROR] ripgrep (rg) is not installed. Run: bash $SCRIPT_DIR/search.sh check"
        exit 1
    fi

    local pattern=""
    local search_path="."
    local literal=false
    local max_results=100
    local context_lines=0
    local types=()

    # 解析参数
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --path)    search_path="$2"; shift 2 ;;
            --type)    types+=("$2"); shift 2 ;;
            --literal) literal=true; shift ;;
            --max)     max_results="$2"; shift 2 ;;
            --context) context_lines="$2"; shift 2 ;;
            -*)        echo "[ERROR] Unknown option: $1"; exit 1 ;;
            *)
                if [ -z "$pattern" ]; then
                    pattern="$1"
                else
                    echo "[ERROR] Unexpected argument: $1"; exit 1
                fi
                shift ;;
        esac
    done

    if [ -z "$pattern" ]; then
        echo "[ERROR] Pattern is required. Usage: search.sh grep <pattern> [--path dir] [--type ext] [--literal] [--max n]"
        exit 1
    fi

    if [ ! -d "$search_path" ]; then
        echo "[ERROR] Directory not found: $search_path"
        exit 1
    fi

    # 构建 rg 命令
    local rg_args=("--json" "--max-count" "$max_results" "--sort" "modified")

    if [ "$literal" = true ]; then
        rg_args+=("--fixed-strings")
    fi

    if [ "$context_lines" -gt 0 ]; then
        rg_args+=("--context" "$context_lines")
    fi

    for t in "${types[@]+"${types[@]}"}"; do
        rg_args+=("--type" "$t")
    done

    # 添加忽略目录
    IFS=',' read -ra IGNORE_ARR <<< "$IGNORE_DIRS"
    for d in "${IGNORE_ARR[@]}"; do
        rg_args+=("--glob" "!$d")
    done

    rg_args+=("$pattern" "$search_path")

    # 执行搜索，解析 JSON 输出
    local raw_output
    raw_output=$(timeout 10 rg "${rg_args[@]}" 2>/dev/null || true)

    if [ -z "$raw_output" ]; then
        echo "[SEARCH RESULTS: grep]"
        echo "Pattern: \"$pattern\""
        echo "Directory: $(cd "$search_path" && pwd)"
        echo "No matches found."
        echo "[END RESULTS]"
        return
    fi

    # 用 awk 解析 rg --json 输出
    local parsed
    parsed=$(echo "$raw_output" | awk '
    BEGIN {
        file_count = 0
        match_count = 0
        current_file = ""
    }
    {
        # 简单 JSON 解析 — 提取 type, path, line_number, lines.text
        if (match($0, /"type":"([^"]+)"/, t)) {
            type = t[1]
        }
        if (type == "match") {
            match_count++
            if (match($0, /"path":\{"text":"([^"]+)"/, p)) {
                file = p[1]
            }
            if (match($0, /"line_number":([0-9]+)/, ln)) {
                line_num = ln[1]
            }
            if (match($0, /"lines":\{"text":"([^"]*)"/, lt)) {
                line_text = lt[1]
                # 去掉尾部 \n
                gsub(/\\n$/, "", line_text)
                gsub(/\\t/, "\t", line_text)
            }
            if (file != current_file) {
                if (current_file != "") print ""
                current_file = file
                file_count++
                print "FILE: " file
            }
            printf "  %s: %s\n", line_num, line_text
        }
    }
    END {
        print "\n__META__:" file_count ":" match_count
    }
    ')

    # 提取元数据
    local meta_line
    meta_line=$(echo "$parsed" | grep "^__META__:" | head -1)
    local file_count match_count
    file_count=$(echo "$meta_line" | cut -d: -f2)
    match_count=$(echo "$meta_line" | cut -d: -f3)

    # 输出结构化结果
    echo "[SEARCH RESULTS: grep]"
    echo "Pattern: \"$pattern\""
    echo "Directory: $(cd "$search_path" && pwd)"
    echo "Files matched: $file_count"
    echo "Total matches: $match_count"
    echo "---"
    echo "$parsed" | grep -v "^__META__:"
    echo "---"

    if [ "$match_count" -ge "$max_results" ]; then
        echo "[TRUNCATED: showing $max_results matches, there may be more. Use --max to increase limit]"
    fi

    echo "[END RESULTS]"
}

# ============================================================
# glob — 文件名搜索
# ============================================================
cmd_glob() {
    if ! command -v fd &>/dev/null; then
        echo "[ERROR] fd is not installed. Run: bash $SCRIPT_DIR/search.sh check"
        exit 1
    fi

    local pattern=""
    local search_path="."
    local max_results=200
    local types=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --path) search_path="$2"; shift 2 ;;
            --type) types+=("$2"); shift 2 ;;
            --max)  max_results="$2"; shift 2 ;;
            -*)     echo "[ERROR] Unknown option: $1"; exit 1 ;;
            *)
                if [ -z "$pattern" ]; then
                    pattern="$1"
                else
                    echo "[ERROR] Unexpected argument: $1"; exit 1
                fi
                shift ;;
        esac
    done

    if [ -z "$pattern" ]; then
        echo "[ERROR] Pattern is required. Usage: search.sh glob <pattern> [--path dir] [--type ext] [--max n]"
        exit 1
    fi

    if [ ! -d "$search_path" ]; then
        echo "[ERROR] Directory not found: $search_path"
        exit 1
    fi

    # 构建 fd 命令 — 使用 -g 启用 glob 模式
    local fd_args=("-g" "--max-results" "$max_results")

    # 添加忽略目录
    IFS=',' read -ra IGNORE_ARR <<< "$IGNORE_DIRS"
    for d in "${IGNORE_ARR[@]}"; do
        fd_args+=("--exclude" "$d")
    done

    # --type f=files, d=directories
    for t in "${types[@]+"${types[@]}"}"; do
        fd_args+=("--type" "$t")
    done

    fd_args+=("$pattern" "$search_path")

    local raw_output
    raw_output=$(timeout 10 fd "${fd_args[@]}" 2>/dev/null | sort || true)

    local file_count=0
    if [ -n "$raw_output" ]; then
        file_count=$(echo "$raw_output" | wc -l)
    fi

    echo "[SEARCH RESULTS: glob]"
    echo "Pattern: \"$pattern\""
    echo "Directory: $(cd "$search_path" && pwd)"
    echo "Files found: $file_count"
    echo "---"

    if [ -z "$raw_output" ]; then
        echo "No matches found."
    else
        echo "$raw_output"
    fi

    echo "---"

    if [ "$file_count" -ge "$max_results" ]; then
        echo "[TRUNCATED: showing $max_results files, there may be more. Use --max to increase limit]"
    fi

    echo "[END RESULTS]"
}

# ============================================================
# tree — 目录结构
# ============================================================
cmd_tree() {
    if ! command -v tree &>/dev/null; then
        echo "[ERROR] tree is not installed. Run: yum install -y tree (or: apt install tree)"
        exit 1
    fi

    local search_path="."
    local depth=3
    local show_size=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --path)  search_path="$2"; shift 2 ;;
            --depth) depth="$2"; shift 2 ;;
            --size)  show_size=true; shift ;;
            -*)      echo "[ERROR] Unknown option: $1"; exit 1 ;;
            *)       echo "[ERROR] Unexpected argument: $1"; exit 1 ;;
        esac
    done

    if [ ! -d "$search_path" ]; then
        echo "[ERROR] Directory not found: $search_path"
        exit 1
    fi

    local tree_args=("-L" "$depth" "-I" ".git|node_modules|__pycache__|.venv|venv|env|vendor|dist|build|target|out" "--charset" "utf-8")

    if [ "$show_size" = true ]; then
        tree_args+=("-s")
    fi

    tree_args+=("$search_path")

    local raw_output
    raw_output=$(timeout 10 tree "${tree_args[@]}" 2>/dev/null || true)

    echo "[DIRECTORY TREE]"
    echo "Path: $(cd "$search_path" && pwd)"
    echo "Depth: $depth"
    echo "---"
    echo "$raw_output"
    echo "---"
    echo "[END TREE]"
}

# ============================================================
# 主入口
# ============================================================
if [ $# -lt 1 ]; then
    echo "Usage: bash search.sh <command> [options]"
    echo ""
    echo "Commands:"
    echo "  grep <pattern>   Search file contents (uses ripgrep)"
    echo "  glob <pattern>   Search file names (uses fd)"
    echo "  tree             Show directory structure"
    echo "  check            Check dependencies"
    exit 1
fi

command="$1"
shift

case "$command" in
    grep)  cmd_grep "$@" ;;
    glob)  cmd_glob "$@" ;;
    tree)  cmd_tree "$@" ;;
    check) cmd_check ;;
    *)     echo "[ERROR] Unknown command: $command. Use: grep, glob, tree, check"; exit 1 ;;
esac
