# GitHub Memory Sync

📝 将 OpenClaw 的 memory 文件同步到 GitHub 进行备份和版本控制。

## 快速开始

### 1. 准备 GitHub Token

1. 访问 https://github.com/settings/tokens/new
2. 选择 **Classic** token 类型
3. 勾选 **repo** 权限（完整仓库控制）
4. 生成并复制 Token

### 2. 创建仓库

在 GitHub 上创建一个新的 **Private** 仓库，例如：
- `yourusername/openclaw-memory-backup`

### 3. 配置环境变量

```bash
export GITHUBTOKEN="ghp_xxxxxxxxxxxxxxxxx"
export GITHUB_REPO="yourusername/openclaw-memory-backup"
```

或者在 `~/.openclaw/openclaw.json` 中配置。

### 4. 开始使用

```bash
# 初始化（首次使用）
~/.openclaw/workspace/skills/github-memory-sync/sync.sh init

# 推送更新
~/.openclaw/workspace/skills/github-memory-sync/sync.sh push

# 拉取更新
~/.openclaw/workspace/skills/github-memory-sync/sync.sh pull

# 查看状态
~/.openclaw/workspace/skills/github-memory-sync/sync.sh status
```

## 安全提示

- 🔒 使用 **Private** 仓库
- 🔐 不要泄露 Token
- 🔄 定期轮换 Token
- ⏰ 设置 Token 过期时间
