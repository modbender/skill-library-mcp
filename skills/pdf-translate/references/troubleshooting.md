# 故障排除指南

本文档提供pdf-translate skill常见问题的解决方案。

## 目录或特殊格式内容丢失

### 问题现象
生成的PDF缺少原文档的目录（TOC）或其他特殊格式内容。

### 问题原因
1. PDF中的目录包含特殊格式字符（如省略号……、页码对齐）
2. 通用Markdown解析器无法正确处理这些特殊格式
3. 特殊格式内容在解析过程中被忽略或跳过

### 解决方案

#### 方案A：显式目录处理（推荐）

```python
# 1. 识别目录内容（通常在文档开头，有规律格式）
# 2. 创建显式的目录数据结构
toc_items = [
    ("分类", "标题", "页码"),
    ("前言", "从辅助到协作", "3"),
    ("基础趋势", "构造性变革", "4"),
]

# 3. 手动构建目录内容
for category, title, page in toc_items:
    if category:  # 有分类的目录项
        story.append(Paragraph(f"<b>{category}</b>：{title} ……………… {page}", body_style))
    else:  # 无分类的目录项
        story.append(Paragraph(f"{title} ……………… {page}", body_style))
```

#### 方案B：保留原始格式

```python
# 1. 直接从提取的文本中识别目录部分
# 2. 使用原始文本构建Paragraph，不进行格式转换
story.append(Paragraph(raw_toc_text, body_style))
```

### 预防措施
- 翻译前先查看PDF提取的文本内容，确认是否有特殊格式
- 对于包含目录的文档，优先使用显式处理方式
- 保留原文档的结构层次（使用标题样式区分不同级别）

## 中文字体不显示

### 问题现象
生成的PDF中文显示为方块或乱码。

### 解决方案

1. **检查系统字体**
   ```bash
   # macOS
   ls /System/Library/Fonts/STHeiti*.ttc

   # Windows
   ls C:/Windows/Fonts/msyh.ttc

   # Linux
   ls /usr/share/fonts/truetype/droid/
   ```

2. **使用自定义字体路径**
   ```bash
   python3 translate_pdf.py input.pdf -o output.pdf --font /path/to/font.ttf
   ```

3. **确保字体文件包含中文字符集**
   - 字体文件必须是TTF或TTC格式
   - 必须包含中文字符集（UTF-8编码支持）

## PDF内容提取不完整

### 问题现象
某些PDF内容无法提取或提取不完整。

### 可能原因
- PDF包含图片或扫描内容
- PDF使用了特殊编码
- PDF有密码保护

### 解决方案

#### 扫描PDF处理

```bash
# 安装OCR依赖
pip3 install pytesseract pdf2image

# 使用OCR提取文本
```

#### 密码保护PDF

```python
import pypdf

reader = PdfReader("encrypted.pdf")
writer = PdfWriter()

# 解密PDF
if reader.is_encrypted:
    reader.decrypt("password")

for page in reader.pages:
    writer.add_page(page)

with open("decrypted.pdf", "wb") as output:
    writer.write(output)
```

## 内存不足

### 问题现象
处理大型PDF时出现内存不足错误。

### 解决方案

```python
# 分页处理，每处理N页保存一次
def process_large_pdf(pdf_path, output_path, chunk_size=10):
    """分块处理大型PDF"""
    # 处理逻辑
    pass
```

## HTML标签嵌套错误

### 问题现象
PDF生成时出现 `Parse error: saw </para> instead of expected </b>` 错误。

### 问题原因
粗体标签使用简单字符串替换导致HTML标签嵌套错误：
```python
# 错误方式
text.replace('**', '<b>').replace('**', '</b>')  # 可能产生 <b><b>text</b></b>
```

### 解决方案

使用正则表达式精确匹配：

```python
import re

# 正确方式
processed_content = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
```

## 粗体文本不显示

### 问题现象
翻译内容中的 `**粗体文本**` 在PDF中没有显示为粗体。

### 解决方案

确保在将Markdown转换为PDF内容时正确处理粗体标签：

```python
def markdown_to_pdf_content(markdown_text):
    """将Markdown文本转换为PDF内容"""
    lines = markdown_text.split('\n')
    content = []

    for line in lines:
        line = line.rstrip()
        if not line:
            continue

        # 识别标题
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

# 处理粗体标签
for item_type, item_content in content:
    if item_type == 'paragraph':
        # 使用正则表达式处理粗体
        processed = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', item_content)
        story.append(Paragraph(processed, body_style))
```

## 其他常见问题

### 依赖包未安装

```bash
# 安装所有必需的依赖
pip3 install pdfplumber reportlab pypdf

# 或使用conda
conda install -c conda-forge pdfplumber reportlab
```

### 文件路径错误

确保使用绝对路径或相对于当前工作目录的正确路径：

```python
import os
from pathlib import Path

# 使用pathlib处理路径
input_path = Path("input.pdf").resolve()
if not input_path.exists():
    raise FileNotFoundError(f"Input file not found: {input_path}")
```

---

## 返回主文档：[SKILL.md](../SKILL.md)
