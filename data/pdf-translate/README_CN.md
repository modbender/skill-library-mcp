# PDF 翻译 Skill

> 学术级 PDF 翻译工具 — 基于 Claude 的高质量英译中 Skill，输出排版精美的中文文档。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skill Version](https://img.shields.io/badge/version-4.0.0-blue.svg)](SKILL.md)
[![Claude Compatible](https://img.shields.io/badge/Claude-compatible-green.svg)](https://claude.ai/)
[![Cursor Compatible](https://img.shields.io/badge/Cursor-compatible-green.svg)](https://cursor.com/)

**[English Documentation](README.md)**

## 功能特点

- **Markdown-first 工作流** — 先翻译为结构化 Markdown，再生成 PDF，排版保真度最高
- **专业排版** — 深色代码块、交替行色表格、蓝色边框引用块、多级标题样式
- **完整 CJK 支持** — 苹方 / 黑体 / 雅黑 / Noto Sans CJK 字体 fallback 链，代码块中文也不乱码
- **双格式输出** — 同时生成 `.md`（可编辑）和 `.pdf`（可分享）
- **学术级翻译** — 三步工作流（重写 → 诊断 → 润色），杜绝翻译腔
- **跨平台** — macOS、Windows、Linux 自动字体检测

## 快速开始

### 安装依赖

```bash
# macOS
brew install pango
pip3 install pdfplumber markdown weasyprint

# Linux（Debian/Ubuntu）
sudo apt install libpango1.0-dev
pip3 install pdfplumber markdown weasyprint

# Windows
pip3 install pdfplumber markdown weasyprint
```

### 在 Claude / Cursor 中使用

1. 将 skill 链接到 skills 目录：

   ```bash
   # Claude Code
   ln -s /path/to/pdf-translate ~/.claude/skills/pdf-translate

   # Cursor
   ln -s /path/to/pdf-translate .cursor/skills/pdf-translate
   ```

2. 用自然语言请求翻译：

   ```
   翻译这个PDF：report.pdf
   Translate this PDF: report.pdf
   ```

3. Skill 自动完成：
   - 使用 `pdfplumber` 提取 PDF 文本
   - 逐章节翻译为中文 Markdown
   - 通过 `md2pdf.py` 生成排版精美的 PDF

### 独立使用

```bash
# 直接将 Markdown 文件转为 PDF
python3 scripts/md2pdf.py input.md output.pdf
```

## 工作流程

```
PDF ──► 提取文本（pdfplumber）
         │
         ▼
     分析文档结构（标题、代码、表格、列表）
         │
         ▼
     逐章节翻译 → 中文 Markdown
         │
         ▼
     输出 .md 文件
         │
         ▼
     md2pdf.py（markdown → HTML → weasyprint → PDF）
         │
         ▼
     排版精美的 .pdf 文档
```

### 翻译质量标准

遵循思果、余光中的"翻译即重写"理念：

- **化形合为意合** — 拆分长句，重组语序，符合中文表达习惯
- **化被动为主动** — 避免"被"字滥用
- **化抽象为具体** — 名词转动词，让表达更生动
- **精简冗余** — 消除欧化表达，保持中文简洁

## 项目结构

```
pdf-translate/
├── SKILL.md                       # 核心 Skill 定义（v4.0.0）
├── README.md                      # 英文文档
├── README_CN.md                   # 中文文档（本文件）
├── CHANGELOG.md                   # 版本变更日志
├── VERSION_HISTORY.md             # 详细版本历史
├── LICENSE                        # MIT 许可证
├── CONTRIBUTING.md                # 贡献指南
├── requirements.txt               # Python 依赖
├── .gitignore
├── scripts/
│   ├── md2pdf.py                  # Markdown → PDF 转换器（推荐）
│   ├── translate_pdf.py           # 旧版：基础 PDF 提取（reportlab）
│   └── generate_complete_pdf.py   # 旧版：完整工作流（reportlab）
└── references/
    ├── translation-standards.md   # 翻译标准与三步工作流
    ├── font-configuration.md      # 字体配置与混排规则
    ├── troubleshooting.md         # 故障排除指南
    └── complete-example.md        # 完整代码示例
```

## PDF 输出效果

生成的 PDF 包含以下排版特性：

| 特性 | 说明 |
|------|------|
| 页面布局 | A4 版面，自动分页，底部居中页码 |
| 标题 | 四级层级，蓝色强调边线 |
| 代码块 | 深色背景（#1e293b），支持中文注释 |
| 表格 | 交替行色，完整边框 |
| 引用块 | 蓝色左边框 + 浅色背景 |
| 列表 | 嵌套有序 / 无序列表 |
| 正文排版 | 中文 10.5pt，两端对齐，行高 1.8 |

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| 代码块中文乱码 | 使用 `md2pdf.py`（v4.0 已修复 CJK 字体 fallback） |
| macOS 报 `libgobject` 找不到 | `DYLD_FALLBACK_LIBRARY_PATH="/opt/homebrew/lib" python3 scripts/md2pdf.py` |
| 中文字体不显示 | 确认系统安装了苹方或黑体字体 |
| Markdown 格式错乱 | 检查块级元素（标题、列表、表格、代码块）前后是否有空行 |

## 版本历史

- **v4.0.0**（2026-02-21）— Markdown-first 工作流；weasyprint 引擎；修复代码块中文乱码
- **v3.0.0**（2026-02-02）— 重大重构：渐进式披露，references 文档拆分
- **v2.3.0** — Markdown 解析优化，中英文字体混排
- **v2.2.0** — 目录处理修复，特殊格式支持
- **v2.1.0** — 黑体默认字体，中英混排
- **v2.0.0** — 学术级翻译标准
- **v1.0.0**（2026-01-30）— 初始版本

完整变更记录见 [CHANGELOG.md](CHANGELOG.md)。

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

1. Fork 本仓库
2. 创建特性分支（`git checkout -b feature/amazing-feature`）
3. 提交更改（`git commit -m 'Add amazing feature'`）
4. 推送到分支（`git push origin feature/amazing-feature`）
5. 创建 Pull Request

## 许可证

本项目基于 MIT 许可证开源 — 详见 [LICENSE](LICENSE) 文件。

---

**由 Claude + 人类协作构建**
