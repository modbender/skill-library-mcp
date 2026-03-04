---
name: sketch-illustration
description: 插画图片生成技能，支持多种手绘风格。使用 Imagen 3（ZenMux API）生成插图，适合流程图、功能说明、PPT配图、教程配图等场景。支持三种风格：A) Sketch 极简手绘风（Notion/Linear 风格，简笔人物，冷淡低饱和）；B) Watercolor 奶油彩铅水彩风（暖色调，纸纹彩铅，适合PPT讲义）；C) Flat Vector Retro 扁平矢量复古风（黑色轮廓线，几何简化，复古配色，适合NotebookLM PPT/课程封面）。生成后自动上传发送到飞书。当用户要求生成插画、配图、手绘风格图、流程示意图、产品插图、PPT配图时触发此技能。
---

# 插画生成 Skill

支持两种手绘插画风格，按需选择，用 Imagen 3 生成并发送到飞书。

## 风格选择

查看 `references/styles.md` 了解三种风格的详细说明和使用场景：
- **风格 A：Sketch 极简手绘风**（默认）— Notion/Linear 风，极简冷淡，适合技术流程图
- **风格 B：Watercolor 奶油彩铅水彩风** — 暖色调纸纹，适合 PPT 配图、课程讲义
- **风格 C：Flat Vector Retro 扁平矢量复古风** — 黑色轮廓线+几何简化，适合 NotebookLM PPT、课程封面、复古感内容

用户未指定时默认用风格 A。

## 执行流程

### 1. 确认内容与风格
- 明确要画什么内容、用什么风格
- 从 `references/styles.md` 取对应风格块
- 风格 B 的布局模板在 `references/image-assistant-templates/`

### 2. 构建 Prompt

基础结构：
```
[风格块（从 styles.md 复制）]

顶部居中标题：'[中文标题]'

[内容描述：人物、场景、元素、布局]

[负面约束]
```

详细提示词模板见 `references/prompt-guide.md`。

### 3. 生成图片

```bash
cd /root/.openclaw/workspace/skills/zenmux-image-generation
ZENMUX_API_KEY="<key>" python3 scripts/generate.py \
  --output /root/myfiles/<filename>.png \
  --prompt "<完整prompt>"
```

API Key 读取：
```bash
cat ~/.openclaw/openclaw.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['models']['providers']['ZenMux']['apiKey'])"
```

### 4. 上传并发送到飞书

```bash
bash scripts/send_to_feishu.sh /root/myfiles/<filename>.png <open_id>
```

猫南北的 open_id：`ou_22f2eefd5abe63e0cd67f4882cec06d4`

## 注意事项

- 模型：`google/gemini-3-pro-image-preview`（需要 ZenMux Pro+）
- 403 偶发，重试即可
- 图片输出到 `/root/myfiles/`
- 所有文字标注默认中文
- 风格 B 的多张成套配图工作流见 `references/image-assistant-workflow.md`
