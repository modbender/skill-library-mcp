# Mini-Agent 配置指南

## 配置文件位置

所有配置文件位于 `~/.mini-agent/` 目录下：

```
~/.mini-agent/
├── config/
│   └── config.yaml      # 主配置文件
└── log/
    └── agent_run_*.log  # 运行日志
```

## 配置文件详解

### config.yaml

```yaml
api_key: "sk-cp-xxxxxxxxxxxxx"      # MiniMax API 密钥（必需）
api_base: "https://api.minimaxi.com" # API 端点（默认）
model: "MiniMax-M2.5"               # 使用的模型（默认）
```

#### 配置项说明

| 配置项 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| `api_key` | string | 是 | - | MiniMax API 密钥 |
| `api_base` | string | 否 | https://api.minimaxi.com | API 端点地址 |
| `model` | string | 否 | MiniMax-M2.5 | 使用的模型名称 |

## 获取 API 密钥

1. 访问 [MiniMax 开放平台](https://platform.minimaxi.com)
2. 注册/登录账号
3. 在控制台创建 API Key
4. 将密钥填入配置文件

## 环境变量

除了配置文件，也可以通过环境变量设置：

```bash
export MINIMAX_API_KEY="sk-cp-xxxxxxxxxxxxx"
export MINIMAX_API_BASE="https://api.minimaxi.com"
export MINIMAX_MODEL="MiniMax-M2.5"
```

## 工作目录

### 当前工作空间

Mini-Agent 的当前工作目录默认设置为：
```
/home/pi/.openclaw/agents/xiaoma
```

所有相对路径都会以此目录为基准进行解析。

### 修改工作目录

在工作指令中指定绝对路径，或在调用时设置不同的初始路径。

## 日志配置

### 日志位置
```
~/.mini-agent/log/
```

### 日志命名格式
```
agent_run_YYYYMMDD_HHMMSS.log
```

例如：`agent_run_20260302_023022.log`

### 日志内容

每个日志文件记录单次运行的完整过程：

1. **请求信息 (REQUEST)**: 用户发送的消息和可用工具
2. **响应信息 (RESPONSE)**: LLM 的思考过程和工具调用
3. **工具结果 (TOOL_RESULT)**: 工具执行的详细结果

### 日志示例

```
================================================================================
Agent Run Log - 2026-03-02 02:30:22
================================================================================

--------------------------------------------------------------------------------
[1] REQUEST
Timestamp: 2026-03-02 02:30:22.582
--------------------------------------------------------------------------------
LLM Request:

{
  "messages": [...],
  "tools": ["bash", "read_file", "write_file", ...]
}

--------------------------------------------------------------------------------
[2] RESPONSE
Timestamp: 2026-03-02 02:30:25.304
--------------------------------------------------------------------------------
LLM Response:

{
  "thinking": "用户想要修改文件...",
  "tool_calls": [...]
}
```

## 高级配置

### 自定义工具

Mini-Agent 支持扩展工具，可以通过配置文件添加自定义工具。

### 调试模式

查看详细日志可以帮助调试问题：

```bash
# 查看最新日志
tail -f ~/.mini-agent/log/agent_run_*.log

# 查看特定时间段的日志
grep "ERROR" ~/.mini-agent/log/agent_run_*.log
```

## 常见问题

### Q: 如何修改 API 密钥？
A: 直接编辑 `~/.mini-agent/config/config.yaml` 文件中的 `api_key` 值。

### Q: 日志文件占用太多空间怎么办？
A: 可以定期清理旧日志文件，或配置日志轮转。

### Q: 如何切换不同的模型？
A: 修改配置文件中的 `model` 字段为其他可用的模型名称。

### Q: API 请求失败怎么办？
A: 检查：
1. 网络连接是否正常
2. API 密钥是否有效
3. API 配额是否用完
4. 查看日志中的错误信息
