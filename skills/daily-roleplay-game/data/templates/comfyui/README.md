# ComfyUI 生图配置（动漫·模块化）

> 全部为动漫风格；针对 Mac Mini M4 16GB。  
> 更新：2026-02-25

---

## 1. 目录与模块

```
comfyui/
├── default.json              # 基础参数（步数 6、尺寸、默认 LoRA，仅动漫）
├── variables/
│   ├── checkpoints.json      # 动漫 Checkpoint 与场景映射
│   ├── scenes.json           # 场景索引（一表查：场景→checkpoint/工作流/提示词）
│   ├── hairstyles.json       # 职业→发型 tag
│   └── media_prefix.json     # 职业→输出文件名前缀
├── lora_presets/             # 动漫 LoRA 预设（职业/场景，无写实）
├── prompts/
│   ├── sfw_base.txt
│   ├── nsfw_base.txt
│   └── negative.txt
└── workflows/
    ├── sfw_morning.json
    ├── nsfw_strip.json
    └── nsfw_punish.json
```

**模块化用法**：先看 `variables/scenes.json` 定场景 → `variables/checkpoints.json` 定模型 → `default.json` 定步数/尺寸 → `lora_presets/` 按职业选 → `prompts/` 按 sfw/nsfw 选模板。

---

## 2. 基础参数（default.json）

| 参数 | 值 | 说明 |
|------|-----|------|
| checkpoint | waiNsfwIllustrious15.tvs0 | 动漫默认 |
| steps | **8** | 质量与速度平衡 |
| cfg | 1.5 | |
| 尺寸 | 512×768 | |
| sampler | dpmpp_sde / sgm_uniform | |
| default_loras | 3 个 | add-detail-xl, ILLofficelady, black pantyhose pony |

若需更快可适当降低 steps（如 6）；若追求更稳可保持 8。

---

## 3. Checkpoint（仅动漫）

`variables/checkpoints.json` 仅保留动漫方案：

| 键 | Checkpoint | 用途 |
|----|------------|------|
| default | waiNsfwIllustrious15.tvs0 | 通用/早安/日常 |
| anime_enhanced | hassakuXLIllustrious_v13StyleA | 强化线条/撩拨/特殊 |
| nsfw_specialized | waiNsfwIllustrious15.tvs0 | 所有 NSFW 场景 |

场景→checkpoint 见同文件 `scene_mapping`。已移除写实/realistic/pornmaster。

---

## 4. 场景索引（variables/scenes.json）

一处定义「场景 → checkpoint + 工作流 + 提示词类型」，方便加新场景、调映射。

| 场景 id | 说明 | checkpoint | 提示词 |
|---------|------|------------|--------|
| sfw_morning | 早安自拍 | default | sfw |
| sfw_daily / sfw_tease / sfw_professional / sfw_intimate | 日常/撩拨/职业/亲密 | default 或 anime_enhanced | sfw |
| nsfw_strip / nsfw_lingerie / nsfw_closeup / nsfw_punish / nsfw_action / nsfw_aftercare | 脱衣/内衣/特写/惩罚/体位/事后 | nsfw_specialized | nsfw |
| special_outdoor / special_costume / special_mood | 户外/特殊服装/情绪 | anime_enhanced | sfw |

调试时：改 `scenes.json` 里该场景的 `checkpoint_key` 或 `workflow` 即可，无需改多份配置。

---

## 5. 年龄与职业多样化

- **年龄**：外形/体型 tag 来自 `data/age_profiles.yaml` 当前年龄段的 `appearance.comfyui_tags`（如 slim / slender / mature body / voluptuous），生成时拼进正向提示词。
- **职业**：`{{PROFESSION_TAGS}}` 来自 roleplay-active.md；发型用 `variables/hairstyles.json`；LoRA 用 `lora_presets/` 下按职业选的预设（见下）。
- **造型多样化**：通过「场景 + 年龄 comfyui_tags + 职业 LoRA 预设 + 职业/穿着 tag」组合实现，无需为每种年龄×职业单独建配置。

---

## 6. LoRA 预设（仅动漫）

| 预设 | 适用 | 说明 |
|------|------|------|
| default.json | 全部 | 3 个 LoRA，通用 |
| casual.json | 调酒师、咖啡师、瑜伽等 | 休闲 |
| elegant.json | 秘书、律师、高管等 | 优雅 |
| special.json | 兔女郎、巫女、女仆等 | 特殊服装 |
| uniform.json | 护士、乘务、空姐、警察等 | 制服 |
| heels_stockings.json | 通用 | 丝袜高跟 |
| nsfw_*.json | 按姿势 | 传教士/后入/颜坐/分腿/自拍等 |

已删除 realistic_nsfw；全部预设仅搭配动漫 checkpoint。

---

## 7. 提示词变量

| 变量 | 来源 |
|------|------|
| {{PROFESSION_TAGS}} | roleplay-active.md ComfyUI 关键词 |
| {{HAIRSTYLE}} | variables/hairstyles.json 按职业 |
| {{OUTFIT_TAGS}} | 当前穿着（guess-log/roleplay-active） |
| {{UNDRESS_STATE}} | variables/hairstyles.json undress_states（NSFW） |
| {{FACE_TAGS}} / {{MOOD_TAGS}} / {{SCENE_TAGS}} | 按场景与年龄设定 |
| {{LORA_EXTRA_TAGS}} | 当前 lora 预设的 extra_tags |
| **年龄外形** | data/age_profiles.yaml 当前 profile 的 appearance.comfyui_tags，拼入正向 |

---

## 8. 调用流程（集约）

1. 确定**场景 id**（如 sfw_morning / nsfw_strip）→ 查 `variables/scenes.json` 得 `checkpoint_key`、`workflow`、`prompt_type`。
2. 读 **default.json** 取 steps、cfg、尺寸、default_loras。
3. 用 **checkpoint_key** 在 `variables/checkpoints.json` 取 checkpoint 文件名。
4. 按**职业**选 **lora_presets/** 下预设（可加 nsfw_* 按姿势），与 default_loras 合并。
5. 按 **prompt_type** 选 prompts/sfw_base.txt 或 nsfw_base.txt，填变量（含年龄 comfyui_tags）。
6. 用 **workflow** 指向的 json 组装节点，提交 ComfyUI。

---

## 9. 调试与扩展

- **改单张速度**：调 default.json 的 `steps`（如 6 更快，8 更稳）。
- **改某场景风格**：改 scenes.json 里该场景的 `checkpoint_key`（如 default ↔ anime_enhanced）。
- **加新场景**：在 scenes.json 的 `scenes` 里追加一条（id、checkpoint_key、prompt_type、workflow）。
- **加新职业/造型**：在 hairstyles.json、media_prefix.json、lora_presets 中补映射或新预设。
