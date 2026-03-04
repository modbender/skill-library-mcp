---
name: ocr
description: 光学字符识别 (OCR) 工具，支持从 PDF 和图片中提取中英文文本。适用场景：(1) 从扫描版 PDF 提取文字，(2) 识别图片中的文字，(3) 提取发票、合同等文档的文字内容
---

# OCR 文字识别

本技能使用 PaddleOCR 进行文字识别，支持中文和英文。

## 快速开始

### 基础用法

直接对图片或 PDF 文件进行 OCR 识别：

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(lang='ch')
result = ocr.predict("file_path.jpg")
```

## 依赖安装

首次使用前请安装依赖：

```bash
pip3 install paddlepaddle paddleocr
```

## 输出格式

识别结果返回 JSON 格式，包含：
- `rec_texts`: 识别出的文字列表
- `rec_scores`: 每段文字的置信度分数

## 典型使用场景

1. **PDF 扫描件**：先用 PyMuPDF 提取图片，再进行 OCR
2. **图片文字识别**：直接对图片进行 OCR
3. **多页 PDF**：逐页处理

## 脚本

常用脚本位于 `scripts/` 目录下。
