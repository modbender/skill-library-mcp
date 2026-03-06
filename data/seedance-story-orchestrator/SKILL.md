---
name: seedance-story-orchestrator
description: Orchestrate script-to-final-video production with a strict stage-gated workflow (outline → episode_plan → storyboard → storyboard_images → render), using Seedream image generation, Seedance multi-shot rendering, checkpoint-based confirmation/resume, and optional FFmpeg concatenation. Use when converting txt/json/staged artifacts into storyboard videos and a final merged mp4.
---

# Seedance Story Orchestrator (v0.2.0-phase1)

阶段性方案（Phase 1）：
- 上层编排：`seedance-story-orchestrator`
- 下层执行：`seedance-video-generation/seedance.py`

以“可审计、可恢复、可控推进”为第一目标。

## Workflow（严格关卡）

固定阶段顺序：

`outline -> episode_plan -> storyboard -> storyboard_images -> render`

规则：
1. 每阶段执行后写入 `checkpoint-{stage}.json`，默认 `confirmed=false`
2. 未确认时，`run` 会立即停止并返回：
   - `pending_confirmation_stage`
   - `next_action`
3. 必须 `confirm --stage <stage>` 后再继续下一阶段

## Prerequisites

- Python 3.8+
- `seedance-video-generation` skill（必须可访问 `seedance.py`）
- `ARK_API_KEY`
- FFmpeg（用于拼接最终视频）

## Quick Start（推荐）

```bash
# 1) 运行到 render（会在每个关卡停下）
python3 {baseDir}/scripts/run_story.py run \
  --project-dir {baseDir}/outputs/my-project \
  --input-file /path/to/story.txt \
  --stage render

# 2) 按提示确认阶段（示例）
python3 {baseDir}/scripts/run_story.py confirm \
  --project-dir {baseDir}/outputs/my-project \
  --stage outline

# 3) 查看整体状态
python3 {baseDir}/scripts/run_story.py status \
  --project-dir {baseDir}/outputs/my-project
```

## End-to-End（从剧本到成片）

```bash
# 首次运行（会停在 outline）
python3 {baseDir}/scripts/run_story.py run \
  --project-dir ./my-project \
  --input-file ./story.txt \
  --stage render

# 逐关确认并继续
python3 {baseDir}/scripts/run_story.py confirm --project-dir ./my-project --stage outline
python3 {baseDir}/scripts/run_story.py run --project-dir ./my-project --stage render

python3 {baseDir}/scripts/run_story.py confirm --project-dir ./my-project --stage episode_plan
python3 {baseDir}/scripts/run_story.py run --project-dir ./my-project --stage render

python3 {baseDir}/scripts/run_story.py confirm --project-dir ./my-project --stage storyboard
python3 {baseDir}/scripts/run_story.py run --project-dir ./my-project --stage render

python3 {baseDir}/scripts/run_story.py confirm --project-dir ./my-project --stage storyboard_images
python3 {baseDir}/scripts/run_story.py run --project-dir ./my-project --stage render

python3 {baseDir}/scripts/run_story.py confirm --project-dir ./my-project --stage render
```

最终视频路径：
`./my-project/videos/run-YYYYMMDD-HHMMSS/final-video.mp4`

## Input Modes

### 1) 非结构化输入（默认推荐：sub-agent-first）

```bash
# 先生成 sub-agent 任务
python3 {baseDir}/scripts/build_subagent_task.py \
  --input-file /path/to/raw.txt \
  --output {baseDir}/outputs/subagent-task.txt

# 用 sessions_spawn 执行后，拿到结构化 JSON，再喂给 prepare
python3 {baseDir}/scripts/prepare_storyboard.py \
  --input-file /path/to/subagent-output.json \
  --output-dir {baseDir}/outputs
```

### 2) 直接文本/JSON输入

```bash
python3 {baseDir}/scripts/prepare_storyboard.py \
  --input-file /path/to/story.txt \
  --output-dir {baseDir}/outputs
```

### 3) staged artifacts 输入

```bash
python3 {baseDir}/scripts/prepare_storyboard.py \
  --staged-artifacts /path/to/staged-artifacts.v1.json \
  --output-dir {baseDir}/outputs
```

## Core Commands

### Prepare

```bash
python3 {baseDir}/scripts/prepare_storyboard.py \
  --input-file /path/to/story.txt \
  --output-dir {baseDir}/outputs
```

### Storyboard Images（Seedream）

```bash
python3 {baseDir}/scripts/seedream_image.py storyboard \
  --storyboard /path/to/storyboard.draft.v1.json \
  --output-dir {baseDir}/outputs/images
```

### Render Videos（Seedance）

```bash
python3 {baseDir}/scripts/orchestrate_story.py run \
  --storyboard /path/to/storyboard.draft.v1.json \
  --output-dir {baseDir}/outputs/videos
```

### Concat Final Video

```bash
python3 {baseDir}/scripts/concat_videos.py \
  --run-dir {baseDir}/outputs/videos/run-YYYYMMDD-HHMMSS
```

## Artifacts

主要产物：
- `plan-*/storyboard.draft.v1.json`
- `plan-*/assets.v1.json`
- `plan-*/staged-artifacts.v1.json`
- `checkpoint-{stage}.json`
- `videos/run-*/result-index.json`
- `videos/run-*/run-summary.json`
- `videos/run-*/final-video.mp4`

## Schemas & References

- `references/storyboard-v1.schema.json`
- `references/assets-v1.schema.json`
- `references/staged-artifacts-v1.schema.json`
- `references/subagent-parser-contract.md`
- `docs/design-doc-v0.2.0-phase1.md`
- `docs/logic-flow-v0.2.0-phase1.md`

## Notes (Phase 1)

- 当前是阶段性方案：优先可控、可恢复、可审计
- 自动“回传最终视频到会话”不在本阶段强制实现（可在 Phase 2 增加）
- `run_story.py` 已内置混合日志 JSON 解析与严格关卡机制
