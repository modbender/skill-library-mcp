#!/bin/bash
# fund-advisor CLI 脚本
# 调用 tools 中的 fund-tools 命令

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TOOLS_DIR="$PROJECT_ROOT/tools"

# 检查 venv 是否有效（目录存在且可执行文件正常）
check_venv() {
    # 检查关键文件是否存在
    [ -x "$TOOLS_DIR/venv/bin/pip" ] || return 1
    [ -x "$TOOLS_DIR/venv/bin/fund-tools" ] || return 1

    # 检查 pip 是否可执行（检测 shebang 路径是否有效）
    "$TOOLS_DIR/venv/bin/pip" --version >/dev/null 2>&1 || return 1

    return 0
}

# 如果 venv 不存在或已损坏，重新创建
if ! check_venv; then
    echo "Creating/repairing virtual environment..."
    rm -rf "$TOOLS_DIR/venv"
    python3 -m venv "$TOOLS_DIR/venv"
    echo "Installing fund-tools..."
    "$TOOLS_DIR/venv/bin/pip" install -e "$TOOLS_DIR" -q
fi

# Run the installed command
"$TOOLS_DIR/venv/bin/fund-tools" "$@"