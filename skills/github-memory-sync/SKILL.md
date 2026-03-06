---
name: GitHub Memory Sync 技能
description: 📝 将 OpenClaw 的 memory 文件同步到 GitHub 仓库进行备份和版本控制。
---

# GitHub Memory Sync 技能

📝 将 OpenClaw 的 memory 文件同步到 GitHub 仓库进行备份和版本控制。

## 同步范围

1. **MEMORY.md** - 长期记忆文件（workspace 根目录）
2. **memory/*.md** - 日常记忆文件（memory 子目录）

## 功能特性

1. **📤 推送到 GitHub** - 将本地 memory 文件推送到 GitHub 仓库
2. **📥 从 GitHub 拉取** - 从 GitHub 拉取最新的 memory 文件
3. **📊 查看状态** - 检查本地和远程的差异
4. **📋 列出文件** - 显示 memory 目录下的所有文件
5. **🔧 初始化仓库** - 首次设置 GitHub 仓库连接

## 配置要求

### 必需配置

**GitHub Token:**
- 需要一个 Personal Access Token
- 权限要求：`repo`（仓库读写权限）
- 生成地址：https://github.com/settings/tokens/new

**GitHub 仓库:**
- 格式：`username/repository-name`
- 示例：`myusername/openclaw-memory-backup`
- 建议设为 **Private**（私有仓库），因为 memory 可能包含敏感信息

### 配置方式

#### 方案 A：使用环境变量（推荐用于测试）

```bash
export GITHUBTOKEN="ghp_xxxxxxxxxxxxxxxxx"
export GITHUB_REPO="yourusername/your-repo"
```

#### 方案 B：配置文件（推荐用于生产）

在 `~/.openclaw/openclaw.json` 中添加：

```json
{
  "skills": {
    "entries": {
      "github-memory-sync": {
        "enabled": true,
        "apiKey": "ghp_xxxxxxxxxxxxxxxxx",
        "env": {
          "GITHUBTOKEN": "ghp_xxxxxxxxxxxxxxxxx",
          "GITHUB_REPO": "username/memory-backup",
          "GITHUB_BRANCH": "main",
          "WORKSPACE_DIR": "/root/.openclaw/workspace"
        }
      }
    }
  }
}
```

## 使用示例

### 首次初始化

```
用户："初始化 GitHub memory 仓库"
AI: [获取 Token 和仓库信息后执行初始化]
```

### 推送更新

```
用户："同步 memory 到 GitHub"
AI: [执行推送操作]
```

### 拉取更新

```
用户："从 GitHub 拉取最新 memory"
AI: [执行拉取操作]
```

### 查看状态

```
用户："检查 memory 同步状态"
AI: [显示本地和远程的差异]
```

## 安全提醒

⚠️ **重要安全注意事项：**

1. **Token 保护**
   - ❌ 不要把 Token 发送到任何公开渠道
   - ❌ 不要在代码中硬编码 Token
   - ✅ 使用环境变量或配置文件
   - ✅ 定期轮换 Token

2. **仓库隐私**
   - 🔒 建议将 GitHub 仓库设为 **Private**（私有）
   - 👁 memory 可能包含敏感信息
   - 📝 审查 memory 内容再上传

3. **权限最小化**
   - 只给 Token 必要的权限（`repo`）
   - 避免使用具有广泛权限的 Token
   - 设置 Token 过期时间（不要永不过期）

## 激活技能

当用户提到以下关键词时激活此技能：
- "GitHub memory"
- "同步 memory"
- "备份 memory"
- "GitHub 备份"
- "memory 同步"
- "github-memory-sync"

## 配置流程

1. **获取配置信息**
   - 向用户询问 GitHub Token
   - 向用户询问 GitHub 仓库地址（或帮其创建）

2. **保存配置**
   - 将 Token 和仓库信息保存到配置文件或环境变量
   - 提醒用户注意安全事项

3. **执行操作**
   - 根据用户请求执行 init/push/pull/status 操作
   - 显示操作结果

## 注意事项

- 首次使用必须先执行 `init` 初始化
- 推送前建议先拉取，避免冲突
- 定期检查 Token 是否过期
- 建议启用 GitHub 的两因素认证
