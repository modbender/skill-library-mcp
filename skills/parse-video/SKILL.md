---
name: 视频链接解析
description: 解析视频分享链接，获取无水印视频下载地址。当用户想要下载视频、解析抖音/快手/小红书/B站链接、获取无水印视频时使用此 skill。
category: tool
tags: [视频下载, 去水印, 抖音, 快手, 小红书, B站, 免费]
featured: false
---

# 视频链接解析

解析各大平台的视频分享链接，获取无水印视频下载地址。**免费使用，无需认证**。

## 工作流程

1. **解析链接** - 调用 MCP `parse_video` 工具获取资源信息
2. **下载资源** - 执行 `scripts/download.py` 脚本下载到本地

## 支持平台

- 抖音 (Douyin)
- 快手 (Kuaishou)
- 小红书 (Xiaohongshu)
- 哔哩哔哩 (Bilibili)
- 微博 (Weibo)
- TikTok
- Instagram
- YouTube
- 其他主流平台

## 使用方法

调用 MCP 工具 `parse_video`：

```json
{
  "url": "视频分享链接"
}
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|-----|------|-----|------|
| url | string | **是** | 视频分享链接，支持带分享文案的文本（自动提取链接） |

### 返回字段

| 字段 | 类型 | 说明 |
|-----|------|------|
| success | boolean | 是否解析成功 |
| title | string | 视频标题 |
| thumbnail | string | 视频封面缩略图 |
| video_url | string | 首选视频下载链接 |
| video_urls | array | 所有视频链接列表 |
| audio_url | string | 音频下载链接 |
| audio_urls | array | 所有音频链接列表 |
| image_url | string | 首选图片链接（图集类型） |
| image_urls | array | 所有图片链接（图集类型） |
| parse_time | string | 解析时间 |

## 示例

### 示例 1：解析抖音分享链接

**用户请求**：帮我解析这个抖音视频 `1.53 y@g.oQ 04/03 Cus:/ 二狗脱口秀 # 脱口秀 https://v.douyin.com/GVOt9Hk6ZzM/ 复制此链接，打开Dou音搜索，直接观看视频！`

**调用 parse_video**：

```json
{
  "url": "1.53 y@g.oQ 04/03 Cus:/ 二狗脱口秀 # 脱口秀 https://v.douyin.com/GVOt9Hk6ZzM/ 复制此链接，打开Dou音搜索，直接观看视频！"
}
```

**返回示例**：

```json
{
  "success": true,
  "title": "二狗脱口秀",
  "thumbnail": "https://...",
  "video_url": "https://...",
  "video_urls": ["https://..."],
  "parse_time": "2025-01-29 10:30:00"
}
```

### 示例 2：解析 B 站链接

**用户请求**：解析 https://www.bilibili.com/video/BV1xx411c7mD

**调用 parse_video**：

```json
{
  "url": "https://www.bilibili.com/video/BV1xx411c7mD"
}
```

### 示例 3：解析小红书图集

**用户请求**：帮我下载这个小红书的图片 http://xhslink.com/xxxxx

**调用 parse_video**：

```json
{
  "url": "http://xhslink.com/xxxxx"
}
```

图集类型返回 `image_urls` 包含所有图片链接。

## 常见问题

### Q: 解析失败怎么办？

1. 检查链接是否正确
2. 某些私密或已删除的内容无法解析
3. 部分平台可能有访问限制

### Q: 支持图集吗？

支持。图集类型的内容会在 `image_urls` 字段返回所有图片链接。

### Q: 需要付费吗？

不需要，此工具**完全免费**，无需登录认证即可使用。

## 下载脚本

MCP 解析完成后，将获取到的资源 URL 传递给下载脚本保存到本地。

### 脚本位置

```
.cursor/skills/parse-video/scripts/download.py
```

### 用法

脚本接收已解析的资源 URL，不负责解析。

```bash
# 下载单个视频
python download.py --video "https://xxx.mp4"

# 下载视频和音频
python download.py --video "https://xxx/v.mp4" --audio "https://xxx/a.mp3"

# 下载多张图片（图集）
python download.py --image "url1" --image "url2" --image "url3"

# 指定输出目录和名称
python download.py --video "url" -o ~/Downloads -n "搞笑视频"
```

### 参数说明

| 参数 | 简写 | 说明 |
|-----|------|------|
| --video | -v | 视频 URL（可多次指定） |
| --audio | -a | 音频 URL（可多次指定） |
| --image | -i | 图片 URL（可多次指定） |
| --thumbnail | -t | 缩略图 URL |
| --output | -o | 输出目录 (默认: ./downloads) |
| --name | -n | 文件名前缀 (默认: video) |

### 完整工作流示例

**用户请求**: 帮我下载这个抖音视频到本地

**执行步骤**:

1. **调用 MCP 工具解析** - 获取资源 URL:

```json
{
  "url": "https://v.douyin.com/xxx"
}
```

**返回结果**:

```json
{
  "success": true,
  "title": "二狗脱口秀",
  "video_url": "https://v26-web.douyinvod.com/xxx.mp4",
  "audio_url": "https://v26-web.douyinvod.com/xxx.mp3"
}
```

2. **执行下载脚本** - 传入解析到的 URL:

```bash
cd /Users/m007/codes/translate_api/.cursor/skills/parse-video
python scripts/download.py \
  --video "https://v26-web.douyinvod.com/xxx.mp4" \
  --name "二狗脱口秀" \
  --output ~/Downloads/videos
```

### 输出示例

```
📹 下载视频 (1 个):
  下载中: https://v26-web.douyinvod.com/xxx.mp4...
  进度: 100.0% (12345678/12345678 bytes)
  ✓ 已保存: ./downloads/二狗脱口秀_20250129_103000.mp4

==================================================
下载完成!
  成功: 1 个
  失败: 0 个
  保存目录: /Users/m007/Downloads/videos

已下载文件:
  - ./downloads/二狗脱口秀_20250129_103000.mp4
```

### 图集下载示例

**小红书图集**:

1. MCP 解析返回:

```json
{
  "success": true,
  "title": "美食分享",
  "image_urls": ["https://xxx/1.jpg", "https://xxx/2.jpg", "https://xxx/3.jpg"]
}
```

2. 下载脚本:

```bash
python scripts/download.py \
  --image "https://xxx/1.jpg" \
  --image "https://xxx/2.jpg" \
  --image "https://xxx/3.jpg" \
  --name "美食分享" \
  --output ~/Downloads/images
```

## 定价

**免费** - 无限制使用
