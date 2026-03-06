---
name: jimeng-ai
description: 基于火山引擎即梦AI的文生图/文生视频能力，支持通过文本描述生成图片和视频。
---

# 即梦AI 文生图/文生视频 Skill

基于火山引擎即梦AI的文生图和文生视频能力，支持通过文本描述生成图片和视频。

## 功能特性

- **执行过程存储**：使用 MD5(提示词) 作为文件夹名保存任务状态
- **异步查询**：支持断点续传，避免重复提交相同任务
- **Base64 图片处理**：直接从 API 响应中解码并保存图片
- 支持即梦AI文生图（v3.0 / v3.1 / v4.0）
- 支持即梦AI文生视频（v3.0 1080P）
- 可配置宽高比、生成数量、自定义尺寸

## 所需环境变量

| 变量名 | 是否必需 | 说明 |
|--------|----------|------|
| `VOLCENGINE_AK` | **必需** | 火山引擎 Access Key |
| `VOLCENGINE_SK` | 条件必需 | 火山引擎 Secret Key（永久凭证必需） |
| `VOLCENGINE_TOKEN` | 可选 | 安全令牌（临时凭证 STS 必需） |

> **注意**：使用临时凭证（AKTP 开头）时，可以只使用 AK + Token，不需要 SK。

### 配置示例

```bash
export VOLCENGINE_AK="your-access-key"
export VOLCENGINE_SK="your-secret-key"

# 如果使用临时凭证(STS)，还需要设置 Token
export VOLCENGINE_TOKEN="your-security-token"
```

获取方式：
1. 登录 [火山引擎控制台](https://console.volcengine.com/)
2. 进入"访问控制" -> "密钥管理"
3. 创建或查看已有访问密钥

## 安装依赖

```bash
cd ~/.openclaw/workspace/skills/jimeng-ai
npm install
```

## 工作流程

### 首次执行（新任务）

使用新提示词运行时，脚本将：
1. 向 API 提交任务
2. 使用 `md5(提示词)` 作为文件夹名创建目录
3. 保存 `param.json`、`response.json` 和 `taskId.txt`
4. 输出：`"任务已提交，TaskId: xxx"`

```bash
$ npx ts-node scripts/text2image.ts "一只可爱的猫咪"
任务已提交，TaskId: 1234567890
```

### 后续执行（异步查询）

使用相同提示词运行将查询已有任务：
1. 如果图片已存在 → 立即返回图片路径
2. 如果任务未完成 → 输出：`"任务未完成，TaskId: xxx"`
3. 如果任务已完成 → 从 `binary_data_base64` 解码并保存图片

```bash
$ npx ts-node scripts/text2image.ts "一只可爱的猫咪"
任务未完成，TaskId: 1234567890

# 或者任务完成时：
$ npx ts-node scripts/text2image.ts "一只可爱的猫咪"
任务已完成，图片保存路径：
  - ./output/<md5_hash>/1.jpg
  - ./output/<md5_hash>/2.jpg
```

## 使用方法

### 基础用法

```bash
npx ts-node scripts/text2image.ts "一只可爱的猫咪"
```

### 完整参数

```bash
npx ts-node scripts/text2image.ts "提示词" \
  --version v40 \
  --ratio 16:9 \
  --count 2
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `prompt` | 图片生成提示词（必填） | - |
| `--version` | API版本: `v30`, `v31`, `v40` | `v31` |
| `--ratio` | 宽高比: `1:1`, `9:16`, `16:9`, `3:4`, `4:3`, `2:3`, `3:2`, `1:2`, `2:1` | `16:9` |
| `--count` | 生成数量 1-4 | `1` |
| `--width` | 指定宽度（可选） | - |
| `--height` | 指定高度（可选） | - |
| `--size` | 指定面积（可选，如 4194304 表示 2048x2048） | - |
| `--seed` | 随机种子（可选） | - |
| `--output` | 图片输出目录 | `./output` |
| `--debug` | 调试模式 | `false` |
| `--no-download` | 不下载图片，只返回URL | `false` |

## 输出格式

### 任务已提交（首次运行）

```json
{
  "success": true,
  "submitted": true,
  "prompt": "一只可爱的猫咪",
  "version": "v40",
  "ratio": "1:1",
  "count": 1,
  "taskId": "1234567890",
  "folder": "./output/<md5_hash>",
  "message": "任务已提交，请稍后使用相同提示词查询结果"
}
```

### 任务已完成

```json
{
  "success": true,
  "prompt": "一只可爱的猫咪",
  "version": "v40",
  "ratio": "1:1",
  "count": 1,
  "taskId": "1234567890",
  "images": [
    "./output/<md5_hash>/1.jpg",
    "./output/<md5_hash>/2.jpg"
  ],
  "outputDir": "./output/<md5_hash>"
}
```

### 任务未完成

```json
{
  "success": true,
  "prompt": "一只可爱的猫咪",
  "version": "v40",
  "ratio": "1:1",
  "count": 1,
  "taskId": "1234567890",
  "folder": "./output/<md5_hash>",
  "message": "任务未完成，请稍后使用相同提示词查询结果"
}
```

### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "MISSING_CREDENTIALS",
    "message": "请设置环境变量 VOLCENGINE_AK 和 VOLCENGINE_SK"
  }
}
```

## 文件夹结构

```
output/
└── <md5(prompt)>/           # md5哈希作为文件夹名
    ├── param.json           # 请求参数
    ├── response.json        # API提交响应
    ├── taskId.txt           # 任务ID
    └── 1.jpg, 2.jpg, ...    # 生成的图片
```

## 示例

### 生成风景画

```bash
npx ts-node scripts/text2image.ts "山水风景画，水墨风格" --version v40 --ratio 16:9
```

### 生成科幻城市

```bash
npx ts-node scripts/text2image.ts "未来科幻城市，霓虹灯光，赛博朋克风格" --version v40 --ratio 16:9 --count 2
```

### 指定尺寸生成

```bash
npx ts-node scripts/text2image.ts "抽象艺术" --width 2048 --height 1152
```

### 自定义输出目录

```bash
npx ts-node scripts/text2image.ts "一只可爱的猫咪" --output ~/Pictures/jimeng
```

## 版本说明

- **v30**: 即梦3.0 基础版本
- **v31**: 即梦3.1 改进版本
- **v40**: 即梦4.0 最新版本（推荐）

## 文生视频使用方法

### 基础用法

```bash
npx ts-node scripts/text2video.ts "一只可爱的猫咪在草地上奔跑"
```

### 完整参数

```bash
npx ts-node scripts/text2video.ts "提示词" \
  --ratio 9:16 \
  --duration 5 \
  --fps 24
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `prompt` | 视频生成提示词（必填） | - |
| `--ratio` | 宽高比: `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, `21:9` | `9:16` |
| `--duration` | 视频时长: `5` 或 `10` 秒 | `5` |
| `--fps` | 帧率: `24` 或 `30` | `24` |
| `--output` | 视频输出目录 | `./output` |
| `--wait` | 等待任务完成 | `false` |
| `--debug` | 调试模式 | `false` |
| `--no-download` | 不下载视频，只返回URL | `false` |

### 视频输出格式

#### 任务已提交

```json
{
  "success": true,
  "submitted": true,
  "prompt": "元宵节灯笼",
  "ratio": "9:16",
  "duration": 5,
  "fps": 24,
  "taskId": "1234567890",
  "folder": "./output/video/<md5_hash>",
  "message": "任务已提交，请稍后使用相同提示词查询结果"
}
```

#### 任务已完成

```json
{
  "success": true,
  "prompt": "元宵节灯笼",
  "ratio": "9:16",
  "duration": 5,
  "fps": 24,
  "taskId": "1234567890",
  "videoUrl": "https://...",
  "data": {}
}
```

#### 任务未完成

```json
{
  "success": true,
  "pending": true,
  "prompt": "元宵节灯笼",
  "ratio": "9:16",
  "duration": 5,
  "fps": 24,
  "taskId": "1234567890",
  "status": "in_queue",
  "message": "任务处理中，请稍后使用相同提示词查询结果"
}
```
### 视频文件夹结构

```
output/video/
└── <md5(prompt)>/           # md5哈希作为文件夹名
    ├── param.json           # 请求参数
    ├── response.json        # API提交响应
    ├── taskId.txt           # 任务ID
    └── video.mp4            # 生成的视频
```

## 参考文档

- [火山引擎即梦AI文生图文档](https://www.volcengine.com/docs/85621/1820192)
- [火山引擎即梦AI文生视频文档](https://www.volcengine.com/docs/85621/1792702)
