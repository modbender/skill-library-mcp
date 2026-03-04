---
name: 图片上传
description: 上传本地图片到云存储，获取公开访问的 URL 链接。当用户需要上传图片、转存网络图片、获取图片 URL 时使用此 skill。
category: tool
tags: [图片上传, 云存储, URL转换, 免费]
featured: false
---

# Upload Image Skill

上传本地图片到云存储，获取公开访问的 URL 链接。

## 使用场景

当用户需要：
- 将本地图片转换为 URL 链接
- 上传图片供 AI 模型使用（如图生视频、图像编辑等）
- 转存网络图片到自有存储

## 使用方法

### 方式 1：Base64 图片上传

适用于本地图片文件，需要先将图片转换为 Base64 编码。

```python
import base64

# 读取本地图片
with open("path/to/image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

# 调用 MCP 工具
result = upload_image(
    image_data=image_data,
    content_type="image/jpeg"  # 可选，会自动检测
)
```

### 方式 2：URL 转存

适用于将网络图片转存到自有云存储。

```python
result = upload_image(
    image_url="https://example.com/image.jpg"
)
```

## MCP 工具参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image_data | string | 二选一 | Base64 编码的图片数据 |
| image_url | string | 二选一 | 网络图片 URL |
| file_name | string | 否 | 自定义文件名（如 my-image.jpg） |
| folder | string | 否 | 存储文件夹，默认 "mcp-uploads" |
| content_type | string | 否 | MIME 类型，自动检测 |

## 返回数据

```json
{
    "success": true,
    "url": "https://cdn-video.51sux.com/mcp-uploads/20260129/xxx.jpg",
    "object_key": "mcp-uploads/20260129/xxx.jpg",
    "bucket_name": "fal-task",
    "content_type": "image/jpeg",
    "size_bytes": 123456,
    "upload_method": "base64",
    "upload_time": "2026-01-29 10:30:00"
}
```

## 支持的图片格式

- JPEG / JPG
- PNG
- GIF
- WebP
- BMP
- SVG

## 存储信息

- **存储桶**: fal-task
- **区域**: 广州 (cn-guangzhou)
- **CDN 域名**: https://cdn-video.51sux.com
- **文件路径格式**: `{folder}/{YYYYMMDD}/{uuid}.{ext}`

## 与其他 Skill 配合使用

### 示例：上传本地图片后生成视频

```python
# 1. 上传本地图片
upload_result = upload_image(image_data=base64_data)
image_url = upload_result["url"]

# 2. 使用 Sora 2 生成视频
submit_task(
    model_id="sora-2",
    parameters={
        "image_url": image_url,
        "prompt": "让画面动起来..."
    }
)
```

### 示例：转存网络图片后进行编辑

```python
# 1. 转存图片（避免原链接失效）
upload_result = upload_image(image_url="https://example.com/photo.jpg")
stable_url = upload_result["url"]

# 2. 使用 Flux 2 Flash 编辑图片
submit_task(
    model_id="flux-2-flash",
    parameters={
        "prompt": "add a sunset background",
        "image_urls": [stable_url]
    }
)
```

## 注意事项

1. **免费使用**: 此工具不收取费用
2. **文件大小**: 建议单个图片不超过 10MB
3. **自动检测**: 不提供 content_type 时，会根据文件头自动检测格式
4. **CDN 加速**: 返回的 URL 使用 CDN 加速访问

## 常见问题

### Q: Base64 数据是否需要去掉前缀？
A: 不需要，工具会自动处理 `data:image/xxx;base64,` 前缀。

### Q: 上传的文件会保留多久？
A: 文件长期保存，不会自动删除。

### Q: 可以上传视频吗？
A: 目前只支持图片格式，视频请使用其他工具。
