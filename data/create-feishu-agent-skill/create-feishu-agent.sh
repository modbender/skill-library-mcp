#!/bin/bash
# create-feishu-agent.sh - 快速创建飞书 Agent
# 用法: ./create-feishu-agent.sh <agent_name> <display_name> <app_id> <app_secret>

set -e

if [ $# -lt 4 ]; then
    echo "用法: $0 <agent_name> <display_name> <app_id> <app_secret>"
    echo "示例: $0 health_manager '健康助手' cli_xxx xxx"
    exit 1
fi

AGENT_NAME=$1
DISPLAY_NAME=$2
APP_ID=$3
APP_SECRET=$4

WORKSPACE="$HOME/.openclaw/workspace"
AGENT_DIR="$WORKSPACE/agents/$AGENT_NAME"
CONFIG_FILE="$HOME/.openclaw/openclaw.json"

echo "=== 创建飞书 Agent: $AGENT_NAME ==="

# 1. 创建目录结构
echo "[1/5] 创建目录结构..."
mkdir -p "$AGENT_DIR/memory"

# 2. 创建 SOUL.md
echo "[2/5] 创建 SOUL.md..."
cat > "$AGENT_DIR/SOUL.md" << 'EOF'
# SOUL.md - <DISPLAY_NAME>

_一句话描述你的agent_

## Core Truths

**原则1。** 解释...

**原则2。** 解释...

## What You Do

### 功能1
- 具体说明

## Boundaries

- 边界1
- 边界2

## Vibe

性格描述
EOF
sed -i '' "s/<DISPLAY_NAME>/$DISPLAY_NAME/g" "$AGENT_DIR/SOUL.md"

# 3. 创建 AGENTS.md
echo "[3/5] 创建 AGENTS.md..."
cat > "$AGENT_DIR/AGENTS.md" << EOF
# AGENTS.md - $DISPLAY_NAME Workspace

继承主 workspace 规则。

## 职责

- 职责1
- 职责2
EOF

# 4. 创建 MEMORY.md
echo "[4/5] 创建 MEMORY.md..."
cat > "$AGENT_DIR/MEMORY.md" << 'EOF'
# MEMORY.md - 长期记忆

## 👤 关于用户

### 关键信息
_(重要背景)_

### 偏好设置
_(发现的偏好)_

## 📚 活跃项目

_(进行中的事项)_

## 🧠 经验教训

_(学到的经验)_

---
*最后更新: (日期)*
EOF

# 5. 更新 openclaw.json
echo "[5/5] 更新配置..."

# 备份配置
cp "$CONFIG_FILE" "$CONFIG_FILE.bak.$(date +%Y%m%d%H%M%S)"

# 使用 Python 更新配置
python3 << PYTHON_SCRIPT
import json
import sys

config_file = "$CONFIG_FILE"
agent_name = "$AGENT_NAME"
display_name = "$DISPLAY_NAME"
app_id = "$APP_ID"
app_secret = "$APP_SECRET"
workspace = "$WORKSPACE"

with open(config_file, 'r') as f:
    config = json.load(f)

# 添加飞书账户
if 'accounts' not in config['channels']['feishu']:
    config['channels']['feishu']['accounts'] = {}

config['channels']['feishu']['accounts'][agent_name] = {
    "appId": app_id,
    "appSecret": app_secret,
    "name": display_name,
    "enabled": True,
    "connectionMode": "websocket",
    "domain": "feishu",
    "groupPolicy": "open",
    "requireMention": False
}

# 添加 Agent
agent_entry = {
    "id": agent_name,
    "name": display_name,
    "workspace": f"{workspace}/agents/{agent_name}",
    "model": "zai/glm-5"
}

if agent_entry not in config['agents']['entries']:
    config['agents']['entries'].append(agent_entry)

# 添加绑定
binding = {
    "agentId": agent_name,
    "match": {
        "channel": "feishu",
        "accountId": agent_name
    }
}

if 'bindings' not in config:
    config['bindings'] = []

# 检查是否已存在相同绑定
exists = False
for b in config['bindings']:
    if b.get('agentId') == agent_name and b.get('match', {}).get('accountId') == agent_name:
        exists = True
        break

if not exists:
    config['bindings'].append(binding)

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)

print("配置更新成功!")
PYTHON_SCRIPT

echo ""
echo "=== 创建完成! ==="
echo ""
echo "Agent 目录: $AGENT_DIR"
echo ""
echo "下一步:"
echo "1. 编辑 $AGENT_DIR/SOUL.md 设置人设"
echo "2. 在飞书开放平台配置权限和事件订阅"
echo "3. 运行: openclaw gateway restart"
echo "4. 将机器人添加到群聊测试"
echo ""
echo "完成!"
