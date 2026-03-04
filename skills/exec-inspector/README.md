# Exec Inspector - OpenClaw 工具执行监控器

一个强大的工具，用于查看和分析 OpenClaw Agent 的 exec 工具执行历史和明细。

## 🚀 快速开始

### 安装

脚本已经安装在：`~/.openclaw/scripts/exec-history.sh`

### 添加便捷别名（推荐）

将以下内容添加到你的 `~/.zshrc` 或 `~/.bashrc`:

```bash
# OpenClaw Exec History 别名
alias exec-history='~/.openclaw/scripts/exec-history.sh'
alias exec-list='~/.openclaw/scripts/exec-history.sh list'
alias exec-stats='~/.openclaw/scripts/exec-history.sh stats'
alias exec-today='~/.openclaw/scripts/exec-history.sh today'
alias exec-search='~/.openclaw/scripts/exec-history.sh search'
```

然后执行 `source ~/.zshrc` 或 `source ~/.bashrc` 使别名生效。

## 📖 功能说明

### 1. 列出最近执行的命令

```bash
exec-history list
# 或
~/.openclaw/scripts/exec-history.sh list
```

**输出示例**:
```
📋 Recent exec commands (last 20):
  1. 2026-02-10 15:30:45 | ls -la
  2. 2026-02-10 15:28:12 | git status
  3. 2026-02-10 15:25:33 | npm install
  ...
```

### 2. 查看命令使用统计

```bash
exec-history stats
```

**输出示例**:
```
📊 Command usage statistics:

   4  null
   3  ls
   3  claude
   2  mc
   2  cd
   1  which
   ...

Total exec commands: 19
```

### 3. 搜索特定命令

```bash
exec-history search git
# 搜索包含 "git" 的所有命令
```

**输出示例**:
```
🔍 Searching for commands containing: git

  1. 2026-02-10 15:28:12 | git status
  2. 2026-02-10 14:45:30 | git pull origin main
  3. 2026-02-10 12:20:15 | git commit -m "update"
```

### 4. 查看今天执行的命令

```bash
exec-history today
```

**输出示例**:
```
📅 Commands executed today (2026-02-10):

  1. 15:30:45 | ls -la
  2. 15:28:12 | git status
  3. 15:25:33 | npm install
```

### 5. 查看 Session 列表和详情

```bash
# 列出所有 sessions
exec-history session

# 查看特定 session 的执行历史
exec-history session aa19ccb2-19ff-4458-84b4-d20e688fd797
```

**输出示例**:
```
Available sessions:

3a7ecd6c-6f6c-4f45-8ed0-f05366ba5523     |   5 execs | 2026-02-10 15:49
dev-session                              |   0 execs | 2026-02-10 10:30
aa19ccb2-19ff-4458-84b4-d20e688fd797     |  13 execs | 2026-02-05 22:55
```

### 6. 查看所有工具的使用统计

```bash
exec-history all-tools
```

**输出示例**:
```
🔧 All tool usage statistics:

  20  exec
  10  browser
   8  read
   3  write
   3  process
   1  edit
```

### 7. 查看命令详细信息

```bash
# 查看最近第 5 条命令的详细信息
exec-history detail 5
```

**输出**: 完整的 JSON 记录，包括模型信息、token 使用等

### 8. 导出执行历史

```bash
# 导出为 JSON 文件
exec-history export

# 导出到指定文件
exec-history export my-history.json
```

### 9. 查看执行时间线图表

```bash
exec-history chart
```

**输出示例**:
```
📊 Command execution timeline (last 7 days):

2026-02-04 |   0 █
2026-02-05 |  13 ███
2026-02-06 |   0 █
2026-02-07 |   0 █
2026-02-08 |   0 █
2026-02-09 |   1 █
2026-02-10 |   5 ██
```

## 💡 使用场景

### 场景 1: 查看最近做了什么

```bash
exec-list
```

快速查看最近 20 条执行过的命令。

### 场景 2: 分析命令使用习惯

```bash
exec-stats
```

查看哪些命令用得最多，优化工作流程。

### 场景 3: 查找某个命令的执行记录

```bash
exec-search docker
```

找出所有与 docker 相关的命令执行记录。

### 场景 4: 审计今天的操作

```bash
exec-today
```

回顾今天执行了哪些命令。

### 场景 5: 分析特定 session 的操作

```bash
# 先列出所有 sessions
exec-history session

# 选择一个 session 查看详情
exec-history session aa19ccb2-19ff-4458-84b4-d20e688fd797
```

### 场景 6: 导出历史记录用于分析

```bash
exec-history export analysis-$(date +%Y%m%d).json
```

导出所有历史记录，用于数据分析或存档。

## 🎨 高级用法

### 结合其他工具使用

```bash
# 查看包含错误的命令
exec-list | grep -i error

# 统计 git 命令的使用频率
exec-search git | wc -l

# 查看最近的 npm 命令
exec-search npm | tail -10
```

### 创建自定义分析脚本

```bash
#!/bin/bash
# 每日命令执行报告

echo "=== 每日命令执行报告 ==="
echo ""
echo "今天执行的命令："
exec-today
echo ""
echo "本周命令统计："
exec-history chart
echo ""
echo "最常用的命令："
exec-stats
```

## 🔧 技术细节

### Session 文件位置

```
~/.openclaw/agents/main/sessions/
├── 3a7ecd6c-6f6c-4f45-8ed0-f05366ba5523.jsonl
├── aa19ccb2-19ff-4458-84b4-d20e688fd797.jsonl
├── dev-session.jsonl
└── sessions.json
```

### 数据格式

每个 exec 工具调用记录包含：

- **timestamp**: 执行时间
- **command**: 执行的命令
- **provider**: 使用的模型提供商
- **model**: 使用的具体模型
- **usage**: Token 使用统计
- **stopReason**: 停止原因

### 依赖工具

- `jq`: JSON 处理工具（必需）
- `grep`: 文本搜索工具（系统自带）
- `awk`: 文本处理工具（系统自带）

## 🐛 故障排查

### 问题 1: 命令找不到

```bash
# 确认脚本存在
ls -l ~/.openclaw/scripts/exec-history.sh

# 确认有执行权限
chmod +x ~/.openclaw/scripts/exec-history.sh
```

### 问题 2: jq 未安装

```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq
```

### 问题 3: 没有数据显示

```bash
# 检查 session 文件是否存在
ls -l ~/.openclaw/agents/main/sessions/

# 检查是否有 exec 记录
grep -c '"name":"exec"' ~/.openclaw/agents/main/sessions/*.jsonl
```

## 📚 相关资源

- [SKILL.md](./SKILL.md) - 完整的 skill 说明文档
- [OpenClaw 官方文档](https://docs.openclaw.ai)
- [OpenClaw Agent 指南](../../docs/guides/OPENCLAW_AGENT_GUIDE.md)

## 🎯 未来功能

计划添加的功能：

- [ ] Web UI 可视化界面
- [ ] 命令执行成功率统计
- [ ] 异常命令自动检测
- [ ] 执行时长分析
- [ ] 命令模式识别和推荐
- [ ] 与其他监控工具集成

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**版本**: 1.0.0  
**作者**: OpenClaw Community  
**许可证**: MIT  
**最后更新**: 2026-02-10
