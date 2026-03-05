---
name: feishu-media
description: 飞书媒体文件发送技能。适用于：发送文件、图片、URL图片、视频、音频、语音消息，以及打包压缩后发送。当用户要求在飞书中发送任何类型的媒体文件时激活此技能。
---

# 飞书媒体发送技能

通过 `message` 工具向飞书发送各类媒体文件。

## 核心用法

所有媒体发送都通过 `message` 工具的 `action=send`，关键参数：
- `channel`: feishu
- `target`: `chat:群ID` 或 `user:open_id`（省略则回复当前会话）
- `message`: 附带的文字说明（可选）
- `filePath`: 本地文件路径
- `media`: URL 地址（网络图片/文件）

---

## 1. 发送本地文件（PDF/DOC/XLS/PPT/TXT等）

```
message action=send channel=feishu filePath=/path/to/file.pdf message="文件说明"
```

支持格式：pdf, doc/docx, xls/xlsx, ppt/pptx, txt, csv, zip, tar.gz 等。

## 2. 发送本地图片

```
message action=send channel=feishu filePath=/path/to/image.png message="图片说明"
```

支持格式：jpg, jpeg, png, gif, webp, bmp。

## 3. 发送 URL 图片

```
message action=send channel=feishu media=https://example.com/image.png message="网络图片"
```

## 4. 发送视频

```
message action=send channel=feishu filePath=/path/to/video.mp4 message="视频说明"
```

视频以文件附件形式发送（飞书 `msg_type: file`）。支持 mp4, mov, avi。

## 5. 发送音频（非语音）

MP3 等音频文件作为普通文件发送：

```
message action=send channel=feishu filePath=/path/to/audio.mp3 message="音频文件"
```

## 6. 发送语音消息（可播放的语音条）

语音消息需要 **Ogg/Opus 格式**。飞书会显示为可播放的语音条。

### 6.1 直接发送 opus/ogg 文件

```
message action=send channel=feishu filePath=/path/to/voice.opus message="语音消息"
```

### 6.2 从 MP3 转换后发送

先用 ffmpeg 转换格式：

```bash
ffmpeg -i input.mp3 -ar 16000 -ac 1 -acodec libopus output.ogg -y
```

然后发送 output.ogg。

### 6.3 技术细节

语音消息的底层流程：
1. 上传：`im.file.create`，`file_type: "opus"`，需带 `duration`（毫秒）
2. 发送：`msg_type: "audio"`，content: `{"file_key":"xxx","duration":3007}`
3. duration 由 ffprobe 自动获取，无需手动指定

## 7. 打压缩包后发送

当需要发送多个文件或不支持的格式时，先打包再发送：

### 7.1 打 zip 包

```bash
zip -j /tmp/archive.zip /path/to/file1 /path/to/file2
```

### 7.2 打 tar.gz 包

```bash
tar czf /tmp/archive.tar.gz -C /path/to/dir .
```

### 7.3 发送压缩包

```
message action=send channel=feishu filePath=/tmp/archive.zip message="打包文件"
```

---

## 格式支持速查表

| 类型 | 格式 | 发送方式 | 飞书显示 |
|------|------|----------|----------|
| 图片 | jpg/png/gif/webp | filePath 或 media(URL) | 内嵌图片 |
| 文档 | pdf/doc/xls/ppt | filePath | 文件卡片 |
| 视频 | mp4/mov/avi | filePath | 文件卡片 |
| 音频 | mp3/wav/flac | filePath | 文件卡片 |
| 语音 | opus/ogg | filePath | 可播放语音条 |
| 压缩包 | zip/tar.gz | filePath | 文件卡片 |
| 网络图片 | URL | media | 内嵌图片 |

## 注意事项

- 文件大小限制：默认 30MB
- 语音必须是 Ogg/Opus 格式才能显示为语音条，其他音频格式只能作为文件发送
- 需要 ffmpeg/ffprobe 支持语音格式转换和时长检测
- 飞书应用需要 `im:message`、`im:resource` 权限
