# SubAgent 创建脚本

此脚本帮助快速创建 SubAgent。

## 用法

```powershell
# 基础用法
.\create-subagent.ps1 "dev-agent" "你是一个开发助手..."

# 使用预设模板
.\create-subagent.ps1 -preset dev
.\create-subagent.ps1 -preset research
.\create-subagent.ps1 -preset writer
.\create-subagent.ps1 -preset data

# 自定义配置
.\create-subagent.ps1 -label "my-agent" -mode "session"
```

## 预设模板

| 预设 | 描述 |
|------|------|
| `dev` | 代码开发助手 |
| `research` | 研究助手 |
| `writer` | 写作助手 |
| `data` | 数据分析 |

## 参数

- `-label` - SubAgent 标签名
- `-task` - SubAgent 任务描述
- `-preset` - 使用预设模板
- `-mode` - run 或 session (默认 run)
- `-cleanup` - delete 或 keep (默认 keep)
