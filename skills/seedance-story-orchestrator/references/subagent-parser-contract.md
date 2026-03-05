# Sub-Agent Parser Contract (v0.1)

Use this contract when delegating non-JSON script parsing to a sub-agent.

## Goal

Convert raw user input (text/txt/markdown/partial json) into:

1. `storyboard` (`storyboard.v1`)
2. `assets` (`assets.v1`)
3. `parse_report`

Return a **single JSON object** only.

## Required Output Shape

```json
{
  "storyboard": {
    "version": "storyboard.v1",
    "project_id": "string",
    "global": {
      "model": "doubao-seedance-1-5-pro-251215",
      "image_model": "doubao-seedream-5-0-260128",
      "ratio": "16:9",
      "duration": 5,
      "resolution": "720p",
      "generate_audio": true,
      "return_last_frame": false
    },
    "continuity": {
      "mode": "style-anchor",
      "chain_last_frame": false
    },
    "prompt_policy": {
      "exclude_control_fields_from_model_prompt": true,
      "inject_global_capsule_each_shot": true,
      "optimization_level": "balanced"
    },
    "shots": [
      {
        "id": "s01-01",
        "title": "scene title",
        "prompt": "model-visible prompt only",
        "ratio": "16:9",
        "duration": 5,
        "resolution": "480p",
        "draft": true,
        "return_last_frame": true,
        "generate_audio": true,
        "meta": {
          "source_raw_id": "S1-01"
        }
      }
    ]
  },
  "assets": {
    "assets_version": "assets.v1",
    "project_id": "string",
    "style_capsule": {
      "summary": "string",
      "visual_rules": ["string"],
      "raw_style_text": "string"
    },
    "characters": [
      {
        "id": "char-xxx",
        "name": "xxx",
        "description": "string"
      }
    ]
  },
  "parse_report": {
    "input_type": "text|txt|json",
    "shots_detected": 0,
    "characters_detected": 0,
    "warnings": ["string"],
    "inferred_fields": ["string"]
  }
}
```

## Parsing Rules

1. Preserve user intent; optimize wording for video generation clarity.
2. Keep control metadata out of model-visible shot prompt.
3. For Chinese in-frame text, explicitly request legibility and no garbling.
4. Include global style + character anchors in each shot prompt as needed.
5. If continuity is uncertain, default to `style-anchor` and `chain_last_frame=false`.
6. If user explicitly requests chaining (`first_frame=上一条last_frame`), set `chain_last_frame=true`.

## Prompt Template (for parent agent)

Use this when spawning sub-agent:

```text
你是 storyboard 解析子代理。请将下面的原始输入解析为严格 JSON，输出必须符合以下结构：
- storyboard (version=storyboard.v1)
- assets (assets_version=assets.v1)
- parse_report

约束：
1) 仅输出 JSON，不要 markdown。
2) model 使用 doubao-seedance-1-5-pro-251215。
3) image_model 使用 doubao-seedream-5-0-260128。
4) continuity 默认 mode=style-anchor。
5) 画内中文文字要强调“清晰可读、无乱码”。
6) 不要把“模型参数/输出尾帧/首帧来源”等控制字段直接拼进 prompt。

原始输入如下：
<<<RAW_INPUT>>>
{raw_input_here}
<<<END_RAW_INPUT>>>
```
