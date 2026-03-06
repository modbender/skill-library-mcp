# OpenCode 快速参考

## 环境设置
```bash
export PATH="/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
```

## 常用命令

### 快速任务
```bash
# 单次任务
opencode run "添加错误处理"

# 指定目录
opencode run --dir ~/project "重构代码"

# 指定模型
opencode run -m openai/gpt-4o "优化查询"

# 附加文件
opencode run -f file1.js -f file2.js "修复 bug"

# 继续上次会话
opencode run --continue
```

### 交互模式
```bash
# 启动 TUI
opencode

# 指定项目
opencode ~/path/to/project

# 指定模型
opencode -m anthropic/claude-sonnet-4
```

### TUI Slash 命令（交互模式专用）

在 TUI 模式下，使用以下命令控制 AI 工作流：

```bash
# 会话管理
/sessions          # 选择/创建会话

# Agent 控制
/agents            # 切换 agent (plan/build/explore/general)

# 模型选择
/models            # 选择模型

# 其他命令
/title             # 修改会话标题
/summary           # 生成会话摘要
/compaction        # 压缩对话历史
```

**Agent 工作流**：
1. `/agents` → 选择 **plan**
2. 描述任务，审查计划
3. `/agents` → 切换到 **build**
4. 实现计划
5. 如有问题，返回 plan

**可用 Agents**：
- `plan` - 规划模式（分析和设计）
- `build` - 构建模式（实现和编码）
- `explore` - 探索模式（理解代码库）
- `general` - 通用助手

### 会话管理
```bash
# 列出会话
opencode session list

# 删除会话
opencode session delete <sessionID>

# 导出会话
opencode export [sessionID]

# 导入会话
opencode import <file>
```

### 模型
```bash
# 列出所有模型
opencode models

# 特定提供商
opencode models openai
opencode models anthropic

# 详细信息（包含成本）
opencode models --verbose
```

### 认证
```bash
# 列出凭证
opencode auth list

# 登录
opencode auth login [url]

# 登出
opencode auth logout
```

### GitHub
```bash
# 处理 PR
opencode pr 123

# GitHub 管理
opencode github --help
```

### 服务器模式
```bash
# 无头服务器
opencode serve

# Web 界面
opencode web

# ACP 服务器
opencode acp
```

### MCP
```bash
# 列出服务器
opencode mcp list

# 添加服务器
opencode mcp add

# 认证
opencode mcp auth [name]
```

### 统计
```bash
# 使用统计
opencode stats
```

## 常用选项

| 选项 | 说明 |
|------|------|
| `-m, --model` | 模型（格式：provider/model） |
| `-c, --continue` | 继续上次会话 |
| `-s, --session` | 继续指定会话 |
| `--fork` | 分支会话 |
| `--agent` | 使用特定 agent |
| `--dir` | 工作目录 |
| `--format` | 输出格式（default/json） |
| `--thinking` | 显示思考过程 |
| `--variant` | 推理强度（high/max/minimal） |

## 模型格式

```
provider/model
```

示例：
- `openai/gpt-4o`
- `anthropic/claude-sonnet-4`
- `google/gemini-2.5-pro`
- `opencode/gpt-4o`

## 推理强度

```bash
opencode run --variant high "复杂算法"
opencode run --variant max "架构设计"
opencode run --variant minimal "快速审查"
```

## JSON 模式

```bash
opencode run --format json "重构代码" | jq .
```

## 故障排除

### sysctl 未找到
```bash
export PATH="/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
```

### 查看版本
```bash
opencode --version
```

### 查看帮助
```bash
opencode --help
opencode <command> --help
```

## 实用模式

### 代码重构
```bash
opencode run "重构这个函数，使其更易读"
```

### 添加功能
```bash
opencode run "添加用户注册的 API 端点"
```

### 修复 Bug
```bash
opencode run -f error.log "修复日志中的错误"
```

### 代码审查
```bash
opencode run "审查这个代码的安全性"
```

### PR 工作流
```bash
opencode pr 123
```

### 继续工作
```bash
opencode run --continue
opencode run --session abc123 --fork
```

## Web 界面

```bash
# 默认设置
opencode web

# 自定义端口
opencode web --port 8080

# 自定义主机
opencode web --hostname 0.0.0.0
```

## 提示

1. **具体提示** = 更好结果
2. **附加文件** = 更多上下文
3. **使用会话** = 保持连续性
4. **尝试分支** = 安全实验
5. **监控成本** = `opencode stats`

---

*快速参考 - OpenCode Skill*
