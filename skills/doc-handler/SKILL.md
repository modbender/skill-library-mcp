---
name: doc-handler
description: 读取和编辑 Word、PDF、Excel 文档。使用 python-docx、pdfplumber、openpyxl
read_when:
  - 读取文档
  - 编辑文档
  - 解析 PDF
  - 处理 Excel
---

# doc-handler - 文档处理工具

## 功能

| 功能 | 命令 |
|------|------|
| 读取 Word | `python3 -m doc_handler read docx 文件` |
| 读取 PDF | `python3 -m doc_handler read pdf 文件` |
| 读取 Excel | `python3 -m doc_handler read xlsx 文件` |
| 写入 Word | `python3 -m doc_handler write docx 文件 "内容"` |

## 使用示例

```bash
# 读取 Word 文档
python3 -c "from docx import Document; d = Document('file.docx'); print('\\n'.join([p.text for p in d.paragraphs]))"

# 读取 PDF
python3 -c "import pdfplumber; with pdfplumber.open('file.pdf') as pdf: print(pdf.pages[0].extract_text())"

# 读取 Excel
python3 -c "import pandas; df = pandas.read_excel('file.xlsx'); print(df)"
```

## 依赖

- python-docx
- pdfplumber
- openpyxl
- pandas
