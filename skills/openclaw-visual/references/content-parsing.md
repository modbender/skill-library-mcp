# 内容解析规则

## 内容类型识别

### 1. 单条消息/文本

**识别特征:**
- 用户直接提供文本内容
- 触发词: "帮我把...做成图片", "生成...的图片", "排版..."
- 文本长度通常 < 500 字

**示例:**
```
用户: "帮我把这句话做成图片: 行动是治愈恐惧的良药"
→ 类型: 单条消息
→ 内容: "行动是治愈恐惧的良药"
→ 推荐模板: quote-card
```

### 2. PhoenixClaw 日志

**识别特征:**
- 用户提及 "日志", "日记", "journal"
- 提及具体日期: "今天", "昨天", "2026-02-01"
- 文件路径: `~/PhoenixClaw/Journal/daily/YYYY-MM-DD.md`

**解析步骤:**
1. 确定日期 (默认今天)
2. 读取 markdown 文件
3. 解析 frontmatter (YAML)
4. 提取 sections (Highlights, Moments, Reflections, Growth)
5. 转换为模板变量

**示例:**
```markdown
---
date: 2026-02-01
weekday: Saturday
type: daily
mood: 😊
energy: high
---

# 🌅 2026-02-01 — Saturday

## ✨ Highlights
- 修好了困扰两天的 bug
- 拍到了美丽的日落

## 🖼️ Moments
...
```

### 3. 聊天记录

**识别特征:**
- 用户提及 "对话", "聊天", "今天聊了什么"
- 触发词: "总结今天的对话", "生成聊天摘要图"

**解析步骤:**
1. 确定日期范围
2. 扫描 `~/.openclaw/sessions/*.jsonl`
3. 按时间戳过滤消息
4. 提取关键话题和决策
5. 统计情绪/能量趋势

### 4. 引用/金句

**识别特征:**
- 文本包含引号 "..."
- 包含作者名或 "——"
- 哲理性质的内容

**示例:**
```
"行动是治愈恐惧的良药" —— 威廉·詹姆斯
→ 类型: 金句
→ 引用: "行动是治愈恐惧的良药"
→ 作者: "威廉·詹姆斯"
→ 推荐模板: quote-card
```

## 内容解析函数

### parsePhoenixClawJournal(filePath)

解析 PhoenixClaw 日志文件，返回结构化数据。

**输入:**
- `filePath`: 日志文件路径

**输出:**
```typescript
{
  date: string;
  weekday: string;
  mood: string;
  energy: string;
  highlights: string[];
  moments: Array<{
    time: string;
    description: string;
    imageUrl?: string;
  }>;
  reflections: string;
  growth: string;
}
```

### parseChatSessions(dateRange)

解析聊天记录，提取关键信息。

**输入:**
- `dateRange`: 日期范围 {start: Date, end: Date}

**输出:**
```typescript
{
  period: string;
  dateRange: string;
  totalMessages: number;
  topics: string[];
  decisions: string[];
  moodTrend: Array<{date: string, mood: string}>;
  energyTrend: Array<{date: string, energy: number}>;
  keyMoments: Array<{
    time: string;
    content: string;
    type: string;
  }>;
}
```

### extractQuote(text)

从文本中提取引用内容。

**输入:**
- `text`: 原始文本

**输出:**
```typescript
{
  quote: string;
  author?: string;
  isQuote: boolean;
}
```

## 模板匹配逻辑

```typescript
function selectTemplate(contentType, content, userIntent) {
  // 用户明确指定模板
  if (userIntent.template) {
    return userIntent.template;
  }

  // 根据内容类型选择
  switch (contentType) {
    case 'single-text':
      if (content.length < 100 && extractQuote(content).isQuote) {
        return 'quote-card';
      }
      return 'quote-card'; // 默认

    case 'photo-moment':
      return 'moment-card';

    case 'phoenixclaw-journal':
      if (userIntent.style === 'social') {
        return 'social-share';
      }
      return 'daily-journal';

    case 'chat-summary':
      if (content.stats || content.timeline) {
        return 'dashboard';
      }
      return 'social-share';

    default:
      return 'quote-card';
  }
}
```

## 变量填充规则

### 文本截断

- **quote-card**: 引用内容最多 200 字，超出显示 "..."
- **moment-card**: 描述最多 150 字
- **daily-journal**: 每个 section 最多显示 5 条
- **social-share**: 标题最多 50 字，副标题最多 100 字

### Emoji 处理

- 保留原始 emoji
- 根据 mood/energy 自动添加相关 emoji
- 避免连续超过 3 个 emoji

### 日期格式化

- **标准格式**: YYYY-MM-DD
- **显示格式**: 2026年2月1日 / February 1, 2026
- **星期**: 根据用户语言显示 (周一/Monday)

### 图片 URL 处理

- 必须是公开可访问的 URL
- 支持格式: jpg, png, webp
- 建议使用 CDN 链接
- 本地图片需要先上传

## 多语言支持

### 语言检测

1. 检测用户输入语言
2. 根据语言选择字体:
   - 中文: Noto Sans SC / LXGW WenKai
   - 英文: Inter / Playfair Display
   - 日文: Noto Sans JP
   - 韩文: Noto Sans KR

### 文本方向

- 默认: LTR (从左到右)
- 阿拉伯语/希伯来语: RTL (从右到左)

## 错误处理

### 文件不存在

```
错误: 找不到 2026-02-01 的日志文件
建议: "该日期暂无日志记录，请检查日期或使用其他内容生成图片。"
```

### 内容为空

```
错误: 解析后的内容为空
建议: "未找到有效内容，请提供更多详细信息。"
```

### 图片 URL 无效

```
错误: 图片 URL 无法访问
建议: "请提供公开可访问的图片链接，或先上传图片。"
```
