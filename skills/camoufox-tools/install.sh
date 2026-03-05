#!/bin/bash
#
# install.sh - 安装 camoufox-tools 到 PATH
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$SCRIPT_DIR/bin"

# 检测 shell
detect_shell() {
    case "$(basename "$SHELL")" in
        zsh)
            echo "$HOME/.zshrc"
            ;;
        bash)
            echo "$HOME/.bashrc"
            ;;
        *)
            echo "$HOME/.profile"
            ;;
    esac
}

# 添加到 PATH
add_to_path() {
    local shell_rc=$(detect_shell)
    local export_line="export PATH=\"$BIN_DIR:\$PATH\""
    
    # 检查是否已存在
    if grep -q "$BIN_DIR" "$shell_rc" 2>/dev/null; then
        echo "✅ PATH 中已存在 camoufox-tools"
        return 0
    fi
    
    # 添加到 shell 配置文件
    echo "" >> "$shell_rc"
    echo "# camoufox-tools" >> "$shell_rc"
    echo "$export_line" >> "$shell_rc"
    
    echo "✅ 已添加到 PATH: $shell_rc"
    echo "请运行以下命令使更改生效:"
    echo "  source $shell_rc"
}

echo "========================================"
echo "  camoufox-tools 安装脚本"
echo "========================================"
echo ""
echo "工具目录: $BIN_DIR"
echo ""

# 显示可用工具
echo "可用工具:"
for tool in "$BIN_DIR"/fox-*; do
    if [[ -x "$tool" ]]; then
        echo "  - $(basename "$tool")"
    fi
done

echo ""

# 添加到 PATH
add_to_path

echo ""
echo "========================================"
echo "✅ 安装完成!"
echo "========================================"
echo ""
echo "使用方法:"
echo "  fox-open <url>       # 打开网页"
echo "  fox-scrape <url>     # 抓取内容"
echo "  fox-eval <js>        # 执行 JavaScript"
echo "  fox-close            # 关闭 browser"
echo "  fox-bilibili-stats <bv>  # B 站视频数据"
echo ""
echo "查看详细文档: cat $SCRIPT_DIR/SKILL.md"
