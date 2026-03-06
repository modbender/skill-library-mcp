#!/bin/bash
#
# Camoufox + Agent-Browser 一键安装脚本
# 
# 这个脚本自动完成：
# 1. 安装 uv
# 2. 用 uv 安装 camoufox
# 3. 下载 camoufox 浏览器二进制
# 4. 安装 agent-browser npm 包
# 5. 修改 agent-browser 源码（自动检测 firefox/camoufox）
# 6. 重新编译 Rust CLI
# 7. 替换系统版本
#

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 获取操作系统类型
get_os() {
    case "$(uname -s)" in
        Darwin*) echo "macos" ;;
        Linux*)  echo "linux" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *)       echo "unknown" ;;
    esac
}

OS=$(get_os)
log_info "检测到操作系统: $OS"

# ==================== 步骤 1: 安装 uv ====================
log_info "步骤 1/7: 检查并安装 uv..."

if command_exists uv; then
    log_success "uv 已安装: $(uv --version)"
else
    log_info "正在安装 uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # 添加 uv 到 PATH
    if [ -f "$HOME/.local/bin/env" ]; then
        . "$HOME/.local/bin/env"
    elif [ -d "$HOME/.cargo/bin" ]; then
        export PATH="$HOME/.cargo/bin:$PATH"
    fi
    
    if command_exists uv; then
        log_success "uv 安装成功: $(uv --version)"
    else
        log_error "uv 安装失败，请手动安装"
        exit 1
    fi
fi

# ==================== 步骤 2: 安装 camoufox Python 包 ====================
log_info "步骤 2/7: 安装 camoufox Python 包..."

if uv pip show camoufox >/dev/null 2>&1 || python3 -c "import camoufox" 2>/dev/null; then
    log_success "camoufox Python 包已安装"
else
    log_info "使用 uv 安装 camoufox..."
    uv pip install camoufox --system || pip3 install camoufox
    
    if python3 -c "import camoufox" 2>/dev/null; then
        log_success "camoufox Python 包安装成功"
    else
        log_warn "uv 安装失败，尝试 pip3..."
        pip3 install camoufox
    fi
fi

# ==================== 步骤 3: 下载 camoufox 浏览器二进制 ====================
log_info "步骤 3/7: 下载 camoufox 浏览器二进制..."

CAMOUFOX_PATH=""
if [ "$OS" = "macos" ]; then
    CAMOUFOX_PATH="$HOME/Library/Caches/camoufox/Camoufox.app/Contents/MacOS/camoufox"
elif [ "$OS" = "linux" ]; then
    CAMOUFOX_PATH="$HOME/.cache/camoufox/camoufox"
else
    CAMOUFOX_PATH="$HOME/.local/bin/camoufox"
fi

if [ -f "$CAMOUFOX_PATH" ]; then
    log_success "camoufox 浏览器已存在: $CAMOUFOX_PATH"
else
    log_info "正在下载 camoufox 浏览器..."
    python3 << 'PYTHON_EOF'
try:
    from camoufox.sync_api import Camoufox
    print("正在初始化 camoufox (这会下载浏览器)...")
    browser = Camoufox()
    print("下载完成!")
except Exception as e:
    print(f"警告: 自动下载失败: {e}")
    print("请手动运行: python3 -c 'from camoufox.sync_api import Camoufox; Camoufox()'")
PYTHON_EOF
fi

# 再次检查
if [ -f "$CAMOUFOX_PATH" ]; then
    log_success "camoufox 浏览器就绪: $CAMOUFOX_PATH"
else
    log_warn "camoufox 浏览器未找到，可能需要手动下载"
    log_info "尝试替代路径..."
    
    # 尝试其他可能的路径
    for path in "$HOME/.local/bin/camoufox" "/usr/local/bin/camoufox" "$(which camoufox 2>/dev/null)"; do
        if [ -f "$path" ]; then
            CAMOUFOX_PATH="$path"
            log_success "找到 camoufox: $CAMOUFOX_PATH"
            break
        fi
    done
fi

# ==================== 步骤 4: 安装 agent-browser ====================
log_info "步骤 4/7: 安装 agent-browser..."

# 找到 npm 全局安装路径
NPM_GLOBAL=$(npm root -g)
AGENT_BROWSER_PATH="$NPM_GLOBAL/agent-browser"

if [ -d "$AGENT_BROWSER_PATH" ]; then
    log_success "agent-browser 已安装: $AGENT_BROWSER_PATH"
    # 备份原版本
    BACKUP_PATH="${AGENT_BROWSER_PATH}.backup.$(date +%Y%m%d_%H%M%S)"
    log_info "备份原版本到: $BACKUP_PATH"
    cp -r "$AGENT_BROWSER_PATH" "$BACKUP_PATH"
else
    log_info "安装 agent-browser..."
    npm install -g agent-browser
    
    if [ -d "$AGENT_BROWSER_PATH" ]; then
        log_success "agent-browser 安装成功"
    else
        log_error "agent-browser 安装失败"
        exit 1
    fi
fi

# ==================== 步骤 5: 修改 agent-browser 源码 ====================
log_info "步骤 5/7: 修改 agent-browser 源码以支持 camoufox/firefox..."

BROWSER_TS_PATH="$AGENT_BROWSER_PATH/src/browser.ts"
BROWSER_JS_PATH="$AGENT_BROWSER_PATH/dist/browser.js"

# 检查是否存在 src/browser.ts
if [ ! -f "$BROWSER_TS_PATH" ]; then
    log_warn "未找到 src/browser.ts，尝试查找源码..."
    
    # 尝试克隆源码
    TEMP_DIR=$(mktemp -d)
    log_info "临时克隆 agent-browser 源码到: $TEMP_DIR"
    
    git clone --depth 1 https://github.com/browser-use/agent-browser.git "$TEMP_DIR/agent-browser" 2>/dev/null || {
        log_warn "无法克隆仓库，尝试直接修改已编译的 JS..."
    }
    
    if [ -d "$TEMP_DIR/agent-browser/src" ]; then
        BROWSER_TS_PATH="$TEMP_DIR/agent-browser/src/browser.ts"
        cd "$TEMP_DIR/agent-browser"
    fi
fi

# 修改 browser.ts
if [ -f "$BROWSER_TS_PATH" ]; then
    log_info "修改 browser.ts..."
    
    # 创建修改后的 getBrowserType 函数
    cat > /tmp/browser_type_patch.txt << 'PATCH_EOF'
  private getBrowserType(executablePath: string): 'chromium' | 'firefox' {
    const lowerPath = executablePath.toLowerCase();
    if (lowerPath.includes('firefox') || lowerPath.includes('camoufox')) {
      return 'firefox';
    }
    return 'chromium';
  }
PATCH_EOF

    # 检查是否已经修改过
    if grep -q "camoufox" "$BROWSER_TS_PATH"; then
        log_success "browser.ts 已包含 camoufox 支持"
    else
        # 尝试找到 getBrowserType 函数并替换
        if grep -q "getBrowserType" "$BROWSER_TS_PATH"; then
            log_info "找到 getBrowserType 函数，进行修改..."
            
            # 使用 sed 替换函数
            # 这里使用更可靠的方法：创建完整的替换文件
            python3 << PYTHON_PATCH
import re

with open("$BROWSER_TS_PATH", "r") as f:
    content = f.read()

# 替换 getBrowserType 函数
old_pattern = r"private getBrowserType\([^)]*\)[^:]*:[^']*'chromium'\s*\|\s*'firefox'[^}]*\{[^}]*\}"
new_func = '''  private getBrowserType(executablePath: string): 'chromium' | 'firefox' {
    const lowerPath = executablePath.toLowerCase();
    if (lowerPath.includes('firefox') || lowerPath.includes('camoufox')) {
      return 'firefox';
    }
    return 'chromium';
  }'''

if re.search(old_pattern, content, re.DOTALL):
    content = re.sub(old_pattern, new_func, content, flags=re.DOTALL)
    with open("$BROWSER_TS_PATH", "w") as f:
        f.write(content)
    print("修改成功")
else:
    # 尝试更简单的方法：在文件末尾添加新方法或替换整个方法
    print("尝试替代修改方法...")
    
    # 查找并替换简单的返回语句
    if 'return "chromium"' in content or "return 'chromium'" in content:
        content = content.replace(
            'return "chromium"',
            '''const lowerPath = executablePath.toLowerCase();
    if (lowerPath.includes('firefox') || lowerPath.includes('camoufox')) {
      return 'firefox';
    }
    return 'chromium'"'''
        )
        with open("$BROWSER_TS_PATH", "w") as f:
            f.write(content)
        print("简单替换完成")
PYTHON_PATCH
            
            log_success "browser.ts 修改完成"
        else
            log_warn "未找到 getBrowserType 函数，尝试其他方法..."
        fi
    fi
else
    log_warn "未找到 browser.ts 文件"
fi

# ==================== 步骤 6: 重新编译 ====================
log_info "步骤 6/7: 重新编译 agent-browser..."

if [ -f "package.json" ]; then
    log_info "在源码目录中，安装依赖并编译..."
    npm install
    
    # 检查是否需要编译 Rust
    if [ -d "src-tauri" ] || [ -d "native" ]; then
        log_info "检测到 Rust 代码，编译 Rust CLI..."
        
        # 检查 Rust
        if ! command_exists cargo; then
            log_info "安装 Rust..."
            curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
            source "$HOME/.cargo/env"
        fi
        
        # 编译 Rust
        if [ -d "src-tauri" ]; then
            cd src-tauri && cargo build --release
            cd ..
        elif [ -d "native" ]; then
            cd native && cargo build --release
            cd ..
        fi
    fi
    
    npm run build
    log_success "编译完成"
    
    # ==================== 步骤 7: 替换系统版本 ====================
    log_info "步骤 7/7: 替换系统版本..."
    
    if [ -d "$AGENT_BROWSER_PATH" ]; then
        # 备份
        BACKUP_PATH="${AGENT_BROWSER_PATH}.backup.final.$(date +%Y%m%d_%H%M%S)"
        mv "$AGENT_BROWSER_PATH" "$BACKUP_PATH"
        log_info "原版本备份到: $BACKUP_PATH"
        
        # 复制新版本
        cp -r . "$AGENT_BROWSER_PATH"
        log_success "新版本已替换到: $AGENT_BROWSER_PATH"
    fi
    
    # 清理临时目录
    cd "$HOME"
    rm -rf "$TEMP_DIR"
else
    log_warn "不在源码目录中，尝试直接修改已编译的 JS 文件..."
    
    if [ -f "$BROWSER_JS_PATH" ]; then
        log_info "修改已编译的 browser.js..."
        
        python3 << PYTHON_JS_PATCH
import re

with open("$BROWSER_JS_PATH", "r") as f:
    content = f.read()

# 检查是否已经修改过
if 'camoufox' in content.lower():
    print("browser.js 已包含 camoufox 支持")
else:
    # 尝试在 JS 中添加检测逻辑
    # 查找类似 getBrowserType 的模式
    patterns = [
        r'(getBrowserType\([^)]*\)\s*\{[^}]*return\s+["\']chromium["\'])',
        r'(return\s+["\']chromium["\'])',
    ]
    
    modified = False
    for pattern in patterns:
        if re.search(pattern, content):
            # 在 return 'chromium' 前添加检测逻辑
            new_code = '''const lowerPath = executablePath.toLowerCase();
        if (lowerPath.includes('firefox') || lowerPath.includes('camoufox')) {
            return 'firefox';
        }
        return 'chromium' '''
            
            content = re.sub(
                r"return\s+['\"]chromium['\"]",
                new_code,
                content
            )
            modified = True
            break
    
    if modified:
        with open("$BROWSER_JS_PATH", "w") as f:
            f.write(content)
        print("browser.js 修改完成")
    else:
        print("无法自动修改 browser.js，请手动修改")
PYTHON_JS_PATCH
    else
        log_error "未找到 browser.js 文件"
    fi
fi

# ==================== 验证安装 ====================
log_info "验证安装..."

echo ""
echo "=========================================="
echo "           安装完成总结"
echo "=========================================="

# 检查 camoufox
if [ -f "$CAMOUFOX_PATH" ]; then
    log_success "✓ camoufox 浏览器: $CAMOUFOX_PATH"
else
    log_warn "✗ camoufox 浏览器未找到"
fi

# 检查 agent-browser
if command_exists agent-browser; then
    log_success "✓ agent-browser 命令可用"
else
    log_warn "✗ agent-browser 命令不可用，尝试使用 npx..."
fi

# 显示使用说明
echo ""
echo "=========================================="
echo "           使用说明"
echo "=========================================="
echo ""
echo "运行 agent-browser 时指定 camoufox 路径:"
echo ""
echo "  agent-browser --executable-path '$CAMOUFOX_PATH'"
echo ""
echo "或在代码中使用:"
echo ""
echo "  const browser = new AgentBrowser({"
echo "    executablePath: '$CAMOUFOX_PATH'"
echo "  });"
echo ""
echo "=========================================="

log_success "安装脚本执行完成!"
