# SafeExec 详细文档

> 完整的使用指南、配置说明、开发文档和常见问题

**主文档：** [README.md](README.md) | **变更日志：** [CHANGELOG.md](CHANGELOG.md)

---

## 📑 目录

- [使用指南](#使用指南)
  - [工作原理](#工作原理)
  - [批准工作流](#批准工作流)
  - [风险等级详解](#风险等级详解)
  - [全局控制](#全局控制)
- [高级配置](#高级配置)
  - [环境变量](#环境变量)
  - [自定义规则](#自定义规则)
  - [非交互式模式](#非交互式模式)
- [开发文档](#开发文档)
  - [架构设计](#架构设计)
  - [文件说明](#文件说明)
  - [API 参考](#api-参考)
  - [贡献指南](#贡献指南)
- [常见问题](#常见问题)
  - [故障排查](#故障排查)
  - [最佳实践](#最佳实践)
  - [性能优化](#性能优化)

---

## 使用指南

### 工作原理

SafeExec 通过以下步骤保护你的系统：

```
1. 命令拦截
   ↓
2. 模式匹配
   ↓
3. 风险评估
   ↓
4. 决策
   ├── 安全 → 直接执行
   └── 危险 → 请求批准
```

#### 架构组件

```
~/.openclaw/safe-exec/
├── pending/              # 待处理的批准请求
│   └── req_*.json       # 请求详情文件
├── safe-exec-rules.json # 规则配置文件
└── safe-exec-audit.log  # 审计日志

~/.openclaw/safe-exec-known-*.txt  # 监控追踪文件
```

### 批准工作流

#### 1. 危险命令检测

当 Agent 尝试执行危险命令时：

```
🚨 **危险操作检测 - 命令已拦截**

**风险等级:** CRITICAL
**命令:** `rm -rf /tmp/test`
**原因:** 递归删除，使用 force 标志

**请求 ID:** `req_1769938492_9730`

ℹ️  此命令需要用户批准才能执行。

**批准方法:**
1. 在终端运行: `safe-exec-approve req_1769938492_9730`
2. 或者: `safe-exec-list` 查看所有待处理请求

**拒绝方法:**
 `safe-exec-reject req_1769938492_9730`
```

#### 2. 批准请求

```bash
# 方法 1: 使用请求 ID
safe-exec-approve req_1769938492_9730

# 方法 2: 列出并批准最近的请求
safe-exec-list
# 输出所有待处理的请求，然后使用 ID 批准
```

#### 3. 命令执行

批准后，命令会执行并记录到审计日志。

### 风险等级详解

#### 🔴 CRITICAL（危急）

系统破坏性命令，需要明确批准：

- `rm -rf /` - 删除根目录
- `dd if=/dev/zero` - 磁盘覆盖
- `mkfs.*` - 格式化文件系统
- `:(){ :|:& };:` - Fork bomb
- `> /dev/sda` - 直接写入磁盘

#### 🟠 HIGH（高危）

可能导致数据丢失或系统变动的命令：

- `rm -rf` (非根目录) - 递归删除
- `chmod 777` - 设置全局可写权限
- `curl | bash` - 管道下载到 shell
- 写入 `/etc/`, `/boot/`, `/sys/` - 系统目录修改
- `wget | sh` - 下载并执行脚本

#### 🟡 MEDIUM（中危）

需要特权或影响系统的操作：

- `sudo` - 使用特权执行
- `iptables`, `firewall-cmd`, `ufw` - 防火墙修改
- `systemctl` - 服务管理
- `crontab -e` - 定时任务编辑

#### 🟢 LOW（低危）

相对安全的操作，可能无需批准：

- `ls`, `cat`, `grep` - 读取操作
- `cp`, `mv` (非系统目录) - 文件操作
- `mkdir`, `touch` - 创建操作
- `cd`, `pwd` - 导航操作

### 全局控制

#### 启用/禁用 SafeExec

**对话式：**
```
Enable SafeExec   # 启用
Disable SafeExec  # 禁用
```

**脚本式：**
```bash
~/.openclaw/skills/safe-exec/safe-exec.sh --enable
~/.openclaw/skills/safe-exec/safe-exec.sh --disable
```

**环境变量：**
```bash
export SAFE_EXEC_DISABLE=1  # 禁用
unset SAFE_EXEC_DISABLE     # 启用
```

#### 查看状态

```bash
# 查看待处理的请求
safe-exec-list

# 查看审计日志（最近 50 条）
tail -n 50 ~/.openclaw/safe-exec-audit.log

# 查看配置
cat ~/.openclaw/safe-exec-rules.json
```

---

## 高级配置

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SAFE_EXEC_DISABLE` | 全局禁用 SafeExec | 未设置 |
| `OPENCLAW_AGENT_CALL` | 标识 Agent 调用（自动检测） | 自动 |
| `SAFE_EXEC_AUTO_CONFIRM` | 自动批准 LOW/MEDIUM 风险 | 未设置 |
| `SAFEXEC_CONTEXT` | 用户上下文信息 | 空 |

**使用示例：**

```bash
# 自动批准低中风险命令
export SAFE_EXEC_AUTO_CONFIRM=1

# 在 Agent 中使用（自动设置）
export OPENCLAW_AGENT_CALL=1

# 完全禁用
export SAFE_EXEC_DISABLE=1
```

### 自定义规则

编辑 `~/.openclaw/safe-exec-rules.json`：

```json
{
  "enabled": true,
  "rules": [
    {
      "pattern": "docker rm.*-f",
      "risk": "medium",
      "reason": "强制删除 Docker 容器"
    },
    {
      "pattern": "kubectl delete",
      "risk": "high",
      "reason": "删除 Kubernetes 资源"
    }
  ]
}
```

### 非交互式模式

在非交互式环境（如 Agent 调用）中：

1. **TTY 检测**：SafeExec 自动检测是否在交互式终端
2. **环境检测**：检测 `OPENCLAW_AGENT_CALL` 环境变量
3. **智能跳过**：在非交互式环境中跳过二次确认

```bash
# Agent 调用时自动启用非交互模式
export OPENCLAW_AGENT_CALL=1
```

---

## 开发文档

### 架构设计

```
┌─────────────┐
│   Agent     │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  safe-exec.sh    │ ← 主入口
└──────┬───────────┘
       │
       ▼
┌────────────────────┐
│  风险评估引擎      │
│  - 模式匹配        │
│  - 上下文分析      │
└──────┬─────────────┘
       │
       ▼
   ┌───┴────┐
   │ 危险？  │
   └───┬────┘
     是 │   │ 否
        │   └──────────→ 直接执行
        ▼
┌──────────────┐
│ 请求批准     │
│ - 写入 pending│
│ - 通知用户   │
└──────────────┘
```

### 文件说明

#### 核心脚本

| 文件 | 功能 |
|------|------|
| `safe-exec.sh` | 主执行脚本，命令拦截和风险评估 |
| `safe-exec-approve.sh` | 批准请求的脚本 |
| `safe-exec-reject.sh` | 拒绝请求的脚本 |
| `safe-exec-list.sh` | 列出待处理的请求 |
| `safe-exec-check-pending.sh` | 检查待处理请求 |

#### 文档文件

| 文件 | 说明 |
|------|------|
| `README.md` | 主要文档，快速开始 |
| `README-detail.md` | 本文档，详细说明 |
| `CHANGELOG.md` | 版本变更日志 |
| `SKILL.md` | ClawdHub skill 描述 |
| `CONTRIBUTING.md` | 贡献指南 |

#### 配置和数据

| 文件/目录 | 说明 |
|-----------|------|
| `~/.openclaw/safe-exec-rules.json` | 规则配置 |
| `~/.openclaw/safe-exec-audit.log` | 审计日志 |
| `~/.openclaw/safe-exec/pending/` | 待处理请求 |

### API 参考

#### safe-exec.sh

```bash
# 执行命令
safe-exec.sh "command"

# 启用/禁用
safe-exec.sh --enable
safe-exec.sh --disable
safe-exec.sh --status
```

#### safe-exec-approve.sh

```bash
# 批准请求
safe-exec-approve.sh <request_id>

# 查看详情
safe-exec-approve.sh --list
```

#### safe-exec-list.sh

```bash
# 列出所有待处理请求
safe-exec-list.sh

# 仅显示 CRITICAL 级别
safe-exec-list.sh --critical
```

### 贡献指南

#### 开发环境设置

```bash
# 1. Fork 并克隆仓库
git clone https://github.com/OTTTTTO/safe-exec.git
cd safe-exec

# 2. 创建功能分支
git checkout -b feature/my-feature

# 3. 测试修改
./test-safeexec.sh

# 4. 提交更改
git commit -m "feat: Add my feature"

# 5. 推送并创建 PR
git push origin feature/my-feature
```

#### 代码规范

- Bash 脚本遵循 [ShellCheck](https://www.shellcheck.net/) 建议
- 文档使用 Markdown 格式
- 提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/)

#### 测试

```bash
# 运行所有测试
./test-safeexec.sh

# 运行特定测试
./test-regression.sh
./test-context-aware.sh
```

---

## 常见问题

### 故障排查

#### Q: SafeExec 没有拦截命令

**A:** 检查以下几点：

1. 是否已启用？
```bash
~/.openclaw/skills/safe-exec/safe-exec.sh --status
```

2. 是否被环境变量禁用？
```bash
echo $SAFE_EXEC_DISABLE
```

3. 命令是否在白名单中？

#### Q: 批准命令后没有执行

**A:** 可能的原因：

1. 请求已超时（5分钟）
2. 命令语法错误
3. 权限不足

查看审计日志：
```bash
tail -f ~/.openclaw/safe-exec-audit.log
```

#### Q: 如何重置所有状态？

**A:** 删除数据文件：
```bash
rm -rf ~/.openclaw/safe-exec/
rm ~/.openclaw/safe-exec-*
```

### 最佳实践

#### 1. 生产环境使用

```bash
# 启用自动确认低中风险操作
export SAFE_EXEC_AUTO_CONFIRM=1

# 定期备份审计日志
cp ~/.openclaw/safe-exec-audit.log ~/.backup/
```

#### 2. 多用户环境

为每个用户配置独立的规则文件：
```bash
export SAFE_EXEC_RULES_FILE="/home/user/.safe-exec-rules.json"
```

#### 3. 与其他工具集成

**与 sudo 集成：**
```bash
# 在 sudoers 中添加
Defaults secure_path = /usr/local/bin:/usr/bin:/bin
```

**与日志系统集成：**
```bash
# 将审计日志发送到 rsyslog
tail -f ~/.openclaw/safe-exec-audit.log | logger -t safeexec
```

### 性能优化

#### 减少延迟

```bash
# 使用更快的磁盘存储
export SAFE_EXEC_DIR="/dev/shm/safe-exec"
```

#### 定期清理

```bash
# 清理过期的 pending 请求
find ~/.openclaw/safe-exec/pending/ -mtime +1 -delete

# 压缩旧日志
logrotate ~/.openclaw/safe-exec-audit.log
```

---

## 附录

### 相关资源

- [OpenClaw 文档](https://docs.openclaw.ai/)
- [ClawdHub 市场](https://www.clawhub.ai/skills)
- [Bash 最佳实践](https://github.com/koalaman/shellcheck)

### 社区

- **GitHub Issues**: https://github.com/OTTTTTO/safe-exec/issues
- **Discussions**: https://github.com/OTTTTTO/safe-exec/discussions
- **Email**: 731554297@qq.com

### 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**最后更新:** 2026-02-01
**维护者:** OTTTTTO
**版本:** v0.3.1
