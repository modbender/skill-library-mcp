---
name: mini-agent
description: Mini-Max AI 编程助手 - 基于 MiniMax M2.5 模型的智能代码开发工具，支持文件操作、命令执行、代码编写等功能。适用于 OpenClaw Agent 系统。
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["mini-agent"] },
        "install":
          [
            {
              "id": "node",
              "kind": "node",
              "package": "mini-agent",
              "bins": ["mini-agent"],
              "label": "安装 Mini-Agent (uv)",
              "command": "uv tool install git+https://github.com/MiniMax-AI/Mini-Agent.git"
            },
          ],
      },
  }
---

# Mini-Agent Skill

## 概述

Mini-Agent 是一个基于 MiniMax M2.5 大语言模型的智能助手框架，专为 OpenClaw Agent 系统设计。它能够帮助你完成各种任务，包括文件操作、代码编写、系统管理等。

## 能力

### 1. 文件操作
- **读取文件**: 读取任意文本文件内容，支持大文件分块读取
- **写入文件**: 创建新文件或完全覆盖已有文件
- **编辑文件**: 使用精确字符串替换的方式修改文件内容

### 2. 命令执行
- **bash 命令**: 执行 Linux/Unix 系统命令
- **后台进程**: 支持启动和管理长时间运行的进程
- **进程监控**: 查看后台进程输出、终止进程

### 3. 知识管理
- **技能查询**: 获取其他 skill 的使用说明和内容
- **笔记记录**: 记录重要信息供后续参考

## 工作原理

```
用户请求 → LLM 思考 → 工具调用 → 执行结果 → 循环迭代 → 最终响应
```

1. **接收请求**: Mini-Agent 接收用户的自然语言指令
2. **智能分析**: LLM 分析任务需求，制定执行计划
3. **工具调用**: 根据需要调用合适的工具（read_file, write_file, bash 等）
4. **结果处理**: 分析工具执行结果，决定下一步操作
5. **循环迭代**: 重复执行直到任务完成

## 配置说明

### 配置文件位置
`~/.mini-agent/config/config.yaml`

### 配置项说明

```yaml
api_key: "your-api-key"      # MiniMax API 密钥
api_base: "https://api.minimaxi.com"  # API 端点地址
model: "MiniMax-M2.5"        # 使用的模型名称
```

### 工作目录
- **当前工作空间**: `/home/pi/.openclaw/agents/xiaoma`
- **所有相对路径**都以此目录为基准

## 使用方法

### 基本语法

由于 Mini-Agent 通常通过 OpenClaw 系统调用，你可以通过以下方式使用：

1. **通过 Agent 界面**: 在 OpenClaw Dashboard 中选择对应的 Agent
2. **通过 API**: 发送请求到 Agent 的 API 端点

### 示例命令

#### 文件操作示例

```bash
# 读取文件
读取 /home/pi/.openclaw/workspace/dashboard/index.html 文件

# 写入文件
在当前目录下创建一个新文件 test.md，内容为：# Test

# 编辑文件
修改 config.yaml 文件，将 model 字段改为 "MiniMax-M2.6"
```

#### 代码开发示例

```bash
# 帮我写一个 Python 脚本
写一个 Python 脚本，实现读取 CSV 文件并统计行数

# 修复 Bug
修复 /home/pi/project/main.py 中的空指针错误

# 代码审查
查看 /home/pi/project/utils.js 文件，给出代码优化建议
```

#### 系统操作示例

```bash
# 执行系统命令
列出当前目录下所有以 .md 结尾的文件

# 启动服务
在后台启动一个 HTTP 服务器，端口 8080
```

## 可用工具

| 工具名称 | 功能描述 |
|---------|---------|
| `read_file` | 读取文件内容 |
| `write_file` | 写入/创建文件 |
| `edit_file` | 编辑文件（精确替换） |
| `bash` | 执行 Shell 命令 |
| `bash_output` | 查看后台进程输出 |
| `bash_kill` | 终止后台进程 |
| `get_skill` | 获取其他技能说明 |
| `record_note` | 记录重要笔记 |

## 日志说明

### 日志位置
`~/.mini-agent/log/`

### 日志格式
日志文件采用时间戳命名，如：`agent_run_20260302_023022.log`

每个日志包含：
- **REQUEST**: LLM 收到的请求（包含 messages 和 tools）
- **RESPONSE**: LLM 的响应（包含思考过程和工具调用）
- **TOOL_RESULT**: 工具执行结果

## 最佳实践

### 1. 明确任务描述
- 提供清晰、具体的任务描述
- 说明期望的输出格式
- 指出需要注意的约束条件

### 2. 逐步完成任务
- 复杂任务拆分为多个简单步骤
- 每完成一步检查结果
- 及时修正方向

### 3. 利用上下文
- 可以在同一会话中连续操作
- Agent 会记住之前的操作和结果
- 合理利用可以提高效率

## 常见问题

### Q: Mini-Agent 支持哪些编程语言？
A: Mini-Agent 基于 LLM，理论上支持所有主流编程语言，包括但不限于 Python、JavaScript、Java、C++、Go、Rust 等。

### Q: 如何处理大文件？
A: 可以使用 `read_file` 的 `limit` 和 `offset` 参数分块读取大文件。

### Q: 后台进程如何管理？
A: 使用 `bash` 的 `run_in_background=true` 参数启动后台进程，通过 `bash_output` 查看输出，`bash_kill` 终止进程。

### Q: 如何查看历史操作？
A: 查看 `~/.mini-agent/log/` 目录下的日志文件。

## 相关链接

- [MiniMax 官网](https://www.minimaxi.com)
- [OpenClaw 项目](https://github.com/openclaw)
- 配置文件: `~/.mini-agent/config/config.yaml`
- 日志目录: `~/.mini-agent/log/`
