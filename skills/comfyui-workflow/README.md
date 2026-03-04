# ComfyUI Workflow Skill

**AI-driven end-to-end image and video generation — just pick a workflow and describe what you want.**

[中文文档](#中文文档) | English

---

## Requirements

| Requirement | Details |
|-------------|---------|
| **Python** | 3.10 or higher |
| **pip packages** | `websocket-client`, `requests` |
| **ComfyUI server** | Must be running before executing workflows |
| **Token** | Required if ComfyUI has authentication enabled |

```bash
pip install websocket-client requests
```

### Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `COMFY_HOST` | ComfyUI server address | `127.0.0.1:8188` |
| `COMFY_WORKFLOW_DIRS` | Additional workflow directories | (none) |

Configuration can be set via:
- Environment variables
- `scripts/config.json` file

---

## The Core Value Proposition

> **Download a workflow → Tell the AI what you want → Get your output.**

Most ComfyUI workflows are complex node graphs with dozens of knobs: samplers, schedulers, LoRA weights, resolution presets, ControlNet strengths, extension steps. Normally you'd need deep technical knowledge to use them correctly.

This skill changes that:

1. **The AI reads the workflow** — inspects every configurable node, understands the graph topology, maps all the input toggles
2. **The AI explains your options** — tells you what the workflow can do: "This workflow supports ControlNet depth guidance, 2-step turbo mode, and three resolution presets"
3. **You decide in plain language** — "use turbo mode, 1024×1024, and apply the depth map from my photo"
4. **The AI executes** — dynamically reconfigures the graph, injects your inputs, runs the workflow, and hands you the output

The result: **less required knowledge, full flexibility, zero manual graph editing.**

---

## What the AI Can Do With Any Workflow

### Explain toggle options
```
User: What can I configure in this DaSiWa video workflow?

AI:  This AiO workflow has powerful toggle options:
     • Mode: "Rendering" (generate video) or "Combining" (merge parts)
     • Model: I2V (image-to-video) or FLF2V (first-last-frame)
     • Stages: 1-3 video extension passes
     • Audio: MMAudio sync or silent output
     • Resolution: 480p to 1080p
     • Steps: 28 (fast) to 52 (quality)
     Which mode would you like?
```

### Guide decisions
```
User: I want to extend my video with good quality

AI:  I'll set it to "Combining" mode with 3 stages.
     Using 52 steps for quality output.
     Ready to process your video frames?
```

### Execute end-to-end
```
User: Here's my starting frame, generate 5 seconds of video

AI:  Running I2V mode with your image...
     ✓ Video saved to ./output/video_20240227_143521.mp4
     (81 frames at 16fps, audio synced)
```

---

## Highlights

- **Zero graph knowledge required** — the AI understands the ComfyUI node graph so you don't have to
- **Dynamic Graph Reconfiguration** — automatically rewires bypassed nodes, resolves virtual wires, adjusts extension chains at runtime
- **Universal Input Support** — text, images, audio, video all handled with consistent flags
- **Smart Node Detection** — auto-discovers positive/negative prompts, resolution nodes, sampler settings across 30+ different node types
- **Virtual Wire Resolution** — transparently handles ComfyUI-Easy-Use wireless connections
- **Real-time Monitoring** — WebSocket-based execution with progress tracking and error detection
- **30 Production Workflows** — spanning image generation, editing, and video synthesis across 8 model families

---

## Quick Start

> **Prerequisites**: Start ComfyUI before using this skill.

```bash
# Install dependencies
pip install websocket-client requests

# Configure ComfyUI connection
cp scripts/config.json.example scripts/config.json
# Edit: {"comfy_host": "127.0.0.1:8188"}

# List available workflows
python scripts/comfy_run.py --list

# Inspect a workflow's configurable inputs
python scripts/comfy_run.py -w "image_flux2_text_to_image_9b" --inspect

# Generate
python scripts/comfy_run.py -w "image_flux2_text_to_image_9b" \
    --prompt "A majestic mountain at golden hour" \
    --width 1024 --height 1024 \
    --output ./output
```

---

## Architecture

```
User natural language
        │
        ▼
┌───────────────────────────────────────────────────┐
│              AI Workflow Agent (SKILL.md)          │
│  • Reads workflow JSON                             │
│  • Explains configurable options to user           │
│  • Translates user decisions to parameters         │
└───────────────────────┬───────────────────────────┘
                        │ parameters
                        ▼
┌───────────────────────────────────────────────────┐
│              comfy_run.py (Graph Rewriter)         │
│                                                    │
│  ┌────────────────┐   ┌─────────────────────────┐ │
│  │ Graph Analysis │   │ Node Injection           │ │
│  │ • Bypass rewire│   │ • Text prompts           │ │
│  │ • Virtual wires│   │ • Images / video / audio │ │
│  │ • Ext. chains  │   │ • Resolution / seed      │ │
│  └────────────────┘   └─────────────────────────┘ │
└───────────────────────┬───────────────────────────┘
                        │ modified workflow JSON
                        ▼
┌───────────────────────────────────────────────────┐
│           ComfyUI API (WebSocket)                  │
│  • Execution monitoring                            │
│  • Progress / error detection                      │
│  • Output file download                            │
└───────────────────────────────────────────────────┘
```

---

## Workflow Library

> ⚠️ **Disclaimer**: These workflow files are EXAMPLES ONLY — prompts, notes, and paths have been sanitized. They will NOT work out of the box. For functional workflows, visit the original authors on Civitai, HuggingFace, or their official repositories. Respect intellectual property.

---

## CLI Reference

```bash
# List all workflows
python scripts/comfy_run.py --list

# Inspect configurable inputs
python scripts/comfy_run.py -w <workflow> --inspect

# Text-to-image
python scripts/comfy_run.py -w <workflow> \
    --prompt "your description" \
    --width 1024 --height 1024

# Image editing
python scripts/comfy_run.py -w <workflow> \
    --prompt "edit instruction" --image input.jpg

# Multiple reference images
python scripts/comfy_run.py -w <workflow> \
    --prompt "..." --image img1.jpg --image img2.jpg

# Video from image
python scripts/comfy_run.py -w <workflow> \
    --prompt "description" --image frame.jpg

# Audio-driven video
python scripts/comfy_run.py -w wan22_smooth_audio_v3 \
    --prompt "..." --audio music.mp3

# Override specific node values
python scripts/comfy_run.py -w <workflow> \
    --override '{"42": {"steps": 30, "cfg": 7.0}}'

# Control video extension steps
python scripts/comfy_run.py -w svi_extend --extend-n-steps 3

# Fixed seed for reproducibility
python scripts/comfy_run.py -w <workflow> --seed 42

# Output directory
python scripts/comfy_run.py -w <workflow> --output ./my_output

# Debug mode
python scripts/comfy_run.py -w <workflow> --verbose --keep-temp
```

---

## How Graph Reconfiguration Works

When you run a workflow, `comfy_run.py` performs several transformations before sending it to ComfyUI:

**1. Bypass Node Rewiring**
Nodes set to bypass mode (`mode=4`) are removed from the graph and their upstream/downstream connections are spliced together using type-matching. This allows workflows to ship with optional nodes disabled by default.

**2. Virtual Wire Resolution**
ComfyUI-Easy-Use's `easy setNode` / `easy getNode` wireless connections are resolved to direct links, so the workflow executes correctly regardless of Easy-Use extension availability.

**3. Input Injection**
Your inputs (prompt, image, audio, video, resolution, seed) are located in the graph by node type matching and injected into the correct widget values or file upload slots.

**4. Extension Chain Control**
For video extension workflows with multiple sequential subgraph passes, you can limit how many passes run (e.g., `--extend-n-steps 3` out of 6 possible).

---

## Configuration

### `scripts/config.json`
```json
{
  "comfy_host": "127.0.0.1:8188",
  "workflow_dirs": ["../workflows"]
}
```

### Environment Variables
```bash
export COMFY_HOST="127.0.0.1:8188"
export COMFY_WORKFLOW_DIRS="/path/to/workflows"
```

---

## Project Structure

```
comfyui-workflow-skill/
├── README.md                 # This file
├── SKILL.md                  # AI agent usage guide
├── GENERATION_RULES.md       # Quality guidelines
├── WORKFLOWS_SUMMARY.md      # Detailed workflow docs
├── MODELS_INVENTORY.md       # Required models list
├── PRACTICAL_GUIDE.md        # Best practices
│
├── scripts/
│   ├── comfy_run.py          # Main executor + graph rewriter
│   ├── comfy_api.py          # ComfyUI API + WebSocket client
│   ├── comfy_control.sh      # Server start/stop/status
│   ├── config.json.example   # Config template
│   └── config.sh.example     # Shell config template
│
└── workflows/
    ├── Image-Civitai/        # Civitai community workflows
    ├── Image-Flux-2/         # Flux 2 workflows
    ├── Image-Qwen/           # Qwen Image workflows
    ├── Image-Qwen-Edit/      # Qwen editing workflows
    ├── Image-Z-Image/        # Z-Image workflows
    ├── Video-DaSiWa/         # DaSiWa fast-fidelity video
    ├── Video-Extend/         # Video extension workflows
    ├── Video-Hunyuan/        # HunyuanVideo workflows
    └── Video-Smooth/         # Wan 2.2 smooth video
```

---

## Acknowledgments

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) — node-based Stable Diffusion UI
- [ComfyUI-Easy-Use](https://github.com/yolain/ComfyUI-Easy-Use) — virtual wire support
- Model creators: Qwen, Flux, HunyuanVideo, Wan, DaSiWa, and the Civitai community

---

## 中文文档

### 简介

ComfyUI Workflow Skill 是一个 AI 驱动的端到端图像和视频生成工具。只需选择工作流并描述你想要的内容，AI 会自动处理其余的工作。

### 核心功能

- **零图知识要求** — AI 理解 ComfyUI 节点图，你无需学习
- **动态图重构** — 自动重连绕过节点、解析虚拟连线
- **通用输入支持** — 文本、图像、音频、视频统一处理
- **智能节点检测** — 自动发现提示词、分辨率、采样器设置
- **实时监控** — WebSocket 执行监控，进度追踪

### 免责声明

> ⚠️ **重要提示**：本仓库中的工作流文件仅供示例参考，无法直接使用。提示词、说明和文件路径已被清理。如需可用的工作流，请访问原作者的 Civitai、HuggingFace 或官方仓库获取完整版本。请尊重知识产权。

### 快速开始

```bash
# 安装依赖
pip install websocket-client requests

# 配置 ComfyUI 连接
cp scripts/config.json.example scripts/config.json
# 编辑: {"comfy_host": "127.0.0.1:8188"}

# 列出可用工作流
python scripts/comfy_run.py --list

# 生成图像
python scripts/comfy_run.py -w "image_flux2_t2i" \
    --prompt "一座雄伟的山峰在金色时分" \
    --width 1024 --height 1024
```

### 工作流列表

| 工作流 | 模型 | 用途 |
|--------|------|------|
| `image_flux2_t2i` | Flux 2 | 文生图 |
| `image_qwen_t2i` | Qwen Image | 文生图 |
| `image_qwen_edit_layered` | Qwen Edit | 图像编辑 |
| `image_z_t2i` | Z-Image | 图生图 |
| `video_hunyuan_i2v` | HunyuanVideo | 图生视频 |
| `video_wan_i2v` | Wan 2.2 | 图生视频 |
| `video_extend_svi` | SVI | 视频延长 |
| `WAN 2.2 i2v FastFidelity C-AiO-52` | Wan 2.2 | 视频全能 |

### 目录结构

```
comfyui-workflow-skill/
├── README.md           # 英文文档
├── SKILL.md            # AI 代理使用指南
├── scripts/            # Python 脚本
│   ├── comfy_run.py    # 主执行器
│   └── comfy_api.py    # API 客户端
└── workflows/          # 工作流文件（示例）
```

### 致谢

- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) — 基于节点的 Stable Diffusion 界面
- [ComfyUI-Easy-Use](https://github.com/yolain/ComfyUI-Easy-Use) — 虚拟连线支持
- 模型创作者：Qwen、Flux、HunyuanVideo、Wan、DaSiWa 及 Civitai 社区
