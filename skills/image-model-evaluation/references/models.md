# 支持的图像模型列表

## Fal.ai 模型（MCP 调用）

通过 `user-速推AI` MCP 服务调用。

### 图像生成模型

| 模型 ID | 分辨率 | 价格 | 特点 |
|---------|--------|------|------|
| `fal-ai/flux-2/flash` | 1024px | 50积分 | Flux 2 最新版，极速（1秒），文字渲染强，支持图像编辑 |
| `fal-ai/flux/schnell` | 1024px | 20积分 | Flux 1 快速版，性价比高 |
| `fal-ai/flux/dev` | 1024px | 50积分 | Flux 1 开发版，质量更高 |
| `fal-ai/seedream-3.0` | 2K | 50积分 | 字节跳动，中文理解强 |

### 模型功能对比

| 模型 | 文生图 | 图像编辑 | 人物一致性 | 文字生成 | 速度 |
|------|--------|----------|------------|----------|------|
| flux-2/flash | ✅ | ✅ 原生支持 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 极快 (1s) |
| flux/schnell | ✅ | ❌ | - | ⭐⭐⭐ | 快 (2s) |
| flux/dev | ✅ | ❌ | - | ⭐⭐⭐⭐ | 中 (5s) |
| seedream-3.0 | ✅ | ✅ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 中 (8s) |

---

## 小北 API (api.xbyjs.top)

通过 HTTP API 调用。

### 图像生成模型

| 模型 | 分辨率 | 价格 | 特点 |
|------|--------|------|------|
| `jimeng-4.5` | 2K | 0.018元 | 中文最强，推荐 |
| `jimeng-4.1` | 2K | 0.018元 | 质量稳定 |
| `jimeng-4.0` | 2K | 0.018元 | 基础版本 |
| `jimeng-4.5-4k` | 4K | 0.048元 | 高清版本 |
| `nano-banana` | 1K | 0.018元 | Google 一代，性价比高 |
| `nano-banana-pro-1k` | 1K | 0.03元 | Google 二代 |
| `nano-banana-pro-2k` | 2K | 0.054元 | Google 二代，推荐 |
| `nano-banana-pro-4k` | 4K | 0.072元 | Google 二代，最高清 |
| `grok-imagine-0.9` | - | 0.018元 | Grok 多模态 |

### 模型功能对比

| 模型系列 | 文生图 | 图生图 | 多图输出 | 比例控制 | 人物一致性 |
|---------|--------|--------|---------|---------|------------|
| jimeng-4.x | ✅ | ✅ | ✅ (4张) | ✅ | ⭐⭐⭐⭐ |
| nano-banana | ✅ | ✅ | ✅ (4张) | ✅ | ⭐⭐⭐ |
| nano-banana-pro | ✅ | ✅ | ✅ (4张) | ✅ | ⭐⭐⭐⭐ |
| grok-imagine | ✅ | ✅ | ✅ | ✅ | ⭐⭐⭐ |

### 推荐测试模型

**经济测试**：
- `nano-banana` - 0.018元/次，性价比最高

**质量测试**：
- `jimeng-4.5` - 中文理解最好，效果稳定
- `nano-banana-pro-2k` - Google 最新技术

**高清测试**：
- `jimeng-4.5-4k` - 4K分辨率
- `nano-banana-pro-4k` - 4K分辨率

## 验证模型可用性

调用 API 获取模型信息：

```bash
curl -s https://api.xbyjs.top/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## 已知问题

| 模型 | 问题 |
|------|------|
| `jimeng-4.5-4k` | 部分时段无可用渠道 |
| `nano-banana-pro-1k` | 偶尔超时 |
| `nano-banana-pro-4k` | 部分时段无可用渠道 |
