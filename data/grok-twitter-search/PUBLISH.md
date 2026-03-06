# 发布到 ClawHub 指南

## 方式 1: 使用 ClawHub CLI（推荐）

### 前提条件
- 已安装 `clawhub` CLI (`npm install -g clawhub`)
- 已有 ClawHub 账号和 API Token

### 无显示屏服务器登录方法

#### 方法 A: 使用已有 Token 登录

如果你在本地机器上有 ClawHub 账号，可以在本地获取 token 然后复制到服务器：

**在本地机器（有浏览器）:**
```bash
# 登录并获取 token
clawhub login
clawhub auth token
# 复制输出的 token
```

**在无显示屏服务器:**
```bash
# 设置环境变量登录
export CLAWHUB_TOKEN="你的_token_这里"

# 验证登录
clawhub whoami
```

#### 方法 B: 直接在服务器配置 Token

```bash
# 创建配置文件
mkdir -p ~/.config/clawhub
echo '{"token": "你的_api_token"}' > ~/.config/clawhub/auth.json

# 验证
clawhub whoami
```

### 发布技能

```bash
# 进入技能目录
cd ~/.openclaw/workspace/skills/grok-twitter-search

# 发布（非交互模式）
clawhub publish . --no-input

# 或者指定 slug
clawhub publish . --slug grok-twitter-search --no-input
```

### 更新已发布技能

```bash
# 同步本地更改
clawhub sync --no-input
```

---

## 方式 2: GitHub + 手动提交到 ClawHub

### 第 1 步: 创建 GitHub 仓库

```bash
cd ~/.openclaw/workspace/skills/grok-twitter-search

# 初始化 git
git init
git add .
git commit -m "Initial release: Grok Twitter Search with WARP proxy support"

# 创建 GitHub 仓库（需要先在 github.com 创建空仓库）
git remote add origin https://github.com/你的用户名/grok-twitter-search.git
git branch -M main
git push -u origin main
```

### 第 2 步: 提交到 ClawHub

1. 访问 https://clawhub.ai/submit （使用本地浏览器）
2. 填写表单：
   - **Name**: `grok-twitter-search`
   - **Description**: 使用 xAI Grok 模型智能搜索 Twitter 内容，支持 Fast/Reasoning 双引擎和 WARP 代理自动检测
   - **GitHub URL**: `https://github.com/你的用户名/grok-twitter-search`
   - **Tags**: `twitter`, `grok`, `xai`, `social-media`, `proxy`, `warp`
   - **License**: MIT

---

## 方式 3: 纯命令行打包分享

如果不想发布到公共 registry，可以直接打包分享：

```bash
# 打包技能
cd ~/.openclaw/workspace/skills
tar czvf grok-twitter-search.tar.gz grok-twitter-search/

# 上传到文件服务器或发送给用户
scp grok-twitter-search.tar.gz user@server:/path/
```

其他用户安装：
```bash
# 解压到 OpenClaw skills 目录
tar xzvf grok-twitter-search.tar.gz -C ~/.openclaw/skills/

# 重启 OpenClaw Gateway
openclaw gateway restart
```

---

## 验证发布

发布后可以通过以下方式验证：

```bash
# 搜索自己的技能
clawhub search grok-twitter-search

# 查看详情
clawhub inspect grok-twitter-search

# 测试安装
clawhub install grok-twitter-search --dir /tmp/test-install
```

---

## 获取 ClawHub API Token

如果没有 token，可以通过以下方式获取：

1. 访问 https://clawhub.ai/settings/tokens （本地浏览器）
2. 点击 "Generate New Token"
3. 复制 token 到服务器配置

或者在命令行使用 GitHub OAuth:
```bash
# 这会提供一个 URL，在本地浏览器打开后粘贴回调 URL
clawhub auth login --method=github
```
