---
name: upload-to-catbox
description: 上传本地图片到 catbox.moe 免费图床，获取公开访问的 URL 链接。当用户需要将本地图片转换为 URL、上传图片到图床、获取图片链接、提到 catbox、或进行图像编辑（如改背景、换脸等）但提供的是本地图片路径时使用此 skill。
triggers:
  - 用户提供本地图片路径（以 / 开头或包含 .cursor/projects/）且需要进行图像处理
  - 用户要求上传图片到图床
  - 用户要求获取图片 URL
  - 用户使用图像编辑模型（如 Seedream、Flux 等）但输入是本地文件
---

# Catbox 图床上传

将本地图片上传到 catbox.moe 免费图床，获取永久 URL 链接。

## 自动触发条件

当以下情况发生时，**必须自动触发此 skill**：

1. **图像编辑任务 + 本地图片**：用户要求编辑图片（换背景、改风格、修图等），但提供的是本地图片路径
2. **AI 模型需要图片 URL**：用户要使用需要图片 URL 的 AI 模型（如 Seedream、Flux、Sora 等），但输入是本地文件
3. **用户附加了图片**：对话中包含 `<image_files>` 标签，里面有本地图片路径

### 识别本地图片路径

本地图片路径通常具有以下特征：
- 以 `/` 开头的绝对路径
- 包含 `.cursor/projects/` 
- 包含 `/Users/` 或 `/home/`
- 以 `./` 或 `../` 开头的相对路径
- 文件扩展名为 `.png`、`.jpg`、`.jpeg`、`.gif`、`.webp`

## 特点

- 免费、无需登录
- 支持直接二进制上传（无需 base64）
- 永久存储（不会自动删除）
- 支持格式：png, jpg, gif, webp 等

## 上传命令

```bash
curl -F'reqtype=fileupload' -F'fileToUpload=@/path/to/image.png' https://catbox.moe/user/api.php
```

返回值直接是图片 URL，例如：`https://files.catbox.moe/abc123.png`

## 使用流程

### 场景 1：直接上传请求

1. 获取用户提供的本地图片路径
2. 执行 curl 命令上传
3. 返回生成的 URL 给用户

### 场景 2：图像编辑任务（重要）

当用户请求图像编辑但提供本地图片时：

1. **先上传图片**：执行 curl 命令上传本地图片到 catbox
2. **获取 URL**：从返回结果获取图片 URL
3. **继续原任务**：使用获取的 URL 调用图像编辑模型（如 Seedream）

**示例**：用户说「把这张图片的背景改成室内」，并附带了本地图片路径

```bash
# 步骤 1：上传图片
curl -F'reqtype=fileupload' -F'fileToUpload=@/Users/xxx/.cursor/projects/xxx/assets/image.png' https://catbox.moe/user/api.php
# 返回：https://files.catbox.moe/abc123.png

# 步骤 2：使用返回的 URL 调用图像编辑模型
# （调用 Seedream 等模型的 submit_task）
```

## 示例

### 示例 1：直接上传

**用户请求**：帮我上传 `/tmp/screenshot.png` 到图床

**执行**：
```bash
curl -F'reqtype=fileupload' -F'fileToUpload=@/tmp/screenshot.png' https://catbox.moe/user/api.php
```

**返回**：
```
https://files.catbox.moe/x7ppwg.png
```

### 示例 2：图像编辑 + 本地图片

**用户请求**：把这个图片的背景改成海边（附带本地图片路径）

**执行流程**：

1. 识别到本地图片路径，触发上传
2. 上传完成后获取 URL
3. 使用 URL 调用 Seedream edit 模型

```bash
# 1. 上传
IMAGE_URL=$(curl -F'reqtype=fileupload' -F'fileToUpload=@/path/to/local/image.png' https://catbox.moe/user/api.php)
echo "图片已上传: $IMAGE_URL"

# 2. 然后用这个 URL 调用图像编辑 API
```

## 注意事项

- 单个文件最大 200MB
- 上传可能需要几秒钟，请耐心等待
- 如果上传失败，可以重试
- **关键**：上传成功后，使用返回的 URL 继续执行用户原本的图像处理任务
