# 上传到 GitHub 指南

## 准备工作

### 1. 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名称：`triple-layer-memory`
3. 描述：三层记忆系统 - 解决 AI Agent 长对话记忆丢失和上下文管理问题
4. 选择 Public（公开）或 Private（私有）
5. 不要勾选 "Initialize this repository with a README"（我们已经有了）
6. 点击 "Create repository"

### 2. 配置 Git 认证

有两种方式：

#### 方式 A：使用 Personal Access Token（推荐）

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 勾选权限：
   - `repo`（完整的仓库访问权限）
   - `workflow`（如果需要 GitHub Actions）
4. 点击 "Generate token"
5. **复制 token**（只显示一次，保存好）

使用 token：
```bash
# 第一次 push 时会要求输入用户名和密码
# 用户名：你的 GitHub 用户名
# 密码：粘贴刚才复制的 token
```

#### 方式 B：使用 SSH Key

1. 生成 SSH key：
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
# 一路回车，使用默认设置
```

2. 复制公钥：
```bash
cat ~/.ssh/id_ed25519.pub
```

3. 添加到 GitHub：
   - 访问 https://github.com/settings/keys
   - 点击 "New SSH key"
   - 粘贴公钥
   - 点击 "Add SSH key"

## 上传步骤

### 1. 初始化 Git 仓库

```bash
cd ~/Desktop/openclaw-workspace/skills/triple-layer-memory
git init
git add .
git commit -m "feat: 初始化三层记忆系统 skill

- Session 自动压缩（150k tokens 触发）
- 记忆写入时机优化（关键时机立即写入）
- 跨 Session 记忆连续性（智能加载）
- 记忆遗忘机制（语义去重、高频升权、低权归档）
- 频道级记忆隔离（Mem0 命名空间）"
```

### 2. 关联远程仓库

**如果使用 HTTPS（Personal Access Token）**：
```bash
git remote add origin https://github.com/YOUR_USERNAME/triple-layer-memory.git
```

**如果使用 SSH**：
```bash
git remote add origin git@github.com:YOUR_USERNAME/triple-layer-memory.git
```

### 3. 推送到 GitHub

```bash
git branch -M main
git push -u origin main
```

如果使用 HTTPS，会要求输入用户名和密码（密码是 token）。

## 验证

访问 https://github.com/YOUR_USERNAME/triple-layer-memory 查看仓库。

## 发布到 ClawHub（可选）

如果想让其他人通过 `clawhub install` 安装：

1. 在 ClawHub 注册：https://clawhub.com
2. 提交你的 skill：https://clawhub.com/submit
3. 填写信息：
   - 名称：triple-layer-memory
   - GitHub URL：https://github.com/YOUR_USERNAME/triple-layer-memory
   - 描述：三层记忆系统 - 解决 AI Agent 长对话记忆丢失和上下文管理问题
   - 标签：memory, session-management, context-management

## 更新 README.md

上传后，记得更新 README.md 和 package.json 中的 `YOUR_USERNAME` 为你的实际 GitHub 用户名。

## 需要提供的信息

请告诉我：
1. 你的 GitHub 用户名
2. 你想使用 HTTPS 还是 SSH
3. 如果使用 HTTPS，你是否已经有 Personal Access Token

我可以帮你生成完整的上传命令。
