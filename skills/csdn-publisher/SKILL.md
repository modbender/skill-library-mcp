---
name: csdn-publisher
version: 2.3.0
description: 写文章并发布到 CSDN。使用浏览器自动化 + 扫码登录。支持通过 Telegram 发送二维码，无需 VNC。集成 blog-writer 写作方法论，产出高质量、有个人风格的技术文章。
---

# CSDN Publisher

通过浏览器自动化发布文章到 CSDN。支持扫码登录，二维码可通过 Telegram 发送。

**v2.0 新增**：集成 blog-writer 写作方法论，自动产出高质量、有个人风格的技术文章。

---

## 🎯 核心工作流（v2.0）

```
1. 用户说"帮我发篇 CSDN 文章"或提供主题/素材
2. 【内容创作阶段】调用 blog-writer 写作方法论
   ├─ 阅读 style-guide-cn.md 校准写作风格
   ├─ 参考 examples/ 目录中的示例文章
   ├─ 整合用户提供的素材/研究材料
   └─ 产出初稿，用户确认后继续
3. 检查登录状态
   ├─ 已登录 → 继续
   └─ 未登录 → 扫码登录流程
4. 启动浏览器，打开编辑器
5. 注入标题和内容
6. 添加标签，点击发布
7. 验证发布成功，返回文章链接
8. 【可选】用户确认终稿后，保存到 examples/ 目录
```

---

## ✍️ 内容创作阶段（核心）

### 触发条件

当用户请求写文章时，**必须先完成内容创作**，再进行发布。

触发词：
- "帮我写篇文章"
- "发布到 CSDN"
- "写一篇关于 XXX 的博客"
- 提供主题、素材、链接等

### 写作流程

#### Step 1: 收集信息

向用户确认：
- **主题**：写什么？
- **角度**：从什么视角切入？（教程、踩坑记录、观点输出、技术分析）
- **素材**：有没有参考链接、笔记、代码片段？
- **长度**：简短（500-800字）/ 标准（800-1500字）/ 深度（1500-3000字）

#### Step 2: 阅读风格指南

**必须阅读** `style-guide-cn.md` 校准写作风格。

核心原则：
- 直接、有观点、不装腔作势
- 口语化表达，像跟朋友聊天
- 第一人称叙述个人经历
- 短段落（2-4句话）
- 多用小标题分隔内容

#### Step 3: 参考示例文章

阅读 `examples/` 目录中的示例文章，感受目标风格。

#### Step 4: 撰写初稿

按照风格指南撰写，完成后展示给用户确认。

#### Step 5: 迭代修改

根据用户反馈修改，直到用户满意。

---

## 📝 写作风格指南（中文版）

详见 `style-guide-cn.md`，核心要点：

### 开头模式

用强有力的观点或个人经历开场：

✅ 好的开头：
- "搞了两个小时，终于把这个坑填上了。"
- "说实话，我一开始是拒绝用 XXX 的。"
- "作为一个写了 5 年代码的人，我可以负责任地说：这玩意儿真的有用。"

❌ 避免的开头：
- "随着人工智能的快速发展..."
- "在当今数字化时代..."
- "众所周知..."

### 结构模式

```markdown
# [直接、有态度的标题]

[开头：1-2句话抛出核心观点或问题]

### [小标题1：问题/背景]
[2-3个短段落]

### [小标题2：过程/分析]
[具体细节、代码、截图]

### [小标题3：解决方案/结论]
[实操步骤或观点总结]

### 写在最后
[个人感想、行动号召、或前瞻性思考]
```

### 语言风格

**用这些：**
- "说实话"、"坦白讲"
- "踩了个坑"、"折腾了半天"
- "真香"、"血泪教训"
- 第一人称："我发现"、"我的做法是"

**避免这些：**
- "首先...其次...最后..."
- "值得注意的是"
- "综上所述"
- "不难发现"

### 新闻资讯类文章特别要求

写新闻汇总、行业日报等资讯类文章时：
- **必须附带原文链接**：每条新闻都要有跳转链接，方便读者查看原文
- 链接格式：`[新闻标题](原文URL)` 或在新闻末尾标注 `👉 [原文链接](URL)`
- 如果原文链接不可用，标注来源名称（如"来源：36氪"）

### 段落长度

- 每段 2-4 句话
- 单句成段用于强调
- 每 150-250 字一个小标题

---

## 🔍 新闻去重（v2.3 新增）

发布新闻汇总类文章时，**必须先去重**，避免同一条新闻反复出现。

### 去重流程

1. **获取已有新闻**：运行 `scripts/notion-query-recent.sh 14` 获取最近 14 天的 Notion 数据库记录
2. **逐条比对**：对每条搜索到的新闻，检查是否与已有记录重复：
   - **URL 精确匹配**：同一个 URL 已存在 → 跳过
   - **语义重复**：标题描述的是同一件事（即使措辞不同）→ 跳过
3. **只保留新新闻**：去重后无新闻则跳过写文章和发布

### 语义重复判断示例

以下算同一条新闻：
- "宇树人形机器人日常训练视频爆火B站，播放量超376万" ≈ "宇树人形机器人日常训练视频爆火：播放量超375万"
- "小鹏Iron人形机器人深圳首秀摔倒" ≈ "小鹏Iron机器人深圳商场演示翻车"
- "Apptronik融资9.35亿美元" ≈ "Apptronik获5.2亿美元融资"（同一轮融资的不同报道）

### 脚本说明

| 脚本 | 用途 |
|------|------|
| `scripts/notion-query-recent.sh [天数]` | 查询最近 N 天的已有新闻，输出 `标题 \| URL \| 日期` |
| `scripts/notion-check-duplicate.sh "标题" ["URL"]` | 精确检查单条新闻是否重复，返回 `duplicate` 或 `new` |

⚠️ 脚本中的 Notion API Key 和 Database ID 需要根据实际环境配置。

---

## 🔧 技术发布流程

### 前置条件

#### 1. 安装 Chrome

```bash
cd /tmp && curl -sL \
  "https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm" \
  -o chrome.rpm && yum install -y ./chrome.rpm
```

#### 2. 安装 Python 依赖

```bash
pip install playwright -i https://pypi.org/simple/
playwright install chromium
```

#### 3. 配置 OpenClaw 浏览器

需要 headless + noSandbox 模式（服务器无显示器）：

```bash
# 通过 gateway config.patch 添加：
{"browser": {"headless": true, "noSandbox": true}}
```

---

### 扫码登录流程 ✨

#### 完整流程（推荐）

1. **启动登录脚本**
```bash
cd /root/.openclaw/workspace/skills/csdn-publisher
nohup python scripts/login.py login --timeout 300 > /tmp/csdn-login.log 2>&1 &
```

2. **等待二维码生成**（约 10-15 秒）
```bash
ls ~/.openclaw/workspace/credentials/csdn-qr.png
```

3. **通过 Telegram 发送二维码**
```
message(action="send", filePath="~/.openclaw/workspace/credentials/csdn-qr.png", target="用户ID", caption="请用 CSDN App 扫码登录")
```

4. **用户扫码后，脚本自动保存 Cookie**
```bash
cat /tmp/csdn-login.log
```

#### 检查 Cookie 有效性

```bash
python scripts/login.py check
```

---

### 发布文章流程（browser 工具）

#### Step 1: 启动浏览器并检查登录状态

```
browser action=start profile=openclaw
browser action=navigate targetUrl=https://editor.csdn.net/md
browser action=snapshot
```

检查 snapshot 结果：
- 看到 `textbox "请输入文章标题"` → **已登录** ✅
- 看到 `登录` 或 `扫码` → **需要扫码登录**

#### Step 2: 扫码登录（仅首次或 Cookie 过期时）

```
browser action=navigate targetUrl=https://passport.csdn.net/login
browser action=screenshot  # 截取二维码发给用户
```

#### Step 3: 注入标题

使用 browser 工具的 `type` 操作：

```
browser action=snapshot  → 找到标题输入框的 ref（通常是 textbox "请输入文章标题"）
browser action=act request={kind: "click", ref: "<标题ref>"}
browser action=act request={kind: "type", ref: "<标题ref>", text: "你的标题"}
```

#### Step 4: 注入内容（⚠️ 关键步骤）

CSDN 使用 cledit 编辑器（contentEditable），**不能**用以下方法：
- ❌ `browser evaluate` 嵌入长字符串 → 参数长度限制
- ❌ `document.execCommand('insertText')` → 换行符不被 cledit 识别
- ❌ `navigator.clipboard` → headless Chrome 无权限
- ❌ HTTP server + fetch → CORS/混合内容拦截

**✅ 正确方案：使用 `scripts/inject-content.js` 通过 CDP 注入**

```bash
# 前置：确保 ws 模块已安装
cd /root/.openclaw/workspace/skills/csdn-publisher
npm install ws 2>/dev/null

# 注入内容（自动跳过 frontmatter）
node scripts/inject-content.js /tmp/csdn-article-YYYY-MM-DD.md
```

脚本原理：
1. 通过 CDP `/json` 找到 CSDN 编辑器 tab
2. 用 `Runtime.evaluate` + `JSON.stringify(content)` 将内容存入 `window` 变量（绕过长度限制）
3. 用 `editor.textContent = content` + `dispatchEvent('input')` 注入（cledit 兼容）
4. 自动验证注入结果（字数、行数）

**注意：** 运行脚本前必须先用 browser 工具打开 CSDN 编辑器页面。

#### Step 5: 发布

```
browser action=snapshot  → 找到"发布文章"按钮的 ref
browser action=act request={kind: "click", ref: "<发布按钮ref>"}
browser action=snapshot  → 检查发布对话框
  - 确认标签已添加（必填）
  - 文章类型选"原创"
browser action=act request={kind: "click", ref: "<对话框中的发布按钮ref>"}
browser action=snapshot  → 验证"发布成功！正在审核中"
```

---

## 🛡️ 容错与重试策略（v2.1 新增）

浏览器自动化容易因网络、服务中断等原因失败。以下策略确保内容不丢失、发布可重试。

### 原则：先存内容，再发布

**内容创作是昂贵的（搜索+写作），发布是廉价的（浏览器操作）。必须先把内容落盘，再尝试发布。**

### Step 1: 内容落盘（发布前必做）

在尝试浏览器发布之前，**必须**将文章保存到本地文件：

```
/tmp/csdn-article-YYYY-MM-DD.md
```

文件格式：
```markdown
---
title: 文章标题
date: YYYY-MM-DD
tags: [标签1, 标签2]
status: draft | published
csdn_url: (发布成功后回填)
---

文章正文 Markdown 内容...
```

这样即使发布失败，文章内容也不会丢失，可以随时重试。

### Step 2: 浏览器健康检查（发布前必做）

在打开 CSDN 编辑器之前，先确认浏览器服务可用：

```
1. browser action=start profile=openclaw
2. browser action=snapshot profile=openclaw
```

如果 `start` 或 `snapshot` 返回错误：
- **不要继续发布流程**
- 跳到 Step 4（兜底通知）

### Step 3: 失败后自动重试（最多 1 次）

如果发布过程中浏览器操作失败：

```
1. browser action=stop profile=openclaw     # 关闭浏览器
2. 等待 5 秒
3. browser action=start profile=openclaw    # 重启浏览器
4. 重新执行发布流程（从打开编辑器开始）
5. 只重试 1 次，避免无限循环
```

**注意：只重试发布步骤，不重跑内容创作。** 从本地文件 `/tmp/csdn-article-YYYY-MM-DD.md` 读取已保存的内容。

### Step 4: 兜底通知

如果重试后仍然失败：

1. 更新本地文件的 `status: failed`
2. 向用户发送通知，包含：
   - 失败原因
   - 文章标题
   - 提示：文章已保存在 `/tmp/csdn-article-YYYY-MM-DD.md`，可以手动触发重新发布

### 完整发布流程（含容错）

```
内容创作完成
    ↓
保存到 /tmp/csdn-article-YYYY-MM-DD.md  ← 落盘
    ↓
browser start + snapshot  ← 健康检查
    ↓ (失败 → 跳到兜底通知)
打开编辑器 → 注入内容 → 发布
    ↓ (失败)
browser stop → 等 5s → browser start  ← 重试
    ↓
重新打开编辑器 → 注入内容 → 发布
    ↓ (仍然失败)
发送失败通知 + 文章保存路径  ← 兜底
```

---

## 📁 目录结构

```
csdn-publisher/
├── SKILL.md              # 本文档
├── style-guide-cn.md     # 中文写作风格指南
├── examples/             # 示例文章库
│   └── *.md              # 示例文章（YYYY-MM-DD-slug.md）
├── scripts/
│   ├── login.py              # 扫码登录脚本
│   ├── inject-content.js     # CDP 内容注入脚本（核心）
│   ├── notion-query-recent.sh   # 查询最近N天已有新闻
│   └── notion-check-duplicate.sh # 精确去重检查
```

---

## 📚 示例文章管理

### 保存终稿

当用户确认文章为**终稿**时，保存到 `examples/` 目录：

```
examples/YYYY-MM-DD-slug-title.md
```

例如：`examples/2025-02-02-gui-agent-overview.md`

### 示例库维护

- 保持 10-20 篇示例文章
- 超过 20 篇时，询问用户是否删除最旧的 5 篇
- 示例文章用于校准写作风格

---

## 🔗 依赖技能

本技能依赖 **blog-writer** 的写作方法论：

```
skills/blog-writer/
├── SKILL.md              # 写作工作流
├── style-guide.md        # 英文风格指南（参考）
└── *.md                  # 示例文章
```

在撰写文章时，可参考 blog-writer 的：
- 结构模式
- 开头/结尾技巧
- 个人经历融入方式

---

## 踩坑记录

| 坑 | 原因 | 解决方案 |
|----|------|----------|
| Playwright 安装失败 | 国内镜像源没有 | `pip install playwright -i https://pypi.org/simple/` |
| 进程被 kill | OpenClaw 超时机制 | 用 `nohup` 后台运行 |
| 二维码定位失败 | 选择器不对 | 用 `img[src*="qrcode"]` |
| 浏览器启动失败 | 服务器无显示器 | 配置 `headless: true, noSandbox: true` |
| Cookie 注入无效 | domain 设置错误 | 必须设置 `domain=.csdn.net` |
| 标签未添加 | 必填项 | 发布前必须添加至少一个标签 |

---

## Cookie 存储

```
~/.openclaw/workspace/credentials/csdn-cookie.json   # Playwright storage_state 格式
~/.openclaw/workspace/credentials/csdn-cookie.txt    # 简单字符串格式（兼容）
~/.openclaw/workspace/credentials/csdn-qr.png        # 登录二维码截图
```

---

## 登录状态说明 🔑

**browser 工具**使用 Chrome 的 user-data 目录，登录状态是**持久化**的：
- 首次使用需要扫码登录
- 登录后状态自动保存到 `/root/.openclaw/browser/openclaw/user-data`
- 下次启动 browser 工具会自动加载登录状态
- Cookie 过期后（通常几天到几周）需要重新扫码

---

## 自动通知配置 🔔

### 配置 Telegram 通知

```bash
python scripts/login.py setup-notify \
  --bot-token "YOUR_BOT_TOKEN" \
  --chat-id "YOUR_CHAT_ID"
```

### 启动带通知的登录

```bash
nohup python scripts/login.py login --timeout 300 --notify > /tmp/csdn-login.log 2>&1 &
```

---

## Changelog

- **v2.3.0**: 新增新闻去重功能（notion-query-recent.sh + notion-check-duplicate.sh），支持 URL 精确匹配和语义重复判断
- **v2.2.0**: 固化 CDP 内容注入方案（scripts/inject-content.js），替换不可靠的 browser evaluate 方法
- **v2.1.0**: 添加容错与重试策略（内容落盘、健康检查、自动重试、兜底通知）
- **v2.0.0**: 集成 blog-writer 写作方法论，添加中文风格指南，重构工作流
- **v1.3.0**: 添加登录成功自动 Telegram 通知功能
- **v1.2.0**: 完善 Telegram 二维码发送流程，添加完整工作流示例
- **v1.1.0**: 添加扫码登录脚本 `scripts/login.py`
- **v1.0.0**: 初始版本，手动 Cookie 注入
