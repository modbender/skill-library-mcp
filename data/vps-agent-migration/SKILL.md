---
name: vps-agent-migration
description: 将本地 OpenClaw 子 Agent 迁移到 VPS 上运行。包括：rsync 复制文件、配置 Discord Bot、添加 bindings 路由、禁用本地账号避免冲突。使用场景：当需要将本地的 creative/dev/qa/strategist/pojun 等子 Agent 迁移到远程 VPS 时使用此 skill。
---

# VPS Agent Migration

将本地 OpenClaw Agent 迁移到 VPS 上运行。

## 前提条件

- VPS 已安装 OpenClaw
- 本地已配置好要迁移的 Agent（workspace、SOUL.md 等）
- 需要迁移的 Agent 名称（如 creative, dev, qa 等）
- SSH 访问 VPS（sshpass 或配置 SSH key）

## 迁移步骤

### Step 1: 连接 VPS 并复制文件

```bash
# 连接 VPS
sshpass -p 'VPS密码' ssh -o StrictHostKeyChecking=no root@VPS_IP

# 复制 Agent 文件（排除 sessions、.DS_Store、memory.md）
rsync -avz --exclude='sessions' --exclude='.DS_Store' --exclude='memory.md' \
  ~/.openclaw/agents/[agent名]/ root@VPS_IP:/root/.openclaw/agents/[agent名]/
```

### Step 2: 获取本地 Discord Token

从本地 `~/.openclaw/openclaw.json` 中查找对应 Agent 的 token：

```bash
cat ~/.openclaw/openclaw.json | grep -A5 '"[Discord_ID]":'
```

### Step 3: 在 VPS 上添加 Discord 账号

在 VPS 上使用 Python 更新配置：

```bash
sshpass -p 'VPS密码' ssh -o StrictHostKeyChecking=no root@VPS_IP 'python3 -c "
import json
with open(\"/root/.openclaw/openclaw.json\") as f:
    data = json.load(f)
data[\"channels\"][\"discord\"][\"accounts\"][\"[Discord_ID]\"] = {
    \"name\": \"[Agent名字]\",
    \"enabled\": True,
    \"token\": \"[Token]\",
    \"groupPolicy\": \"allowlist\",
    \"streaming\": \"off\"
}
with open(\"/root/.openclaw/openclaw.json\", \"w\") as f:
    json.dump(data, f, indent=2)
"'
```

### Step 4: 更新 Bindings

```bash
sshpass -p 'VPS密码' ssh -o StrictHostKeyChecking=no root@VPS_IP 'openclaw config set bindings \"[{\\\"agentId\\\":\\\"[agentId]\\\",\\\"match\\\":{\\\"channel\\\":\\\"discord\\\",\\\"accountId\\\":\\\"[Discord_ID]\\\"}}]\"'
```

### Step 5: 重启 VPS Gateway

```bash
sshpass -p 'VPS密码' ssh -o StrictHostKeyChecking=no root@VPS_IP "openclaw gateway restart"
```

### Step 6: 禁用本地账号

```bash
# 禁用本地账号
openclaw config patch --json '{"channels": {"discord": {"accounts": {"[Discord_ID]": {"enabled": false}}}}}'

# 重启本地 Gateway
openclaw gateway restart
```

## 关键坑点

1. **requireMention**: 默认 `true` 会导致 Agent 不自动回复，需要在 `guilds` 中设为 `false`
2. **多账号配置**: `channels.discord.token` 是默认账号，`channels.discord.accounts[id].token` 是多账号模式
3. **SSH 连接**: 偶尔会断开，多试几次即可
4. **Token 获取**: Discord Bot Token 在 openclaw.json 的 `channels.discord.accounts[id].token` 中

## 常见 Discord ID 格式

- 频道 ID: 18位数字（如 1475374006226915434）
- 用户/Bot ID: 18位数字（如 1475676302215221278）
