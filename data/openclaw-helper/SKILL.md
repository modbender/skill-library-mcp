---
name: openclaw-helper
description: "OpenClaw 部署与故障排查速查表，提供9阶段部署导航、常见错误解决方案和日志关键字说明"
---

# OpenClaw 部署与故障排查

快速查询 OpenClaw 部署步骤和错误解决方案。

## 触发词

用户询问以下内容时启动本 skill：
- OpenClaw 部署、安装、配置
- OpenClaw 报错、故障、不回复、连不上
- "openclaw 怎么..." / "小龙虾报错"

---

## 部署导航（九阶段）

| 阶段 | 内容 | 关键验证 |
|-----|------|---------|
| 1 | 服务器购买与初始访问 | 能看到 `root@主机名` 提示符 |
| 2 | SSH 免密登录配置 | `ssh root@IP "echo ok"` 无需密码 |
| 3 | 服务器环境确认 | `openclaw --version` 输出版本号 |
| 4 | 配置 AI 模型（models.providers） | providers 列表非空，primary model 已设置 |
| 5 | 飞书应用创建 | 获得 App ID（cli_ 开头）和 App Secret |
| 6 | 飞书通道配置（服务器端） | `channels.feishu.enabled=true`，凭证已设置 |
| 7 | 飞书权限与事件订阅 | im:message 等权限已开通，版本已上线 |
| 8 | 重启网关与端到端测试 | 机器人成功回复消息 |
| 9 | 安装 Claude Code（可选） | `claude --version` 输出版本号 |

---

## 关键命令模板

### 远程执行前缀（必需）
```bash
export NVM_DIR=/root/.nvm; . "$NVM_DIR/nvm.sh";
```

### 配置 AI 模型（阶段4）
```bash
ssh root@<IP> 'export NVM_DIR=/root/.nvm; . "$NVM_DIR/nvm.sh"; openclaw config set "models.providers.<名称>" --json "{
  \"baseUrl\": \"<代理地址>\",
  \"apiKey\": \"<API_Key>\",
  \"api\": \"anthropic-messages\",
  \"models\": [{
    \"id\": \"claude-sonnet-4-6\",
    \"name\": \"Claude Sonnet 4.6\",
    \"reasoning\": true,
    \"input\": [\"text\", \"image\"],
    \"contextWindow\": 200000,
    \"maxTokens\": 32000
  }]
}"'
```

### 设置主模型
```bash
ssh root@<IP> 'export NVM_DIR=/root/.nvm; . "$NVM_DIR/nvm.sh"; openclaw config set "agents.defaults.model.primary" "<名称>/claude-sonnet-4-6"'
```

### 配置飞书通道（阶段6）
```bash
ssh root@<IP> 'export NVM_DIR=/root/.nvm; . "$NVM_DIR/nvm.sh"; openclaw config set "channels.feishu" --json "{
  \"enabled\": true,
  \"domain\": \"feishu\",
  \"groupPolicy\": \"open\",
  \"appId\": \"<App_ID>\",
  \"appSecret\": \"<App_Secret>\"
}"'
```

### 重启网关（阶段8）
```bash
ssh root@<IP> 'systemctl --user restart openclaw-gateway.service'
```

### 查看日志
```bash
ssh root@<IP> 'journalctl --user -u openclaw-gateway.service --no-pager -n 30'
```

---

## 故障速查表

### 飞书相关

| 错误现象 | 可能原因 | 解决方案 |
|---------|---------|---------|
| 机器人收到消息但不回复 | models 未配置 | 执行阶段4配置 models.providers |
| 日志显示 99991672 | 飞书 API 权限不足 | 飞书开放平台添加 im:message 等权限并重新发布 |
| "应用未建立长连接" | appId/appSecret 未正确写入 | 凭证必须写入 channels.feishu，不是环境变量 |
| 飞书连接后秒断 | Encrypt Key/Verification Token 不匹配 | 核对飞书开放平台的加密策略 |
| 搜索不到机器人 | 应用未发布 | 创建版本并发布 |

### 模型相关

| 错误现象 | 可能原因 | 解决方案 |
|---------|---------|---------|
| "No API key found for provider" | models.providers 为空 | 执行阶段4配置模型 |
| "Embedded agent failed" | API Key 无效或代理地址错误 | 检查 baseUrl 和 apiKey |
| 模型回复乱码/格式错误 | api 字段选错 | Anthropic 用 `anthropic-messages`，OpenAI 用 `openai-responses` |
| "must NOT have additional properties" | 配置字段名错误 | 删除无效字段 |
| HTTP 404: Invalid URL /v1/v1/messages | baseUrl 多了 /v1 | baseUrl 填 `https://域名`，不加 /v1 |

### 服务相关

| 错误现象 | 可能原因 | 解决方案 |
|---------|---------|---------|
| 网关启动失败 | 配置文件 JSON 语法错误 | `node -e "JSON.parse(require('fs').readFileSync('/root/.openclaw/openclaw.json'))"` |
| 网关启动超时 | 被禁用的插件仍在尝试连接 | 禁用不需要的插件 |
| SSH 远程命令 node 找不到 | nvm 未加载 | 命令前加远程执行前缀 |

---

## 日志关键字

| 关键字 | 含义 |
|--------|------|
| `agent model: xxx/xxx` | 模型配置已识别 |
| `feishu[default]: WebSocket client started` | 飞书连接成功 |
| `[ws] ws client ready` | WebSocket 就绪 |
| `listening on ws://0.0.0.0:18789` | 网关正在监听 |
| `received message from` | 消息已收到 |
| `Embedded agent failed` | 模型调用失败 |
| `Access denied` + `99991672` | 飞书权限不足 |
| `No API key found` | models.providers 配置有误 |

---

## 使用说明

1. 先确认用户在哪个阶段或遇到什么错误
2. 提供对应的命令模板或解决方案
3. 所有远程命令都需要加 nvm 前缀
