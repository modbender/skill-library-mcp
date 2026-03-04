# 安装和使用指南

## 🚀 快速安装

### 方法 1: 从 ClawHub 安装（推荐）
```bash
# 安装 ClawHub CLI（如果尚未安装）
curl -fsSL https://clawhub.com/install.sh | bash

# 搜索技能
clawhub search notion-sync

# 安装技能
clawhub install notion-sync-obsidian
```

### 方法 2: 手动安装
```bash
# 1. 下载技能
git clone https://github.com/your-username/notion-sync-obsidian.git
# 或直接复制文件到技能目录

# 2. 复制到 OpenClaw 技能目录
cp -r notion-sync-obsidian ~/.openclaw/workspace/skills/
```

## ⚙️ 配置步骤

### 步骤 1: 获取 Notion API 密钥
1. 访问 [Notion Integrations](https://notion.so/my-integrations)
2. 创建新集成
3. 复制 API 密钥（以 `ntn_` 开头）
4. 将集成分享到你的工作空间

### 步骤 2: 配置技能
```bash
# 进入技能目录
cd ~/.openclaw/workspace/skills/notion-sync-obsidian

# 复制配置文件模板
cp config.json.example config.json

# 编辑配置文件
nano config.json
```

### 步骤 3: 修改配置文件
编辑 `config.json`:
```json
{
  "notion": {
    "api_key": "ntn_your_actual_api_key_here",
    "api_version": "2022-06-28"
  },
  "obsidian": {
    "root_dir": "/path/to/your/obsidian/vault",
    "organize_by_month": true
  },
  "sync": {
    "check_interval_minutes": 15,
    "quiet_hours_start": "00:00",
    "quiet_hours_end": "08:30"
  }
}
```

**重要配置项**:
- `api_key`: 你的 Notion API 密钥
- `root_dir`: Obsidian 笔记库的根目录
- `check_interval_minutes`: 检查频率（分钟）

## 🧪 测试安装

### 测试 API 连接
```bash
cd ~/.openclaw/workspace/skills/notion-sync-obsidian
./scripts/simple_checker.sh
```

**预期输出**:
```
✅ API连接成功
   用户: Your Name
   工作空间: Your Workspace
✅ 创建测试文件: Notion同步测试_20260224_154322.md
```

### 测试完整同步
```bash
# 运行完整 Python 检查器
python3 ./scripts/real_notion_checker.py
```

## 🚀 启动定时同步

### 启动定时器
```bash
./scripts/start_timer.sh
```

**输出示例**:
```
🚀 启动Notion定时同步...
启动时间: 2026-02-24 15:45:37
时区: Asia/Shanghai
检查间隔: 15 分钟
日志文件: sync_timer.log
✅ 定时同步已启动
📋 定时进程PID: 4538
```

### 查看状态
```bash
./scripts/status_timer.sh
```

### 停止定时器
```bash
./scripts/stop_timer.sh
```

## 📱 使用技巧

### 手动同步（忽略安静时段）
```bash
FORCE_CHECK=1 ./scripts/simple_checker.sh
```

### 查看最近文章
```bash
./scripts/list_recent_articles.sh
```

### 调试页面结构
```bash
python3 ./scripts/debug_page_structure.py
```

### 查看日志
```bash
# 实时查看日志
tail -f sync_timer.log

# 查看最后100行
tail -n 100 sync_timer.log
```

## 🔧 故障排除

### 常见问题 1: API 连接失败
**症状**: "API连接失败" 或 "未找到数据库"
**解决方案**:
```bash
# 1. 检查 API 密钥
grep api_key config.json

# 2. 测试 API 连接
curl -s -X GET "https://api.notion.com/v1/users/me" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Notion-Version: 2022-06-28"

# 3. 确认集成已分享到工作空间
```

### 常见问题 2: Python 依赖缺失
**症状**: "ModuleNotFoundError: No module named 'requests'"
**解决方案**:
```bash
# 安装 Python 依赖
pip install requests pytz

# 或使用系统包管理器
apt-get install python3-requests python3-pytz
```

### 常见问题 3: 权限问题
**症状**: "Permission denied" 或无法创建文件
**解决方案**:
```bash
# 检查目录权限
ls -la /path/to/your/obsidian

# 修改权限（如果需要）
chmod 755 /path/to/your/obsidian
```

## 📊 监控和维护

### 定期检查
1. **查看状态**: `./scripts/status_timer.sh`
2. **检查日志**: `tail -f sync_timer.log`
3. **验证导出**: 检查 Obsidian 目录中的文件

### 清理操作
```bash
# 清理旧日志（保留最近7天）
find . -name "*.log" -mtime +7 -delete

# 清理 PID 文件（如果进程异常）
rm -f sync_timer.pid
```

### 备份配置
```bash
# 备份配置文件
cp config.json config.json.backup

# 备份日志
cp sync_timer.log sync_timer.log.backup
```

## 🔄 更新技能

### 检查更新
```bash
# 如果从 ClawHub 安装
clawhub update notion-sync-obsidian

# 如果手动安装
cd ~/.openclaw/workspace/skills/notion-sync-obsidian
git pull origin main
```

### 更新后操作
1. 停止定时器: `./scripts/stop_timer.sh`
2. 备份配置: `cp config.json config.json.backup`
3. 更新文件
4. 恢复配置: `cp config.json.backup config.json`
5. 启动定时器: `./scripts/start_timer.sh`

## 🎯 高级配置

### 自定义检查频率
```json
{
  "sync": {
    "check_interval_minutes": 30,  // 每30分钟检查
    "quiet_hours_start": "23:00",
    "quiet_hours_end": "07:00"
  }
}
```

### 自定义导出目录
```json
{
  "obsidian": {
    "root_dir": "/mnt/obsidian/vault",
    "organize_by_month": false,  // 不按月份组织
    "subdirectory": "imports/notion"  // 自定义子目录
  }
}
```

### 启用详细日志
```json
{
  "logging": {
    "log_level": "DEBUG",
    "max_log_size_mb": 50,
    "backup_count": 10
  }
}
```

## 🤝 获取帮助

### 查看文档
- `SKILL.md` - 技能详细说明
- `references/NOTION_API_GUIDE.md` - API 使用指南
- `examples/` - 示例文件

### 社区支持
- [OpenClaw Discord](https://discord.com/invite/clawd)
- [GitHub Issues](https://github.com/your-username/notion-sync-obsidian/issues)
- [ClawHub 社区](https://clawhub.com)

### 报告问题
1. 描述具体问题
2. 提供相关日志
3. 说明复现步骤
4. 附上配置文件（隐藏敏感信息）

---

**技能版本**: v1.0.0  
**最后更新**: 2026-02-24  
**维护者**: OpenClaw 社区  
**状态**: ✅ 生产就绪