# 完整PDF生成示例

本文档提供完整的端到端PDF生成示例，包含Markdown解析、目录生成、中英文字体混排等功能。

## 完整工作流示例

以下是一个完整的端到端PDF生成脚本，展示如何从Markdown文本生成包含封面、目录、正文的PDF文档。

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import os
import re

# 1. 注册字体
def register_fonts():
    """注册中英文字体"""
    chinese_font_paths = [
        '/System/Library/Fonts/STHeiti Light.ttc',  # macOS 黑体
        '/System/Library/Fonts/PingFang.ttc',       # macOS 苹方
        'C:/Windows/Fonts/msyh.ttc',                # Windows 微软雅黑
        'C:/Windows/Fonts/simhei.ttf',              # Windows 黑体
    ]

    chinese_font = None
    for font_path in chinese_font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('ChineseFont', font_path, subfontIndex=0))
                chinese_font = 'ChineseFont'
                break
            except:
                continue

    if not chinese_font:
        chinese_font = 'Helvetica'

    try:
        pdfmetrics.registerFont(TTFont('EnglishFont', '/System/Library/Fonts/Helvetica.ttc', subfontIndex=0))
        english_font = 'EnglishFont'
    except:
        english_font = 'Helvetica'

    return chinese_font, english_font

# 2. Markdown解析函数
def markdown_to_pdf_content(markdown_text):
    """将Markdown文本转换为PDF内容结构"""
    lines = markdown_text.split('\n')
    content = []

    for line in lines:
        line = line.rstrip()
        if not line:
            continue

        if line.startswith('## '):
            content.append(('heading1', line[3:].strip()))
        elif line.startswith('### '):
            content.append(('heading2', line[4:].strip()))
        elif line.startswith('---'):
            content.append(('pagebreak', ''))
        else:
            if line.strip():
                content.append(('paragraph', line.strip()))

    return content

# 3. 中英文字体混排
def apply_mixed_font(text, english_font):
    """应用中英文字体混排"""
    english_pattern = r'([a-zA-Z0-9_\-\.]+(?:\s+[a-zA-Z0-9_\-\.]+)*)'

    def replace_english(match):
        english_text = match.group(1)
        common_terms = ['API', 'JSON', 'PDF', 'AI', 'Claude', 'REST']
        if any(term in english_text for term in common_terms):
            return f'<font name="{english_font}">{english_text}</font>'
        if len(english_text.split()) > 2 or len(english_text) > 10:
            return f'<font name="{english_font}">{english_text}</font>'
        return english_text

    return re.sub(english_pattern, replace_english, text)

# 4. 完整PDF生成
def create_complete_pdf(markdown_content, output_path):
    """生成包含封面、目录、正文的完整PDF"""

    # 注册字体
    chinese_font, english_font = register_fonts()

    # 创建文档
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            leftMargin=0.75*inch, rightMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)

    # 定义样式
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
        fontName=chinese_font, fontSize=24,
        textColor=HexColor('#1a1a1a'), spaceAfter=30,
        alignment=TA_CENTER, leading=32)

    heading1_style = ParagraphStyle('CustomHeading1', parent=styles['Heading1'],
        fontName=chinese_font, fontSize=18,
        textColor=HexColor('#2563eb'), spaceAfter=12,
        spaceBefore=20, leading=24)

    body_style = ParagraphStyle('CustomBody', parent=styles['BodyText'],
        fontName=chinese_font, fontSize=11,
        textColor=HexColor('#374151'), spaceAfter=8,
        leading=16, alignment=TA_JUSTIFY)

    story = []

    # 封面页
    story.append(Paragraph("文档标题", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("副标题", ParagraphStyle('CustomSubtitle', parent=styles['Normal'],
        fontName=chinese_font, fontSize=14, textColor=HexColor('#666666'),
        alignment=TA_CENTER, leading=20)))
    story.append(PageBreak())

    # 目录页（使用显式数据结构）
    story.append(Paragraph("目录", heading1_style))
    story.append(Spacer(1, 20))

    toc_items = [
        ("", "第一章", "3"),
        ("", "第二章", "5"),
        ("", "第三章", "7"),
    ]

    for category, title, page in toc_items:
        if category:
            story.append(Paragraph(f"<b>{category}</b>：{title} ………………………… {page}", body_style))
        else:
            story.append(Paragraph(f"{title} ………………………… {page}", body_style))
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    # 解析Markdown内容
    content = markdown_to_pdf_content(markdown_content)

    for item_type, item_content in content:
        if item_type == 'heading1':
            story.append(Paragraph(apply_mixed_font(item_content, english_font), heading1_style))
        elif item_type == 'heading2':
            story.append(Paragraph(apply_mixed_font(item_content, english_font),
                ParagraphStyle('CustomHeading2', parent=styles['Heading2'],
                fontName=chinese_font, fontSize=16, textColor=HexColor('#1e40af'),
                spaceAfter=10, spaceBefore=15, leading=22)))
        elif item_type == 'paragraph':
            # 正确处理粗体标签（使用正则表达式避免嵌套错误）
            processed = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', item_content)
            story.append(Paragraph(apply_mixed_font(processed, english_font), body_style))
        elif item_type == 'pagebreak':
            story.append(PageBreak())

    # 生成PDF
    doc.build(story)
    print(f"✅ PDF生成成功：{output_path}")

# 使用示例
FULL_TRANSLATION = '''# 文档标题

## 第一章

这是**粗体文本**和普通文本的混合。

### 1.1 小节

更多内容...

---

## 第二章

继续内容...
'''

create_complete_pdf(FULL_TRANSLATION, "output.pdf")
```

## 关键要点总结

### 1. Markdown解析
使用`markdown_to_pdf_content()`函数按行解析，返回结构化内容：
```python
content = [('heading1', '标题'), ('paragraph', '内容'), ...]
```

### 2. 粗体处理
使用正则表达式`\*\*([^*]+)\*\*`避免HTML标签嵌套错误：
```python
processed = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
```

### 3. 字体混排
使用`apply_mixed_font()`自动识别英文关键词：
```python
mixed_text = apply_mixed_font("Claude Code 支持 RESTful API", english_font)
```

### 4. 目录结构
使用显式数据结构确保目录不会丢失：
```python
toc_items = [("分类", "标题", "页码"), ...]
```

### 5. 完整流程
封面 → 目录 → 正文

## 使用场景

此完整工作流适用于：
- 需要生成包含目录的专业文档
- 需要中英文字体混排的技术文档
- 需要从Markdown生成格式化PDF

## 更多示例

参见主脚本：`scripts/generate_complete_pdf.py`

---

## 返回主文档：[SKILL.md](../SKILL.md)
