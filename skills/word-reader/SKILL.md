---
name: word-reader
description: |
  读取 Word 文档（.docx 和 .doc 格式）并提取文本内容。支持文档解析、表格提取、图片处理等功能。使用当用户需要分析 Word 文档内容、提取文本信息或批量处理文档时。
homepage: https://python-docx.readthedocs.io/
metadata:
  {
    "openclaw":
      {
        "emoji": "📄",
        "requires": { "bins": ["python3"], "env": ["PYTHONPATH"] },
        "install":
          [
            {
              "id": "pip",
              "kind": "pip",
              "package": "python-docx",
              "bins": ["python3"],
              "label": "Install python-docx (pip)",
            },
            {
              "id": "system",
              "kind": "system",
              "command": "sudo apt-get install antiword -y",
              "label": "Install antiword for .doc support (optional)",
              "platform": "linux-debian"
            }
          ],
      },
  }
---

# Word 文档读取器

使用 Python 解析 Word 文档，提取文本内容和结构化信息。

## 支持的功能

- **文档文本提取** - 提取段落、标题、页眉页脚内容
- **表格解析** - 读取表格数据并转换为结构化格式
- **图片处理** - 提取文档中的图片信息
- **元数据获取** - 读取文档属性（作者、标题、创建时间等）
- **批量处理** - 支持处理多个文档

## 用法

### 基本文本提取

```bash
python3 {baseDir}/scripts/read_word.py <文件路径>
```

### 指定输出格式

```bash
# JSON 输出
python3 {baseDir}/scripts/read_word.py <文件路径> --format json

# 纯文本输出
python3 {baseDir}/scripts/read_word.py <文件路径> --format text

# Markdown 格式
python3 {baseDir}/scripts/read_word.py <文件路径> --format markdown
```

### 提取特定内容

```bash
# 只提取文本
python3 {baseDir}/scripts/read_word.py <文件路径> --extract text

# 提取表格数据
python3 {baseDir}/scripts/read_word.py <文件路径> --extract tables

# 获取文档元数据
python3 {baseDir}/scripts/read_word.py <文件路径> --extract metadata
```

### 批量处理

```bash
# 处理目录下所有 .docx 文件
python3 {baseDir}/scripts/read_word.py <目录路径> --batch
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--format` | 输出格式（json/text/markdown） | text |
| `--extract` | 提取内容类型（text/tables/images/metadata/all） | all |
| `--batch` | 批量处理模式 | false |
| `--output` | 输出文件路径 | stdout |
| `--encoding` | 文本编码（utf-8/gb2312） | utf-8 |

## 输出格式

### JSON 格式

```json
{
  "metadata": {
    "title": "文档标题",
    "author": "作者姓名",
    "created": "2024-01-01T10:00:00",
    "modified": "2024-01-01T12:00:00"
  },
  "text": "文档全文内容...",
  "tables": [
    [
      ["表头1", "表头2"],
      ["行1列1", "行1列2"],
      ["行2列1", "行2列2"]
    ]
  ],
  "images": [
    {
      "filename": "image1.png",
      "description": "图片描述",
      "size": "1024x768"
    }
  ]
}
```

### Markdown 格式

```markdown
# 文档标题

**作者**：作者姓名  
**创建时间**：2024-01-01 10:00:00

## 正文内容

这是文档的正文内容...

### 表格示例

| 表头1 | 表头2 |
|-------|-------|
| 行1列1 | 行1列2 |
| 行2列1 | 行2列2 |

![图片描述](image1.png)

## 图片列表

1. **image1.png** (1024x768) - 图片描述
```

## 错误处理

- 文件不存在：显示错误信息并退出
- 格式不支持：提示支持的文件类型
- 权限问题：提示文件访问权限
- 编码问题：尝试自动检测编码

## 示例场景

### 1. 查看项目文档

```bash
python3 {baseDir}/scripts/read_word.py 项目需求.docx --format markdown
```

### 2. 提取会议记录

```bash
python3 {baseDir}/scripts/read_word.py 会议记录.docx --extract text
```

### 3. 批量处理文档

```bash
python3 {baseDir}/scripts/read_word.py ./文档目录 --batch --format json --output results.json
```

## 注意事项

- 支持 .docx 格式（Office 2007+）
- .doc 格式需要额外依赖（如 antiword）
- 大文档处理可能需要较长时间
- 图片提取仅获取元数据，不包含实际图片数据
- 表格格式可能需要手动调整

## 故障排除

### 常见问题

1. **ModuleNotFoundError**: 确保已安装 python-docx
2. **PermissionError**: 检查文件读取权限
3. **UnicodeDecodeError**: 尝试不同的编码格式

### 安装依赖

```bash
pip3 install python-docx
```

对于 .doc 格式支持：
```bash
# Ubuntu/Debian
sudo apt-get install antiword

# macOS
brew install antiword
```

## 高级功能

### 自定义样式处理

脚本会自动处理以下文档元素：
- 标题级别（H1-H6）
- 段落样式
- 列表项目
- 页眉页脚
- 文档属性

### 性能优化

- 大文件流式处理
- 内存使用优化
- 进度显示（批量模式）