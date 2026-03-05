---
name: youtube-summarizer
description: 总结 YouTube 视频内容，自动获取视频信息、搜索相关报道、生成结构化详细总结。支持中英文输出。
---

# YouTube 视频总结技能

当用户要求总结 YouTube 视频时使用此技能。支持事件发布会、技术讲座、新闻等各类视频。

## 使用场景

- 用户分享 YouTube 链接并要求总结
- 用户想了解某个视频的核心内容
- 用户想要详细的视频内容分析

## 工作流程

### Step 1: 提取视频 ID

从 URL 中提取视频 ID（11 位字符）：
- `https://www.youtube.com/watch?v=YZVpUeEvGxs` → `YZVpUeEvGxs`
- `https://m.youtube.com/watch?v=YZVpUeEvGxs` → `YZVpUeEvGxs`
- `https://youtu.be/YZVpUeEvGxs` → `YZVpUeEvGxs`

### Step 2: 获取基本信息

使用 `web_fetch` 获取视频页面信息：
```
https://www.youtube.com/watch?v=<VIDEO_ID>
```

提取：
- 视频标题
- 频道名称
- 发布时间
- 描述（如有）

### Step 3: 搜索相关内容

使用 `web_search` 搜索：
1. 视频标题关键词
2. 频道/发布者名称
3. 主题相关新闻报道
4. 如果是活动/发布会，搜索活动名称

搜索参数建议：
- `count: 8-10`
- `freshness: "pd"` (如果是近期视频)
- 搜索词示例：`"<视频标题> summary announcements keynote`

### Step 4: 获取详细报道

从搜索结果中选择 2-3 个高质量来源（TechCrunch、VentureBeat、官方博客等），
使用 `web_fetch` 获取完整内容，`maxChars: 8000-10000`。

### Step 5: 生成结构化总结

## 输出格式

根据视频类型选择合适的模板：

### 🎬 事件/发布会模板

```markdown
# 📋 [活动名称] 详细总结

**时间：** [日期]
**形式：** [线上/线下/混合]
**主讲人：** [姓名和职位]

---

## 🎯 核心信息

### 背景与动机
[为什么是现在？解决了什么问题？]

---

## 📢 主要发布内容

### 1️⃣ [产品/功能 1]
- 功能描述
- 目标用户
- 关键特性

### 2️⃣ [产品/功能 2]
...

---

## 🏢 合作伙伴（如有）

| 合作方 | 合作内容 |
|--------|----------|
| ... | ... |

---

## 🔐 企业级功能（如适用）

| 功能 | 说明 |
|------|------|
| ... | ... |

---

## 📊 市场影响

- 股市反应
- 竞争格局
- 行业趋势

---

## 🆚 竞争对比

| 公司 | 产品 | 优势 |
|------|------|------|
| ... | ... | ... |

---

## 💡 关键引用

> "[引用内容]"
> — [发言人], [职位]

---

## 📅 上线时间

| 产品 | 时间 |
|------|------|
| ... | ... |

---

## 📌 一句话总结

[核心理念的精炼表达]
```

### 📚 技术讲座模板

```markdown
# 📖 [讲座标题] 总结

**演讲者：** [姓名], [公司/机构]
**时长：** [分钟]
**主题：** [核心主题]

---

## 🎯 核心观点

[3-5 个核心观点]

---

## 📚 主要内容

### 1. [章节 1]
- 要点 1
- 要点 2

### 2. [章节 2]
...

---

## 💡 关键洞察

[深度分析和个人见解]

---

## 🔗 相关资源

- [链接 1]
- [链接 2]

---

## 📌 总结

[一句话总结]
```

---

## 输出语言

- 如果用户用中文提问 → 中文总结
- 如果用户用英文提问 → 英文总结
- 始终保持语言一致性

---

## 质量标准

✅ **必须包含：**
- 视频基本信息（标题、发布者、时间）
- 核心内容总结
- 结构化输出（使用表格、列表等）
- 关键引用（如有）
- 相关链接

✅ **建议包含：**
- 背景上下文
- 市场影响分析
- 竞争对比
- 时间线/上线计划
- 个人洞察

❌ **避免：**
- 过于简短的总结（用户要求"详细"时）
- 遗漏重要信息
- 语言混杂（中英混用）

---

## 示例对话

**用户：** 帮我总结下这个视频 https://www.youtube.com/watch?v=YZVpUeEvGxs

**Agent：** 
1. 提取视频 ID: YZVpUeEvGxs
2. 获取视频页面信息
3. 搜索 "Enterprise Agents Anthropic February 2026"
4. 获取 TechCrunch、CNBC 等报道
5. 生成结构化总结（使用事件发布会模板）

---

## 注意事项

1. **视频不可访问：** 如果视频是私有的或已删除，告知用户并尝试通过标题搜索相关报道
2. **信息不足：** 如果搜索结果有限，基于可用信息提供总结，并说明信息来源
3. **时效性：** 对于旧视频，不需要搜索最新新闻；对于新视频（<7天），使用 `freshness: "pw"` 或 `"pd"`
4. **多次搜索：** 如果第一次搜索结果不理想，尝试不同的关键词组合

---

## 🔧 辅助脚本

### youtube-info.js

**位置：** `scripts/youtube-info.js` (相对于 SKILL.md)

**功能：**
- ✅ 从各种 URL 格式提取视频 ID
- ✅ 获取视频元数据（标题、频道、时长、观看数、描述）
- ✅ 获取字幕/转录文本（支持多语言）
- ✅ 支持带时间戳的字幕输出

**使用方式：**

```bash
# 基本用法 - 获取视频信息
node ~/.openclaw/workspace/skills/youtube-summarizer/scripts/youtube-info.js "https://www.youtube.com/watch?v=YZVpUeEvGxs"

# 获取字幕
node ~/.openclaw/workspace/skills/youtube-summarizer/scripts/youtube-info.js "https://youtu.be/YZVpUeEvGxs" --transcript

# 获取带时间戳的字幕
node ~/.openclaw/workspace/skills/youtube-summarizer/scripts/youtube-info.js YZVpUeEvGxs --transcript-full

# 指定字幕语言
node ~/.openclaw/workspace/skills/youtube-summarizer/scripts/youtube-info.js YZVpUeEvGxs --transcript --lang en

# 输出 JSON 格式（方便程序解析）
node ~/.openclaw/workspace/skills/youtube-summarizer/scripts/youtube-info.js YZVpUeEvGxs --transcript --json
```

**输出示例：**

```
============================================================
📺 The Briefing: Enterprise Agents
============================================================
频道: Anthropic
时长: 45:32
观看: 125,432
链接: https://www.youtube.com/watch?v=YZVpUeEvGxs

📝 字幕:
------------------------------------------------------------
[0:00] Welcome to The Briefing Enterprise Agents event...
[0:15] Today we're excited to announce...
...
```

---

## 扩展能力

此技能可与以下能力结合：
- **EvoMap 同步：** 如果视频中的技术方案有价值，可发布到 EvoMap
- **记忆记录：** 重要视频总结可记录到 `memory/YYYY-MM-DD.md`
- **跨会话引用：** 使用 `MEMORY.md` 保存重要视频的关键信息

---

## 📋 技能加载说明

此技能位于 `~/.openclaw/workspace/skills/youtube-summarizer/`

OpenClaw 会自动扫描以下目录的技能：
- `~/.openclaw/workspace/skills/`
- `~/.openclaw/skills/`

只要 SKILL.md 存在且包含正确的 frontmatter（name + description），技能就会被自动识别。

**触发条件：** 当用户消息包含以下关键词时，AI 会自动读取此技能：
- "总结 youtube 视频"
- "这个视频讲了什么"
- "帮我总结下这个视频"

---

_技能版本: 1.1.0_
_更新时间: 2026-02-25_
_新增: youtube-info.js 辅助脚本_
