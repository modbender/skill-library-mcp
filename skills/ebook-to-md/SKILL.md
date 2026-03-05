---
name: ebook-to-md
description: Convert PDF/PNG/JPEG/MOBI/EPUB to Markdown. Uses Baidu OCR only. Use when 扫描PDF转Markdown、pdf ocr、图像识别、电子书转Markdown、ebook to markdown.
---

# ebook_to_md Skill

将 PDF、图片、MOBI、EPUB 转为 Markdown。仅使用百度 OCR。

## 输入格式

- **PDF**：扫描版/图像型 PDF
- **PNG/JPEG**：单张图片
- **MOBI/EPUB**：需安装 Calibre，先转 PDF 再处理

图片 OCR 输出会自动添加 Markdown 分段：首行若为短标题则转为 `##`，对话段落前插入空行。

## 输出格式

仅输出 **Markdown**（.md）。

## 参数

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|--------------|
| input_path | string | yes | - | 文档路径（pdf/png/jpeg/mobi/epub）或 base64 图片 |
| output_path | string | no | - | 输出文件路径 |
| ocr_backend | string | no | "baidu" | 保留参数，仅支持百度 |
| inline_images | bool | no | true | 图片是否 base64 内联 |

## 快速开始

```bash
# PDF 转 Markdown（百度 OCR）
python scripts/ebook_to_md.py --input_path=./scanned.pdf
# 图片转 Markdown
python scripts/ebook_to_md.py --input_path=./screenshot.png
# 指定输出路径
python scripts/ebook_to_md.py --input_path=./report.pdf --output_path=./report.md
```

## 依赖

### Python

```bash
pip install requests
```

### 系统

- **Calibre**（mobi/epub）：`brew install calibre`
- **百度 OCR**：设置 `BAIDU_OCR_API_KEY`、`BAIDU_OCR_SECRET_KEY`

## 使用示例

### 百度 OCR（默认）

```python
from skills.ebook_to_md import main
main(input_path='./report.pdf', output_path='./report.md')
main(input_path='./image.png')  # 图片识别
```


### MOBI/EPUB（需 Calibre）

```python
main(input_path='./book.epub', output_path='./book.md')
main(input_path='./book.mobi', output_path='./book.md')
```

## 返回格式

成功：返回字符串，含预览；若指定 output_path 则写入文件。
失败：返回 "错误: ..."

## 相关

- **pdf_to_markdown**：原生文本 PDF 转换（docling）
