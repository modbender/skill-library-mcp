# OpenRouter 图像生成分辨率指南

本文档详细说明 OpenRouter 图像生成 API 的分辨率限制、参数格式和实际输出尺寸。

## 参数格式

### `--size` / `image_config.image_size`

**只接受以下三个字符串值**：

- `"1K"` - 标准分辨率（默认）
- `"2K"` - 高分辨率
- `"4K"` - 最高分辨率

**⚠️ 重要**：
- 不要使用像素格式如 `"1024x1024"`、`"2048x2048"` 或 `"3840x2160"`
- OpenRouter API 不接受像素尺寸，只接受上述三个字符串值

## 实际输出像素尺寸

实际输出的像素尺寸由 **`size` 和 `aspect_ratio` 共同决定**。

### 常见组合的实际像素

| size | aspect | 实际像素 | 约等于 | 说明 |
|------|--------|----------|--------|------|
| `1K` | `1:1` | 1024×1024 | ~1 MP | 默认正方形 |
| `1K` | `16:9` | ~1344×768 | ~1 MP |  widescreen |
| `2K` | `1:1` | 2048×2048 | ~4 MP | 高质量正方形 |
| `2K` | `16:9` | ~2560×1440 | ~3.7 MP | 接近 1440p |
| `4K` | `1:1` | 4096×4096 | ~16 MP | 超高清正方形 |
| `4K` | `16:9` | 3840×2160 | ~8.3 MP | 标准 4K UHD |

**注意**：实际像素可能因模型而异，OpenRouter 会根据模型能力进行调整。

## 模型支持情况

### 完整支持 4K 的模型

- `google/gemini-3-pro-image-preview` (Nano Banana Pro)
- `google/gemini-2.5-flash-image-preview` (Nano Banana)
- `black-forest-labs/flux.2-pro`
- `black-forest-labs/flux.2-max`

### 仅支持到 2K 的模型

- `bytedance-seed/seedream-4.5`（可能，需验证）
- `openai/dall-e-3`
- 部分其他模型

### 使用建议

1. **日常使用推荐 `2K`**：
   - 与 `1K` 价格相同
   - 质量显著提升（4倍像素）
   - 大多数模型都支持

2. **4K 使用场景**：
   - 打印用途
   - 大尺寸展示
   - 需要后期裁剪的素材
   - **注意**：4K 价格通常是 2K 的 1.5-2 倍

## 常见问题

### Q: 为什么我设置了 `--size 4K` 但输出只有 ~1280px？

**可能原因**：
1. **模型不支持 4K**：部分模型最高只输出 2K
2. **参数格式错误**：确保传递的是 `"4K"` 字符串，而不是 `"4096x4096"`
3. **OpenRouter 路由问题**：API 可能路由到不支持 4K 的提供商

**排查步骤**：
1. 确认使用的模型支持 4K（查看上方模型支持列表）
2. 检查参数传递是否正确（查看 CLI 调试输出）
3. 尝试使用 `google/gemini-3-pro-image-preview` 测试（确认支持 4K）

### Q: 为什么 4K + 16:9 输出的是 3840×2160 而不是 4096×2304？

**解释**：
- `4K` 指的是长边的目标像素数（约 4096px）
- 当使用 `16:9` 宽高比时，OpenRouter 保持 4K UHD 标准分辨率（3840×2160）
- 这是符合行业标准（如 4K TV/显示器分辨率）的行为

### Q: 如何获得最大的输出尺寸？

**使用 `4K` + `1:1` 组合**：
```bash
node generate.js --prompt "..." --size 4K --aspect 1:1
```
这会输出约 4096×4096 像素的图像（约 16MP）。

## 支持的宽高比

所有 OpenRouter 图像生成模型支持以下宽高比：

| 比例 | 典型用途 |
|------|----------|
| `1:1` | 社交媒体、头像、产品图（默认）|
| `16:9` | 视频缩略图、桌面壁纸、横幅 |
| `9:16` | 手机壁纸、短视频封面、Story |
| `21:9` | 超宽屏、电影画面 |
| `4:3` | 传统照片、文档插图 |
| `3:4` | 杂志封面、海报 |
| `3:2` | 摄影作品 |
| `2:3` | 人像摄影 |
| `4:5` | Instagram 帖子 |
| `5:4` | 打印照片 |

## 价格参考（Nano Banana Pro）

| 分辨率 | 价格 | 性价比 |
|--------|------|--------|
| `1K` | $0.134 | 基准 |
| `2K` | $0.134 | ⭐ 最高（同价，4倍像素）|
| `4K` | $0.24 | 高（约 2x 价格，16倍像素）|

## API 调用示例

### 生成 4K UHD 图像
```json
{
  "model": "google/gemini-3-pro-image-preview",
  "messages": [{"role": "user", "content": "A cinematic mountain landscape"}],
  "modalities": ["image"],
  "image_config": {
    "image_size": "4K",
    "aspect_ratio": "16:9"
  }
}
```

### 生成高质量正方形图像
```json
{
  "model": "google/gemini-3-pro-image-preview",
  "messages": [{"role": "user", "content": "Abstract geometric art"}],
  "modalities": ["image"],
  "image_config": {
    "image_size": "2K",
    "aspect_ratio": "1:1"
  }
}
```

## 相关文档

- [SKILL.md](../SKILL.md) - 技能使用指南
- [cli-contract.md](./cli-contract.md) - CLI 接口规范
- [OpenRouter 官方文档](https://openrouter.ai/docs/guides/overview/multimodal/image-generation)
