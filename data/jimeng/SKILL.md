---
name: jimeng
description: 即梦AI（字节跳动火山引擎）全功能API调用技能，支持文生图、图生图、文生视频、图生视频、数字人等全系列即梦AI能力。Use when needing to generate images or videos using Jimeng AI (Volcengine), including text-to-image, image-to-image, text-to-video, image-to-video, and digital human generation.
---

# 即梦AI Skill

即梦AI（字节跳动火山引擎）完整功能封装，提供图片生成、视频生成、数字人等全系列AI能力。

## 前置要求

- 已设置环境变量 `VOLC_ACCESS_KEY` 和 `VOLC_SECRET_KEY`
- 火山引擎账号已开通视觉智能服务

## 环境变量配置

```bash
export VOLC_ACCESS_KEY="<your-access-key>"
export VOLC_SECRET_KEY="<your-secret-key>"
```

## 安装依赖

```bash
cd <skill-path>
npm install
```

## 功能列表

### 1. 文生图 (text2image)

根据文本描述生成图片，支持 v3.0/v3.1/v4.0 版本。

```bash
npx ts-node scripts/text2image.ts "<提示词>" [选项]
```

**参数:**

| 参数 | 必填 | 说明 |
|------|------|------|
| `提示词` | 是 | 图片描述文本 |
| `--version` | 否 | API版本: `v30`, `v31`, `v40` (默认: `v40`) |
| `--ratio` | 否 | 宽高比: `1:1`, `9:16`, `16:9`, `3:4`, `4:3`, `2:3`, `3:2` (默认: `1:1`) |
| `--count` | 否 | 生成数量 1-4 (默认: `1`) |
| `--width` | 否 | 指定宽度 (如: 2048) |
| `--height` | 否 | 指定高度 (如: 1152) |
| `--seed` | 否 | 随机种子 |
| `--debug` | 否 | 调试模式 |

**示例:**

```bash
# 基础用法
npx ts-node scripts/text2image.ts "一只可爱的猫咪"

# 使用v4.0生成多张图
npx ts-node scripts/text2image.ts "山水风景画" --version v40 --ratio 16:9 --count 2

# 指定分辨率
npx ts-node scripts/text2image.ts "科幻城市" --width 2048 --height 1152
```

### 2. 图生图 (image2image)

根据输入图片进行编辑或风格转换。

```bash
npx ts-node scripts/image2image.ts --image "<图片>" --prompt "<描述>" [选项]
```

**参数:**

| 参数 | 必填 | 说明 |
|------|------|------|
| `--image` | 是 | 输入图片路径或URL |
| `--prompt` | 是 | 编辑描述（如"背景换成演唱会"） |
| `--mode` | 否 | 模式: `v30`, `seed3` (默认: `v30`) |
| `--ratio` | 否 | 输出宽高比 (默认: `1:1`) |
| `--scale` | 否 | 文本影响程度 0-1 (默认: `0.5`) |
| `--count` | 否 | 生成数量 (默认: `1`) |
| `--seed` | 否 | 随机种子 |
| `--debug` | 否 | 调试模式 |

**示例:**

```bash
# 基础编辑
npx ts-node scripts/image2image.ts --image "./photo.jpg" --prompt "背景换成演唱会现场"

# 风格转换
npx ts-node scripts/image2image.ts --image "./portrait.jpg" --prompt "转换成动漫风格" --mode seed3 --scale 0.7
```

### 3. 文生视频 (text2video)

根据文本描述生成视频。

```bash
npx ts-node scripts/text2video.ts "<提示词>" [选项]
```

**参数:**

| 参数 | 必填 | 说明 |
|------|------|------|
| `提示词` | 是 | 视频描述文本 |
| `--ratio` | 否 | 宽高比: `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, `21:9` (默认: `16:9`) |
| `--frames` | 否 | 帧数: `121`(5秒), `241`(10秒) (默认: `121`) |
| `--seed` | 否 | 随机种子 |
| `--debug` | 否 | 调试模式 |

**示例:**

```bash
# 生成5秒视频
npx ts-node scripts/text2video.ts "千军万马在草原上奔腾"

# 生成10秒竖屏视频
npx ts-node scripts/text2video.ts "科幻城市夜景" --ratio 9:16 --frames 241
```

### 4. 图生视频 (image2video)

根据图片生成视频（支持首帧和首尾帧模式）。

```bash
npx ts-node scripts/image2video.ts --image "<图片>" --prompt "<描述>" [选项]
```

**参数:**

| 参数 | 必填 | 说明 |
|------|------|------|
| `--image` | 是 | 输入图片路径或URL |
| `--prompt` | 是 | 视频动作描述 |
| `--mode` | 否 | 模式: `first`(首帧), `first-tail`(首尾帧) (默认: `first`) |
| `--frames` | 否 | 帧数: `121`, `241` (默认: `121`) |
| `--seed` | 否 | 随机种子 |
| `--debug` | 否 | 调试模式 |

**示例:**

```bash
# 首帧模式
npx ts-node scripts/image2video.ts --image "./landscape.jpg" --prompt "让风景动起来"

# 生成10秒视频
npx ts-node scripts/image2video.ts --image "https://example.com/img.jpg" --prompt "千军万马" --frames 241
```

### 5. 数字人 (dream-actor)

生成数字人视频或虚拟形象。

```bash
npx ts-node scripts/dream-actor.ts --image "<人物图片>" --prompt "<动作描述>" [选项]
```

**参数:**

| 参数 | 必填 | 说明 |
|------|------|------|
| `--image` | 是 | 人物图片路径或URL |
| `--prompt` | 条件 | 动作/表情描述（M1/M20模式必填） |
| `--mode` | 否 | 模式: `m1`, `m20`, `avatar` (默认: `m1`) |
| `--ratio` | 否 | 宽高比 (默认: `9:16`) |
| `--frames` | 否 | 帧数: `121`, `241` (默认: `121`) |
| `--seed` | 否 | 随机种子 |
| `--debug` | 否 | 调试模式 |

**模式说明:**

- `m1` - Dream Actor M1 基础数字人
- `m20` - Dream Actor M20 高级数字人
- `avatar` - RealMan Avatar 形象生成

**示例:**

```bash
# M1基础数字人
npx ts-node scripts/dream-actor.ts --image "./person.jpg" --prompt "微笑并点头"

# M20高级数字人
npx ts-node scripts/dream-actor.ts --image "./face.jpg" --prompt "说话并做手势" --mode m20 --frames 241

# 形象生成
npx ts-node scripts/dream-actor.ts --image "./avatar.jpg" --mode avatar
```

## API参考

详细的API文档位于 `references/` 目录：

| 文档 | 说明 |
|------|------|
| `jimeng_t2i_v40.md` | 文生图v4.0 API详细文档 |
| `jimeng_t2i_v31.md` | 文生图v3.1 API详细文档 |
| `jimeng_t2i_v30.md` | 文生图v3.0 API详细文档 |
| `jimeng_i2i_v30.md` | 图生图v3.0 API详细文档 |
| `jimeng_t2v_v30_1080p.md` | 文生视频API详细文档 |
| `jimeng_i2v_first_v30_1080.md` | 图生视频（首帧）API详细文档 |
| `jimeng_dream_actor_m1_gen_video_cv.md` | 数字人M1 API详细文档 |
| ... | 其他API文档 |

## 错误码

| 错误码 | 说明 |
|--------|------|
| `MISSING_CREDENTIALS` | 缺少环境变量 VOLC_ACCESS_KEY 或 VOLC_SECRET_KEY |
| `INVALID_ARGUMENTS` | 参数错误（如不支持的宽高比、超出范围的值等） |
| `AUTH_FAILED` | 鉴权失败（Access Key 或 Secret Key 错误） |
| `QUOTA_EXCEEDED` | 配额不足 |
| `TASK_FAILED` | 任务执行失败 |
| `TASK_TIMEOUT` | 任务超时 |
| `TEXT_RISK_NOT_PASS` | 文本审核未通过 |
| `IMAGE_RISK_NOT_PASS` | 图片审核未通过 |
| `UNKNOWN_ERROR` | 未知错误 |

## 使用建议

### 提示词优化

1. **详细描述**: 包含主体、风格、光线、氛围等要素
2. **避免敏感词**: 不要使用版权相关或敏感词汇
3. **控制长度**: 建议在400字以内，不超过800字

### 性能优化

1. **批量生成**: 使用 `--count` 参数一次生成多张图片
2. **合理等待**: 视频生成需要较长时间，请耐心等待
3. **调试模式**: 遇到问题时使用 `--debug` 查看详细日志

### 图片要求

- 格式: JPEG, PNG
- 大小: 最大 4.7MB（视频）/ 15MB（图片编辑）
- 分辨率: 最大 4096x4096，最短边不低于320
- 比例: 长边与短边比例在3以内

## 输出格式

所有脚本统一返回JSON格式：

**成功:**

```json
{
  "success": true,
  "taskId": "task-xxx-xxx",
  "images": [{"url": "...", "width": 1024, "height": 1024}],
  "videoUrl": "https://...",
  "usage": {"requestId": "req-xxx-xxx"}
}
```

**失败:**

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  }
}
```