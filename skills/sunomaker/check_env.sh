#!/bin/bash
# Suno Headless 环境检查脚本
# 专为无图形界面的 Linux 服务器设计
# 用法: bash suno-headless/check_env.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COOKIE_FILE="${SUNO_COOKIE_FILE:-$HOME/.suno/cookies.json}"
PYTHON="${SUNO_PYTHON:-python3}"
HAS_ERROR=0

echo "=== 🎵 Suno Headless 环境检查 ==="
echo "   专为无图形界面的 Linux 服务器设计"
echo ""

# ====== 1. 检查操作系统 ======
echo "=== 1. 检查操作系统 ==="
OS_TYPE="$(uname -s)"
if [ "$OS_TYPE" = "Linux" ]; then
    echo "✅ Linux 系统"
    if [ -z "$DISPLAY" ]; then
        echo "   ℹ️ 无图形界面环境（DISPLAY 未设置）— 将依赖 Xvfb"
    else
        echo "   ℹ️ DISPLAY=$DISPLAY（有图形环境，Xvfb 可选）"
    fi
elif [ "$OS_TYPE" = "Darwin" ]; then
    echo "⚠️ macOS 系统 — 本 skill 专为 Linux 无 GUI 服务器设计"
    echo "   macOS 用户建议使用原版 suno skill（带 GUI 支持）"
else
    echo "⚠️ 未知系统: $OS_TYPE"
fi

# ====== 2. 检查 Python3 ======
echo ""
echo "=== 2. 检查 Python3 ==="
if command -v "$PYTHON" &>/dev/null; then
    PY_VER=$("$PYTHON" --version 2>&1)
    echo "✅ $PY_VER"
else
    echo "❌ 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

# ====== 3. 检查 Playwright ======
echo ""
echo "=== 3. 检查 Playwright ==="
if "$PYTHON" -c "import playwright" 2>/dev/null; then
    echo "✅ Playwright 已安装"
else
    echo "❌ Playwright 未安装"
    echo "   请执行: pip3 install playwright && playwright install"
    HAS_ERROR=1
fi

# ====== 4. 检查 Google Chrome ======
echo ""
echo "=== 4. 检查 Google Chrome ==="
CHROME_BIN=""
for bin in google-chrome google-chrome-stable chromium chromium-browser; do
    if command -v "$bin" &>/dev/null; then
        CHROME_BIN="$bin"
        break
    fi
done

if [ -n "$CHROME_BIN" ]; then
    CHROME_VER=$("$CHROME_BIN" --version 2>&1 | head -1)
    echo "✅ $CHROME_VER ($CHROME_BIN)"
else
    echo "❌ 未找到 Google Chrome / Chromium"
    echo "   安装方法:"
    echo "   Ubuntu/Debian: sudo apt install -y google-chrome-stable"
    echo "   或: wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && sudo dpkg -i google-chrome-stable_current_amd64.deb"
    HAS_ERROR=1
fi

# ====== 5. 检查 Xvfb（无 GUI 环境必需） ======
echo ""
echo "=== 5. 检查 Xvfb 虚拟显示 ==="
if [ -z "$DISPLAY" ]; then
    if command -v Xvfb &>/dev/null; then
        echo "✅ Xvfb 已安装"
    else
        echo "❌ Xvfb 未安装（无 GUI 环境必需）"
        echo "   请执行: sudo apt install -y xvfb"
        HAS_ERROR=1
    fi
else
    echo "ℹ️ 有图形环境，Xvfb 可选（跳过检查）"
fi

# ====== 6. 检查 PyVirtualDisplay ======
echo ""
echo "=== 6. 检查 PyVirtualDisplay ==="
if [ -z "$DISPLAY" ]; then
    if "$PYTHON" -c "from pyvirtualdisplay import Display" 2>/dev/null; then
        echo "✅ PyVirtualDisplay 已安装"
    else
        echo "❌ PyVirtualDisplay 未安装（无 GUI 环境必需）"
        echo "   请执行: pip3 install PyVirtualDisplay"
        HAS_ERROR=1
    fi
else
    echo "ℹ️ 有图形环境，PyVirtualDisplay 可选（跳过检查）"
fi

# ====== 7. 检查 hcaptcha-challenger ======
echo ""
echo "=== 7. 检查 hcaptcha-challenger ==="
if "$PYTHON" -c "import hcaptcha_challenger" 2>/dev/null; then
    echo "✅ hcaptcha-challenger 已安装"
else
    echo "❌ hcaptcha-challenger 未安装"
    echo "   请执行: pip3 install hcaptcha-challenger"
    HAS_ERROR=1
fi

# ====== 8. 检查 requests ======
echo ""
echo "=== 8. 检查 requests ==="
if "$PYTHON" -c "import requests" 2>/dev/null; then
    echo "✅ requests 已安装"
else
    echo "❌ requests 未安装"
    echo "   请执行: pip3 install requests"
    HAS_ERROR=1
fi

# ====== 9. 检查 Gemini API Key ======
echo ""
echo "=== 9. 检查 Gemini API Key ==="
GEMINI_KEY=""
if [ -n "$GEMINI_API_KEY" ]; then
    GEMINI_KEY="$GEMINI_API_KEY"
    echo "✅ 已通过环境变量设置 (GEMINI_API_KEY)"
elif [ -f "$HOME/.suno/.env" ]; then
    GEMINI_KEY=$(grep "^GEMINI_API_KEY=" "$HOME/.suno/.env" 2>/dev/null | cut -d= -f2)
    if [ -n "$GEMINI_KEY" ]; then
        echo "✅ 已通过 ~/.suno/.env 设置"
    else
        echo "⚠️ ~/.suno/.env 存在但未找到 GEMINI_API_KEY"
        echo "   创建歌曲时需要 Gemini API Key 来自动解决 hCaptcha 验证码"
        echo "   获取: https://aistudio.google.com/app/apikey"
    fi
else
    echo "⚠️ 未设置 Gemini API Key"
    echo "   创建歌曲时需要 Gemini API Key 来自动解决 hCaptcha 验证码"
    echo "   设置方法: echo 'GEMINI_API_KEY=<your_key>' > ~/.suno/.env"
    echo "   获取地址: https://aistudio.google.com/app/apikey"
fi

# ====== 10. 检查 Cookie / 登录状态 ======
echo ""
echo "=== 10. 检查登录状态 ==="
if [ $HAS_ERROR -ne 0 ]; then
    echo "⚠️ 存在依赖缺失，跳过登录状态检查"
else
    if [ -f "$COOKIE_FILE" ]; then
        COOKIE_COUNT=$("$PYTHON" -c "import json; print(len(json.load(open('$COOKIE_FILE'))))" 2>/dev/null || echo "0")
        COOKIE_AGE=$("$PYTHON" -c "
import os, time
age = time.time() - os.path.getmtime('$COOKIE_FILE')
days = age / 86400
if days < 1:
    print(f'{age/3600:.1f} 小时前')
else:
    print(f'{days:.1f} 天前')
" 2>/dev/null || echo "未知")
        echo "✅ Cookie 文件存在: $COOKIE_FILE"
        echo "   数量: ${COOKIE_COUNT} 条"
        echo "   保存: ${COOKIE_AGE}"
    else
        echo "⚠️ Cookie 文件不存在: $COOKIE_FILE"
        echo "   需要先登录（运行 suno_login.py）"
    fi

    # 实际检查登录状态
    "$PYTHON" "$SCRIPT_DIR/suno_login.py" --check-only 2>/dev/null
    CHECK_EXIT=$?

    if [ $CHECK_EXIT -eq 0 ]; then
        echo "✅ 已登录 Suno.com"
    elif [ $CHECK_EXIT -eq 2 ]; then
        echo "⚠️ 未登录 Suno.com（需要先运行登录流程）"
        echo "   python3 $SCRIPT_DIR/suno_login.py --email <邮箱> --password <密码>"
    else
        echo "⚠️ 登录状态检查失败"
    fi
fi

# ====== 11. 虚拟显示功能测试 ======
echo ""
echo "=== 11. Xvfb 功能测试 ==="
if [ -z "$DISPLAY" ] && command -v Xvfb &>/dev/null; then
    "$PYTHON" -c "
from pyvirtualdisplay import Display
d = Display(visible=0, size=(1280, 800))
d.start()
import os
print(f'   ✅ Xvfb 虚拟显示测试通过 (DISPLAY={os.environ.get(\"DISPLAY\", \"\")})')
d.stop()
" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "   ❌ Xvfb 虚拟显示测试失败"
        HAS_ERROR=1
    fi
else
    echo "   ℹ️ 跳过（有图形环境或 Xvfb 未安装）"
fi

# ====== 总结 ======
echo ""
echo "========================================="
if [ $HAS_ERROR -ne 0 ]; then
    echo "❌ 存在依赖缺失，请按提示安装后重试"
    echo ""
    echo "快速安装全部依赖:"
    echo "  sudo apt update && sudo apt install -y xvfb google-chrome-stable fonts-noto-cjk"
    echo "  pip3 install -r $SCRIPT_DIR/requirements.txt"
    echo "  playwright install"
    exit 1
else
    echo "✅ 所有检查通过，可以正常使用！"
    exit 0
fi
