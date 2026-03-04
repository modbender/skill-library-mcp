# Context Restore - 5分钟快速开始

> 📚 **预计时间**：5 分钟  
> 🎯 **目标**：学会使用 Context Restore 技能恢复工作状态

---

## ⏱️ 第一步：安装技能（1分钟）

### 方式一：ClawdHub 安装（推荐）

```bash
clawdhub install context-restore
```

### 方式二：手动安装

```bash
# 克隆仓库
git clone https://github.com/openclaw/context-restore.git ~/.openclaw/skills/context-restore

# 验证安装
ls -la ~/.openclaw/skills/context-restore/
```

✅ **验证**：看到 `scripts/` 目录说明安装成功

---

## ⏱️ 第二步：基本使用（2分钟）

### 场景：继续昨天的工作

**1. 进入新会话，说：**

```
继续之前的工作
```

**2. 技能自动恢复上下文，输出：**

```
✅ 上下文已恢复

📊 压缩信息:
- 原始消息: 45
- 压缩后: 12
- 压缩率: 26.7%

🔄 最近操作:
- 完成数据管道测试
- 部署新功能到生产环境
- 添加 3 个 cron 任务

🚀 当前项目:
1. Hermes Plan (80%)
2. Akasha Plan (45%)

📋 待办任务:
- [高] 编写测试用例
- [中] 设计 UI 组件
```

### 使用命令行工具

```bash
# 默认恢复（Normal 级别）
python ~/.openclaw/skills/context-restore/scripts/restore_context.py

# 详细模式
python ~/.openclaw/skills/context-restore/scripts/restore_context.py --level detailed

# 极简模式
python ~/.openclaw/skills/context-restore/scripts/restore_context.py --level minimal
```

---

## ⏱️ 第三步：进阶功能（2分钟）

### 功能 1：时间线回顾

查看本周或更长时间的进度：

```bash
# 按周显示
python restore_context.py --timeline --period weekly

# 按月显示
python restore_context.py --timeline --period monthly
```

**输出示例**：
```
📅 Week 6 (Feb 2-8)
├── ✅ 完成数据管道测试
├── ✅ 部署新功能
└── 🚀 Hermes, Akasha

📅 Week 5 (Jan 26 - Feb 1)
├── ✅ 启动 UI 改进
└── 🚀 Hermes Plan
```

### 功能 2：过滤特定内容

只显示感兴趣的内容：

```bash
# 只显示 Hermes 相关
python restore_context.py --filter "Hermes"

# 只显示项目信息
python restore_context.py --filter "project"
```

### 功能 3：对比两个版本

查看上下文变化：

```bash
# 基本对比
python restore_context.py --diff old.json new.json

# 详细对比
python restore_context.py --diff old.json new.json --level detailed
```

---

## ⏱️ 第四步：自动监控（可选）

### 设置自动上下文监控

```bash
# 安装 cron 任务（每5分钟检查）
python restore_context.py --install-cron

# 自定义间隔（每10分钟）
python restore_context.py --install-cron --cron-interval 10
```

**输出**：
```
✅ Cron script created: scripts/auto_context_monitor.sh

安装命令：
echo "*/5 * * * * /path/to/auto_context_monitor.sh" >> ~/.crontab
crontab ~/.crontab
```

### 自动恢复模式

```bash
# 检测到变化时自动恢复
python restore_context.py --auto

# 静默模式（适合 cron）
python restore_context.py --auto --quiet

# 仅检查变化
python restore_context.py --check-only
# 退出码 0 = 无变化
# 退出码 1 = 有变化
```

---

## 📋 恢复级别速查表

| 级别 | 命令 | 适用场景 |
|------|------|---------|
| **Minimal** | `--level minimal` | 快速确认当前状态 |
| **Normal** | `--level normal` | 日常继续工作（默认） |
| **Detailed** | `--level detailed` | 深度回顾/汇报 |

---

## 🆘 常见问题

### Q: 提示 "文件不存在"？

```bash
# 检查上下文文件是否存在
ls -la ~/.openclaw/workspace/compressed_context/

# 如果不存在，说明还没有保存过上下文
# 先正常使用 OpenClaw 一段时间，context-save 会自动保存
```

### Q: 输出内容太少？

```bash
# 使用详细模式查看完整内容
python restore_context.py --level detailed
```

### Q: 如何输出到文件？

```bash
python restore_context.py --output report.md
```

### Q: Telegram 消息太长？

```bash
# 使用 Telegram 模式（自动分块）
python restore_context.py --telegram
```

---

## 🎯 下一步

掌握基础后，建议探索：

1. **与 context-save 配合使用** - 自动保存+恢复的完整流程
2. **集成到工作流** - 设置 cron 自动监控
3. **自定义输出格式** - 根据需求调整

---

## 📚 相关资源

- 📖 [完整文档](README.md)
- 🛠️ [API 参考](SKILL.md)
- 🐛 [问题反馈](https://github.com/openclaw/context-restore/issues)

---

*快速开始完成！🎉*
