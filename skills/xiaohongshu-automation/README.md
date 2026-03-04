# 小红书自动化工具集

**作者：赛博螃蟹Clawdbob**  
赛博螃蟹の小红书Skill | OpenClaw自动发帖+评论回复

让你的AI助手（OpenClaw）自动管理小红书账号：

• ✅ **自动发布长文笔记**（通过创作者中心）

• ✅ **自动读取和回复评论**（带防prompt injection）

• ✅ **关键词验证机制**，不会回错人

• ✅ **stealth模式**，模拟真人浏览器行为

## 🦀 **使用约定**

> **让AI助手创造真诚、高质量的内容，而不是用广告或低质量信息淹没人类的信息流。**

这是一个专为**OpenClaw**设计的小红书内容发布和评论管理自动化工具集合。

## 🎯 **推荐使用方式**

**建议通过Claude Code等CLI工具将整个项目打包安装到OpenClaw中使用**，这样可以获得：
- 🚀 **开箱即用**：无需手动配置stealth.min.js等组件
- 🔧 **智能集成**：与OpenClaw的AI工作流无缝对接
- 📚 **完整文档**：包含详细的使用说明和最佳实践
- 🛡️ **安全可靠**：内置反检测机制和错误处理

## 项目结构

```
├── xiaohongshu-publish/     # 发布相关工具
│   ├── SKILL.md            # 发布技能说明文档
│   └── publish_long_text.py # 长文发布脚本
│
└── xiaohongshu-reply/       # 评论回复工具
    ├── SKILL.md            # 回复技能说明文档
    ├── check_comments.py   # 主要的评论检查和回复工具
    ├── reply_fixed.py      # 修复版回复工具（备用）
    ├── generate_replies.py # 回复模板生成器
    └── fetch_latest.py     # 最新评论获取工具
```

## 功能说明

### 📝 发布工具 (xiaohongshu-publish)

- **publish_long_text.py**: 自动发布小红书长文内容
  - 支持标题和正文内容输入
  - 自动排版和发布
  - 命令行参数支持

### 💬 评论管理工具 (xiaohongshu-reply)

- **check_comments.py**: 主要的评论管理工具
  - 自动获取最新评论
  - 批量回复指定评论
  - 支持自定义回复模板

- **reply_fixed.py**: 备用的评论回复工具
  - 提供额外的回复功能
  - 包含错误处理和调试功能

- **generate_replies.py**: 回复模板生成器
  - 生成标准化的回复模板
  - 便于批量回复管理

- **fetch_latest.py**: 评论获取工具
  - 专门用于获取最新评论
  - 保存评论数据和截图

## 环境配置

### 🔥 **OpenClaw集成 (推荐)**

本工具集专为**OpenClaw AI工作流**设计，建议通过以下方式集成：

#### **Claude Code CLI 安装 (推荐)**
```bash
# 1. 将获得的项目文件包解压到本地目录
# 2. 通过Claude Code安装本地项目到OpenClaw
claude-code install ./xiaohongshu-skill

# 3. 根据Claude Code或者OpenClaw的指示，配置所有依赖和路径（包括小红书Cookie）
# 4. 直接通过AI对话使用："帮我发布一条小红书长文" 或 "检查小红书评论"
```

#### **手动集成到OpenClaw**
```bash
# 1. 将项目文件包复制到OpenClaw技能目录
cp -r ./xiaohongshu-skill ~/.openclaw/skills/

# 2. 安装依赖
cd ~/.openclaw/skills/xiaohongshu-skill
pip install playwright
playwright install chromium

# 3. 配置cookie文件（见下方说明）
```

### 📋 **独立使用配置**

如果需要独立使用（不通过OpenClaw），请配置以下文件：

### 必需文件

1. **Cookie配置**: `~/.openclaw/secrets/xiaohongshu.json`
   ```json
   {
     "a1": "your_a1_cookie",
     "web_session": "your_web_session",
     "webId": "your_webId",
     "websectiga": "your_websectiga"
   }
   ```

2. **Stealth脚本**: `stealth.min.js` ✅ **已内置**
   - 用于绕过反爬虫检测
   - 来源: [puppeteer-extra](https://github.com/berstend/puppeteer-extra) (MIT License)
   - 项目中已包含，无需额外配置

### 依赖安装

```bash
pip install playwright
playwright install chromium
```

## 使用方法

### 🤖 **OpenClaw AI对话使用 (推荐)**

安装到OpenClaw后，支持多种使用方式：

#### **💬 即时AI对话**
```
用户："帮我发布一条小红书长文，标题是'AI时代的思考'，内容是..."
AI：自动调用发布工具，处理整个发布流程

用户："检查我的小红书评论，有新评论就回复一下"
AI：自动获取评论，生成合适回复，经用户确认后发送

用户："生成10条小红书评论的标准回复模板"
AI：调用回复生成器，创建个性化回复模板
```

**🚀 AI工作流优势**：
- 🧠 **智能理解**：AI理解你的需求，自动选择合适的工具
- 🔄 **上下文记忆**：记住你的偏好和历史操作
- 🛡️ **安全审核**：AI会先预览内容，经确认后执行
- 📊 **结果反馈**：实时报告操作状态和结果
- ⚡ **扩展能力**：可以此为基础，让OpenClaw助手安排cron job等自动化任务

### 🖥️ **命令行直接使用 (高级用户)**

如需直接使用CLI命令：

### 发布长文

```bash
# 基本使用
python xiaohongshu-publish/publish_long_text.py --title "文章标题" --content "文章内容"

# 显示浏览器窗口（调试用）
python xiaohongshu-publish/publish_long_text.py --title "标题" --content "内容" --visible
```

### 管理评论

```bash
# 检查并回复评论
python xiaohongshu-reply/check_comments.py

# 获取最新评论
python xiaohongshu-reply/fetch_latest.py

# 生成回复模板
python xiaohongshu-reply/generate_replies.py
```

## 注意事项

1. **Cookie安全**: 请妥善保管cookie文件，不要泄露给他人
2. **使用频率**: 建议合理控制使用频率，避免被平台检测
3. **内容合规**: 确保发布和回复的内容符合平台规范
4. **路径配置**: 首次使用前请确保所有必需文件路径正确配置

## 技术特性

### 🚀 **OpenClaw集成优势**
- **AI驱动操作**：通过自然语言对话控制所有功能
- **上下文智能**：AI记住用户偏好和操作历史
- **自动化工作流**：复杂任务一句话完成
- **安全审核机制**：AI预览内容，用户确认后执行
- **扩展性强**：可基于此技能让OpenClaw安排cron job等自动化任务

### 🔧 **核心技术特性**
- **基于 Playwright** 的稳定自动化操作
- **内置反检测机制** (stealth.min.js)
- **支持无头模式和可视化调试**
- **通用路径配置，适配不同用户环境**
- **智能模板化回复，便于批量管理**
- **完善的错误处理和日志记录**
- **开箱即用，零配置启动**

## 第三方组件说明

### stealth.min.js

项目中包含的 `stealth.min.js` 文件用于浏览器反爬虫检测绕过：

- **来源**: [berstend/puppeteer-extra](https://github.com/berstend/puppeteer-extra)
- **生成工具**: `extract-stealth-evasions`
- **许可证**: MIT License
- **生成时间**: 2026-02-02
- **大小**: ~200KB (压缩版)

**功能说明**:
- 隐藏 `navigator.webdriver` 标识
- 模拟完整的Chrome浏览器环境
- 补全插件和MIME类型信息
- 伪装硬件和WebGL信息
- 修补权限和通知API行为

详细信息请参阅: [`STEALTH_INFO.md`](./STEALTH_INFO.md)

## 📦 **Claude Code CLI 集成说明**

### 项目结构
```
xiaohongshu-skill/
├── README.md                    # 主要说明文档
├── STEALTH_INFO.md             # stealth.min.js技术文档
├── stealth.min.js              # 反检测脚本 (内置)
├── xiaohongshu-publish/        # 发布模块
│   ├── SKILL.md                # 发布技能文档
│   └── publish_long_text.py    # 长文发布脚本
└── xiaohongshu-reply/          # 评论管理模块
    ├── SKILL.md                # 回复技能文档
    ├── check_comments.py       # 评论检查和回复
    ├── reply_fixed.py          # 备用回复工具
    ├── generate_replies.py     # 回复模板生成
    └── fetch_latest.py         # 评论获取工具
```

### 安装要求
- **项目文件包** (通过网盘获取)
- **Python 3.8+**
- **playwright** (Claude Code自动安装)
- **chromium** (通过 playwright install 安装)
- **小红书cookie配置** (用户提供)

### 获取和安装流程
1. 📦 **获取文件包**：从提供的网盘链接下载项目文件
2. 📁 **解压到本地**：解压到任意本地目录
3. 🔧 **Claude Code安装**：`claude-code install ./xiaohongshu-skill`

### 自动配置说明
安装时Claude Code会自动：
1. 📦 **安装Python依赖**：`pip install playwright`
2. 🌐 **下载浏览器**：`playwright install chromium`
3. 📁 **创建配置目录**：`~/.openclaw/secrets/`
4. 🔧 **配置技能路径**：自动设置所有相对路径
5. 🛡️ **验证stealth.min.js**：确保反检测脚本可用

### Cookie配置指南
用户需要手动配置 `~/.openclaw/secrets/xiaohongshu.json`：
```json
{
  "a1": "从浏览器开发者工具获取",
  "web_session": "从浏览器开发者工具获取",
  "webId": "从浏览器开发者工具获取",
  "websectiga": "从浏览器开发者工具获取",
  "access-token-creator.xiaohongshu.com": "发布功能需要",
  "galaxy_creator_session_id": "发布功能需要",
  "x-user-id-creator.xiaohongshu.com": "发布功能需要"
}
```

### AI对话命令示例
安装完成后，用户可以通过以下方式与AI交互：

```
# 发布内容
"发布小红书长文：标题'AI编程助手'，内容包括..."

# 管理评论
"检查小红书新评论，如有技术问题就回复"

# 生成模板
"创建10个小红书评论回复模板，风格要专业友好"

# 批量操作
"回复所有包含'bug'关键词的评论，解释这是正常现象"
```

**💡 扩展提示**：你还可以基于这些基础功能，让OpenClaw助手帮你安排cron job定时任务，实现自动化发布和回复。

## 许可证

本项目仅供学习和研究使用，请遵守相关平台的使用条款。

**第三方组件许可**:
- `stealth.min.js`: MIT License (来自 puppeteer-extra 项目)
