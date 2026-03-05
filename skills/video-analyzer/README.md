# Video Analyzer Skill

智能分析 Bilibili、YouTube 或本地视频，生成转写、评估和总结。

## 功能特性

- 🎬 **多平台支持**: B站、YouTube、本地视频文件
- 🎤 **高精度转写**: 使用 Whisper AI 模型
- 🤖 **智能分析**: 内容评估、总结、格式化
- 📸 **关键帧截图**: 自动提取关键节点并配图（默认启用）
- 📁 **文件输出**: Markdown 格式保存结果
- 🔍 **批量处理**: B站关键词搜索并批量分析

## 安装

首次运行会自动安装依赖：

```bash
# 安装依赖
pip install -r requirements.txt

# 安装 FFmpeg (必需)
# Windows: winget install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

## 使用方法

### Python API

```python
from main import skill_main

# 基础用法
result = skill_main("https://www.bilibili.com/video/BV1xx411c7mD")

# 高级配置
result = skill_main(
    url="https://www.youtube.com/watch?v=xxx",
    whisper_model="large-v3",       # tiny/base/small/medium/large-v2/large-v3/turbo/distil-large-v2/distil-large-v3/distil-large-v3.5
    transcribe_language=None,       # 自动识别语言；可显式传 "zh"/"en"/"ja"
    analysis_types=["evaluation", "summary"],  # 分析类型
    output_dir="./my-analysis",     # 输出目录
    save_transcript=True,           # 保存原始转写
    enable_screenshots=True,        # 启用关键帧截图（默认启用）
    publish_to_feishu=True,         # 完成后发布到飞书知识库
    feishu_space_id="your_space_id",
    feishu_parent_node_token="your_parent_node_token"
)
```

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `url` | string | 必填 | 视频链接或本地文件路径 |
| `whisper_model` | string | large-v2 | Whisper模型名称（仅多语言）：tiny/base/small/medium/large-v2/large-v3/turbo/distil-large-v2/distil-large-v3/distil-large-v3.5 |
| `transcribe_language` | string | None | Whisper语言代码（如 zh/en/ja），为空时自动识别 |
| `analysis_types` | list | [evaluation, summary] | 分析类型列表 |
| `output_dir` | string | ./video-analysis | 输出目录 |
| `save_transcript` | bool | true | 是否保存原始转写 |
| `enable_screenshots` | bool | true | 启用关键帧截图（自动在总结中插入关键节点截图） |
| `config_path` | string | None | 配置文件路径 |
| `publish_to_feishu` | bool | true | 是否自动发布到飞书知识库 |
| `feishu_space_id` | string | None | 飞书知识库 space_id（发布时必填） |
| `feishu_parent_node_token` | string | None | 飞书知识库父节点 token（发布时必填） |

## 返回结果

```python
{
    "success": True,
    "video_title": "视频标题",
    "duration_seconds": 623.8,
    "processing_seconds": 145.3,
    "transcript_length": 3245,
    "output_files": {
        "transcript": "./video-analysis/xxx_transcript.md",
        "evaluation": "./video-analysis/xxx_evaluation.md",
        "summary": "./video-analysis/xxx_summary.md"
    },
    "feishu_publish": {
        "enabled": true,
        "success": true,
        "doc_token": "doccnxxxx",
        "doc_url": "https://feishu.cn/docx/doccnxxxx"
    },
    "summary": "Analyzed in 145.3s | 3245 chars | 2 analyses"
}
```

## 分析类型

| 类型 | 说明 |
|------|------|
| `evaluation` | 多维度内容评估（信息准确性、逻辑严谨性、价值稀缺性等） |
| `summary` | 高质量内容总结和重构 |
| `format` | 原始转写净化和格式化 |

## 依赖要求

- Python 3.8+
- FFmpeg (必需)
- 其他依赖自动安装

## 配置文件

复制 `config.example.json` 为 `config.json`，配置 LLM API：

```json
{
  "llm": {
    "provider": "openai",
    "api_key": "your-api-key",
    "model": "gpt-4o-mini"
  },
  "feishu": {
    "space_id": "your_space_id",
    "parent_node_token": "your_parent_node_token"
  }
}
```

飞书 appId/appSecret 不存放在技能 `config.json`，默认从 OpenClaw 的 `openclaw.json`（`channels.feishu`）读取，也可通过环境变量 `FEISHU_APP_ID` / `FEISHU_APP_SECRET` 指定。

## 故障排除

**Q: 提示缺少 FFmpeg**
A: 根据系统运行安装命令：
- Windows: `winget install ffmpeg`
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

**Q: 模型下载很慢**
A: 使用 ModelScope 国内镜像，通常几分钟内完成

**Q: API 调用失败**
A: 检查 `config.json` 中的 API key 是否正确
