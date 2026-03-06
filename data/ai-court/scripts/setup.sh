#!/bin/bash
# ============================================
# AI 朝廷一键部署
# Ubuntu 22.04/24.04
# ============================================
set -e

REPO_RAW="https://raw.githubusercontent.com/wanikua/ai-court-skill/main/ai-court/references"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}AI 朝廷一键部署${NC}"
echo "================================"
echo ""

# ---- 1. 系统更新 ----
echo -e "${YELLOW}[1/7] 系统更新...${NC}"
sudo apt-get update -qq

# ---- 2. 防火墙 ----
echo -e "${YELLOW}[2/7] 配置防火墙...${NC}"
sudo iptables -D INPUT -j REJECT --reject-with icmp-host-prohibited 2>/dev/null || true
sudo iptables -D FORWARD -j REJECT --reject-with icmp-host-prohibited 2>/dev/null || true
sudo netfilter-persistent save 2>/dev/null || true
echo -e "  ${GREEN}✓ 防火墙已配置${NC}"

# ---- 3. Swap ----
echo -e "${YELLOW}[3/7] 配置 Swap...${NC}"
if [ ! -f /swapfile ]; then
    sudo fallocate -l 4G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab > /dev/null
    echo -e "  ${GREEN}✓ 4GB Swap 已创建${NC}"
else
    echo -e "  ${GREEN}✓ Swap 已存在${NC}"
fi

# ---- 4. Node.js ----
echo -e "${YELLOW}[4/7] 安装 Node.js 22...${NC}"
if command -v node &>/dev/null && [[ "$(node -v)" == v22* ]]; then
    echo -e "  ${GREEN}✓ Node.js $(node -v) 已安装${NC}"
else
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - > /dev/null 2>&1
    sudo apt-get install -y nodejs -qq
    echo -e "  ${GREEN}✓ Node.js $(node -v) 安装完成${NC}"
fi

# ---- 5. GitHub CLI ----
echo -e "${YELLOW}[5/7] 安装 GitHub CLI...${NC}"
if command -v gh &>/dev/null; then
    echo -e "  ${GREEN}✓ gh 已安装${NC}"
else
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg 2>/dev/null
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt-get update -qq && sudo apt-get install gh -y -qq
    echo -e "  ${GREEN}✓ gh CLI 安装完成${NC}"
fi

# ---- 6. Chromium（浏览器 Skill 需要：搜索/截图）----
echo -e "${YELLOW}[6/8] 安装 Chromium...${NC}"
if command -v chromium-browser &>/dev/null || snap list chromium &>/dev/null 2>&1; then
    echo -e "  ${GREEN}✓ Chromium 已安装${NC}"
else
    sudo snap install chromium 2>/dev/null || sudo apt-get install -y chromium-browser -qq
    echo -e "  ${GREEN}✓ Chromium 安装完成${NC}"
fi
if ! grep -q PUPPETEER_EXECUTABLE_PATH ~/.bashrc 2>/dev/null; then
    CHROME_BIN="/snap/chromium/current/usr/lib/chromium-browser/chrome"
    [ ! -f "$CHROME_BIN" ] && CHROME_BIN=$(which chromium-browser 2>/dev/null || echo "$CHROME_BIN")
    echo "export PUPPETEER_EXECUTABLE_PATH=\"$CHROME_BIN\"" >> ~/.bashrc
fi

# ---- 7. Clawdbot ----
echo -e "${YELLOW}[7/8] 安装 Clawdbot...${NC}"
sudo npm install -g clawdbot --loglevel=error
echo -e "  ${GREEN}✓ Clawdbot $(clawdbot --version 2>/dev/null) 安装完成${NC}"

# ---- 8. 初始化工作区 ----
echo -e "${YELLOW}[8/8] 初始化朝廷工作区...${NC}"
WORKSPACE="$HOME/clawd"
CONFIG_DIR="$HOME/.clawdbot"
mkdir -p "$WORKSPACE/memory"
mkdir -p "$CONFIG_DIR"

# 优先用本地文件（git clone），没有则从 GitHub 下载
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd 2>/dev/null || echo "")"
LOCAL_REF="${SCRIPT_DIR:+$SCRIPT_DIR/../references}"

download_ref() {
    local file="$1" dest="$2"
    [ -f "$dest" ] && return 0
    if [ -n "$LOCAL_REF" ] && [ -f "$LOCAL_REF/$file" ]; then
        cp "$LOCAL_REF/$file" "$dest"
    else
        curl -fsSL "$REPO_RAW/$file" -o "$dest"
    fi
    echo -e "  ${GREEN}✓ $(basename "$dest") 已创建${NC}"
}

for f in SOUL.md IDENTITY.md USER.md AGENTS.md; do
    download_ref "$f" "$WORKSPACE/$f"
done

if [ ! -f "$CONFIG_DIR/clawdbot.json" ]; then
    download_ref "clawdbot-template.json" "$CONFIG_DIR/clawdbot.json"
    sed -i "s|\$HOME|$HOME|g" "$CONFIG_DIR/clawdbot.json"
fi

echo -e "${YELLOW}安装 Gateway 服务...${NC}"
clawdbot gateway install 2>/dev/null \
    && echo -e "  ${GREEN}✓ Gateway 服务已安装（开机自启）${NC}" \
    || echo -e "  ${YELLOW}⚠ 配置填好后运行 clawdbot gateway install${NC}"

echo ""
echo "================================"
echo -e "${GREEN}部署完成！${NC}"
echo "================================"
echo ""
echo "下一步："
echo ""
echo -e "  ${YELLOW}1.${NC} 编辑 ~/.clawdbot/clawdbot.json"
echo "     填入 LLM API Key + Discord Bot Token"
echo ""
echo -e "  ${YELLOW}2.${NC} 每个 Discord Bot 开启 Message Content Intent + Server Members Intent"
echo ""
echo -e "  ${YELLOW}3.${NC} systemctl --user start clawdbot-gateway"
echo ""
echo -e "  ${YELLOW}提示：${NC}Discord Guild ID 获取方法："
echo "     服务器设置 → 小组件 → 服务器 ID"
echo "     或右键服务器名 → 复制服务器 ID（需开启开发者模式）"
echo ""
echo -e "  教程：${BLUE}https://github.com/wanikua/ai-court-skill${NC}"
echo ""
