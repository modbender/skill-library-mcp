# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- 支持更多语言对（英语→日语、英语→韩语等）
- OCR功能支持扫描版PDF
- 批量翻译工具
- GUI界面

## [4.0.0] - 2026-02-21

### Added
- 新增 `scripts/md2pdf.py` — 基于 weasyprint 的 Markdown → PDF 转换脚本
- Markdown-first 工作流：先翻译为结构化 Markdown，再生成 PDF
- 完整 CJK 字体 fallback（苹方 / 黑体 / 雅黑 / Noto Sans CJK）
- 专业排版样式：深色代码块、交替行色表格、蓝色引用边框
- A4 版面 + 自动分页 + 页码
- macOS `DYLD_FALLBACK_LIBRARY_PATH` 自动检测（脚本内置）
- 同时兼容 Cursor Skills 和 Claude Code Skills

### Changed
- PDF 引擎从 `reportlab` 切换为 `weasyprint`（支持完整 HTML/CSS 排版）
- SKILL.md 重写为 v4.0.0，采用 6 步工作流
- 依赖新增 `markdown` 和 `weasyprint`，系统需安装 `pango`
- 旧版脚本 `translate_pdf.py`、`generate_complete_pdf.py` 保留但标记为旧版

### Fixed
- 修复代码块中文乱码（`<code>` / `<pre>` 添加 CJK 字体 fallback）
- 修复列表、表格、引用块渲染失败问题（reportlab 不支持，weasyprint 原生支持）
- 修复 macOS 上 weasyprint 找不到 `libgobject` 的问题

## [3.0.0] - 2026-02-02

### Added
- 完整重构skill结构，符合skill-creator标准
- 新增VERSION_HISTORY.md文档（285行完整版本历史）
- 新增完整的Markdown到PDF转换函数
- 新增中英文字体自动混排功能
- 新增显式目录处理机制
- 新增4个reference文档（707行详细内容）
- 新增完整工作流脚本`generate_complete_pdf.py`
- 新增MIT开源许可证
- 新增README.md、CONTRIBUTING.md等开源文档

### Changed
- SKILL.md从500+行精简到202行核心内容
- 翻译标准从SKILL.md拆分到references/translation-standards.md
- 字体配置从SKILL.md拆分到references/font-configuration.md
- 故障排除从SKILL.md拆分到references/troubleshooting.md
- 完整示例从SKILL.md拆分到references/complete-example.md
- 改进description字段，更精确的trigger说明

### Fixed
- 修复粗体标签嵌套导致的HTML解析错误
- 修复目录在生成PDF时丢失的问题
- 优化Markdown解析，支持##标题、**粗体**、---分页符

### Removed
- 移除冗余的辅助文档文件

## [2.3.0] - 2026-02-02

### Added
- 完整的Markdown解析函数`markdown_to_pdf_content()`
- 中英文字体混排函数`apply_mixed_font()`
- 端到端PDF生成示例

### Fixed
- 修复粗体标签处理（使用正则表达式而非字符串替换）

## [2.2.0] - 2026-02-02

### Added
- 特殊格式内容处理指南
- 显式目录处理机制
- 目录解析问题的完整解决方案

### Fixed
- 修复目录（TOC）在PDF生成时丢失的问题

## [2.1.0] - 2026-02-02

### Added
- 中文字体默认使用STHeiti（黑体）
- 中英文字体混排功能
- 自动识别英文关键词（API、AI、Claude等）

### Changed
- 字体优先级调整：STHeiti > PingFang > 其他

## [2.0.0] - 2026-02-02

### Added
- "翻译即重写"理念
- 三步翻译工作流（重写→诊断→润色）
- 四大中西语言转换策略
- 学术级翻译质量承诺

### Changed
- 完全重写翻译标准
- 从简单翻译提升到学术级翻译

## [1.0.0] - 2026-01-30

### Added
- 初始版本发布
- PDF文本提取功能
- 基础翻译工作流
- 中文字体自动检测
- PDF生成功能
- 自定义样式配置
- 命令行参数支持
