# Markdown to PDF 技能

将 Markdown 文件转换为精美的 PDF 文档，完美支持中文、代码高亮、自定义样式。

## 特性

- ✅ **完美中文支持**（使用 Noto Sans CJK 字体）
- ✅ **自动安装依赖**（首次运行时自动安装）
- ✅ **专业排版样式**（代码高亮、表格美化）
- ✅ **轻量级**（无需 LaTeX，仅 Python）
- ✅ **跨平台**（支持 Linux、macOS、Windows）

## 快速开始

```bash
# 转换 Markdown 为 PDF
bash /root/.openclaw/workspace/skills/md2pdf/scripts/convert-weasyprint.sh input.md

# 指定输出文件名
bash /root/.openclaw/workspace/skills/md2pdf/scripts/convert-weasyprint.sh input.md output.pdf
```

## 依赖

- Python 3.x
- markdown
- weasyprint

依赖会在首次运行时自动安装。

## 作者

franklu0819-lang

## 许可证

MIT
