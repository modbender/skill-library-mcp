---
name: elegant-sync
description: 优雅安全的 OpenClaw 配置同步工具 - 支持选择性备份、.gitignore 规则、版本控制
---

# Elegant Sync

优雅安全的 OpenClaw 配置同步工具

## 功能

- 🏷️ 版本化备份 - 每次同步创建 git tag，可回滚任意版本
- 🔒 安全优先 - 不上传配置文件、密钥、敏感信息
- 📂 .gitignore 支持 - 使用项目 .gitignore 规则选择
- 🎯 选择性同步 - 可选择备份哪些目录
- 💾 灾难恢复 - 自动本地备份，支持一键恢复
- 🌿 **多实例独立分支** - 每个设备一个分支，互不干扰

## 备份结构

```
mini-claw/
├── main/         # 介绍文档
├── omen16/       # 设备1
├── omen16-2/     # 设备2
└── macbook/      # 设备3
```

## 备份内容

| 目录/文件 | 说明 |
|-----------|------|
| **workspace/memory/** | ⭐ 最重要！个人记忆，无价 |
| workspace/AGENTS.md | 代理规范 |
| workspace/IDENTITY.md | 身份信息 |
| workspace/USER.md | 用户信息 |
| workspace/SOUL.md | 灵魂配置 |
| workspace/TOOLS.md | 工具配置 |
| workspace/HEARTBEAT.md | 心跳配置 |
| workspace/skills/ | 自定义技能 |

## 不备份（安全）

| 目录/文件 | 原因 |
|-----------|------|
| .env | 含 API 密钥 |
| openclaw.json | 含配置密钥 |
| credentials/ | 凭证信息 |
| .git/ | Git 仓库 |
| logs/ | 日志文件 |
| media/ | 媒体文件 |

## 配置

### 1. 配置环境变量

```bash
# 在 ~/.openclaw/.backup.env 中配置
BACKUP_REPO=https://github.com/你的用户名/你的仓库名
BACKUP_TOKEN=ghp_xxx
INSTANCE_ID=你的主机名
```

### 2. 首次配置提示

运行 `/sync` 时会自动检测是否已配置，如果没有配置会提示。

---

## 多实例管理

### 当前实例

此机器实例名：`opi5b`（主机名）

### 其他实例配置

| 实例 | INSTANCE_ID | 配置示例 |
|------|-------------|----------|
| Orange Pi | opi5b | 默认 |
| Mac | macbook | INSTANCE_ID=macbook |
| VPS | vps-1 | INSTANCE_ID=vps-1 |

---

## 恢复流程

### 场景：新机器或重装系统

#### 1. 安装 OpenClaw

```bash
# 在新机器上安装 OpenClaw
```

#### 2. 克隆备份

```bash
git clone https://github.com/你的用户名/你的仓库名
```

#### 3. 查看分支

```bash
cd mini-claw
git branch -a
```

#### 4. 切换并恢复指定实例

```bash
# 例如恢复 omen16
git checkout omen16
cp -r omen16/* ~/.openclaw/workspace/
```

#### 5. 更新 Instance ID

在新机器的 `~/.openclaw/.backup.env` 中更新：

```bash
INSTANCE_ID=new-machine-name
```

#### 6. 验证

```bash
node elegant-sync/index.js status
```

---

## 重要原则

### Memory 是最宝贵的资产
- 每个实例的 memory 都是无价的
- 备份到私有仓库 (mini-claw)
- 确保无损保留

## 更新日志

- 2026-02-28 v1.0.1: 修复多实例备份，每个设备独立分支
- 2026-02-28 v1.0.0: 初始版本
