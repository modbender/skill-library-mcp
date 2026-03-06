---
name: douyin-video-parse
description: 从抖音分享链接或视频页 URL 解析出可下载的视频直链、标题与描述，并可下载到本地或上传到飞书云盘。适用于需要解析抖音 URL（短链、/video/、/note/、modal_id 等）并获取真实播放地址或下载视频时使用。
---

## 何时使用

- 用户提供抖音分享链接或视频页 URL，需要得到可下载的视频地址或直接下载视频文件
- 需要将视频上传到飞书云盘并获取分享链接

## 使用方式选择

用户可以使用以下任一方式处理抖音视频：

### 方式一：上传飞书云盘（推荐）
```bash
# 获取飞书token
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"<app_id>","app_secret":"<app_secret>"}' | python3 -c "import json,sys; print(json.load(sys.stdin)['tenant_access_token'])")

# 执行上传
node scripts/parse-douyin-video.js <抖音URL> --feishu <token> <folder_token>
```
- 优点：支持大文件（>30MB），用户可直接在云盘下载
- 返回：feishu_url（云盘链接）

**首次使用需要配置：**
1. 在飞书云盘创建一个文件夹（如"抖音视频"）
2. 将文件夹分享给机器人，添加成员并设置权限
3. 参考 [飞书开放平台文档](https://open.feishu.cn/document/faq/trouble-shooting/how-to-add-permissions-to-app) 开通文件夹权限
4. 给机器人分配 `drive:drive.metadata:readonly` 权限

### 方式二：仅解析
```bash
node scripts/parse-douyin-video.js <抖音URL>
```
- 返回：title, desc, video_urls 等信息
- 适用于：只需要视频直链
- ⚠️ 注意：返回的 video_url 直接访问会403，需要在请求时添加 `Referer: https://www.douyin.com/` 才能下载

### 方式三：下载到本地
```bash
# 下载到临时目录（自动创建临时目录）
node scripts/parse-douyin-video.js <抖音URL> --download

# 下载到指定路径
node scripts/parse-douyin-video.js <抖音URL> /path/to/video.mp4
```
- 返回：download_path
- ⚠️ 飞书聊天发送限制：文件大小 ≤ 30MB，超过则需要使用方式一（上传云盘）
- ⚠️ 通过飞书发送文件时：
  - 上传接口 file_type 必须用 `"stream"`（不是 mp4）
  - 发送消息接口 msg_type 用 `"file"`
  - content 必须是字符串格式：`"{\"file_key\":\"xxx\"}"`

## 配置用户偏好

当用户选择了使用方式后，需要将偏好配置保存到 TOOLS.md：

```
## 抖音视频处理（使用偏好）

### 固定配置
- **飞书token获取**: app_id / app_secret
- **云盘文件夹**: folder_token

### 使用方式
收到抖音链接时，自动使用【飞书云盘】方式上传
```

## 常见错误
- **1061004**: forbidden - 云盘文件夹未分享给机器人
