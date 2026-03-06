---
name: api-monitor
description: ">"
---


# API 使用量监控技能（询问确认模式）

## 概述
监控 OpenClaw 模型 API 使用量，配额不足时**询问用户确认后再切换**，确保用户知情。

## 功能
- ✅ 实时监控当前模型 API 状态
- ✅ 检测配额不足/错误
- ✅ 询问用户确认后再切换模型
- ✅ 支持多个模型优先级配置
- ✅ 手动指定切换到某个模型

## 使用方法

### 准备工作
```bash
# 确认Python环境
python3 --version

# 确认脚本存在（路径根据实际安装位置调整）
ls -la ~/.openclaw/skills/api-monitor/api_monitor.py
```

### 查看当前状态
```bash
# 替换为实际脚本路径
SCRIPT_PATH="$HOME/.openclaw/skills/api-monitor/api_monitor.py"
python3 "$SCRIPT_PATH" --check
```

### 询问是否切换（生成询问消息）
```bash
SCRIPT_PATH="$HOME/.openclaw/skills/api-monitor/api_monitor.py"
python3 "$SCRIPT_PATH" --ask
```

### 确认切换（用户确认后执行）
```bash
SCRIPT_PATH="$HOME/.openclaw/skills/api-monitor/api_monitor.py"
python3 "$SCRIPT_PATH" --confirm
```

### 指定切换到某个模型
```bash
# 替换为目标模型
TARGET_MODEL="mydamoxing/MiniMax-M2.5"
SCRIPT_PATH="$HOME/.openclaw/skills/api-monitor/api_monitor.py"
python3 "$SCRIPT_PATH" --model "$TARGET_MODEL"
```

### 列出所有可用模型
```bash
SCRIPT_PATH="$HOME/.openclaw/skills/api-monitor/api_monitor.py"
python3 "$SCRIPT_PATH" --list-models
```

## 可用模型列表
1. `mydamoxing/MiniMax-M2.5-highspeed` - MiniMax高速版
2. `mydamoxing/MiniMax-M2.5` - MiniMax普通版
3. `volcengine/ark-code-latest` - 火山引擎
4. `hajimi/claude-sonnet-4-20250511` - 免费模型

## 工作流程

1. **定时检查** → 运行 `--check` 查看状态
2. **发现问题** → 运行 `--ask` 生成询问消息
3. **用户确认** → 运行 `--confirm` 执行切换
4. **或者** → 用户指定 `--model xxx` 直接切换

## 示例对话

```
用户: 检查一下API状态
助手: (运行 --check)
当前模型: mydamoxing/MiniMax-M2.5-highspeed
状态: API配额可能不足，建议切换模型
错误次数: 3

用户: 那就切换吧
助手: (运行 --confirm)
确认切换: mydamoxing/MiniMax-M2.5-highspeed → mydamoxing/MiniMax-M2.5
切换成功!
```

## 定时任务配置（可选）

如需定时自动检查，可配置 cron：
```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每30分钟检查一次）
# 替换为实际路径
*/30 * * * * cd $HOME/.openclaw/skills/api-monitor && python3 api_monitor.py --check >> /var/log/api-monitor.log 2>&1
```

## 注意事项
- 切换模型会中断当前会话
- 建议在非高峰期操作
- 始终需要用户确认才切换
- 定期检查日志 `/var/log/api-monitor.log` 了解运行状态
