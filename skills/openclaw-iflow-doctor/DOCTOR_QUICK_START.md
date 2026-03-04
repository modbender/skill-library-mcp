# OpenClaw iFlow Doctor - 快速启动指南

## ✅ 安装完成！

技能位置：`~/.openclaw/skills/openclaw-iflow-doctor/`

## 使用方法

### 1. 自动触发（推荐）
技能会自动在 OpenClaw 出错时激活，无需手动操作。

### 2. 手动诊断
```bash
# 进入技能目录
cd ~/.openclaw/skills/openclaw-iflow-doctor

# 查看统计信息
python3 openclaw_memory.py --stats

# 列出所有维修案例
python3 openclaw_memory.py --list-cases

# 诊断并修复问题
python3 openclaw_memory.py --fix "Gateway service crashed"

# 检查配置
python3 openclaw_memory.py --check-config
```

### 3. 快速命令
```bash
# 使用快捷脚本
./heal.sh --stats
./heal.sh --fix "error message"
```

## 功能特性

- 🔍 **智能问题分类** - 自动识别 8 种问题类型
- 📚 **维修案例库** - 10 个预定义常见问题解决方案
- 📝 **维修历史** - 跟踪所有维修记录
- 🛠️ **动态工具生成** - 根据问题类型生成修复脚本
- 🌐 **多语言支持** - 自动生成中文/英文报告
- 🧹 **自动清理** - 修复脚本执行后自动删除
- 🤖 **iFlow CLI 集成** - 无法自动修复时调用 iflow 协助

## 维修案例库

1. Memory Search Function Broken - 记忆索引损坏
2. Gateway Service Not Starting - 网关启动失败
3. API Rate Limit Exceeded - API 额度限制
4. Agent Spawn Failed - Agent 配置问题
5. Channel Configuration Error - 钉钉/飞书集成
6. Model Provider Connection Failed - API 连接问题
7. Configuration File Corrupted - JSON 配置错误
8. Multiple Agents Conflict - Agent 路由冲突
9. Permission Denied Errors - 文件权限问题
10. Log File Too Large - 日志清理

## 工作流程

```
OpenClaw 出错
    ↓
自动触发 Self-Healing
    ├─ 能修复 → 自动修复 → 记录 → 完成 ✓
    └─ 不能修复 → 生成诊断报告 + BAT 工具
                   ↓
              提示调用 iflow-helper
                   ↓
              iflow CLI 修复 → 同步记录
```

## 下次 OpenClaw 出错时

系统会自动：
1. 捕获错误
2. 检索案例库
3. 尝试自动修复
4. 生成修复报告
5. 必要时提示调用 iflow

**无需手动干预！** 🎉

---

安装时间：2026-02-28
版本：v1.0.0
