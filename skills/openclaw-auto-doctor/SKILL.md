---
name: openclaw-auto-doctor
description: 实时监控 OpenClaw 日志，自动诊断错误，搜索解决方案，并自动修复问题或创建 Pull Request
version: 1.0.0
model: sonnet
---

# OpenClaw Auto-Doctor

作为 OpenClaw 的智能运维助手，本 skill 能够自动监控 OpenClaw 日志、诊断错误、搜索解决方案并尝试自动修复。

## 触发条件

当用户请求以下操作时使用此 skill：
- "监控 OpenClaw 日志"
- "启动 OpenClaw 医生"
- "分析 OpenClaw 错误"
- "诊断 OpenClaw 问题"
- "检查 OpenClaw 状态"
- 或者直接提及 OpenClaw 相关的错误/问题

## 核心功能

### 1. 日志监控

**启动监控**：
```
使用 tail -f 命令实时监控指定的 OpenClaw 日志文件
```

**配置日志路径**：
首次使用时，需要用户指定 OpenClaw 的日志文件路径，例如：
- `~/openclaw/logs/claude-code.log`
- `~/openclaw/logs/error.log`
- 或其他用户指定的路径

### 2. 错误识别与解析

能够识别以下类型的错误：
- JavaScript/TypeScript 异常（Error, TypeError, ReferenceError 等）
- Python 异常（Traceback）
- Go panic
- 系统错误（ENOENT, EACCES, ECONNREFUSED 等）
- HTTP 错误（4xx, 5xx）
- 自定义 OpenClaw 错误码

**提取信息**：
- 错误类型和消息
- 错误堆栈跟踪
- 发生位置（文件、行号、列号）
- 时间戳
- 上下文代码

### 3. 智能搜索解决方案

按优先级搜索以下渠道：

1. **本地解决方案库** - 已知的错误和修复方案
2. **GitHub Issues** - 使用 GitHub API 搜索相关 issues
   ```
   搜索关键词：错误消息 + OpenClaw
   筛选：state:closed（已解决）
   ```
3. **GitHub Pull Requests** - 搜索已合并的修复
4. **OpenClaw 社区** - 搜索社区讨论
5. **官方文档** - 搜索故障排除文档

### 4. 自动修复

**修复策略**：

| 错误类型 | 修复方式 |
|---------|---------|
| 依赖缺失 | 执行 npm install / pip install 等 |
| 配置错误 | 修改配置文件 |
| 权限问题 | 修复文件/目录权限 |
| 服务未启动 | 启动相关服务 |
| 代码 bug | 生成补丁文件 |

**安全机制**：
- 修复前创建备份
- 修复后验证结果
- 失败时回滚

### 5. 自动创建 Pull Request

当无法自动修复时：
1. 分析错误根因
2. 生成修复代码
3. Fork OpenClaw 仓库
4. 创建分支并提交更改
5. 创建 Pull Request 并关联相关 Issue

## 工作流程

### 完整工作流

```
1. 接收用户请求或检测到新错误
         │
         ▼
2. 解析错误信息（类型、消息、堆栈）
         │
         ▼
3. 检查本地解决方案库
    ├── 找到方案 → 应用修复 → 验证 → 通知用户
    │
    ▼
4. 多渠道搜索解决方案
    ├── 找到高置信度方案 → 用户确认 → 应用修复
    │
    ▼
5. 自主分析尝试修复
    ├── 成功 → 创建 PR → 通知用户
    │
    ▼
6. 无法修复 → 详细报告给用户
```

### 命令参考

- **启动监控**: `tail -f <日志路径>`
- **搜索 Issues**: `gh search issues --repo openclaudeai/openclaude --state closed --match <错误关键词>`
- **查看日志**: 读取用户指定的日志文件路径

## 响应格式

### 发现错误时

```markdown
## 🚨 检测到新错误

**错误类型**: TypeError
**消息**: Cannot read property 'foo' of undefined
**位置**: src/index.ts:42:5
**时间**: 2024-01-15T10:30:00Z

### 搜索解决方案中...
[显示搜索进度]
```

### 找到解决方案时

```markdown
## ✅ 找到解决方案

**来源**: GitHub Issue #123
**方案**: 更新依赖包版本
**修复方式**:
```bash
npm update openclaude-sdk
```

是否立即应用修复？
```

### 修复成功时

```markdown
## ✅ 修复成功

**错误**: Cannot find module 'openclaude-sdk'
**修复**: 执行 npm install
**验证**: OpenClaw 已正常运行

[可选] 已自动创建 PR: https://github.com/openclaudeai/openclaude/pull/xxx
```

### 无法修复时

```markdown
## ⚠️ 需要人工协助

**错误**: [错误描述]
**尝试过的方案**:
1. 搜索 GitHub Issues - 无相关解决方案
2. 搜索社区论坛 - 无有效答案

**建议**:
- 检查 OpenClaw 版本是否过旧
- 在 GitHub 提交 Issue 寻求帮助
- 查看官方文档了解更多

如需我尝试生成修复代码，请回复 "尝试修复"
```

## 配置项

用户可以配置以下选项（存储在 ~/.claude/openclaw-doctor.yaml）：

```yaml
openclaw:
  log_paths:
    - ~/openclaw/logs/main.log
    - ~/openclaw/logs/error.log

github:
  repository: openclaudeai/openclaude

auto_fix:
  enabled: true
  require_confirmation: true
  backup_before_fix: true
```

## 重要提示

1. **安全优先**: 所有自动修复都会先创建备份
2. **透明操作**: 所有操作都会记录并告知用户
3. **学习能力**: 成功修复的方案会加入解决方案库
4. **用户控制**: 用户可以随时中断或调整自动化程度

## 注意事项

- 本 skill 需要用户配置 OpenClaw 日志路径
- 自动创建 PR 需要 GitHub 认证（使用 gh auth）
- 某些修复可能需要管理员权限
- 修复后请验证 OpenClaw 是否正常工作
