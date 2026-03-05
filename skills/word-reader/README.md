# Word Reader 技能

## 📋 概述

Word Reader 是一个强大的 Word 文档读取工具，支持 .docx 和 .doc 格式，能够提取文本内容、表格数据、文档元信息，并提供多种输出格式。

## ✨ 功能特性

- ✅ **文本提取** - 提取文档中的所有段落文本
- ✅ **表格解析** - 解析表格数据并转换为结构化格式
- ✅ **元数据获取** - 读取文档属性（标题、作者、创建时间等）
- ✅ **图片信息** - 获取文档中图片的基本信息
- ✅ **多格式支持** - 支持 .docx 和 .doc 格式
- ✅ **多种输出** - JSON、Text、Markdown 格式
- ✅ **批量处理** - 支持处理整个目录的文档
- ✅ **自动安装** - 一键安装所有依赖

## 🚀 安装

### 自动安装（推荐）
```bash
cd word-reader/
./install.sh
```

### 手动安装
```bash
# 安装 Python 依赖
pip3 install python-docx --break-system-packages

# 安装系统依赖（可选，用于 .doc 格式支持）
# Ubuntu/Debian
sudo apt-get install antiword

# macOS
brew install antiword

# 设置执行权限
chmod +x scripts/read_word.py
```

## 📖 使用方法

### 基本用法
```bash
# 读取文档并输出为文本格式
python3 scripts/read_word.py 文档.docx

# 输出为 JSON 格式
python3 scripts/read_word.py 文档.docx --format json

# 输出为 Markdown 格式
python3 scripts/read_word.py 文档.docx --format markdown

# 只提取文本内容
python3 scripts/read_word.py 文档.docx --extract text
```

### 批量处理
```bash
# 批量处理目录下所有 Word 文档
python3 scripts/read_word.py ./文档目录 --batch

# 批量处理并保存为 JSON 文件
python3 scripts/read_word.py ./文档目录 --batch --format json --output results.json
```

### 高级用法
```bash
# 将结果保存到文件
python3 scripts/read_word.py 文档.docx --format markdown --output output.md

# 提取表格数据
python3 scripts/read_word.py 文档.docx --extract tables

# 获取文档元数据
python3 scripts/read_word.py 文档.docx --extract metadata
```

## 📊 输出示例

### JSON 格式输出
```json
{
  "metadata": {
    "filename": "测试文档.docx",
    "size": "2048 bytes",
    "created": "2024-01-01T10:00:00",
    "modified": "2024-01-01T12:00:00",
    "title": "测试文档",
    "author": "测试用户"
  },
  "format": "docx",
  "text": "这是文档的正文内容...",
  "tables": [
    {
      "id": 1,
      "rows": 3,
      "columns": 3,
      "data": [
        ["表头1", "表头2", "表头3"],
        ["数据1", "数据2", "数据3"],
        ["数据4", "数据5", "数据6"]
      ]
    }
  ],
  "images": [
    {
      "id": "rId1",
      "filename": "image1.png",
      "size": "1024 bytes"
    }
  ]
}
```

### Markdown 格式输出
```markdown
# 测试文档.docx

**标题**：测试文档  
**作者**：测试用户  
**文件大小**：2048 bytes  
**创建时间**：2024-01-01T10:00:00  
**修改时间**：2024-01-01T12:00:00  

## 正文内容

这是文档的正文内容...

## 表格内容

### 表格 1 (3行 x 3列)

| 表头1 | 表头2 | 表头3 |
|-------|-------|-------|
| 数据1 | 数据2 | 数据3 |
| 数据4 | 数据5 | 数据6 |
```

## 🎯 应用场景

- **文档内容分析** - 快速查看 Word 文档内容
- **批量处理** - 处理大量文档
- **内容提取** - 提取特定信息
- **格式转换** - 转换为其他格式
- **自动化工作流** - 集成到文档处理系统

## 📤 发布到 ClawHub

要将此技能发布到 ClawHub，请参考 `PUBLISHING.md` 文件。

## 🔧 故障排除

### 常见问题
1. **ModuleNotFoundError**: 确保已安装 python-docx
2. **PermissionError**: 检查文件读取权限
3. **FileNotFoundError**: 确认文件路径正确
4. **编码问题**: 尝试使用 `--encoding gb2312` 参数

### 性能优化
- 大文档处理时建议使用 `--format json` 以获得更好的性能
- 批量模式下建议使用 `--output` 参数将结果保存到文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个技能！

## 📄 许可证

MIT License