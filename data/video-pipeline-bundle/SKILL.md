---
name: video-pipeline-bundle
description: 视频一站式工作流技能包。整合视频剪辑、转写、烧录、拼接全流程，支持分步执行和用户确认。包含：(1) auto-editor -
  视频剪辑去除静音片段；(2) Faster Whisper + MiniMax LLM - 语音转字幕；(3) ffmpeg - 烧录字幕到视频；(4)
  FFmpeg 工具箱 - 拼接、格式转换；(5) pipeline.py - 完整工作流编排。使用场景：批量处理视频、从原始素材到成品的完整流程。
---


# Video Pipeline Bundle

视频一站式工作流技能包，整合剪辑、转写、烧录、拼接全流程。

## 文件结构

```
video-pipeline-bundle/
├── SKILL.md
└── scripts/
    ├── pipeline.py      # 工作流编排
    ├── video_clip.py    # 视频剪辑（去静音）
    ├── video_to_text.py # 语音转字幕
    ├── burn_subtitle.py # 烧录字幕
    └── ffmpeg_tools.py  # FFmpeg 工具箱
```

## 依赖

- ffmpeg + ffprobe
- Python 3.8+
- auto-editor（视频剪辑）
- faster-whisper + requests（语音转写）
- MiniMax API Key（LLM 纠错）

## 安装与配置

### 1. 自动安装依赖

首次使用时，脚本会自动检测并安装所需依赖：

```bash
# 自动检测并安装
python3 skills/video-pipeline-bundle/scripts/pipeline.py --install-deps
```

**自动安装的内容：**
- `pip3 install auto-editor --break-system-packages`
- `pip3 install faster-whisper requests`

### 2. 配置 MiniMax API Key

**方式一：环境变量（推荐）**
```bash
export MINIMAX_API_KEY="your-api-key-here"
```

**方式二：运行时传入**
```bash
python3 skills/video-pipeline-bundle/scripts/pipeline.py \
  --all \
  --input "/path/to/videos" \
  --api-key "your-api-key-here"
```

**获取 API Key：**
1. 访问 [MiniMax 开放平台](https://platform.minimaxi.com/)
2. 注册账号并创建 API Key
3. 充值或获取免费额度

### 3. 依赖检查脚本

如果不确定环境是否满足要求，可以运行：

```bash
python3 skills/video-pipeline-bundle/scripts/pipeline.py --check-deps
```

输出示例：
```
✅ ffmpeg: 已安装 (6.1.1)
❌ auto-editor: 未安装
❌ faster-whisper: 未安装
❌ MINIMAX_API_KEY: 未设置

请运行: python3 skills/video-pipeline-bundle/scripts/pipeline.py --install-deps
```
如果有存在未安装的，就自动检测用户系统并帮用户安装。

## 核心功能

### 1. 视频剪辑 (video_clip.py)

去除视频中的静音片段，保留有效内容。

```bash
python3 skills/video-pipeline-bundle/scripts/video_clip.py \
  --input "/path/to/input.mp4" \
  --output "/path/to/output.mp4" \
  --threshold -40
```

### 2. 语音转写 (video_to_text.py)

用 Faster Whisper 识别语音，生成 SRT 字幕，然后用 MiniMax LLM 词级别纠错。

```bash
python3 skills/video-pipeline-bundle/scripts/video_to_text.py \
  --input "/path/to/video.mp4" \
  --output "/path/to/subtitle.srt" \
  --model small \
  --api-key "your-api-key"
```

**参数：**
| 参数 | 说明 | 默认 |
|------|------|------|
| --model | Whisper 模型 (tiny/small/base) | small |
| --margin | 静音片段缓冲秒数 | 0.5 |
| --api-key | MiniMax API Key | 环境变量 MINIMAX_API_KEY |

**模型选择：**
| 模型 | 内存 | 速度 |
|------|------|------|
| tiny | ~1GB | 最快 |
| **small** | ~2GB | 较快 |
| base | ~3GB | 中等 |

### 3. 烧录字幕 (burn_subtitle.py)

将 SRT 字幕烧录进视频。

```bash
python3 skills/video-pipeline-bundle/scripts/burn_subtitle.py \
  --input "/path/to/video.mp4" \
  --subtitle "/path/to/subtitle.srt" \
  --output "/path/to/output.mp4"
```

### 4. FFmpeg 工具箱 (ffmpeg_tools.py)

支持拼接、格式转换等操作。

```bash
# 拼接视频
python3 skills/video-pipeline-bundle/scripts/ffmpeg_tools.py concat \
  --inputs "1.mp4" "2.mp4" \
  --output "merged.mp4"

# 格式转换
python3 skills/video-pipeline-bundle/scripts/ffmpeg_tools.py convert \
  --input "video.mov" \
  --output "video.mp4"

# 查看视频信息
python3 skills/video-pipeline-bundle/scripts/ffmpeg_tools.py info \
  --input "/path/to/videos"
```

### 5. 完整工作流 (pipeline.py)

一站式处理，支持分步执行。

```bash
# 检查依赖
python3 skills/video-pipeline-bundle/scripts/pipeline.py --check-deps

# 安装依赖
python3 skills/video-pipeline-bundle/scripts/pipeline.py --install-deps

# 扫描目录
python3 skills/video-pipeline-bundle/scripts/pipeline.py \
  --list \
  --input "/path/to/videos"

# 执行单步
python3 skills/video-pipeline-bundle/scripts/pipeline.py \
  --step 1 \
  --input "/path/to/videos" \
  --output "/path/to/output"

# 执行全量
python3 skills/video-pipeline-bundle/scripts/pipeline.py \
  --all \
  --input "/path/to/videos" \
  --output "/path/to/output" \
  --subtitle "/path/to/subtitles" \
  --api-key "your-api-key"

# 带确认模式
python3 skills/video-pipeline-bundle/scripts/pipeline.py \
  --all \
  --input "/path/to/videos" \
  --output "/path/to/output" \
  --confirm
```

## 步骤说明

| 步骤 | 功能 | 输入 | 输出 |
|------|------|------|------|
| 1 | 剪辑（去静音） | 原始视频 | 已剪辑视频 |
| 2 | 转写（生成字幕） | 已剪辑视频 | SRT 字幕 |
| 3 | 烧录 | 已剪辑视频 + 字幕 | 已烧录视频 |
| 4 | 拼接 | 多个视频 | 合并视频 |

## 输出目录结构

```
输入目录/
├── 文字稿/           # 字幕文件
├── 项目名/           # 处理后的视频
│   ├── 1_已剪辑.mp4
│   └── 2_已剪辑.mp4
└── 项目名_成品/     # 最终成品
    └── 合并视频.mp4
```

## ⚠️ 安全注意事项

### 1. 消息通知（可选，默认关闭）

脚本支持发送进度通知到 Feishu，但：
- **默认不发送消息**（`--notify false` 即可禁用）
- 如需启用，请设置 `OPENCLAW_TARGET` 环境变量为可信目标
- 通知内容会包含文件名，请注意信息安全

```bash
# 禁用通知（推荐）
python3 ... --notify false

# 启用通知（仅可信目标）
export OPENCLAW_TARGET="your-safe-target"
```

### 2. 自动安装（默认仅提示）

`--install-deps` 选项会检测缺失的依赖并提供安装命令，但：
- **不会自动执行 sudo/apt-get/brew**
- 仅显示需要手动执行的命令
- 建议在虚拟环境或容器中安装

### 3. API Key 安全

- 使用环境变量 `MINIMAX_API_KEY` 而非硬编码
- 或使用 `--api-key` 参数（注意命令历史）
- 建议使用受限权限的 API Key

### 4. 建议的测试方式

```bash
# 1. 先检查依赖
python3 skills/video-pipeline-bundle/scripts/pipeline.py --check-deps

# 2. 手动安装缺失的依赖（不要用 --install-deps 自动安装系统包）

# 3. 在隔离环境测试
python3 skills/video-pipeline-bundle/scripts/pipeline.py \
  --list \
  --input "/path/to/test/videos" \
  --notify false
```

## 常见问题

**Q: 提示 "auto-editor 未安装"**
A: 运行 `python3 skills/video-pipeline-bundle/scripts/pipeline.py --install-deps`

**Q: 提示 "MINIMAX_API_KEY 未设置"**
A: 设置环境变量 `export MINIMAX_API_KEY="your-key"`，或使用 `--api-key` 参数

**Q: 显存不够怎么办？**
A: 使用 `--model tiny` 参数，tiny 模型只需要 ~1GB 内存

**Q: ffmpeg 未安装？**
A: Ubuntu/Debian: `sudo apt install ffmpeg` | macOS: `brew install ffmpeg` | Windows: 下载 ffmpeg.exe
