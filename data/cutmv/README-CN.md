# 🎬 OpenClaw 技能：cutmv 视频工具

一个基于 FFmpeg 的视频处理 OpenClaw 技能，支持视频/音频剪辑、格式转换和压缩。

## 功能特性

- ✂️ **视频剪辑** - 按时间范围分割视频/音频
- 🔄 **格式转换** - 视频/音频格式互转
- 🗜️ **视频压缩** - 可控质量的视频压缩
- 🖼️ **帧提取** - 从视频中提取画面
- 🎵 **音频提取** - 从视频中提取音频
- 🔊 **音频替换** - 替换或混合音轨
- 📝 **文字水印** - 添加文字水印（需要freetype）
- 💬 **字幕** - 添加字幕文件 (.srt, .ass)

## 环境要求

- 系统已安装 FFmpeg
- Python 3.7+

## 安装步骤

### 1. 安装 FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

**Windows:**
从 [ffmpeg.org](https://ffmpeg.org/download.html) 下载，或使用 Winget:
```bash
winget install ffmpeg
```

### 2. 安装技能

将技能文件放入你的 OpenClaw 工作区：

```
~/openclaw-workspace/skills/cutmv-video-tool/
├── SKILL.md
├── skill.py
└── README-CN.md
```

## 使用方法

### 视频剪辑

```python
from skill import VideoTool

tool = VideoTool()
# 剪辑 0 到 480 秒的视频
tool.cut(input_file="input.mp4", output_file="output.mp4", start_time=0, end_time=480)
```

### 格式转换

```python
# 转换视频格式
tool.convert(input_file="input.mp4", output_file="output.avi", output_format="avi")

# 转换音频格式
tool.convert(input_file="input.mp4", output_file="output.mp3", output_format="mp3")
```

### 视频压缩

```python
# 指定码率压缩视频
tool.compress(input_file="input.mp4", output_file="compressed.mp4", bitrate="1000k")
```

### 帧提取

```python
# 提取指定时间的单帧
tool.extract_frame(input_file="input.mp4", output_file="frame.jpg", timestamp="00:01:30")

# 提取多帧（每秒一帧）
tool.extract_frames(input_file="input.mp4", output_dir="./frames/", interval=1)
```

## API 参考

### VideoTool 类

#### `cut(input_file, output_file, start_time, end_time)`
按时间范围剪辑视频/音频文件。

**参数：**
- `input_file` (str): 输入文件路径
- `output_file` (str): 输出文件路径
- `start_time` (int/float): 开始时间（秒）
- `end_time` (int/float): 结束时间（秒）

#### `convert(input_file, output_file, output_format)`
转换视频/音频格式。

**参数：**
- `input_file` (str): 输入文件路径
- `output_file` (str): 输出文件路径
- `output_format` (str): 目标格式（mp4, avi, mp3, wav 等）

#### `compress(input_file, output_file, bitrate)`
使用指定码率压缩视频。

**参数：**
- `input_file` (str): 输入文件路径
- `output_file` (str): 输出文件路径
- `bitrate` (str): 目标码率（如 "1000k", "1M"）

#### `extract_frame(input_file, output_file, timestamp)`
从视频中提取单帧。

**参数：**
- `input_file` (str): 输入视频路径
- `output_file` (str): 输出图片路径
- `timestamp` (str): 时间位置（HH:MM:SS）

#### `extract_frames(input_file, output_dir, interval=1)`
从视频中提取多帧。

**参数：**
- `input_file` (str): 输入视频路径
- `output_dir` (str): 输出目录
- `interval` (int): 帧间隔（秒）

## 与 OpenClaw 集成

该技能可用于 OpenClaw 工作流：

```python
# 在你的 OpenClaw 技能中
from skill import VideoTool

def process_video(video_path):
    tool = VideoTool()
    # 压缩以便通过通讯软件发送
    tool.compress(video_path, "compressed.mp4", "1000k")
    return "compressed.mp4"
```

## 使用示例

### 示例 1：压缩视频以便微信/飞书发送

```python
from skill import VideoTool

def compress_for_messaging(input_path):
    tool = VideoTool()
    # 压缩到 15MB 以兼容通讯软件
    tool.compress(input_path, "output.mp4", "1000k")
    return "output.mp4"
```

### 示例 2：提取视频截图

```python
from skill import VideoTool

def create_video_grid(video_path):
    tool = VideoTool()
    # 每 10 秒提取一帧
    tool.extract_frames(video_path, "./frames/", interval=10)
    return "./frames/"
```

## 故障排除

### "ffmpeg not found"

请确保 FFmpeg 已安装并在系统 PATH 中可用。

```bash
# 验证安装
ffmpeg -version
```

### "Permission denied"

请确保你对输入/输出目录有读写权限。

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 作者

- **焱焱 (Yanyan)** - yanyan@3c3d77679723a2fe95d3faf9d2c2e5a65559acbc97fef1ef37783514a80ae453


- **Isaac** - [GitHub](https://github.com/QiaoTuCodes)

## 鸣谢

- 感谢 [OpenClaw](https://github.com/openclaw/openclaw) 团队提供的优秀平台
- FFmpeg 团队提供的强大媒体处理工具

---

*此技能来自 OpenClaw 技能集合。*
