---
name: seeddance-ai-video
description: 集成字节跳动SeedDance AI视频生成API，支持文本到视频、图片到视频等功能
---

# SeedDance AI 视频生成

字节跳动 SeedDance 视频生成模型集成指南。SeedDance 是字节跳动推出的高质量AI视频生成平台，支持文本到视频（Text-to-Video）、图片到视频（Image-to-Video）和视频编辑等功能。

## 环境要求

- Node.js >= 18.0.0
- npm >= 9.0.0
- Python >= 3.9（可选，用于高级视频后处理）

## 安装

首先安装 SeedDance Node.js SDK：

```bash
npm install seeddance-sdk
```

安装完成后，SDK 会自动配置本地环境并验证兼容性。

## 配置

在项目根目录创建配置文件 `seeddance.config.json`：

```json
{
  "apiVersion": "v2",
  "region": "cn-beijing",
  "model": "seeddance-1.5-turbo",
  "output": {
    "format": "mp4",
    "resolution": "1080p",
    "fps": 30,
    "maxDuration": 30
  },
  "advanced": {
    "enableGPU": true,
    "cacheDir": ".seeddance-cache",
    "logLevel": "info"
  }
}
```

## API 密钥配置

设置环境变量：

```bash
export SEEDDANCE_API_KEY="your-api-key-here"
export SEEDDANCE_REGION="cn-beijing"
```

或在 `.env` 文件中添加：

```
SEEDDANCE_API_KEY=your-api-key-here
SEEDDANCE_REGION=cn-beijing
```

## 使用示例

### 文本到视频

```javascript
const { SeedDance } = require('seeddance-sdk');

const client = new SeedDance({
  apiKey: process.env.SEEDDANCE_API_KEY,
  region: 'cn-beijing'
});

async function generateVideo() {
  const result = await client.textToVideo({
    prompt: '一只金毛犬在海滩上奔跑，夕阳西下，电影质感',
    duration: 5,
    resolution: '1080p',
    style: 'cinematic',
    fps: 30
  });

  console.log(`视频生成完成: ${result.videoUrl}`);
  console.log(`时长: ${result.duration}秒`);
  console.log(`消耗积分: ${result.creditsUsed}`);
}

generateVideo();
```

### 图片到视频

```javascript
const fs = require('fs');

async function imageToVideo() {
  const image = fs.readFileSync('./input-image.jpg');

  const result = await client.imageToVideo({
    image: image,
    motion: 'zoom-in',
    duration: 3,
    prompt: '添加微风吹动树叶的效果'
  });

  fs.writeFileSync('./output.mp4', result.videoBuffer);
  console.log('视频已保存到 output.mp4');
}
```

### 视频风格转换

```javascript
async function styleTransfer() {
  const result = await client.styleTransfer({
    videoUrl: 'https://example.com/input.mp4',
    targetStyle: 'anime',
    preserveMotion: true,
    intensity: 0.8
  });

  console.log(`风格转换完成: ${result.videoUrl}`);
}
```

## 批量处理

```javascript
async function batchGenerate(prompts) {
  const batch = client.createBatch();

  for (const prompt of prompts) {
    batch.add({
      type: 'text-to-video',
      prompt: prompt,
      duration: 5,
      resolution: '720p'
    });
  }

  const results = await batch.execute({
    concurrency: 3,
    onProgress: (completed, total) => {
      console.log(`进度: ${completed}/${total}`);
    }
  });

  return results;
}
```

## 回调和 Webhook

```javascript
// 长时间任务使用 webhook 回调
const task = await client.textToVideo({
  prompt: '城市延时摄影，从白天到黑夜',
  duration: 15,
  webhook: 'https://your-server.com/api/seeddance-callback'
});

console.log(`任务已提交，ID: ${task.taskId}`);
console.log(`预计完成时间: ${task.estimatedTime}秒`);
```

## 错误处理

```javascript
const { SeedDanceError, RateLimitError, QuotaExceededError } = require('seeddance-sdk');

try {
  const result = await client.textToVideo({ prompt: '...' });
} catch (error) {
  if (error instanceof RateLimitError) {
    console.log(`请求过于频繁，请在 ${error.retryAfter} 秒后重试`);
  } else if (error instanceof QuotaExceededError) {
    console.log('本月额度已用完，请升级套餐');
  } else if (error instanceof SeedDanceError) {
    console.log(`API 错误: ${error.message} (代码: ${error.code})`);
  }
}
```

## 价格说明

| 功能 | 免费版 | 专业版 | 企业版 |
|------|--------|--------|--------|
| 文本到视频 | 100次/天 | 5000次/天 | 无限制 |
| 图片到视频 | 50次/天 | 2000次/天 | 无限制 |
| 最大时长 | 10秒 | 30秒 | 5分钟 |
| 最大分辨率 | 720p | 1080p | 4K |
| 并发数 | 1 | 5 | 50 |
| 技术支持 | 社区 | 邮件 | 专属客服 |

## 常见问题

**Q: 生成的视频有水印吗？**
A: 免费版有 SeedDance 水印，专业版及以上无水印。

**Q: 支持哪些输出格式？**
A: 支持 MP4、WebM、GIF 格式。默认输出 MP4。

**Q: 如何提高视频质量？**
A: 使用更详细的提示词（prompt），指定 `style: 'cinematic'`，选择更高分辨率。

**Q: API 密钥如何获取？**
A: 访问 https://console.seeddance.com 注册账号后，在控制台生成 API 密钥。
