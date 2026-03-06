# 字体配置指南

本文档详细说明pdf-translate skill的字体配置和中英文字体混排规则。

## 字体优先级

**默认中文字体**：黑体（STHeiti）- 优先用于中文文本
**默认英文字体**：Helvetica - 用于英文关键词和专有名词

## 系统字体配置

### macOS系统字体（优先级从高到低）

1. **STHeiti Light**（黑体）- 默认选择，适合正式文档
2. **PingFang**（苹方）- 备选方案
3. **Helvetica** - 后备字体（也用于英文）

### Windows系统字体

1. **Microsoft YaHei**（微软雅黑）
2. **SimHei**（黑体）
3. **Helvetica** - 英文字体

### Linux系统字体

1. **Droid Sans Fallback**
2. **WenQuanYi Micro Hei**
3. **Helvetica** - 英文字体

## 中英文字体混排规则

在翻译后的PDF中，遵循以下字体使用规则：

| 文本类型 | 使用字体 | 说明 |
|---------|---------|------|
| 中文正文、标题 | 黑体（ChineseFont） | 默认中文字体 |
| 英文关键词 | Helvetica（EnglishFont） | 专业术语、技术名词 |
| 英文专有名词 | Helvetica（EnglishFont） | 人名、地名、公司名 |
| 英文缩写 | Helvetica（EnglishFont） | API、JSON、PDF等 |
| 混合文本 | 按字符自动切换 | 中文用黑体，英文用Helvetica |

### 混排示例

```
Claude Code 是一个强大的 AI 编程助手，支持 RESTful API 和 JSON 格式。
↑ 黑体        ↑ 黑体      ↑ 黑体            ↑ Helvetica  ↑ 黑体   ↑ Helvetica  ↑ 黑体
```

## 代码实现

### 字体注册

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 注册中文字体
pdfmetrics.registerFont(TTFont('ChineseFont', '/System/Library/Fonts/STHeiti Light.ttc', subfontIndex=0))

# 注册英文字体
pdfmetrics.registerFont(TTFont('EnglishFont', '/System/Library/Fonts/Helvetica.ttc', subfontIndex=0))
```

### 字体混排函数

```python
import re

def apply_mixed_font(text, english_font):
    """应用中英文字体混排"""
    # 匹配英文文本的模式（包括常见缩写）
    english_pattern = r'([a-zA-Z0-9_\-\.]+(?:\s+[a-zA-Z0-9_\-\.]+)*)'

    def replace_english(match):
        english_text = match.group(1)
        # 常见技术术语列表
        common_terms = ['API', 'JSON', 'PDF', 'AI', 'URL', 'HTTP', 'REST', 'SQL', 'HTML', 'CSS', 'Claude', 'GitHub', 'SDK']
        if any(term in english_text for term in common_terms):
            return f'<font name="{english_font}">{english_text}</font>'
        # 较长的英文短语（可能是专有名词）
        if len(english_text.split()) > 2 or len(english_text) > 10:
            return f'<font name="{english_font}">{english_text}</font>'
        return english_text

    # 应用字体到英文文本
    result = re.sub(english_pattern, replace_english, text)
    return result
```

### 使用示例

```python
# 在段落中使用混合字体
text = '<font name="ChineseFont">中文文本</font><font name="EnglishFont">English Keywords</font>'
story.append(Paragraph(text, body_style))
```

## 混排规则详细说明

### 自动识别规则

1. **英文缩写**：自动应用英文字体
   - 包括：API、JSON、PDF、AI、URL、HTTP、REST、SQL、HTML、CSS等

2. **专业术语**：保留英文并应用英文字体
   - 包括：Claude、GitHub、SDK等技术名词

3. **长英文短语**：应用英文字体
   - 字符数>10 或 单词数>2 的英文短语

4. **混合文本**：按字符自动切换字体
   - 中文用ChineseFont（黑体）
   - 英文用EnglishFont（Helvetica）

## PDF样式配置

### 颜色方案

| 元素 | 颜色代码 | 用途 |
|------|----------|------|
| 标题 | `#1a1a1a` | 主标题颜色 |
| 一级标题 | `#2563eb` | 蓝色强调 |
| 二级标题 | `#1e40af` | 深蓝色 |
| 三级标题 | `#374151` | 灰色 |
| 正文 | `#374151` | 深灰色 |
| 副标题/页脚 | `#666666` | 浅灰色 |

### 字体大小

| 元素 | 字号 | 行距 |
|------|------|------|
| 主标题 | 24pt | 32pt |
| 副标题 | 14pt | 20pt |
| 一级标题 | 18pt | 24pt |
| 二级标题 | 16pt | 22pt |
| 三级标题 | 14pt | 20pt |
| 正文 | 11pt | 16pt |

### 间距配置

- 页边距：0.75英寸（上下左右）
- 标题后间距：30pt
- 段落后间距：8pt
- 段落前间距：12-20pt（根据标题级别）

---

## 返回主文档：[SKILL.md](../SKILL.md)
