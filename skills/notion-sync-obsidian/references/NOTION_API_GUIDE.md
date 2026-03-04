# Notion API 使用指南

## 📋 概述

本文档提供 Notion API 的基本使用指南，帮助配置和使用 notion-sync-obsidian 技能。

## 🔑 获取 API 密钥

### 步骤 1: 创建集成
1. 访问 [Notion Integrations](https://notion.so/my-integrations)
2. 点击 "New integration"
3. 填写集成信息:
   - **Name**: 例如 "Obsidian Sync"
   - **Logo** (可选): 上传图标
   - **Associated workspace**: 选择你的工作空间
4. 点击 "Submit"

### 步骤 2: 获取 API 密钥
创建成功后，你会看到:
- **Internal Integration Token**: 以 `ntn_` 或 `secret_` 开头的字符串
- 这就是你的 API 密钥

### 步骤 3: 分享集成到工作空间
1. 在 Notion 中打开要同步的页面或数据库
2. 点击右上角的 "..." 菜单
3. 选择 "Add connections" 或 "Connect to"
4. 找到你创建的集成并连接

## 📊 API 版本说明

### 当前使用的版本: `2022-06-28`
这是最稳定和广泛支持的版本。

### 关键特性:
- 支持页面和数据库查询
- 支持内容块获取
- 支持富文本格式
- 稳定的 API 端点

## 🔧 配置技能

### 配置文件 (`config.json`)
```json
{
  "notion": {
    "api_key": "ntn_your_api_key_here",
    "api_version": "2022-06-28"
  },
  "obsidian": {
    "root_dir": "/path/to/your/obsidian",
    "organize_by_month": true
  },
  "sync": {
    "check_interval_minutes": 15,
    "quiet_hours_start": "00:00",
    "quiet_hours_end": "08:30"
  }
}
```

### 配置说明
1. **api_key**: 从 Notion Integrations 获取的密钥
2. **root_dir**: Obsidian 笔记库的根目录
3. **check_interval_minutes**: 检查更新的频率（分钟）
4. **quiet_hours**: 安静时段，避免夜间打扰

## 🚀 快速测试

### 测试 API 连接
```bash
cd /path/to/skill
./scripts/simple_checker.sh
```

### 手动同步
```bash
# 忽略安静时段
FORCE_CHECK=1 ./scripts/simple_checker.sh

# 使用完整 Python 检查器
python3 ./scripts/real_notion_checker.py
```

## 🔍 调试技巧

### 查看页面结构
```bash
python3 ./scripts/debug_page_structure.py
```

### 列出最近文章
```bash
./scripts/list_recent_articles.sh
```

### 查看日志
```bash
tail -f sync_timer.log
```

## ⚠️ 常见问题

### 问题 1: API 连接失败
**症状**: "API连接失败" 或 "未找到数据库"
**解决方案**:
1. 检查 API 密钥是否正确
2. 确认集成已分享到工作空间
3. 检查网络连接

### 问题 2: 标题提取错误
**症状**: 文件名使用摘要而非标题
**解决方案**:
1. 运行调试脚本查看页面结构
2. 确认页面有 "标题" 或 "Title" 属性
3. 修改 `real_notion_checker.py` 中的 `get_page_title` 函数

### 问题 3: 权限不足
**症状**: "没有找到数据库"
**解决方案**:
1. 将集成分享到所有需要同步的数据库
2. 检查数据库是否在集成的工作空间内

## 📈 API 限制

### 速率限制
- 普通用户: 约 3 请求/秒
- 集成: 可能有额外限制

### 数据限制
- 页面内容: 可能有限制（通常足够）
- 数据库查询: 分页支持

## 🔄 同步逻辑

### 增量同步
- 只同步最近 24 小时内编辑的页面
- 避免重复导出相同内容
- 基于 `last_edited_time` 时间戳

### 文件命名
- 使用页面标题作为文件名
- 特殊字符自动过滤
- 避免文件名冲突

### 目录结构
```
obsidian_root/
└── notion/
    └── YYYY-MM/
        ├── 文章标题1.md
        ├── 文章标题2.md
        └── ...
```

## 🛠️ 高级配置

### 自定义标题提取
修改 `scripts/real_notion_checker.py` 中的 `get_page_title` 函数:
```python
# 添加你的特定属性名
preferred_title_names = ['标题', 'Title', '名称', 'Name', '你的属性名']
```

### 自定义导出格式
修改 `save_page_as_markdown` 函数来自定义 Markdown 格式。

### 扩展功能
1. 图片下载
2. 标签同步
3. 双向同步
4. 多数据库支持

## 📚 参考资源

### 官方文档
- [Notion API Documentation](https://developers.notion.com)
- [API Reference](https://developers.notion.com/reference)
- [Integration Guide](https://developers.notion.com/docs/getting-started)

### 社区资源
- [OpenClaw 社区](https://discord.com/invite/clawd)
- [ClawHub 技能市场](https://clawhub.com)
- [GitHub 仓库](https://github.com/openclaw/openclaw)

## 🆘 技术支持

### 获取帮助
1. 查看日志文件 `sync_timer.log`
2. 运行调试脚本
3. 联系 OpenClaw 社区

### 报告问题
1. 描述具体问题
2. 提供相关日志
3. 说明复现步骤

---

**最后更新**: 2026-02-24  
**版本**: notion-sync-obsidian v1.0.0  
**维护者**: OpenClaw 社区