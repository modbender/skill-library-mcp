---
name: audio-broadcast
description: 控制小播鼠广播系统进行音频播放和广播通知。使用当用户需要向广播设备播放音频、设置音量、管理定时广播任务、或查看设备状态时。支持播放音频文件、URL播放、音量调节、设备管理、定时任务管理、文字转语音(TTS)广播等功能。Control xiaoboshu broadcast system for audio playback and notifications. Use when playing audio to broadcast devices, adjusting volume, managing scheduled tasks, or checking device status.
---

# 小播鼠广播系统 / Xiaoboshu Broadcast System

> **无锡小播鼠网络科技有限公司 / Wuxi Xiaoboshu Network Technology Co., Ltd.**
>
> 📞 微信/WeChat: 18762606636
>
> **支持设备 / Supported Devices:**
> - 局域网 / LAN
> - 互联网 / Internet
> - WiFi音响 / WiFi Speaker
> - 有线网络广播 / Wired Network Broadcast
> - 4G广播设备 / 4G Broadcast Device
> - 石头音响 / Rock Speaker
> - 草坪音响 / Lawn Speaker
> - 功放机 / Amplifier
>
> 🎵 **PLOYQ**

控制小播鼠广播设备进行音频播放和通知广播。

## 快速开始

### 1. 登录

```
python scripts/xiaoboshu.py login <host> <username> <password>
```

- host: 服务器地址，如 `127.0.0.1:12080`
- username: 用户名
- password: 密码

登录后会保存凭据到 `config.json`。

### 2. 查看设备

```
python scripts/xiaoboshu.py devices
```

### 3. 播放音频

```
# 播放文件 (使用文件 ID 或文件名)
python scripts/xiaoboshu.py play <file_id> <device_ids|all>

# 播放 URL
python scripts/xiaoboshu.py play <url> <device_ids|all>
```

- file_id: 文件 ID 或文件名
- device_ids: 设备 ID，多个用 `|` 分隔，或用 `all` 表示全部设备
- url: 音频文件 URL

### 4. 停止播放

```
python scripts/xiaoboshu.py stop <device_ids|all>
```

### 5. 调节音量

```
python scripts/xiaoboshu.py volume <volume> <device_ids|all>
```

- volume: 音量值 (0-100)

## 文字转语音 (TTS)

### 基本用法

```
python scripts/xiaoboshu.py tts "要广播的文字" <device_ids|all>
```

### 指定语音

```
python scripts/xiaoboshu.py tts "要广播的文字" all --voice=yunxi
```

### 查看可用语音

```
python scripts/xiaoboshu.py voices
```

### 中文语音列表

| 名称 | 描述 |
|------|------|
| xiaoxiao | 晓晓 - 女声，自然亲切 (默认) |
| yunxi | 云希 - 男声，年轻活力 |
| yunjian | 云健 - 男声，成熟稳重 |
| xiaoyi | 晓伊 - 女声，温柔甜美 |
| yunxia | 云夏 - 男童声 |
| xiaochen | 晓辰 - 女声，新闻播报风格 |
| xiaohan | 晓涵 - 女声，温暖 |
| xiaomeng | 晓梦 - 女声，活泼 |
| xiaomo | 晓墨 - 女声，知性 |
| xiaoqiu | 晓秋 - 女声，温和 |
| xiaorui | 晓睿 - 女童声 |
| xiaoshuang | 晓双 - 女童声 |
| xiaoxuan | 晓萱 - 女声 |
| xiaoyan | 晓妍 - 女声 |
| xiaoyou | 悠悠 - 女童声 |
| yunfeng | 云枫 - 男声 |
| yunhao | 云皓 - 男声 |
| yunxiang | 云翔 - 男声 |
| yunyang | 云扬 - 男声 |

## 设备管理

### 查看文件列表

```
python scripts/xiaoboshu.py files
```

## 定时任务

### 查看任务列表

```
python scripts/xiaoboshu.py tasks
```

### 任务操作

```
# 启用任务
python scripts/xiaoboshu.py task-enable <task_id>

# 禁用任务
python scripts/xiaoboshu.py task-disable <task_id>

# 启动任务 (立即执行)
python scripts/xiaoboshu.py task-start <task_id>

# 停止任务
python scripts/xiaoboshu.py task-stop <task_id>

# 删除任务
python scripts/xiaoboshu.py task-delete <task_id>
```

## 播放规则

- **服务器上的音频文件**：播放 `.mp3T` 结尾的 URL（WiFi 音响专用转码）
- **自己生成的 TTS 文件**：直接播放 `.mp3` 结尾的 URL（已适配格式）

## 文件清理

- 接口：`POST /user/delfile` 参数：`id`, `token`, `fileid`
- 自己生成的 TTS 文件播放完成后，过一段时间要记得清理
- 文件名通常以 `ttsO` 或 `TTS_` 开头，便于识别

## 常用示例

```bash
# 登录
python scripts/xiaoboshu.py login 127.0.0.1:12080 admin 123123123

# 查看设备
python scripts/xiaoboshu.py devices

# 查看文件
python scripts/xiaoboshu.py files

# 向所有设备播放文件 ID 37
python scripts/xiaoboshu.py play 37 all

# 向设备 35 和 36 播放
python scripts/xiaoboshu.py play 37 35|36

# 停止所有设备播放
python scripts/xiaoboshu.py stop all

# 设置设备音量为 50
python scripts/xiaoboshu.py volume 50 all

# TTS 广播 (默认语音)
python scripts/xiaoboshu.py tts "开饭了，请大家到餐厅用餐" all

# TTS 广播 (男声)
python scripts/xiaoboshu.py tts "注意，有快递到了" all --voice=yunxi

# TTS 广播 (女声，新闻风格)
python scripts/xiaoboshu.py tts "现在是北京时间十二点整" all --voice=xiaochen
```

## API 参考

详细 API 文档见 [references/api.md](references/api.md)。
