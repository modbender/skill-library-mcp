---
name: Image OCR Reader
description: 从图片中提取文字内容的技能，支持中文和英文识别。
---

# Image OCR Reader

从图片中提取文字内容的技能，支持中文和英文识别。

## 功能

- 从图片文件中提取文字 (OCR)
- 支持中文、英文混合识别
- 使用 Tesseract OCR 引擎
- 兼容 jpg、png、jpeg 等常见图片格式

## 依赖

- Python 3
- tesseract-ocr
- pytesseract
- Pillow

## 安装

### 1. 安装系统依赖

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# CentOS/RHEL
sudo yum install tesseract
```

### 2. 安装 Python 依赖

```bash
pip install pytesseract Pillow
```

## 使用方法

### 命令行

```bash
python3 image_ocr_reader.py --file /path/to/image.jpg
```

### Python API

```python
from image_ocr_reader import extract_text

text = extract_text("/path/to/image.jpg")
print(text)
```

## 输出示例

输入一张包含文字的图片，输出提取的文字内容。

---

## 积分

- 版本: 1.0.0
- 作者: OpenClaw
- 许可证: MIT
