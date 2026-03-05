---
name: ofdreader
description: OFD 文档读取和转换工具。支持从 OFD（Open Fixed-layout Document）文件中提取文本内容，并将其转换为 Markdown 格式。使用此 skill 处理 .ofd 文档时：提取纯文本内容、转换为包含基本格式（标题、段落、表格）的 Markdown、处理中文版式文档。OFD 是中国国家标准版式文档格式，常用于电子公文、证照等场景。
---

# OfdReader

OFD（Open Fixed-layout Document）文档读取和转换工具。从 OFD 文件中提取内容并转换为 Markdown。

## 快速开始

### 提取纯文本

```bash
python scripts/ofd_to_text.py <ofd文件路径>
```

输出到文件：

```bash
python scripts/ofd_to_text.py <ofd文件路径> output.txt
```

### 转换为 Markdown

```bash
python scripts/ofd_to_markdown.py <ofd文件路径>
```

输出到文件：

```bash
python scripts/ofd_to_markdown.py <ofd文件路径> output.md
```

## 工作流程

1. **验证文件**：确认 OFD 文件存在且格式有效（OFD 本质是 ZIP 压缩包）

2. **提取内容**：
   - 解压 OFD 文件
   - 解析内部 XML 结构
   - 提取 TextCode 和 TextContent 元素

3. **格式转换**：
   - **文本模式**：直接拼接所有文本内容
   - **Markdown 模式**：识别段落、标题和表格，转换为对应 Markdown 语法

4. **输出结果**：打印到控制台或写入文件

## 脚本说明

- `scripts/ofd_to_text.py`：提取纯文本，保留所有文字内容但不处理格式
- `scripts/ofd_to_markdown.py`：转换为 Markdown，保留段落、标题和表格结构
- `scripts/install_dependencies.py`：安装可选依赖（核心功能使用标准库）

## OFD 格式说明

OFD 文件结构：
- 根目录包含 `OFD.xml`（文档清单）
- `Doc_0/` 目录包含文档内容
- 内容以 XML 格式存储，使用 `http://www.ofdspec.org/2016` 命名空间

关键元素：
- `TextCode`：文本内容
- `Paragraph`：段落
- `Table`：表格
- `Row`/`Cell`：表格行和单元格

## 限制和注意事项

1. **格式保真度**：OFD 支持复杂的排版布局，脚本仅提取逻辑内容，无法完全保留视觉效果

2. **表格识别**：基于 XML 结构推断表格，复杂表格可能转换不完整

3. **标题检测**：使用启发式规则（短文本、特定模式），可能误判

4. **编码**：OFD 通常使用 UTF-8，脚本自动处理编码

5. **依赖**：核心脚本使用 Python 标准库（zipfile, xml.etree.ElementTree），无需额外依赖

## 使用示例

提取 OFD 文档文本：

```bash
# 用户询问时
python "C:\Users\zhan\.claude\plugins\skills\OfdReader\scripts\ofd_to_text.py" "document.ofd" "extracted.txt"
```

转换为 Markdown：

```bash
python "C:\Users\zhan\.claude\plugins\skills\OfdReader\scripts\ofd_to_markdown.py" "document.ofd" "document.md"
```

## 故障排除

**错误："文件不是有效的 OFD (ZIP) 格式"**
- 文件可能损坏或不是 OFD 格式
- 检查文件扩展名是否为 .ofd

**错误："OFD 文件不存在"**
- 检查文件路径是否正确
- Windows 路径需要用引号括起来

**提取内容为空**
- OFD 文件可能是扫描版图片（无文本层）
- 尝试用其他工具打开确认是否有可提取的文本

**表格格式混乱**
- 复杂表格可能无法完美转换
- 考虑使用 ofd_to_text.py 提取纯文本后手动整理
