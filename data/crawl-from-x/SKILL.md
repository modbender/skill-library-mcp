---
name: crawl-from-x
description: X/Twitter 帖子抓取工具。管理关注用户列表，自动抓取当天最新帖子，导出 Markdown。
---

# Crawl From X

X/Twitter 帖子抓取工具。

⚠️ **前置要求**：需要 **OpenClaw Browser Relay** 和浏览器扩展。

---

## 安装

```bash
npx clawhub@latest install crawl-from-x
```

安装位置：
- `$CLAWD/skills/crawl-from-x/scripts/craw_hot.py` - 主脚本
- `$CLAWD/skills/crawl-from-x/users.txt` - 用户列表
- `$CLAWD/skills/crawl-from-x/results/` - 抓取结果

---

## 准备

### 1. 安装 OpenClaw

访问 https://github.com/openclaw/openclaw 下载安装。

### 2. 安装浏览器扩展

在 OpenClaw 设置中进入 "Browser Relay"，安装扩展。完成后扩展显示绿色图标。

### 3. 启动 Browser Relay

```bash
openclaw browser start
openclaw browser status  # 确认显示 "browser: enabled"
```

### 4. 登录 X 账号

在安装了扩展的浏览器中登录 X (Twitter)。

---

## 快速开始

```bash
cd $CLAWD/skills/crawl-from-x/scripts

# 添加用户
python3 craw_hot.py add username

# 列出用户
python3 craw_hot.py list

# 删除用户
python3 craw_hot.py remove username

# 抓取所有用户
python3 craw_hot.py crawl

# 抓取单个用户
python3 craw_hot.py crawl username
```

**结果文件：**
- `posts_YYYYMMDD_HHMMSS.md` - 完整内容（Markdown），媒体 URL 已替换为本地路径
- `posts_YYYYMMDD_HHMMSS.txt` - URL 列表（仅全部用户抓取）
- `images/` - 下载的图片和视频

**说明：**
- 单用户抓取和全部用户抓取使用相同的策略
- 所有媒体文件（图片、动图、视频）都会下载到 `images/` 目录
- Markdown 文件中的媒体 URL 会自动替换为本地相对路径

---

## 注意事项

1. **浏览器要求**：必须安装 OpenClaw 浏览器扩展
2. **登录状态**：浏览器必须登录 X 账号
3. **速率限制**：脚本已内置随机延迟
4. **私密账号**：无法抓取私密账号内容
