---
name: pdf-process-mineru
description: 基于本地 MinerU 的 PDF 文档解析工具，支持将 PDF 转换为 Markdown、JSON 等机器可读格式。
---

## 工具列表

### 1. pdf_to_markdown

将 PDF 文档转换为 Markdown 格式，保留文档结构、公式、表格和图片。

**描述**: 使用 MinerU 解析 PDF 文档，输出为 Markdown 格式，支持 OCR、公式识别、表格提取等功能。

**参数**:
- `file_path` (string, required): PDF 文件的绝对路径
- `output_dir` (string, required): 输出目录的绝对路径
- `backend` (string, optional): 解析后端，可选值：`hybrid-auto-engine`(默认)、`pipeline`、`vlm-auto-engine`
- `language` (string, optional): OCR 语言代码，如 `en`(英语)、`ch`(中文)、`ja`(日语) 等，默认为自动检测
- `enable_formula` (boolean, optional): 是否启用公式识别，默认为 true
- `enable_table` (boolean, optional): 是否启用表格提取，默认为 true
- `start_page` (integer, optional): 起始页码（从 0 开始），默认为 0
- `end_page` (integer, optional): 结束页码（从 0 开始），默认为 -1 表示解析所有页面

**返回值**:
```json
{
  "success": true,
  "output_path": "/path/to/output",
  "markdown_content": "转换后的 Markdown 内容...",
  "images": ["图片路径列表"],
  "tables": ["表格信息列表"],
  "formula_count": 10
}
```

**示例**:
```bash
python .claude/skills/pdf-process/script/pdf_parser.py \
  '{"name": "pdf_to_markdown", "arguments": {"file_path": "/path/to/document.pdf", "output_dir": "/path/to/output"}}'

# 使用特定后端
python .claude/skills/pdf-process/script/pdf_parser.py \
  '{"name": "pdf_to_markdown", "arguments": {"file_path": "/path/to/document.pdf", "output_dir": "/path/to/output", "backend": "pipeline"}}'

# 解析特定页面
python .claude/skills/pdf-process/script/pdf_parser.py \
  '{"name": "pdf_to_markdown", "arguments": {"file_path": "/path/to/document.pdf", "output_dir": "/path/to/output", "start_page": 0, "end_page": 5}}'
```

---

### 2. pdf_to_json

将 PDF 文档转换为 JSON 格式，包含详细的布局和结构信息。

**描述**: 使用 MinerU 解析 PDF 文档，输出为 JSON 格式，包含文本块、图片、表格、公式等结构化信息。

**参数**:
- `file_path` (string, required): PDF 文件的绝对路径
- `output_dir` (string, required): 输出目录的绝对路径
- `backend` (string, optional): 解析后端，可选值：`hybrid-auto-engine`(默认)、`pipeline`、`vlm-auto-engine`
- `language` (string, optional): OCR 语言代码，如 `en`(英语)、`ch`(中文)、`ja`(日语) 等，默认为自动检测
- `enable_formula` (boolean, optional): 是否启用公式识别，默认为 true
- `enable_table` (boolean, optional): 是否启用表格提取，默认为 true
- `start_page` (integer, optional): 起始页码（从 0 开始），默认为 0
- `end_page` (integer, optional): 结束页码（从 0 开始），默认为 -1 表示解析所有页面

**返回值**:
```json
{
  "success": true,
  "output_path": "/path/to/output.json",
  "pages": [
    {
      "page_no": 0,
      "page_size": [595, 842],
      "blocks": [
        {
          "type": "text",
          "text": "文本内容",
          "bbox": [x, y, x, y]
        }
      ],
      "images": [],
      "tables": [],
      "formulas": []
    }
  ],
  "metadata": {
    "total_pages": 10,
    "author": "作者",
    "title": "标题"
  }
}
```

**示例**:
```bash
python .claude/skills/pdf-process/script/pdf_parser.py \
  '{"name": "pdf_to_json", "arguments": {"file_path": "/path/to/document.pdf", "output_dir": "/path/to/output"}}'

# 使用特定后端和语言
python .claude/skills/pdf-process/script/pdf_parser.py \
  '{"name": "pdf_to_json", "arguments": {"file_path": "/path/to/document.pdf", "output_dir": "/path/to/output", "backend": "hybrid-auto-engine", "language": "ch"}}'
```

---

## 安装说明

### 1. 安装 MinerU

```bash
# 更新 pip 并安装 uv
pip install --upgrade pip
pip install uv

# 安装 MinerU（包含所有功能）
uv pip install -U "mineru[all]"
```

### 2. 验证安装

```bash
# 检查 MinerU 是否安装成功
mineru --version

# 测试基本功能
mineru --help
```

### 3. 系统要求

- **Python 版本**: 3.10-3.13
- **操作系统**: Linux / Windows / macOS 14.0+
- **内存**:
  - 使用 `pipeline` 后端：最少 16GB，推荐 32GB+
  - 使用 `hybrid/vlm` 后端：最少 16GB，推荐 32GB+
- **磁盘空间**: 最少 20GB（SSD 推荐）
- **GPU**（可选）:
  - `pipeline` 后端：支持纯 CPU
  - `hybrid/vlm` 后端：需要 NVIDIA GPU（Volta 架构及以上）或 Apple Silicon

## 使用场景

1. **学术论文解析**: 提取公式、表格、图片等结构化内容
2. **技术文档转换**: 将 PDF 文档转换为 Markdown 以便于版本控制和在线发布
3. **OCR 处理**: 处理扫描 PDF 和乱码 PDF
4. **多语言文档**: 支持 109 种语言的 OCR 识别
5. **批量处理**: 批量转换多个 PDF 文档

## 后端选择建议

- **hybrid-auto-engine** (默认): 平衡准确率和速度，适合大多数场景
- **pipeline**: 适合纯 CPU 环境，兼容性最好
- **vlm-auto-engine**: 最高准确率，需要 GPU 加速

## 注意事项

1. **文件路径**: 所有路径必须是绝对路径
2. **输出目录**: 会自动创建不存在的目录
3. **性能**: 使用 GPU 可显著提升解析速度
4. **页码**: 页码从 0 开始计数
5. **内存**: 处理大型文档时可能占用较多内存

## 故障排除

### 常见问题

1. **安装失败**:
   - 确保使用 Python 3.10-3.13
   - Windows 上仅支持 Python 3.10-3.12（ray 不支持 3.13）
   - 使用 `uv pip install` 可以解决大部分依赖冲突

2. **内存不足**:
   - 使用 `pipeline` 后端
   - 限制解析页数：`start_page` 和 `end_page`
   - 减少虚拟显存分配

3. **解析速度慢**:
   - 启用 GPU 加速
   - 使用 `hybrid-auto-engine` 后端
   - 禁用不需要的功能（公式、表格）

4. **OCR 准确率低**:
   - 指定正确的文档语言
   - 确保后端支持 OCR（使用 `pipeline` 或 `hybrid-*`）

## 相关资源

- MinerU 官方文档: https://opendatalab.github.io/MinerU/
- MinerU GitHub: https://github.com/opendatalab/MinerU
- 在线体验: https://mineru.net/
