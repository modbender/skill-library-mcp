# exec-inspector

查看和分析 OpenClaw Agent 的 exec 工具执行历史和明细。

## 🎯 AI 自动使用指南

**当用户提出以下需求时，AI 应该立即执行相应命令，而不是只告诉用户怎么做：**

### 触发关键词和对应动作

| 用户说什么 | AI 应该做什么 | 执行命令 |
|-----------|--------------|---------|
| "最近执行了哪些命令" | 列出最近 20 条 | `~/.openclaw/scripts/exec-history.sh list` |
| "统计命令使用情况" | 显示统计数据 | `~/.openclaw/scripts/exec-history.sh stats` |
| "查找/搜索 XXX 命令" | 搜索特定命令 | `~/.openclaw/scripts/exec-history.sh search XXX` |
| "今天执行了什么" | 显示今天的命令 | `~/.openclaw/scripts/exec-history.sh today` |
| "查看 session 列表" | 列出所有 sessions | `~/.openclaw/scripts/exec-history.sh session` |
| "查看所有工具使用" | 统计所有工具 | `~/.openclaw/scripts/exec-history.sh all-tools` |
| "实时监控 exec" | 启动实时监控 | `~/.openclaw/scripts/exec-history.sh watch` |
| "导出执行历史" | 导出 JSON 文件 | `~/.openclaw/scripts/exec-history.sh export` |

## 🤖 AI 行为准则

1. **主动执行，不要只解释** - 用户问历史记录时，直接运行命令并展示结果
2. **美化输出** - 将原始输出整理成易读的格式
3. **提供洞察** - 分析数据，给出有价值的观察
4. **记住脚本路径** - `~/.openclaw/scripts/exec-history.sh`

### 示例对话

**❌ 错误示例** (只告诉，不执行):
```
用户: 我最近执行了哪些命令？
AI: 你可以运行 exec-history.sh list 来查看...
```

**✅ 正确示例** (立即执行):
```
用户: 我最近执行了哪些命令？
AI: 让我查看一下... [运行命令]

📋 最近 20 条 exec 命令：
1. ls -la (今天 15:30)
2. git status (今天 15:28)
...

看起来你今天主要在做 git 操作和文件管理。
```

## 功能

- 🔍 查看 session 中所有 exec 命令的执行历史
- 📊 统计最常用的命令
- 🕐 按时间筛选执行记录
- 🔎 搜索特定命令的执行记录
- 📈 分析命令执行频率和模式
- 🔴 实时监控新执行的命令
- 🚀 **后台守护进程 - 自动捕获所有 exec 执行并实时输出**

## 🔥 自动实时输出 - 守护进程模式

### 启动自动监控

```bash
# 启动后台守护进程
~/.openclaw/scripts/exec-monitor-daemon.sh start

# 查看实时输出
~/.openclaw/scripts/exec-monitor-daemon.sh tail
```

**效果**：从此刻起，OpenClaw 每次执行 exec 命令时，都会自动在日志中实时输出！

### 示例输出

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ EXEC COMMAND DETECTED
🕐 Time:     15:30:45
🤖 Model:    gpt-4.1 (friday-aws)
📋 Command:  ls -la
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ EXEC COMMAND DETECTED
🕐 Time:     15:30:48
🤖 Model:    gpt-4.1 (friday-aws)
📋 Command:  git status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 守护进程命令

| 命令 | 说明 |
|------|------|
| `start` | 启动后台监控守护进程 |
| `stop` | 停止守护进程 |
| `restart` | 重启守护进程 |
| `status` | 查看守护进程状态 |
| `tail` | 实时查看监控输出 |

### 使用流程

**1. 启动守护进程**
```bash
~/.openclaw/scripts/exec-monitor-daemon.sh start
```

**2. 在另一个终端查看实时输出**
```bash
~/.openclaw/scripts/exec-monitor-daemon.sh tail
```

**3. 正常使用 OpenClaw**
- 在 OpenClaw 对话中执行任何命令
- 监控终端会自动实时显示所有 exec 执行

**4. 停止监控**
```bash
~/.openclaw/scripts/exec-monitor-daemon.sh stop
```

### 设置别名（推荐）

```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
alias exec-monitor='~/.openclaw/scripts/exec-monitor-daemon.sh'
alias exec-monitor-start='~/.openclaw/scripts/exec-monitor-daemon.sh start && ~/.openclaw/scripts/exec-monitor-daemon.sh tail'
alias exec-monitor-stop='~/.openclaw/scripts/exec-monitor-daemon.sh stop'
```

然后：
```bash
exec-monitor-start    # 启动并立即查看输出
exec-monitor status   # 查看状态
exec-monitor-stop     # 停止
```

## 命令

### 1. 查看最近的 exec 执行记录

```bash
# 查看最近 10 条 exec 执行记录
grep '"name":"exec"' ~/.openclaw/agents/main/sessions/*.jsonl | tail -10 | while read line; do echo "$line" | jq -r '.message.content[0].arguments.command'; done

# 或者使用更详细的格式
grep '"name":"exec"' ~/.openclaw/agents/main/sessions/*.jsonl | tail -10 | jq -r '"\(.timestamp) | \(.message.content[0].arguments.command)"'
```

### 2. 统计命令使用频率

```bash
# 统计所有 exec 命令的使用频率
grep '"name":"exec"' ~/.openclaw/agents/main/sessions/*.jsonl | jq -r '.message.content[0].arguments.command' | sort | uniq -c | sort -rn
```

### 3. 查看特定 session 的执行历史

```bash
# 查看特定 session 的所有 exec 命令
SESSION_ID="aa19ccb2-19ff-4458-84b4-d20e688fd797"
grep '"name":"exec"' ~/.openclaw/agents/main/sessions/${SESSION_ID}.jsonl | jq -r '"\(.timestamp) | \(.message.content[0].arguments.command)"'
```

### 4. 搜索特定命令

```bash
# 搜索包含特定关键字的命令执行记录
grep '"name":"exec"' ~/.openclaw/agents/main/sessions/*.jsonl | jq -r 'select(.message.content[0].arguments.command | contains("git")) | "\(.timestamp) | \(.message.content[0].arguments.command)"'
```

### 5. 查看完整的 exec 工具调用详情

```bash
# 查看包含输入输出的完整记录
grep '"name":"exec"' ~/.openclaw/agents/main/sessions/*.jsonl | jq -C '.'
```

### 6. 分析工具使用统计

```bash
# 统计所有工具的使用频率
grep -o '"name":"[^"]*"' ~/.openclaw/agents/main/sessions/*.jsonl | sort | uniq -c | sort -rn
```

### 7. 按日期查看执行记录

```bash
# 查看今天的 exec 执行记录
TODAY=$(date +%Y-%m-%d)
grep '"name":"exec"' ~/.openclaw/agents/main/sessions/*.jsonl | jq -r "select(.timestamp | startswith(\"$TODAY\")) | \"\(.timestamp) | \(.message.content[0].arguments.command)\""
```

### 8. 创建交互式查看器脚本

创建一个便捷的脚本来查看 exec 历史：

```bash
cat > ~/.openclaw/scripts/exec-history.sh <<'EOF'
#!/bin/bash
# OpenClaw Exec History Viewer

SESSION_DIR="$HOME/.openclaw/agents/main/sessions"

case "$1" in
  list|"")
    echo "📋 Recent exec commands (last 20):"
    grep '"name":"exec"' "$SESSION_DIR"/*.jsonl 2>/dev/null | tail -20 | jq -r '"\(.timestamp | split("T")[0]) \(.timestamp | split("T")[1] | split(".")[0]) | \(.message.content[0].arguments.command)"' | nl
    ;;
    
  stats)
    echo "📊 Command usage statistics:"
    grep '"name":"exec"' "$SESSION_DIR"/*.jsonl 2>/dev/null | jq -r '.message.content[0].arguments.command' | awk '{print $1}' | sort | uniq -c | sort -rn | head -20
    ;;
    
  search)
    if [ -z "$2" ]; then
      echo "Usage: $0 search <keyword>"
      exit 1
    fi
    echo "🔍 Searching for commands containing: $2"
    grep '"name":"exec"' "$SESSION_DIR"/*.jsonl 2>/dev/null | jq -r "select(.message.content[0].arguments.command | contains(\"$2\")) | \"\(.timestamp | split(\"T\")[0]) \(.timestamp | split(\"T\")[1] | split(\".\")[0]) | \(.message.content[0].arguments.command)\"" | nl
    ;;
    
  today)
    TODAY=$(date +%Y-%m-%d)
    echo "📅 Commands executed today ($TODAY):"
    grep '"name":"exec"' "$SESSION_DIR"/*.jsonl 2>/dev/null | jq -r "select(.timestamp | startswith(\"$TODAY\")) | \"\(.timestamp | split(\"T\")[1] | split(\".\")[0]) | \(.message.content[0].arguments.command)\"" | nl
    ;;
    
  session)
    if [ -z "$2" ]; then
      echo "Available sessions:"
      ls -1 "$SESSION_DIR"/*.jsonl | xargs basename -s .jsonl | nl
      exit 0
    fi
    SESSION_FILE="$SESSION_DIR/$2.jsonl"
    if [ ! -f "$SESSION_FILE" ]; then
      echo "Session not found: $2"
      exit 1
    fi
    echo "📝 Exec history for session: $2"
    grep '"name":"exec"' "$SESSION_FILE" 2>/dev/null | jq -r '"\(.timestamp | split("T")[0]) \(.timestamp | split("T")[1] | split(".")[0]) | \(.message.content[0].arguments.command)"' | nl
    ;;
    
  all-tools)
    echo "🔧 All tool usage statistics:"
    grep -o '"name":"[^"]*"' "$SESSION_DIR"/*.jsonl 2>/dev/null | grep -v '"name":"[A-Z]' | sort | uniq -c | sort -rn
    ;;
    
  *)
    echo "Usage: $0 {list|stats|search|today|session|all-tools} [args]"
    echo ""
    echo "Commands:"
    echo "  list          - Show recent 20 exec commands"
    echo "  stats         - Show command usage statistics"
    echo "  search <kw>   - Search for commands containing keyword"
    echo "  today         - Show today's executed commands"
    echo "  session [id]  - Show exec history for a specific session"
    echo "  all-tools     - Show usage stats for all tools"
    ;;
esac
EOF

chmod +x ~/.openclaw/scripts/exec-history.sh
```

## AI 助手使用指南

当用户询问 exec 执行历史时，你应该：

1. **直接执行相应命令** - 不要只是告诉用户怎么做，直接帮他们查询
2. **美化输出** - 将结果整理成易读的格式
3. **提供洞察** - 分析执行模式，提供有价值的观察

### 示例对话

**用户**: "我最近执行了哪些命令？"

**AI 回复**:
```
让我查看一下你最近的 exec 执行记录...

📋 最近 10 条 exec 命令：

1. 2026-02-10 15:30:45 | ls -la
2. 2026-02-10 15:28:12 | git status
3. 2026-02-10 15:25:33 | npm install
4. 2026-02-10 14:55:20 | grep '"name":"exec"' ~/.openclaw/agents/main/sessions/*.jsonl
5. 2026-02-10 14:50:10 | cat package.json
6. 2026-02-10 14:45:05 | pwd
7. 2026-02-10 14:40:22 | node --version
8. 2026-02-10 14:35:15 | docker ps
9. 2026-02-10 14:30:08 | tail -f logs/app.log
10. 2026-02-10 14:25:45 | find . -name "*.js"

📊 最常用的命令类型：
- git (15次)
- npm (12次)
- ls (10次)
- grep (8次)
- docker (5次)
```

## 技术细节

### Session 文件格式

Session 文件存储在 `~/.openclaw/agents/main/sessions/` 目录下，每个 session 对应一个 `.jsonl` 文件。

**Exec 工具调用记录结构**:

```json
{
  "type": "message",
  "id": "d3478fcf",
  "parentId": "9631fadb",
  "timestamp": "2026-02-05T12:15:25.206Z",
  "message": {
    "role": "assistant",
    "content": [
      {
        "type": "toolCall",
        "id": "call_2e8e8fa469e14f478aa15ae5",
        "name": "exec",
        "arguments": {
          "command": "ls -la"
        }
      }
    ],
    "api": "openai-completions",
    "provider": "friday-longcat",
    "model": "LongCat-Flash-Chat",
    "usage": {
      "input": 15688,
      "output": 21,
      "totalTokens": 15709
    },
    "stopReason": "toolUse",
    "timestamp": 1770293723959
  }
}
```

### 关键字段说明

- `timestamp`: ISO 8601 格式的执行时间
- `message.content[0].name`: 工具名称 (exec)
- `message.content[0].arguments.command`: 执行的命令
- `message.provider`: 使用的模型提供商
- `message.model`: 使用的具体模型
- `message.usage`: Token 使用统计

## 快速参考

```bash
# 创建便捷别名
alias exec-history='~/.openclaw/scripts/exec-history.sh'
alias exec-list='exec-history list'
alias exec-stats='exec-history stats'
alias exec-today='exec-history today'

# 使用示例
exec-list              # 查看最近执行的命令
exec-stats             # 查看统计信息
exec-search git        # 搜索 git 相关命令
exec-today             # 查看今天执行的命令
exec-history all-tools # 查看所有工具的使用统计
```

## 相关文件

- Session 文件: `~/.openclaw/agents/main/sessions/*.jsonl`
- Gateway 日志: `~/.openclaw/logs/gateway.log`
- Agent 配置: `~/.openclaw/agents/main/agent/`

## 注意事项

1. **隐私保护**: Session 文件包含所有命令历史，请妥善保管
2. **文件大小**: Session 文件会随时间增长，定期清理旧 session
3. **权限**: 确保有读取 session 文件的权限
4. **JSON 格式**: 使用 `jq` 工具处理 JSON 数据，请确保已安装

## 扩展功能

你可以基于这个 skill 创建：

- 🎨 Web UI 可视化工具
- 📊 命令执行时间线图表
- 🔔 异常命令监控告警
- 📝 自动生成操作日志报告
- 🔐 命令审计和合规检查

---

**版本**: 1.0.0  
**作者**: OpenClaw Community  
**最后更新**: 2026-02-10
