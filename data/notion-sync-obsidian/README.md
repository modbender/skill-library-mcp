# notion-sync-obsidian

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-orange)

自动将 Notion 文章同步到本地 Obsidian 目录的完整解决方案。

## ✨ 特性

### ✅ 核心功能
- **自动同步**: 定时检查 Notion 更新并同步到本地
- **完整导出**: 导出文章标题、元数据、完整内容
- **智能标题**: 正确提取文章原始标题（非摘要）
- **移动通知**: 移动端优化格式，智能通知

### ⚙️ 高级功能
- **可配置检查频率** (默认15分钟)
- **安静时段支持** (默认00:00-08:30)
- **强制检查模式** (用户手动触发)
- **增量同步** (避免重复导出)
- **错误处理和日志记录**

## 🚀 快速开始

### 安装
```bash
# 从 ClawHub 安装
clawhub install notion-sync-obsidian

# 或手动安装
git clone https://github.com/your-username/notion-sync-obsidian.git
cp -r notion-sync-obsidian ~/.openclaw/workspace/skills/
```

### 配置
1. 获取 Notion API 密钥: https://notion.so/my-integrations
2. 复制配置文件: `cp config.json.example config.json`
3. 编辑配置: 设置 API 密钥和 Obsidian 目录

### 使用
```bash
# 测试连接
./scripts/simple_checker.sh

# 启动定时同步
./scripts/start_timer.sh

# 查看状态
./scripts/status_timer.sh
```

## 📁 目录结构

```
notion-sync-obsidian/
├── SKILL.md                    # 技能详细文档
├── README.md                   # 项目说明
├── INSTALL.md                  # 安装指南
├── config.json                 # 配置文件
├── config.json.example         # 配置示例
├── scripts/                    # 核心脚本
│   ├── real_notion_checker.py  # 完整Python检查器
│   ├── simple_checker.sh       # 简化Shell检查器
│   ├── timer_checker.sh        # 定时检查器
│   ├── start_timer.sh          # 启动定时器
│   ├── stop_timer.sh           # 停止定时器
│   ├── status_timer.sh         # 查看状态
│   ├── list_recent_articles.sh # 列出最近文章
│   └── debug_page_structure.py # 调试页面结构
├── references/                 # 参考文档
│   └── NOTION_API_GUIDE.md     # Notion API指南
├── examples/                   # 示例文件
│   └── exported_article.md     # 导出文件示例
└── LICENSE                     # 许可证文件
```

## 🔧 技术细节

### 标题提取算法
```python
# 智能标题提取，避免使用摘要内容
preferred_title_names = ['标题', 'Title', '名称', 'Name']
# 1. 按属性名优先查找
# 2. 按类型查找 (title类型)
# 3. 使用页面ID作为后备
```

### 同步逻辑
- **增量同步**: 只同步最近24小时编辑的页面
- **错误处理**: 完善的异常处理和日志记录
- **重试机制**: 网络错误自动重试

### 文件管理
- **安全命名**: 特殊字符自动过滤
- **冲突处理**: 自动添加序号避免冲突
- **目录组织**: 按年月自动组织文件

## 📊 系统要求

### 最低要求
- **操作系统**: Linux, macOS, Windows (WSL)
- **Python**: 3.6+ (用于完整功能)
- **Notion**: 有效API密钥和工作空间
- **Obsidian**: 本地笔记库目录

### 推荐配置
- **内存**: 512MB+
- **存储**: 100MB+ 可用空间
- **网络**: 稳定的互联网连接

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

### 开发流程
1. Fork 仓库
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

### 代码规范
- 遵循 PEP 8 Python 代码规范
- 添加适当的注释和文档
- 编写单元测试
- 更新 CHANGELOG.md

## 📄 许可证

本项目基于 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- Notion 官方 API 团队
- OpenClaw 社区
- 所有贡献者和用户
- 测试和反馈的早期用户

## 🔗 相关链接

- [OpenClaw 官网](https://openclaw.ai)
- [ClawHub 技能市场](https://clawhub.com)
- [Notion API 文档](https://developers.notion.com)
- [GitHub 仓库](https://github.com/your-username/notion-sync-obsidian)

## 📞 支持

### 文档
- [安装指南](INSTALL.md)
- [API 指南](references/NOTION_API_GUIDE.md)
- [技能文档](SKILL.md)

### 社区
- [OpenClaw Discord](https://discord.com/invite/clawd)
- [GitHub Issues](https://github.com/your-username/notion-sync-obsidian/issues)

### 问题排查
1. 查看日志文件 `sync_timer.log`
2. 运行调试脚本 `debug_page_structure.py`
3. 检查配置文件 `config.json`

---

**版本**: 1.0.0  
**最后更新**: 2026-02-24  
**维护者**: OpenClaw 社区  
**状态**: ✅ 生产就绪