---
name: glm-plan-usage
displayName: GLM Plan Usage
version: 1.0.0
description: 查询 GLM 编码套餐使用统计，包括配额、模型使用和 MCP 工具使用情况 | Query GLM coding plan usage statistics, including quota, model usage, and MCP tool usage
author: OpenClaw Community
license: MIT
tags:
  - glm
  - usage
  - monitoring
  - statistics
  - zhipu
  - chinese
  - english
requirements:
  - curl
  - jq
---

# GLM Plan Usage Skill

查询 GLM 编码套餐使用统计的 OpenClaw 技能。
OpenClaw skill for querying GLM coding plan usage statistics.

## 功能特性 / Features

- **配额监控**: 查看 Token 使用量（5小时）和 MCP 使用量（1个月）
  **Quota Monitoring**: View token usage (5-hour) and MCP usage (1-month)
- **模型使用**: 显示 24 小时内的 Token 数和调用次数
  **Model Usage**: Display token count and call count within 24 hours
- **工具使用**: 跟踪 24 小时内的 MCP 工具使用情况
  **Tool Usage**: Track MCP tool usage within 24 hours
- **自动检测**: 自动从 OpenClaw 配置中检测 GLM 编码套餐提供商
  **Auto Detection**: Automatically detect GLM coding plan provider from OpenClaw configuration
- **双语支持**: 支持中文和英文输出
  **Bilingual Support**: Support Chinese and English output

## 依赖要求 / Requirements

- **curl** - HTTP 客户端（通常预装） | HTTP client (usually pre-installed)
- **jq** - JSON 处理器 | JSON processor

如需安装 `jq`：
To install `jq`:
```bash
sudo apt-get install jq  # Linux
brew install jq           # macOS
```

## 安装 / Installation

1. 将此仓库克隆到本地：
   Clone this repository to local:
```bash
git clone https://github.com/OrientLuna/openclaw-glm-plan-usage.git
cd openclaw-glm-plan-usage
```

2. 复制技能文件到 OpenClaw 技能目录：
   Copy skill files to OpenClaw skills directory:
```bash
cp -r . ~/.openclaw/skills/glm-plan-usage/
chmod +x ~/.openclaw/skills/glm-plan-usage/scripts/query-usage.sh
```

3. 确保已配置 GLM 编码套餐提供商（见下方配置说明）
   Ensure GLM coding plan provider is configured (see Configuration below)

## 使用方法 / Usage

### 直接运行脚本 / Run Script Directly

```bash
bash ~/.openclaw/skills/glm-plan-usage/scripts/query-usage.sh
```

### 通过 OpenClaw 技能调用 / Via OpenClaw Skill

```bash
openclaw /glm-plan-usage:usage-query
```

### 语言切换 / Language Switching

脚本会自动检测语言环境。您也可以通过环境变量强制指定语言：
The script automatically detects language environment. You can also force language via environment variable:

```bash
# 中文输出 / Chinese output
OPENCLAW_LANGUAGE=zh bash ~/.openclaw/skills/glm-plan-usage/scripts/query-usage.sh

# 英文输出 / English output
OPENCLAW_LANGUAGE=en bash ~/.openclaw/skills/glm-plan-usage/scripts/query-usage.sh
```

### 示例输出 / Sample Output

```
📊 GLM 编码套餐使用统计 / GLM Coding Plan Usage Statistics

提供商 / Provider: zhipu
统计时间 / Statistics Time: 2026-02-13 20:30:15

配额限制 / Quota Limits
---
  Token 使用 (5小时) / Token Usage (5-hour): 45.2%
  MCP 使用 (1个月) / MCP Usage (1-month):   12.3%  (15000/120000 秒 / sec) [LEVEL_4]

模型使用 (24小时) / Model Usage (24 hours)
---
  总 Token 数 / Total Tokens:  12,500,000
  总调用次数 / Total Calls:  1,234

工具使用 (24小时) / Tool Usage (24 hours)
---
  bash: 156 次 / times
  file-read: 89 次 / times
  web-search: 34 次 / times
```

## 配置说明 / Configuration

技能会自动读取 `~/.openclaw/openclaw.json` 中的提供商配置。
The skill automatically reads provider configuration from `~/.openclaw/openclaw.json`.

### 示例配置 / Sample Configuration

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "zhipu/glm-4-flash"
      }
    }
  },
  "models": {
    "providers": {
      "zhipu": {
        "baseUrl": "https://open.bigmodel.cn/api/coding/paas/v4",
        "apiKey": "your-api-key-here"
      }
    }
  }
}
```

**重要**: `baseUrl` 必须包含 `api/coding/paas/v4` 或 `open.bigmodel.cn`，技能才能识别其为 GLM 编码套餐提供商。
**Important**: `baseUrl` must contain `api/coding/paas/v4` or `open.bigmodel.cn` for the skill to recognize it as a GLM coding plan provider.

### 提供商检测逻辑 / Provider Detection Logic

技能会检查以下条件来识别 GLM 编码套餐提供商：
The skill checks the following conditions to identify GLM coding plan providers:

1. `baseUrl` 包含 `api/coding/paas/v4` 或 `open.bigmodel.cn`
   `baseUrl` contains `api/coding/paas/v4` or `open.bigmodel.cn`
2. 提供商名称包含 `coding`、`glm-coding`、`zhipu` 或 `bigmodel`
   Provider name contains `coding`, `glm-coding`, `zhipu`, or `bigmodel`

## API 端点 / API Endpoints

技能查询三个监控端点：
The skill queries three monitoring endpoints:

| 端点 | Endpoint | 用途 | Purpose |
|------|----------|------|---------|
| `/api/monitor/usage/quota/limit` | 配额百分比（5小时 Token，1个月 MCP） | Quota percentage (5-hour token, 1-month MCP) |
| `/api/monitor/usage/model-usage` | 24小时模型使用统计 | 24-hour model usage statistics |
| `/api/monitor/usage/tool-usage` | 24小时 MCP 工具使用 | 24-hour MCP tool usage |

详见 [API 文档](references/api-endpoints.md)。
See [API Documentation](references/api-endpoints.md) for details.

## 错误处理 / Error Handling

脚本为常见问题提供友好的错误提示：
The script provides friendly error messages for common issues:

- 缺少依赖工具（curl、jq） | Missing dependencies (curl, jq)
- 缺少或无效的 OpenClaw 配置 | Missing or invalid OpenClaw configuration
- 提供商未配置为 GLM 编码套餐 | Provider not configured as GLM coding plan
- API 认证失败 | API authentication failed
- 网络超时 | Network timeout

## 故障排除 / Troubleshooting

### "缺少依赖工具，请安装: jq" / "Missing dependency, please install: jq"

使用包管理器安装 jq：
Install jq using package manager:
```bash
sudo apt-get install jq  # Linux
brew install jq           # macOS
```

### "未找到配置 GLM 编码套餐的提供商" / "No GLM coding plan provider configured"

确保提供商的 `baseUrl` 包含 `api/coding/paas/v4`。更新配置：
Ensure the provider's `baseUrl` contains `api/coding/paas/v4`. Update configuration:

```json
{
  "models": {
    "providers": {
      "your-provider": {
        "baseUrl": "https://open.bigmodel.cn/api/coding/paas/v4",
        "apiKey": "your-key"
      }
    }
  }
}
```

### "认证失败，请检查 API 密钥配置" / "Authentication failed, please check API key"

验证 API 密钥是否正确：
Verify API key is correct:
```bash
jq -r '.models.providers.zhipu.apiKey' ~/.openclaw/openclaw.json
```

## 贡献指南 / Contributing

欢迎贡献！请遵循以下步骤：
Contributions welcome! Please follow these steps:

1. Fork 本仓库 | Fork this repository
2. 创建特性分支 (`git checkout -b feature/amazing-feature`) | Create feature branch
3. 提交更改 (`git commit -m 'Add some amazing feature'`) | Commit changes
4. 推送到分支 (`git push origin feature/amazing-feature`) | Push to branch
5. 开启 Pull Request | Open Pull Request

## 许可证 / License

MIT License - 详见 [LICENSE](LICENSE) 文件。
MIT License - See [LICENSE](LICENSE) file for details.

## 致谢 / Acknowledgments

- 原始实现: [zai-coding-plugins](https://github.com/zai-org/zai-coding-plugins) | Original implementation
- 参考实现: [opencode-glm-quota](https://github.com/guyinwonder168/opencode-glm-quota) | Reference implementation
- OpenClaw 集成: 本技能 | OpenClaw integration: This skill

## 相关资源 / Resources

- [OpenClaw 文档](https://openclaw.dev) | [OpenClaw Documentation](https://openclaw.dev)
- [GLM 编码套餐](https://open.bigmodel.cn) | [GLM Coding Plan](https://open.bigmodel.cn)
- [API 文档](references/api-endpoints.md) | [API Documentation](references/api-endpoints.md)
- [安装指南](docs/INSTALLATION.md) | [Installation Guide](docs/INSTALLATION.md)
