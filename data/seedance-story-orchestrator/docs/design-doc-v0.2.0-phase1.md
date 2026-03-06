# Seedance Story Orchestrator 设计文档（阶段性方案）

版本：v0.2.0-phase1  
状态：Draft（等待 Kenny 确认后冻结）

---

## 1. 背景与目标

`seedance-video-generation` 本身擅长**单镜头**生成，但在“剧本到成片”场景中，仍需要一个上层导演做：

1. 多镜头结构化解析（文本/混合输入）
2. 分阶段产物管理（staged artifacts）
3. 镜头级调度与结果索引
4. 自动拼接与最终交付

本方案将 `seedance-story-orchestrator` 定义为“上层编排器”，`seedance-video-generation` 作为“底层执行引擎”。

---

## 2. 范围（Phase 1）

### 2.1 In Scope（本阶段覆盖）

- 输入：txt / json / staged artifacts
- 解析：sub-agent-first（契约化输出），规则解析兜底
- 中间产物：outline / episode_plan / subject_catalog / scene_catalog / storyboard / assets
- 渲染：分镜视频串行生成（支持 dry-run）
- 拼接：FFmpeg concat 生成 `final-video.mp4`
- 状态机：严格 stage-gating（每阶段必须 confirm）
- 可恢复：通过 `project_dir` + checkpoint 续跑

### 2.2 Out of Scope（本阶段不覆盖）

- 完整自动发布到外部平台（如 Feishu/Discord 自动上传）
- 独立 TTS 管线（当前沿用 Seedance `generate_audio`）
- 高级资产库（角色长期记忆、风格库多项目复用）

---

## 3. 设计原则

1. **可验证优先**：每阶段产物落盘，便于审计与回放。
2. **失败可恢复**：任何阶段失败不破坏已确认阶段。
3. **解析鲁棒性优先**：混合 stdout 的 JSON 解析必须稳健。
4. **确认即关卡**：未 confirm 不允许推进下一阶段。
5. **最小惊讶**：路径、命令、产物命名保持一致与可预期。

---

## 4. 核心架构

### 4.1 组件

- `scripts/prepare_storyboard.py`
  - 输入解析
  - staged artifacts 合并
  - 生成 `storyboard.draft.v1.json` / `assets.v1.json` 等

- `scripts/seedream_image.py`
  - 根据 storyboard 的 `image_prompt` 产出分镜图（可 dry-run）

- `scripts/orchestrate_story.py`
  - 调用 `seedance.py create` 执行镜头级视频生成
  - 输出 `run-summary.json` / `result-index.json` / `result-index.md`

- `scripts/concat_videos.py`
  - 基于镜头输出进行 FFmpeg concat，生成最终视频

- `scripts/run_story.py`
  - 状态机总控（run / confirm / status）
  - 执行阶段推进、checkpoint 管理、自动拼接

### 4.2 关键依赖

- `seedance-video-generation/seedance.py`
- FFmpeg
- `ARK_API_KEY`

---

## 5. 数据模型与产物

### 5.1 规范文件

- `references/storyboard-v1.schema.json`
- `references/assets-v1.schema.json`
- `references/staged-artifacts-v1.schema.json`

### 5.2 主要产物

- `plan-*/storyboard.draft.v1.json`
- `plan-*/assets.v1.json`
- `plan-*/staged-artifacts.v1.json`
- `images/*`
- `videos/run-*/shot-*.json|mp4`
- `videos/run-*/final-video.mp4`
- `checkpoint-*.json`

---

## 6. 状态机（Stage-Gated Workflow）

阶段顺序：

1. `outline`
2. `episode_plan`
3. `storyboard`
4. `storyboard_images`
5. `render`

规则：

- 每阶段执行后默认 `confirmed=false`
- 必须执行 `confirm --stage <stage>` 才可继续
- 若检测到任一已存在但未确认的 checkpoint，流程立即停止并返回 `next_action`

---

## 7. 关键修复（纳入本阶段基线）

### 7.1 Fix A：assets 合并空指针

- 问题：`merge_staged_into_primary` 在 `None` 上写入
- 修复：引入 `primary_assets` 参数，统一 `merged_assets` 路径；补 staged-only 输入处理

### 7.2 Fix B：子进程输出混合日志导致 JSON 解析失败

- 问题：`json.loads(stdout)` 对日志+JSON混合文本失败
- 修复：`parse_last_json()` 提取最后一个有效 JSON 对象

### 7.3 Fix C：确认关卡未生效

- 问题：阶段虽生成 checkpoint，但流程仍自动往下跑
- 修复：`run_stages()` 内新增“未确认即中断”逻辑，并输出 `pending_confirmation_stage` + `next_action`

### 7.4 Fix D：outline 产物强依赖导致误失败

- 问题：某些输入不产生 `outline.v1.json` 即失败
- 修复：outline 文件降级为可选，不阻断流程

### 7.5 Fix E：`status/confirm` 命令读取 `project_id` 异常

- 问题：`args.project_id` 仅 run 子命令存在
- 修复：将 `project_id` 读取限定在 run 分支

---

## 8. CLI 交互契约

### 8.1 run

```bash
python3 scripts/run_story.py run \
  --project-dir /tmp/seedance_proj \
  --input-file /tmp/story.txt \
  --stage render \
  --dry-run
```

返回字段（摘要）：

- `stages_run`
- `pending_confirmation_stage`
- `ready_to_continue`
- `next_action`

### 8.2 confirm

```bash
python3 scripts/run_story.py confirm \
  --project-dir /tmp/seedance_proj \
  --stage outline
```

### 8.3 status

```bash
python3 scripts/run_story.py status --project-dir /tmp/seedance_proj
```

---

## 9. 失败处理与恢复

- 单阶段失败：保留历史产物与 checkpoint，不回滚文件
- 重新执行：同 `project_dir` 下从未确认阶段继续
- 渲染失败：可选 `--continue-on-error`（尽可能完成可执行镜头）

---

## 10. 质量门禁（发布前）

1. `python3 -m py_compile scripts/*.py`
2. 文本输入 dry-run 走通到首个关卡
3. `confirm + run` 多次推进验证 stage-gating
4. `orchestrate_story.py run --dry-run` 输出可被 `parse_last_json` 解析
5. `concat_videos.py` 在有镜头输入时可输出 `final-video.mp4`

---

## 11. 后续规划（Phase 2 建议）

1. Preflight 检查器：运行前统一检测 `ARK_API_KEY` / FFmpeg / seedance skill
2. 自动回传：将最终视频自动发送到当前 OpenClaw 会话
3. 渲染并发与速率控制：可配置并发镜头渲染
4. 场景资产缓存：跨项目复用角色/风格

---

## 12. 新 Logic Flow（文档内嵌版）

```text
[User Script Input]
      |
      v
[run_story.py run]
      |
      +--> Stage 1: outline (prepare_storyboard)
      |         |
      |         +--> write checkpoint-outline (confirmed=false)
      |         +--> STOP (wait confirm)
      |
      +--> confirm outline
      |
      +--> Stage 2: episode_plan (artifact check)
      |         |
      |         +--> checkpoint-episode_plan(false)
      |         +--> STOP (wait confirm)
      |
      +--> confirm episode_plan
      |
      +--> Stage 3: storyboard (draft check)
      |         |
      |         +--> checkpoint-storyboard(false)
      |         +--> STOP (wait confirm)
      |
      +--> confirm storyboard
      |
      +--> Stage 4: storyboard_images (seedream_image)
      |         |
      |         +--> checkpoint-storyboard_images(false)
      |         +--> STOP (wait confirm)
      |
      +--> confirm storyboard_images
      |
      +--> Stage 5: render (orchestrate_story)
                |
                +--> optional concat_videos -> final-video.mp4
                +--> checkpoint-render(false)
                +--> STOP (wait confirm)

Any stage found unconfirmed? --> immediate STOP + next_action
```

---

## 13. 兼容性声明

- 当前方案是**阶段性方案**：优先可控、可审计、可恢复。
- 在 Kenny 确认本文档后，可删除 docs 目录旧版本文档，仅保留本版与后续增量文档。
