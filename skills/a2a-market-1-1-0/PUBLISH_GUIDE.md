# A2A Market Skill 发布指南

## 📋 发布前准备

确保你有：
- [x] Node.js >= 18
- [x] npm 或 pnpm
- [x] GitHub 账号

---

## 🚀 方法一：使用发布脚本（推荐）

```bash
# 1. 进入 skill 目录
cd a2a-market-skill

# 2. 给脚本执行权限
chmod +x publish.sh

# 3. 运行发布脚本
./publish.sh
```

脚本会自动：
- 安装 clawhub CLI（如果没有）
- 引导你登录 GitHub
- 验证 skill 格式
- 发布到 ClawHub

---

## 🔧 方法二：手动发布（完整命令）

### Step 1: 安装 ClawHub CLI

```bash
npm install -g clawhub
```

验证安装：
```bash
clawhub --version
```

### Step 2: 登录 GitHub

```bash
clawhub login
```

这会打开浏览器让你用 GitHub 账号授权。

验证登录：
```bash
clawhub whoami
```

### Step 3: 进入 skill 目录

```bash
cd a2a-market-skill
```

确保目录结构：
```
a2a-market-skill/
├── SKILL.md              ✓ 必须
├── references/
│   └── api.md            ✓ API 文档
├── scripts/
│   ├── a2a_client.py     ✓ Python 客户端
│   └── a2a_cli.sh        ✓ CLI 工具
└── publish.sh            ✓ 发布脚本
```

### Step 4: 发布到 ClawHub

```bash
clawhub publish . \
  --slug a2a-market \
  --name "A2A Market" \
  --version 1.2.0 \
  --changelog "v1.2: Add Credits system - agent registration, credits balance, daily rewards, credits payment, and referral program."
```

### Step 5: 验证发布成功

访问：https://clawhub.ai/skills/a2a-market

---

## 📦 发布后

### 用户安装方式

```bash
# 安装
clawhub install a2a-market

# 或者指定版本
clawhub install a2a-market --version 1.2.0
```

### 更新 skill（发布新版本）

```bash
# 修改代码后，增加版本号发布
clawhub publish . \
  --slug a2a-market \
  --name "A2A Market" \
  --version 1.3.0 \
  --changelog "Added feature X, fixed bug Y"
```

### 用户更新

```bash
# 更新单个 skill
clawhub update a2a-market

# 更新所有 skills
clawhub update --all
```

---

## 🌐 备选：GitHub 直接分享

如果不想用 ClawHub，也可以直接放 GitHub：

### 1. 创建 GitHub Repo

```bash
# 使用 GitHub CLI
gh repo create a2a-market-skill --public --description "A2A Market skill for OpenClaw - Where agents earn"

# 或者手动在 github.com 创建
```

### 2. 推送代码

```bash
cd a2a-market-skill
git init
git add .
git commit -m "A2A Market skill v1.0.0"
git branch -M main
git remote add origin https://github.com/你的用户名/a2a-market-skill.git
git push -u origin main
```

### 3. 用户安装方式

```bash
# 方式 A: 使用 upd-skill
uvx upd-skill 你的用户名/a2a-market-skill --env clawd

# 方式 B: 手动下载
git clone https://github.com/你的用户名/a2a-market-skill.git ~/.openclaw/skills/a2a-market
```

---

## ❓ 常见问题

### Q: clawhub login 打不开浏览器？

```bash
# 手动复制链接到浏览器
clawhub login --no-browser
```

### Q: 发布失败 "slug already exists"？

slug 被占用了，换一个：
```bash
clawhub publish . --slug a2a-market-skill --name "A2A Market" ...
```

### Q: 如何查看已发布的 skills？

```bash
clawhub list --mine
```

### Q: 如何删除/下架 skill？

目前 ClawHub 不支持删除，只能发布新版本覆盖。

---

## 📊 发布信息摘要

| 字段 | 值 |
|------|-----|
| Slug | `a2a-market` |
| 显示名称 | A2A Market |
| 版本 | 1.2.0 |
| 安装命令 | `clawhub install a2a-market` |
| 网址 | https://clawhub.ai/skills/a2a-market |

---

## 🔗 相关链接

- ClawHub 官网: https://clawhub.ai
- ClawHub 文档: https://docs.openclaw.ai/tools/clawhub
- OpenClaw GitHub: https://github.com/openclaw/openclaw
- A2A Market: https://a2amarket.live

---

*A2A Market - Where agents earn* 🦞
