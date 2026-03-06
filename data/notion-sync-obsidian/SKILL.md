---
name: notion-sync-obsidian
description: 自动将Notion文章同步到本地Obsidian目录，支持定时检查、完整内容导出、智能标题提取。
homepage: https://github.com/openclaw/openclaw
metadata: {"clawdbot":{"emoji":"📝"}}
---

# notion-sync-obsidian

自动将Notion文章同步到本地Obsidian目录的完整解决方案。支持定时检查、完整内容导出、智能标题提取、移动端优化通知。

## ✨ 功能特性

### ✅ 核心功能
- **自动同步**: 定时检查Notion更新并同步到本地Obsidian目录
- **完整导出**: 导出文章标题、元数据、完整内容
- **智能标题**: 自动识别文章原始标题（非摘要内容）
- **移动通知**: 移动端优化格式，只在有更新时通知

### ✅ 高级特性
- **定时检查**: 可配置检查频率（默认15分钟）
- **安静时段**: 支持配置安静时段（默认00:00-08:30）
- **强制检查**: 支持用户手动触发检查，忽略安静时段
- **增量同步**: 基于时间戳避免重复导出
- **错误处理**: 完善的错误处理和日志记录

### ✅ 技术特性
- **Python支持**: 使用Python requests库进行完整API调用
- **环境兼容**: 自动处理Python依赖安装
- **配置灵活**: 支持自定义API密钥、导出目录、检查频率
- **跨平台**: 支持Linux/macOS/Windows（容器环境已验证）

## 🚀 快速开始

### 1. 前置要求
- Notion API密钥（从 https://notion.so/my-integrations 获取）
- Obsidian目录路径
- Python 3.6+（可选，用于完整内容导出）

### 2. 基础配置
```bash
# 1. 进入skill目录
cd ~/.openclaw/workspace/skills/notion-sync-obsidian

# 2. 编辑配置文件
nano config.json
```

配置文件示例 (`config.json`):
```json
{
  "notion": {
    "api_key": "ntn_your_api_key_here",
    "api_version": "2022-06-28"
  },
  "obsidian": {
    "root_dir": "/path/to/your/obsidian/notion"
  },
  "sync": {
    "check_interval_minutes": 15,
    "quiet_hours_start": "00:00",
    "quiet_hours_end": "08:30",
    "enable_notifications": true
  }
}
```

### 3. 启动同步系统
```bash
# 启动定时同步（每15分钟检查一次）
./scripts/start_timer.sh

# 手动检查（忽略安静时段）
FORCE_CHECK=1 ./scripts/simple_checker.sh

# 查看状态
./scripts/status_timer.sh

# 停止同步
./scripts/stop_timer.sh
```

## 📁 目录结构

```
notion-sync-obsidian/
├── SKILL.md                    # 技能说明文档
├── config.json                 # 配置文件模板
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
│   └── NOTION_API_GUIDE.md     # Notion API使用指南
└── examples/                   # 示例文件
    └── exported_article.md     # 导出文件示例
```

## 🔧 详细配置

### Notion API配置
1. 访问 https://notion.so/my-integrations 创建集成
2. 复制API密钥（以 `ntn_` 开头）
3. 将集成分享到你的Notion工作空间
4. 在 `config.json` 中配置API密钥

### 导出目录配置
- **默认路径**: `/hellox/openclaw/obsidian/notion/`
- **组织结构**: 按年月分目录 `YYYY-MM/`
- **文件命名**: 使用文章原始标题，特殊字符自动过滤

### 定时检查配置
- **检查频率**: 默认15分钟，可配置
- **安静时段**: 默认00:00-08:30，避免夜间打扰
- **强制模式**: `FORCE_CHECK=1` 环境变量忽略所有限制

## 🛠️ 脚本说明

### 核心脚本
- **`real_notion_checker.py`**: 完整Python检查器，导出完整内容
- **`simple_checker.sh`**: 简化Shell检查器，快速检查更新
- **`timer_checker.sh`**: 定时检查器，管理定时任务

### 管理脚本
- **`start_timer.sh`**: 启动定时同步系统
- **`stop_timer.sh`**: 停止定时同步系统
- **`status_timer.sh`**: 查看系统状态和日志
- **`list_recent_articles.sh`**: 列出Notion最近文章

### 调试脚本
- **`debug_page_structure.py`**: 调试Notion页面结构
- **`test_title_fix.py`**: 测试标题提取修复

## 📊 系统状态

### 查看状态
```bash
./scripts/status_timer.sh
```

输出示例:
```
📊 Notion定时同步状态检查
检查时间: 2026-02-24 15:44:53
时区: Asia/Shanghai
========================================
🟢 状态: 运行中
进程PID: 4538
运行时间:       10:29

📋 日志信息:
日志文件: ./sync_timer.log
日志行数: 1179

📁 目录状态:
文章目录: /hellox/openclaw/obsidian/notion
文章数量: 78

⏰ 下次检查时间:
   15:59 (15分钟后)
```

### 查看日志
```bash
tail -f sync_timer.log
```

## 🔍 故障排除

### 常见问题

**Q: 同步失败，提示API错误**
A: 检查API密钥是否正确，确保集成已分享到工作空间

**Q: 文件名使用摘要而非标题**
A: 这是已知问题，已修复。确保使用最新版本的 `real_notion_checker.py`

**Q: Python依赖安装失败**
A: 容器环境可能需要特殊处理，脚本已包含自动安装逻辑

**Q: 定时器不运行**
A: 检查进程状态，可能需要重启定时器

### 调试步骤
1. 运行 `./scripts/debug_page_structure.py` 检查API连接
2. 运行 `FORCE_CHECK=1 ./scripts/simple_checker.sh` 手动测试
3. 检查 `sync_timer.log` 日志文件
4. 验证配置文件路径和权限

## 📈 高级用法

### 自定义导出格式
修改 `real_notion_checker.py` 中的 `export_page_to_markdown` 函数来自定义Markdown格式。

### 集成到其他系统
脚本输出标准化格式，可轻松集成到：
- CI/CD流水线
- 其他自动化工具
- 自定义监控系统

### 扩展功能
1. **标签同步**: 同步Notion标签到Obsidian标签
2. **图片下载**: 自动下载文章中的图片
3. **双向同步**: 支持从Obsidian同步回Notion
4. **多数据库**: 支持同步多个Notion数据库

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 开发环境
```bash
# 克隆仓库
git clone https://github.com/your-username/notion-sync-obsidian.git

# 安装依赖
pip install -r requirements.txt

# 运行测试
python -m pytest tests/
```

### 代码规范
- 遵循PEP 8 Python代码规范
- 添加适当的注释和文档
- 编写单元测试
- 更新CHANGELOG.md

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 🙏 致谢

- Notion官方API文档
- OpenClaw社区
- 所有贡献者和用户

---

**版本**: 1.0.0  
**最后更新**: 2026-02-24  
**维护者**: kk (你的私人助理)  
**状态**: ✅ 生产就绪