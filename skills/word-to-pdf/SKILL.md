---
name: word-to-pdf
version: 1.0.0
description: >
  Convert Word documents (.docx) to PDF using Python's reportlab library.
  Supports Chinese characters, emojis, and proper formatting preservation.
  Usage: word-to-pdf <input_file> [output_file]
author: OpenClaw User
keywords: [word, pdf, convert, reportlab, chinese, docx]
---

# Word to PDF — Word 文档转 PDF

## 功能

将 Microsoft Word 文档（.docx）转换为 PDF 格式，支持：
- ✅ 中文文本正确显示
- ✅ 保留文档格式和样式
- ✅ 保留 emoji 表情符号
- ✅ 自动处理列表和标题
- ✅ 支持多种字体

## 安装依赖

```bash
pip install reportlab python-docx
```

## 使用方法

### 基本用法

```bash
word-to-pdf input.docx output.pdf
```

### 参数说明

- `input_file` - Word 文档路径（必填）
- `output_file` - PDF 输出路径（可选，默认与输入文件同名）

### 示例

```bash
# 转换文档
word-to-pdf document.docx document.pdf

# 转换到指定路径
word-to-pdf input.docx C:\output\converted.pdf
```

## 工作原理

1. 使用 `python-docx` 读取 Word 文档内容
2. 使用 `reportlab` 生成 PDF 文件
3. 注册中文字体（微软雅黑/黑体）
4. 保留原始文档的段落、标题和列表格式

## 注意事项

- 需要安装 Python 3.6+
- 需要安装 reportlab 和 python-docx 库
- Windows 系统会自动使用微软雅黑字体
- Linux/Mac 系统需要手动指定字体路径

## 故障排除

### 字体问题
如果出现乱码，请确保系统中安装了中文字体：
- Windows: 微软雅黑 (msyh.ttc)
- Linux: 安装 fonts-noto-cjk 或其他中文字体
- Mac: 使用系统默认字体

### 依赖问题
如果提示缺少依赖，运行：
```bash
pip install --upgrade reportlab python-docx
```

## 依赖

- **Python 库**: reportlab, python-docx
- **系统字体**: 中文字体（微软雅黑/黑体）

## 许可

MIT License
