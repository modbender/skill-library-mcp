# OpenClaw Auto-Doctor

自动监控 OpenClaw 日志、诊断错误、搜索解决方案并自动修复问题的智能运维助手。

## 功能特性

- **实时日志监控** - 自动监控 OpenClaw 运行日志，实时捕获错误
- **智能错误解析** - 识别 JavaScript、Python、Go 等多种错误类型
- **多渠道搜索** - 在 GitHub Issues、社区论坛、官方文档中搜索解决方案
- **自动修复** - 对已知错误自动应用修复方案
- **自动创建 PR** - 无法自动修复时，自动生成修复代码并提交 Pull Request

## 安装

```bash
clawhub install openclaw-auto-doctor
```

## 配置

首次使用需要指定 OpenClaw 日志路径：

```yaml
# ~/.claude/openclaw-doctor.yaml
openclaw:
  log_paths:
    - ~/.openclaw/logs/gateway.log
    - ~/.openclaw/logs/gateway.err.log
```

## 使用方法

### 启动日志监控

```
请监控 OpenClaw 日志
```

### 分析错误

```
分析 OpenClaw 错误
```

### 检查状态

```
检查 OpenClaw 状态
```

## 支持的错误类型

| 错误类型 | 说明 |
|---------|------|
| MODULE_NOT_FOUND | 依赖模块缺失 |
| API Key 错误 | 认证配置问题 |
| JSON 解析错误 | 配置文件语法错误 |
| 连接错误 | 服务无法访问 |
| TypeError | JavaScript 类型错误 |
| Traceback | Python 异常 |

## 工作流程

```
检测错误 → 解析错误信息 → 搜索解决方案 → 应用修复 → 创建 PR
```

## 安全机制

- 修复前自动创建备份
- 不确定时请求用户确认
- 所有操作记录详细日志

## 相关链接

- [OpenClaw 官网](https://openclaude.ai)
- [OpenClaw GitHub](https://github.com/openclaudeai/openclaude)
- [ClawHub](https://clawhub.dev)

## 许可证

MIT License
