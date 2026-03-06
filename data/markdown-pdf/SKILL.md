---
name: md2pdf
description: Markdown 转 PDF 技能。将 Markdown 文件转换为精美的 PDF 文档，完美支持中文、代码高亮、自定义样式。
metadata: {
  "openclaw": {
    "requires": {
      "bins": ["python3"],
      "python": ["markdown", "weasyprint"]
    }
  }
}

---

# Markdown 转 PDF 技能

将 Markdown 文件转换为精美的 PDF 文档，支持中文、代码高亮、自定义样式。

## ⭐ 推荐方案：WeasyPrint

**完美支持中文，无需 LaTeX，自动处理依赖！**

### 快速开始

```bash
# 转换 Markdown 为 PDF（推荐）
bash /root/.openclaw/workspace/skills/md2pdf/scripts/convert-weasyprint.sh input.md

# 指定输出文件名
bash /root/.openclaw/workspace/skills/md2pdf/scripts/convert-weasyprint.sh input.md output.pdf
```

### 优点

- ✅ **完美中文支持**（使用 Noto Sans CJK 字体）
- ✅ **自动安装依赖**（首次运行时自动安装）
- ✅ **专业排版样式**（代码高亮、表格美化）
- ✅ **轻量级**（无需 LaTeX，仅 Python）
- ✅ **跨平台**（支持 Linux、macOS、Windows）

## 功能特性

- ✅ Markdown 转 PDF
- ✅ **完美中文支持**（无乱码）
- ✅ 代码语法高亮（深色主题）
- ✅ 专业表格样式（斑马纹、圆角）
- ✅ 多级标题样式
- ✅ 引用块美化
- ✅ 列表、链接、图片支持
- ✅ 自定义 CSS 样式

## 使用方法

### 方法 1：WeasyPrint（推荐）⭐

**适合场景：** 需要完美中文显示、专业排版

```bash
# 使用 Bash 脚本（自动处理依赖）
bash scripts/convert-weasyprint.sh document.md

# 指定输出文件
bash scripts/convert-weasyprint.sh document.md output.pdf

# 直接使用 Python 脚本
python3 scripts/convert-weasyprint.py input.md output.pdf
```

### 方法 2：Pandoc（备选）

**适合场景：** 已安装 LaTeX 环境

```bash
bash scripts/convert.sh input.md output.pdf
```

### 方法 3：简化 HTML

**适合场景：** 需要在浏览器中打印

```bash
bash scripts/convert-simple.sh input.md output.pdf
```

## 脚本说明

### convert-weasyprint.sh ⭐

**推荐使用** - WeasyPrint 方案，完美支持中文。

**特性：**
- 自动检测并安装 Python 依赖（markdown、weasyprint）
- 自动检测并安装中文字体（google-noto-sans-cjk-fonts）
- 专业的 CSS 样式（代码高亮、表格美化）
- 完整的错误处理

**用法：**
```bash
bash scripts/convert-weasyprint.sh <输入.md> [输出.pdf]
```

**参数：**
- `输入.md` (必需): Markdown 文件路径
- `输出.pdf` (可选): PDF 输出路径（默认：输入文件名.pdf）

**示例：**
```bash
# 转换单个文件
bash scripts/convert-weasyprint.sh README.md

# 指定输出路径
bash scripts/convert-weasyprint.sh README.md /tmp/readup.pdf

# 批量转换
for md in *.md; do
    bash scripts/convert-weasyprint.sh "$md"
done
```

### convert-weasyprint.py

Python 转换脚本，被 `convert-weasyprint.sh` 调用，也可直接使用。

**用法：**
```bash
python3 scripts/convert-weasyprint.py <输入.md> [输出.pdf]
```

**功能：**
- Markdown 解析（支持表格、代码块、列表）
- HTML 生成
- CSS 样式应用
- PDF 输出

### convert.sh

Pandoc 传统方案（需要 LaTeX）。

**用法：**
```bash
bash scripts/convert.sh <输入.md> [输出.pdf]
```

**前置要求：**
- `pandoc`
- `xelatex` (LaTeX)
- 中文字体

### convert-simple.sh

简化版，生成 HTML 供浏览器打印。

**用法：**
```bash
bash scripts/convert-simple.sh <输入.md> [输出.pdf]
```

## 技术实现

### WeasyPrint 方案

使用 Python 的 WeasyPrint 库进行转换：

```python
# 1. Markdown → HTML
html_content = markdown.markdown(
    md_content,
    extensions=['tables', 'fenced_code', 'nl2br', 'sane_lists']
)

# 2. HTML + CSS → PDF
HTML(string=html_content).write_pdf(
    output_file,
    stylesheets=[CSS(string='...')]
)
```

**CSS 样式特性：**
- 中文字体：Noto Sans CJK SC
- 代码块：深色主题（#2c3e50 背景）
- 表格：蓝色表头 + 斑马纹
- 引用块：左边框 + 浅灰背景
- 响应式设计

### Pandoc 方案

使用 pandoc 的 LaTeX 引擎：

```bash
pandoc input.md -o output.pdf \
  --pdf-engine=xelatex \
  -V CJKmainfont="Noto Sans CJK SC" \
  -V geometry:margin=2cm
```

## 支持的 Markdown 特性

- ✅ 标题（h1-h6）
- ✅ 段落和换行
- ✅ 列表（有序、无序）
- ✅ 代码块（支持语法高亮）
- ✅ 表格
- ✅ 链接和图片
- ✅ 引用块
- ✅ 水平线
- ✅ 粗体和斜体
- ✅ 自动链接

## 依赖管理

### Python 依赖

```bash
# 自动安装（首次运行时）
python3 -m pip install markdown weasyprint
```

### 中文字体

```bash
# 自动安装（首次运行时）
yum install -y google-noto-sans-cjk-fonts
```

### Pandoc（可选）

```bash
# CentOS/RHEL
yum install -y pandoc

# Ubuntu/Debian
apt-get install -y pandoc
```

## 故障排查

### 问题 1：中文显示为方块或乱码

**解决方案（WeasyPrint）：**
```bash
# 安装中文字体
yum install -y google-noto-sans-cjk-fonts

# 验证字体
fc-list | grep "Noto Sans CJK"
```

**解决方案（Pandoc）：**
```bash
# 安装中文字体
yum install -y google-noto-sans-cjk-sc-fonts

# 使用 xelatex
pandoc input.md -o output.pdf --pdf-engine=xelatex -V CJKmainfont="Noto Sans CJK SC"
```

### 问题 2：Python 模块未找到

**解决方案：**
```bash
# 安装 Python 依赖
python3 -m pip install markdown weasyprint

# 验证安装
python3 -c "import markdown, weasyprint; print('OK')"
```

### 问题 3：字体渲染问题

**解决方案：**
```bash
# 清除字体缓存
fc-cache -fv

# 重新安装字体
yum reinstall -y google-noto-sans-cjk-fonts
```

### 问题 4：PDF 文件过大

**原因：** WeasyPrint 会嵌入完整字体

**解决方案：**
- 使用子集化字体（需要额外工具）
- 或使用在线字体（需要网络连接）
- 或接受文件大小（通常 500KB-2MB）

## 完整示例

### 示例 1：基本转换

```bash
# 创建测试文件
cat > test.md << 'EOF'
# 测试文档

这是中文测试文档。

## 功能列表

- 支持 Markdown
- 代码高亮
- 表格样式

| 列1 | 列2 |
|-----|-----|
| A   | B   |

\`\`\`python
print("Hello, World!")
\`\`\`
EOF

# 转换为 PDF
bash scripts/convert-weasyprint.sh test.md
```

### 示例 2：批量转换

```bash
# 转换目录下所有 Markdown 文件
for file in *.md; do
    echo "转换: $file"
    bash scripts/convert-weasyprint.sh "$file"
done
```

### 示例 3：集成到脚本

```bash
#!/bin/bash
# 自动转换脚本

INPUT_DIR="/path/to/markdown/files"
OUTPUT_DIR="/path/to/pdf/output"

mkdir -p "$OUTPUT_DIR"

for md in "$INPUT_DIR"/*.md; do
    output="$OUTPUT_DIR/$(basename "$md" .md).pdf"
    bash /root/.openclaw/workspace/skills/md2pdf/scripts/convert-weasyprint.sh "$md" "$output"
done
```

## 样式自定义

### 修改 CSS 样式

编辑 `scripts/convert-weasyprint.py` 中的 CSS 字符串：

```python
css = CSS(string='''
    /* 修改字体大小 */
    body {
        font-size: 12pt;  /* 默认 11pt */
    }

    /* 修改主色调 */
    h1, h2 {
        color: #e74c3c;  /* 改为红色 */
    }

    /* 修改代码块背景 */
    pre {
        background-color: #34495e;  /* 深色主题 */
    }
''')
```

### 自定义模板

修改 HTML 模板以添加页眉、页脚等：

```python
full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
</head>
<body>
    <header>
        <h1>我的公司</h1>
    </header>
    {html_content}
    <footer>
        <p>机密文档</p>
    </footer>
</body>
</html>
"""
```

## 性能优化

### 加速转换

1. **使用缓存：** 保存字体缓存
2. **批量处理：** 合并多个 Markdown 为一个 PDF
3. **并行处理：** 使用 GNU parallel

```bash
# 并行转换
ls *.md | parallel -j 4 bash scripts/convert-weasyprint.sh {}
```

## 相关技能

- `feishu-doc`: 飞书文档操作
- `feishu-drive`: 飞书云文件管理
- `md2pdf`: Markdown 转 PDF（本技能）

## 常见问题

**Q: WeasyPrint 和 Pandoc 哪个更好？**

A: 推荐使用 WeasyPrint：
- ✅ 完美中文支持（无需配置）
- ✅ 自动安装依赖
- ✅ 轻量级（无需 LaTeX）
- ✅ 跨平台

Pandoc 适合已有 LaTeX 环境的场景。

**Q: 可以在 Docker 中使用吗？**

A: 可以，但需要安装字体：

```dockerfile
FROM python:3.11
RUN pip install markdown weasyprint
RUN apt-get update && apt-get install -y fonts-noto-cjk
```

**Q: 支持数学公式吗？**

A: WeasyPrint 不直接支持，可以：
1. 使用 MathJax（需要 JavaScript）
2. 或使用 Pandoc + LaTeX 方案

## 更新日志

### v2.0 (2026-02-16)

- ✨ 新增 WeasyPrint 方案（推荐）
- ✨ 完美中文支持
- ✨ 自动依赖安装
- ✨ 专业 CSS 样式
- ✨ 代码高亮深色主题
- 🐛 修复中文乱码问题

### v1.0

- ⚠️ 初始版本（Pandoc 方案）
- ⚠️ 需要手动安装 LaTeX
- ⚠️ 中文支持有限

## 许可证

MIT License

---

**作者**: 小美 ⭐
**最后更新**: 2026-02-16
**推荐方案**: WeasyPrint (convert-weasyprint.sh)
