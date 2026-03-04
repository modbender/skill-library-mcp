---
name: quiverai-quickstart
description: QuiverAI API快速入门指南。当用户想要学习如何使用QuiverAI的SVG生成API时使用此技能。包括API密钥创建、环境配置、SDK安装和发送请求的完整流程。
metadata: {"openclaw": {"emoji": "🎨", "requires": {"env": ["QUIVERAI_API_KEY"]}, "primaryEnv": "QUIVERAI_API_KEY", "homepage": "https://quiver.ai"}}
---

# QuiverAI 快速入门指南

本指南将帮助你快速上手QuiverAI的SVG生成API，包括账户创建、API密钥配置、SDK安装和发送请求的完整流程。

## 前期准备

### 1. 创建账户

首先访问 [quiver.ai/start](https://quiver.ai/start) 创建QuiverAI公开测试账户，然后登录 [app.quiver.ai](https://app.quiver.ai)。

### 2. 创建API密钥

1. 在应用中打开 [API Keys](https://app.quiver.ai/settings/api-keys)（Settings > Developers > API Keys）
2. 点击 **Create API key** 并命名
3. **立即复制密钥** —— 密钥只显示一次，无法后续找回

### 3. 配置环境变量

QuiverAI API使用Bearer认证方式。将密钥保存为 `QUIVERAI_API_KEY`：

**macOS/Linux:**
```bash
export QUIVERAI_API_KEY="<your-key>"
```

**Windows PowerShell:**
```bash
$env:QUIVERAI_API_KEY="<your-key>"
```

## 安装SDK

### Node.js SDK

使用官方Node.js SDK：

```bash
npm install @quiverai/sdk
```

或使用 pnpm/bun：
```bash
pnpm add @quiverai/sdk
# 或
bun add @quiverai/sdk
```

## 发送第一个请求

### 使用Node.js SDK

```javascript
import { QuiverAI } from "@quiverai/sdk";

const client = new QuiverAI({
  bearerAuth: process.env["QUIVERAI_API_KEY"],
});

const logo = await client.createSVGs.generateSVG({
  model: "arrow-preview",
  prompt: "A logo for the next AI Design startup",
});

console.log(logo);
```

### 使用REST API

也可以直接使用HTTP请求：

```bash
curl --request POST \
  --url https://api.quiver.ai/v1/svgs/generations \
  --header 'Authorization: Bearer <QUIVERAI_API_KEY>' \
  --header 'Content-Type: application/json' \
  --data '{
    "model": "arrow-preview",
    "prompt": "A logo for the next AI Design startup",
    "n": 1,
    "stream": false
  }'
```

## 错误处理

API返回JSON错误载荷：

```json
{
  "status": 429,
  "code": "rate_limit_exceeded",
  "message": "Rate limit exceeded",
  "request_id": "req_01J..."
}
```

常见错误码：
- `401 Unauthorized`: API密钥缺失或无效
- `402 Payment Required`: 积分不足
- `429 Too Many Requests`: 请求过于频繁，请稍后重试

## 计费模型

- 每次成功的API请求消耗1积分
- 计费按请求次数计算，即使 `n` 大于1也只消耗1积分

## 下一步

- 查看 [API参考文档](https://docs.quiver.ai/api-reference/introduction)
- 了解 [定价和套餐](https://docs.quiver.ai/api/pricing)
- 探索模型：[Text to SVG](https://docs.quiver.ai/models/text-to-svg) 和 [Image to SVG](https://docs.quiver.ai/models/image-to-svg)

## 重要提示

- **永远不要将API密钥提交到版本控制仓库**
- 确保环境变量在生产环境中安全存储
- 关注API调用频率以避免触发速率限制
