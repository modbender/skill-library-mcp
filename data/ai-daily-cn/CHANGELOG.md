# Changelog

All notable changes to the AI Daily skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-27

### Added
- 📝 **智能摘要功能**
  - 精选文章：基于标题关键词生成中文摘要（≤150 字）
  - KOL 观点：从原文内容截取（≤150 字）
  - 推荐论文：智能生成中文摘要（≤80 字）
- 🎯 **来源配额控制**
  - 单一来源最多占比 80%（8 条/10 条）
  - 确保内容多样性
- 📚 **论文中文摘要**
  - 自动识别研究领域（agent/reasoning/benchmark）
  - 自动识别应用场景（math/code/vision/gui）
  - 自动生成简洁中文说明

### Changed
- ⬇️ 降低量子位优先级（10 → 8），允许其他源入选
- 📋 优化输出格式，增加摘要标识（📝）

### Fixed
- 🐛 36 氪 RSS 内容提取问题（部分修复）

## [1.0.0] - 2026-02-26

### Added
- 🎉 **初始版本发布**
- 📡 **三源数据整合**
  - RSS Feed（量子位、机器之心、36 氪、Hugging Face 等）
  - Tavily Search（KOL 动态、热点新闻）
  - arXiv API（最新学术论文）
- 🎯 **智能质量评分**
  - 10 分制评分系统
  - 基于关键词、来源、内容长度等多维度
- 🔧 **高度可配置**
  - 自定义数据源优先级
  - 自定义过滤规则
  - 自定义输出数量限制
- 📊 **结构化输出**
  - 精选文章（10 条）
  - KOL 观点（3 条）
  - 推荐论文（3 篇）
  - 总计 16 条精选信息
- 🚀 **一键生成**
  - `bash scripts/generate.sh` 30 秒产出日报
- 📱 **多平台推送**
  - 支持 DingTalk 推送
  - 支持 Markdown 格式输出

### Tech Stack
- Python 3.8+
- FeedParser（RSS 解析）
- Tavily API（搜索）
- arXiv API（论文）

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2026-02-27 | 智能摘要 + 配额控制 |
| 1.0.0 | 2026-02-26 | 初始版本 |
