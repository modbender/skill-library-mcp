# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-02-27

### Added
- 🎭 官方账号过滤功能 - 默认排除品牌官方账号，关注第三方真实声音
- 📊 数据质量评估 - 评估和标注数据完整度
- 🤖 智能数据补充 - 使用 web_fetch 自动补充重要内容
- 👥 作者影响力估算 - 补充缺失的粉丝数
- 📋 汽车媒体白名单 - 自动识别知名汽车媒体
- 🧪 测试脚本 - 可在不安装 OpenClaw 的情况下测试功能
- 📚 完整文档 - 包括使用指南、故障排查、数据质量分析等

### Changed
- 💪 改进影响力计算公式 - 降低对缺失数据的依赖，增加作者影响力维度
- 🔍 优化数据提取逻辑 - 改进正则表达式，提高数据提取准确率
- 📝 更新 monitor.md 流程 - 添加数据质量评估和智能补充策略
- 🌐 默认使用百度搜索引擎 - 对中文平台效果更好

### Fixed
- 🐛 修复 Windows 编码问题 - 添加 UTF-8 编码支持
- 🔧 修复官方账号识别逻辑 - 改进匹配规则
- 📊 修复数据提取不完整问题 - 优化提取算法

### Documentation
- 📖 添加《如何使用Skill.md》
- 📖 添加《发布到ClawHub指南.md》
- 📖 添加《官方账号过滤说明.md》
- 📖 添加《数据质量分析报告.md》
- 📖 添加《数据质量改进方案.md》
- 📖 更新 README.md - 添加官方账号过滤和数据质量说明

## [1.1.0] - 2026-02-26

### Added
- ⚡ SerpAPI 集成 - 使用专业搜索服务替代 web_search API
- 🎯 支持多个搜索引擎 - Google、百度、Bing
- 🧪 Mock 模式 - 无限免费测试
- 📊 改进数据提取 - 从搜索结果摘要中提取结构化数据
- 🔍 自动平台识别 - 通过 URL 自动识别平台
- ⏰ 时间过滤支持 - 支持最近24小时、一周等时间范围

### Changed
- 🔄 从 web_search API 迁移到 SerpAPI
- 📝 更新所有 prompts 使用新的爬虫
- 📚 更新文档和使用指南

### Fixed
- 🐛 修复搜索结果为空的问题
- 🔧 改进错误处理

## [1.0.0] - 2026-02-25

### Added
- 🎉 初始发布
- 🔍 多平台监控 - 支持 9+ 国内主流平台
- 😊 情感分析 - 自动分析正面/中性/负面情感
- 🚨 实时警报 - 及时发现负面提及和病毒式传播
- 📊 趋势分析 - 生成品牌趋势报告
- 🎯 汽车行业优化 - 识别汽车媒体大V
- 📱 飞书推送 - 自动推送监控报告
- 🐍 自定义 Python 爬虫 - 直接访问各平台

### Documentation
- 📖 完整的 README.md
- 📖 SKILL.md 元数据
- 📖 配置示例和安装脚本

---

## 版本说明

### 版本号格式

遵循 [Semantic Versioning](https://semver.org/)：

- **主版本号（Major）**: 不兼容的 API 变更
- **次版本号（Minor）**: 向后兼容的功能新增
- **修订号（Patch）**: 向后兼容的问题修正

### 变更类型

- **Added**: 新功能
- **Changed**: 现有功能的变更
- **Deprecated**: 即将移除的功能
- **Removed**: 已移除的功能
- **Fixed**: Bug 修复
- **Security**: 安全性修复
- **Documentation**: 文档更新

### 链接

- [1.2.0]: https://github.com/你的用户名/brand-monitor-skill/releases/tag/v1.2.0
- [1.1.0]: https://github.com/你的用户名/brand-monitor-skill/releases/tag/v1.1.0
- [1.0.0]: https://github.com/你的用户名/brand-monitor-skill/releases/tag/v1.0.0

