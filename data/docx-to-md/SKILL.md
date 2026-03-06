---
name: docx-to-md
description: 将Word文档(.docx)转换为Markdown格式并提取图片。使用此技能当用户需要:(1)将Word文档转换为Markdown格式,(2)从Word文档中提取图片,(3)同时完成文档格式转换和图片提取任务。
---

# docx-to-md

将Word文档(.docx)转换为Markdown格式,并提取文档中的图片到指定目录。

## 使用方法

运行脚本进行转换:
```python
import sys
sys.path.insert(0, '<skill目录>/scripts')
from docx_to_md import docx_to_md

docx_to_md('输入文件.docx', '输出目录')
```

或在命令行运行(需手动处理参数转义):
```bash
python <skill路径>/scripts/docx_to_md.py "文件.docx"
```

## 参数

- `input_file`: Word文档路径(.docx)
- `output_dir`: 输出目录(可选,默认创建同名_output文件夹)

## 输出

- `*.md`: 转换后的Markdown文件
- `image_*.png/jpg/gif`: 提取的图片文件

## 转换规则

| Word格式 | Markdown |
|----------|----------|
| 标题1 | # 标题 |
| 标题2 | ## 标题 |
| 标题3 | ### 标题 |
| 标题4 | #### 标题 |
| 无序列表 | - 内容 |
| 有序列表 | 1. 内容 |
| 表格 | Markdown表格 |
| 图片 | ![](图片) |

## 依赖

- Python 3.7+
- python-docx

```bash
pip install python-docx
```
