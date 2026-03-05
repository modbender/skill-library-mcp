---
name: ai-drama-prompt-factory
description: AI短剧提示词工厂 - 端到端将小说/故事创意转化为结构化提示词包（角色立绘+场景+道具+分镜图片+视频+音频）的完整流水线。一个入口启动全流程，内部自动按阶段推进：策划→设计→剧本→诊断→提示词组装→API JSON输出。支持小说改编和原创短剧两条路径。触发词：AI短剧、短剧制作、小说转短剧、短剧提示词、提示词工厂、短剧全流程、小说改编短剧、生成短剧、AI视频剧本、短剧项目、分镜提示词、视频提示词、prompt factory。
---

# AI短剧提示词工厂 (AI Drama Prompt Factory)

端到端将小说或故事创意转化为结构化提示词包，输出标准JSON供外部AI生成工具消费。

**系统边界：只生产提示词数据，不做图片/视频/音频的实际生成。**

---

## ⚡ 启动协议（每次任务开始时必须执行）

**任何短剧相关任务触发后，在执行任何工作之前，必须先向用户确认以下信息：**

### Step 1：确认项目类型

向用户确认：
- **A 小说改编** — 用户提供小说/故事文本，改编为短剧提示词
- **B 原创短剧** — 用户提供创意/主题，从零创建短剧提示词

### Step 2：确认执行模式

向用户确认交付方式：
- **🚀 全程模式** — 一次跑完全部Phase，中间不停，最终一次性交付所有产出文件
- **📋 分阶段模式** — 每个Phase完成后输出交付物，等用户确认/修改后再进入下一阶段（推荐）
- **🎯 单阶段模式** — 只执行用户指定的某个Phase（需已有前序Phase的产出）

### Step 3：确认基础参数

向用户确认：
- **视觉风格** — 电影写实 / 日系动漫 / 2.5D（默认：电影写实）
- **剧本风格** — 标准叙事 / 爽文漫剧（默认：标准叙事）
- **目标集数** — 预计多少集（可后续调整）
- **每集时长** — 1分钟 / 2分钟 / 3分钟（默认：1-2分钟）
- **剧本分镜Markdown输出** — 是否同时输出可读性更强的Markdown分镜表格文档？（默认：否，仅输出JSON）

**确认完成后，开始执行第一个Phase。**

---

## 核心铁律（Phase 5组装时必须遵守）

**铁律一：分镜图片提示词中必须使用角色和道具的名字**
```
✅ 张慧芬转身替病床上的陈易（觉醒前）整理输液管
❌ 48岁中年女性转身替24岁苍白男性整理输液管
```

**铁律二：视频提示词必须基于分镜图片提示词派生**
视频是图片的动态延伸，不能独立生成。

**铁律三：提示词使用中文自然语言描述**
连贯的场景叙述句，不是英文标签堆叠。

---

## 全流程架构

```
启动协议 → Phase 1 策划 → Phase 2 设计 → Phase 3 剧本 → Phase 4 诊断 → Phase 5 组装
                                                          ↑        │
                                                          └────────┘
                                                          (修改≤3轮)
```

| 路径 | 流程 | 诊断 |
|------|------|------|
| A: 小说改编 | 全5阶段 | 必须 |
| B: 原创短剧 | Phase 1→2→3→5 | 可选 |

---

## Phase 1：策划

### 📥 输入
- 路径A：小说/故事文本（短篇直接读取，超过3万字先建索引，参见 [references/doc-reader-guide.md](references/doc-reader-guide.md)）
- 路径B：用户的创意描述/主题

### 📤 交付物（2个文件）

**文件1：`planning/story-outline.md`**

必须包含以下完整结构：

```markdown
# 故事大纲：{作品名称}

## 1. 基础信息
- 作品名称：{名称}
- 来源：{原创/改编自《XX》}
- 写作视角：{第一人称/第三人称全知/等}
- 视觉风格：{电影写实/日系动漫/2.5D}
- 剧本风格：{标准叙事/爽文漫剧}
- 目标集数：{N}集
- 每集时长：{N}分钟

## 2. 时空背景
{年代、地点、社会环境、特殊设定，150-300字}

## 3. 叙事结构
- 结构类型：{三幕/五幕/单元剧}
- 递进模式：{描述}
- 情绪曲线概要：{描述}

## 4. 核心冲突
{主角+困境+对抗力量+逆袭路径，100-200字}

## 5. 角色清单

### 主要角色
| 角色名 | 性别 | 年龄 | 身份 | 核心特征 | 外观变体 |
|--------|------|------|------|---------|---------|
| 陈易 | 男 | 24 | 大学生/觉醒者 | 外表懦弱内心坚韧 | 觉醒前、觉醒后 |
| ... | | | | | |

### 次要角色
| 角色名 | 性别 | 身份 | 故事功能 |
|--------|------|------|---------|
| ... | | | |

## 6. 关键道具
| 道具名 | 外观概述 | 剧情功能 | 首次出现 |
|--------|---------|---------|---------|
| 天机古卷 | 泛黄线装古书 | 主角能力来源 | 第1集 |

## 7. 核心场景清单
| 场景名 | 类型 | 出现集数 |
|--------|------|---------|
| 医院普通病房 | 室内 | 第1-2集 |
| 世界杯决赛球场 | 室外 | 第5-6集 |
```

**文件2：`planning/episodes-plan.md`**

```markdown
# 分集规划

## 第1集「{标题}」
- 核心事件：{一句话概述}
- 涉及角色：{角色列表}
- 主要场景：{场景列表}
- 情绪走向：{如：压抑→微光}
- 集尾钩子：{悬念/反转描述}
- 预计镜头数：{N}

## 第2集「{标题}」
...
```

### ✅ Phase 1 完成标志
- story-outline.md 包含全部7个章节
- episodes-plan.md 覆盖所有目标集数
- 每集有明确的集尾钩子

### ⏸️ 分阶段模式
输出以上2个文件后，告知用户：
> Phase 1 策划完成。请查看故事大纲和分集规划，确认无误后我将进入 Phase 2 设计阶段。如需调整请告知。

---

## Phase 2：设计

### 📥 输入
- Phase 1 的 story-outline.md（角色清单、场景清单、道具清单、风格定义）

### 📤 交付物（4类文件）

**文件1：`characters/{角色名}.json`（每个角色一个文件）**

```json
{
  "name": "陈易",
  "character_id": "char_chenyi",
  "gender": "男",
  "age": 24,
  "identity": "被雷劈获得超能力的普通大学生",
  "personality": {
    "core_traits": "外表懦弱内心坚韧",
    "speech_style": "初期怯懦，觉醒后沉稳有力",
    "motivation": "证明自己的价值"
  },
  "voice_default": {
    "gender": "male",
    "age_desc": "青年男性",
    "timbre": "初期虚弱低沉，觉醒后清亮有力"
  },
  "variants": {
    "觉醒前": {
      "description": "病号服状态，虚弱苍白",
      "appearance": "短发凌乱/黑色、面色苍白",
      "outfit": "蓝白条纹病号服、病号裤、无鞋、无配饰",
      "prompt": "现代、24岁、男、短发凌乱/黑色、蓝白条纹病号服、病号裤、无、面色苍白，电影写实风格，高质量，真实光影，电影级打光，8K分辨率，超高清细节，全身，纯色背景，面向镜头"
    },
    "觉醒后": {
      "description": "运动装状态，精神焕发",
      "appearance": "短发利落/黑色、目光锐利",
      "outfit": "灰色运动外套、深蓝色运动裤、白色运动鞋、无配饰",
      "prompt": "现代、24岁、男、短发利落/黑色、灰色运动外套、深蓝色运动裤、白色运动鞋、无配饰，电影写实风格，高质量，真实光影，电影级打光，8K分辨率，超高清细节，全身，纯色背景，面向镜头"
    }
  }
}
```

**角色提示词公式：**
```
{时代}、{年龄}岁、{性别}、{发型/发色}、{上装}、{下装}、{鞋/配饰}、{面部特征}，
{风格标签}，全身，纯色背景，面向镜头
```

**文件2：`scenes/{场景名}.json`（每个场景一个文件）**

```json
{
  "name": "医院普通病房",
  "scene_id": "scene_hospital_room",
  "type": "室内",
  "era": "中国现代",
  "key_elements": ["白色墙面", "输液架", "病床", "窗户"],
  "variants": {
    "白天": {
      "lighting": "窗户透入柔和自然光",
      "prompt": "中国现代，电影写实风格，室内，白天，现代医院普通病房，白色墙面干净整洁，输液架立在病床旁，病床白色床单，窗户透入柔和自然光"
    },
    "夜晚": {
      "lighting": "走廊灯光透过门缝微弱照入",
      "prompt": "中国现代，电影写实风格，室内，深夜，现代医院普通病房，白色墙面，病床旁输液架，走廊灯光透过门缝微弱照入，氛围安静压抑"
    }
  }
}
```

**场景提示词公式：** `{时代}，{风格}，{室内/室外}，{时间}，{环境详描}`

**文件3：`props/{道具名}.json`（每个关键道具一个文件，普通道具不需要）**

```json
{
  "name": "天机古卷",
  "prop_id": "prop_ancient_book",
  "type": "信物",
  "story_function": "主角能力来源，被雷劈时的护身符",
  "prompt": "中国古代，电影写实风格，信物，泛黄卷边的线装书，封面为深蓝色布面，边角磨损严重，书页间夹有干枯的银杏叶书签，纸质泛黄，封面深蓝色布面，书签枯黄色"
}
```

**道具提示词公式：** `{时代}，{风格}，{类型}，{外观详描}，{材质/颜色}`

**文件4：`style/style-guide.json`（全局唯一）**

```json
{
  "style_type": "电影写实",
  "era": "中国现代",
  "character_prompt_suffix": "电影写实风格，高质量，真实光影，电影级打光，8K分辨率，超高清细节",
  "scene_prompt_suffix": "电影写实风格",
  "storyboard_prompt_suffix": "写实风格，电影级打光，8K分辨率，超细节刻画",
  "storyboard_enhance_tags": ["高对比度光影", "动态模糊感", "电影级质感", "8K超高清"],
  "target_ratio": "9:16"
}
```

**详细规范：** [references/design-guide.md](references/design-guide.md)

### ✅ Phase 2 完成标志
- 所有主要角色都有 .json 文件，每个角色至少1个variant且含完整prompt
- 所有核心场景都有 .json 文件，至少1个variant且含完整prompt
- 所有关键道具都有 .json 文件且含完整prompt
- style-guide.json 已创建
- 所有提示词风格后缀与 style-guide 一致

### ⏸️ 分阶段模式
输出所有设计文件后，向用户展示：
> Phase 2 设计完成。共生成 {N} 个角色（含 {M} 个状态变体）、{N} 个场景、{N} 个道具的设计卡和提示词。
>
> 角色一览：
> - 陈易：觉醒前（病号服）/ 觉醒后（运动装）
> - 张慧芬：默认（护士装）
> - ...
>
> 请确认角色/场景/道具设计是否需要调整，确认后进入 Phase 3 剧本生成。

---

## Phase 3：剧本

### 📥 输入
- Phase 1 的 episodes-plan.md
- Phase 2 的全部角色/场景/道具设计文件
- 路径A：原著对应章节文本

### 📤 交付物（每集2-3个文件）

**文件1：`scripts/ep{NN}/script.json`（核心交付物）**

```json
{
  "episode": {
    "number": 1,
    "title": "天降奇才",
    "duration_target": "90s",
    "style": "标准叙事",
    "emotion_arc": "压抑→微光"
  },
  "shots": [
    {
      "shot_id": "ep01_sh01",
      "shot_number": 1,
      "duration": "3s",
      "characters": [
        { "name": "陈勇", "variant": "默认" },
        { "name": "张慧芬", "variant": "默认" },
        { "name": "陈易", "variant": "觉醒前" }
      ],
      "scene": "医院普通病房",
      "scene_variant": "白天",
      "shot_type": "近景",
      "camera_movement": "固定",
      "action_desc": "画面右侧陈勇背影离去，张慧芬转身替病床上的陈易整理输液管，轻叹气，眼神略带无奈",
      "dialogue": {
        "speaker": "张慧芬",
        "text": "唉，陈易，你的医药费已经拖欠三天了...",
        "emotion": "无奈叹息"
      },
      "sfx": ["脚步声远去", "输液管碰撞"],
      "bgm": "无",
      "source_anchor": "P-003",
      "emotion_level": 2,
      "narration": null
    },
    {
      "shot_id": "ep01_sh02",
      "shot_number": 2,
      "...": "..."
    }
  ],
  "episode_summary": {
    "total_shots": 15,
    "characters_used": ["陈易", "张慧芬", "陈勇"],
    "scenes_used": ["医院普通病房"],
    "hook": "陈易在病床上突然睁开双眼，瞳孔中闪过金色光芒"
  }
}
```

**每个shot必须包含的字段：**

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| shot_id | string | ✅ | `ep{NN}_sh{NN}` 全局唯一 |
| shot_number | int | ✅ | 集内序号 |
| duration | string | ✅ | 目标时长（如"3s"） |
| characters | array | ✅ | 出场角色，每个含name和variant |
| scene | string | ✅ | 场景名（对应scenes/下的文件） |
| scene_variant | string | ✅ | 场景变体（白天/夜晚等） |
| shot_type | string | ✅ | 特写/近景/中景/全景/远景 |
| camera_movement | string | ✅ | 固定/推/拉/摇/跟 |
| action_desc | string | ✅ | 动作+表情+位置的自然语言描述 |
| dialogue | object/null | ✅ | 有对白时：speaker+text+emotion；无对白时：null |
| sfx | array | ✅ | 音效列表（可为空数组） |
| bgm | string | ✅ | BGM描述或"无" |
| source_anchor | string | ✅ | 原文锚点（改编）或"原创" |
| emotion_level | int | ✅ | 情绪强度1-5 |
| narration | string/null | ✅ | 旁白文本（爽文风格时使用）或null |

**文件2：`continuity/ep{NN}-state.json`（连贯性状态）**

```json
{
  "episode": 1,
  "character_states": {
    "陈易": {
      "variant": "觉醒前",
      "location": "医院病房",
      "emotion": "昏迷中",
      "carrying": []
    },
    "张慧芬": {
      "variant": "默认",
      "location": "医院病房",
      "emotion": "无奈疲惫",
      "carrying": []
    }
  },
  "planted_threads": [
    { "thread": "陈易的医药费问题", "planted_at": "ep01_sh01" }
  ],
  "resolved_threads": [],
  "props_status": {
    "天机古卷": "在陈易枕头下"
  },
  "next_hook": "陈易在病床上突然睁开双眼，瞳孔中闪过金色光芒"
}
```

**详细规范：** [references/script-generation-guide.md](references/script-generation-guide.md)
**爽文风格：** [references/manga-drama-guide.md](references/manga-drama-guide.md)
**连贯性管理：** [references/continuity-guide.md](references/continuity-guide.md)

**文件3（可选）：`scripts/ep{NN}/script.md`（Markdown分镜表格文档）**

> 仅当用户在启动协议中选择"是"输出Markdown时才生成此文件。

```markdown
# 第{N}集「{标题}」分镜剧本

> 情绪走向：{情绪弧线}　｜　目标时长：{时长}　｜　镜头总数：{N}

## 分镜表

| 镜头号 | 时长 | 角色 | 场景/变体 | 景别 | 运镜 | 动作描述 | 对白 | 音效 | BGM | 原文锚点 |
|--------|------|------|----------|------|------|---------|------|------|-----|---------|
| ep01_sh01 | 3s | 陈勇（默认）、张慧芬（默认）、陈易（觉醒前） | 医院普通病房/白天 | 近景 | 固定 | 画面右侧陈勇背影离去，张慧芬转身替病床上的陈易整理输液管，轻叹气，眼神略带无奈 | 张慧芬："唉，陈易，你的医药费已经拖欠三天了..."（无奈叹息） | 脚步声远去、输液管碰撞 | 无 | P-003 |
| ep01_sh02 | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

## 集尾钩子

{钩子描述}

## 本集统计

- 总镜头数：{N}
- 涉及角色：{角色列表}
- 涉及场景：{场景列表}
- 含对白镜头：{N}个
- 情绪高点镜头：{镜头号列表}
```

**Markdown分镜表生成规则：**
- 表格字段与 `script.json` 中的 shot 字段一一对应
- 角色列写为 `角色名（变体）`，无变体时只写角色名
- 对白列格式为 `说话人："台词"（情绪）`，无对白时填 `—`
- 音效列多个音效用顿号分隔，无音效时填 `—`
- 此文件作为可读性辅助文档，**script.json 仍为唯一权威数据源**

### ✅ Phase 3 完成标志（每集）
- script.json 包含所有镜头，每个shot的所有必须字段齐全
- shot_id 全局无重复
- characters 中引用的角色名和variant都存在于Phase 2的设计文件中
- scene 引用的场景名和variant都存在于Phase 2的设计文件中
- 集尾有钩子
- ep{NN}-state.json 已生成
- 【如用户选择Markdown输出】script.md 已生成，表格内容与 script.json 一致

### ⏸️ 分阶段模式
每集剧本完成后，向用户展示：
> Phase 3 第{N}集剧本完成。共 {M} 个镜头，涉及角色：{列表}，涉及场景：{列表}。
> 集尾钩子：{钩子描述}
> [如已选择Markdown输出] 同时输出了 Markdown 分镜表格文档 `scripts/ep{NN}/script.md`。
>
> [如为改编项目] 即将进入 Phase 4 诊断，对照原著校验忠实度。
> [如为原创项目] 是否需要调整？确认后可直接进入 Phase 5 组装提示词。

---

## Phase 4：诊断（小说改编必须，原创可选）

### 📥 输入
- Phase 3 的 script.json
- 原著文本（通过source_anchor定位对应段落）

### 📤 交付物（1个文件）

**文件：`continuity/diagnosis-ep{NN}.md`**

```markdown
# 第{N}集诊断报告

## 总评
- **综合评分：{分数}/100**
- **结论：{✅ 通过 / ❌ 未通过}**
- 致命问题（🔴）：{数量}个
- 严重问题（🟠）：{数量}个
- 一般问题（🟡）：{数量}个

## 各维度评分

| 维度 | 得分 | 权重 | 加权分 |
|------|------|------|--------|
| 情节忠实度 | {x}/100 | 35% | {y} |
| 对白还原度 | {x}/100 | 25% | {y} |
| 角色一致性 | {x}/100 | 20% | {y} |
| 情感曲线 | {x}/100 | 10% | {y} |
| 连贯性 | {x}/100 | 10% | {y} |
| **合计** | | **100%** | **{总分}** |

## 问题清单

### 🔴 致命问题
1. **[ep01_sh05]** {问题描述}
   - 原著：{原文内容}
   - 剧本：{剧本内容}
   - 修改建议：{具体修改方案}

### 🟠 严重问题
...

### 🟡 一般问题
...

## 亮点
- {做得好的地方}

## 修改清单（按镜头号排序）
| 镜头 | 级别 | 修改内容 |
|------|------|---------|
| ep01_sh05 | 🔴 | {具体修改指导} |
| ep01_sh12 | 🟠 | {具体修改指导} |
```

### 通过标准
- 综合评分 ≥ 75
- 无致命问题（🔴）
- 严重问题（🟠）≤ 2个

### 诊断闭环
```
剧本 → 诊断 → ✅ 通过(≥75) → Phase 5
              → ❌ 未通过 → 按修改清单逐镜头修改 → 再诊断（最多3轮）
                                                    → 仍未通过 → 提示用户人工介入
```

**详细规范：** [references/diagnosis-guide.md](references/diagnosis-guide.md)

### ✅ Phase 4 完成标志
- diagnosis-ep{NN}.md 已输出
- 综合评分 ≥ 75 且满足通过标准
- 如未通过，修改后的script.json已更新

### ⏸️ 分阶段模式
诊断完成后，向用户展示：
> Phase 4 诊断完成。第{N}集评分：{分数}/100，{✅通过/❌未通过}。
> [通过] 即将进入 Phase 5 组装提示词包。
> [未通过] 发现 {N} 个问题需要修改（致命{N}个/严重{N}个），是否立即修改？

---

## Phase 5：提示词组装

### 📥 输入
- Phase 2 的全部角色/场景/道具/风格文件
- Phase 3 的 script.json（已通过诊断）

### 📤 交付物（2个文件）

**文件1：`output/project-manifest.json`（全项目唯一，首次生成后增量更新）**

```json
{
  "project": {
    "title": "项目名",
    "source_title": "原著名（如有）",
    "genre": "都市逆袭",
    "era": "中国现代",
    "total_episodes": 20,
    "target_ratio": "9:16"
  },
  "style": {
    "style_type": "电影写实",
    "character_prompt_suffix": "电影写实风格，高质量，真实光影，电影级打光，8K分辨率，超高清细节",
    "storyboard_prompt_suffix": "写实风格，电影级打光，8K分辨率，超细节刻画"
  },
  "characters": {
    "陈易": {
      "gender": "男",
      "age": 24,
      "variants": {
        "觉醒前": { "prompt": "完整角色提示词..." },
        "觉醒后": { "prompt": "完整角色提示词..." }
      }
    }
  },
  "scenes": {
    "医院普通病房": {
      "variants": {
        "白天": { "prompt": "完整场景提示词..." },
        "夜晚": { "prompt": "完整场景提示词..." }
      }
    }
  },
  "props": {
    "天机古卷": { "prompt": "完整道具提示词..." }
  }
}
```

**文件2：`output/ep{NN}-prompt-package.json`（每集一个）**

```json
{
  "episode": {
    "number": 1,
    "title": "天降奇才",
    "shot_count": 15,
    "characters_used": ["陈易", "张慧芬", "陈勇"],
    "scenes_used": ["医院普通病房"]
  },
  "shots": [
    {
      "shot_id": "ep01_sh01",
      "shot_number": 1,
      "duration": "3s",

      "script": {
        "characters": [
          { "name": "陈勇", "variant": "默认" },
          { "name": "张慧芬", "variant": "默认" },
          { "name": "陈易", "variant": "觉醒前" }
        ],
        "scene": "医院普通病房",
        "scene_variant": "白天",
        "shot_type": "近景",
        "action_desc": "画面右侧陈勇背影离去，张慧芬转身替病床上的陈易整理输液管",
        "dialogue": {
          "speaker": "张慧芬",
          "text": "唉，陈易，你的医药费已经拖欠三天了...",
          "emotion": "无奈叹息"
        },
        "source_anchor": "P-003"
      },

      "storyboard_prompt": "中国现代，医院普通病房，白色墙面，输液架，病床，柔和冷光，近景镜头（胸部以上），画面右侧陈勇背影离去，张慧芬转身替病床上的陈易（觉醒前）整理输液管，轻叹气，眼神略带无奈，写实风格，电影级打光，8K分辨率，超细节刻画",

      "video_prompt": "场景为中国现代医院普通病房，白色墙面干净整洁，输液架立在病床旁，柔和冷光洒满房间。镜头从张慧芬(女)的近景开始，她站在病床边，目光望向画面右侧，陈勇(男)的背影正缓缓走出病房门口，写实风格，电影级打光。切镜到张慧芬(女)的近景（胸部以上），她收回目光转身面向病床上的陈易，双手轻柔整理输液管，轻叹气，嘴唇微动说着：\"唉，陈易，你的医药费已经拖欠三天了...\"，眼神略带无奈，超细节刻画手部动作，8K分辨率。最后切镜到两人同框的中景，张慧芬(女)整理好输液管后低头看着陈易，病房里安静无声，氛围忧虑而沉重，无背景音乐。陈勇是男性，张慧芬是女性",

      "audio_spec": {
        "dialogue": {
          "text": "唉，陈易，你的医药费已经拖欠三天了...",
          "speaker": "张慧芬",
          "speaker_gender": "female",
          "voice_desc": "中年女性，声音疲惫温和，带叹息感，语速缓慢",
          "emotion": "无奈叹息"
        },
        "sfx": [
          { "type": "脚步声远去", "timing": "陈勇离开时", "volume": "低" },
          { "type": "输液管碰撞", "timing": "张慧芬整理时", "volume": "轻微" }
        ],
        "bgm": {
          "mood": "无",
          "note": "无背景音乐，保持安静压抑氛围"
        }
      }
    }
  ],
  "continuity": {
    "character_states": {
      "陈易": { "variant": "觉醒前", "location": "医院病房" },
      "张慧芬": { "variant": "默认", "location": "医院病房" }
    },
    "next_hook": "陈易在病床上突然睁开双眼，瞳孔中闪过金色光芒"
  }
}
```

**每个shot必须包含的3个提示词字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| storyboard_prompt | string | 分镜图片提示词。中文自然语言。角色用名字引用。 |
| video_prompt | string | 视频提示词。基于storyboard_prompt派生。含切镜/对白/性别声明。 |
| audio_spec | object | 音频描述。含dialogue(对白+voice_desc)、sfx(音效)、bgm(BGM)。 |

### 分镜图片提示词组装公式
```
{时代}，{场景描述}，{光影}，{景别}，
{角色名(状态)} + {位置} + {动作} + {表情}，
{风格}，{画质标签}
```

### 视频提示词派生公式
```
场景为{场景描述扩写}。
镜头从{角色名(性别)}的{景别}开始，{动作}，{风格}。
切镜到{角色名(性别)}的{景别}，{动作}，{对白："台词"}，{表情}。
最后切镜到{景别}，{氛围收束}。
{角色A}是{性别}，{角色B}是{性别}
```

**详细组装规则：** [references/assembly-rules.md](references/assembly-rules.md)
**提示词示例：** [references/prompt-examples.md](references/prompt-examples.md)
**平台适配：** [references/platform-adapters.md](references/platform-adapters.md)
**完整Schema：** [references/api-schema.md](references/api-schema.md)

### ✅ Phase 5 完成标志（每集）
- project-manifest.json 已生成/更新
- ep{NN}-prompt-package.json 已生成
- 每个shot都包含 storyboard_prompt + video_prompt + audio_spec
- storyboard_prompt 中角色用名字引用，有变体的标注了状态
- video_prompt 基于 storyboard_prompt 派生，角色标注了性别，末尾有性别汇总
- 全部提示词风格标签与 style-guide 一致
- JSON 合法可被 JSON.parse() 解析

### ⏸️ 分阶段模式
每集提示词包完成后，向用户展示：
> Phase 5 第{N}集提示词包组装完成。
> - 共 {M} 个镜头
> - 分镜图片提示词：{M} 条
> - 视频提示词：{M} 条
> - 含对白镜头：{M} 个
> - 输出文件：output/ep{NN}-prompt-package.json
>
> 是否继续生成下一集？或需要调整某个镜头的提示词？

---

## 交付物总览

### 全项目文件清单

```
{project-name}/
├── planning/
│   ├── story-outline.md              ← Phase 1
│   └── episodes-plan.md              ← Phase 1
│
├── characters/
│   ├── 陈易.json                      ← Phase 2
│   ├── 张慧芬.json                    ← Phase 2
│   └── ...
│
├── scenes/
│   ├── 医院普通病房.json              ← Phase 2
│   └── ...
│
├── props/
│   └── 天机古卷.json                  ← Phase 2
│
├── style/
│   └── style-guide.json              ← Phase 2
│
├── scripts/
│   ├── ep01/script.json              ← Phase 3
│   ├── ep01/script.md                ← Phase 3（可选，Markdown分镜表）
│   ├── ep02/script.json              ← Phase 3
│   ├── ep02/script.md                ← Phase 3（可选）
│   └── ...
│
├── continuity/
│   ├── ep01-state.json               ← Phase 3
│   ├── ep02-state.json               ← Phase 3
│   ├── diagnosis-ep01.md             ← Phase 4
│   └── diagnosis-ep02.md             ← Phase 4
│
└── output/
    ├── project-manifest.json          ← Phase 5（首次生成后增量更新）
    ├── ep01-prompt-package.json       ← Phase 5
    ├── ep02-prompt-package.json       ← Phase 5
    └── ...
```

### 各Phase交付物速查

| Phase | 交付物 | 文件格式 | 数量 |
|-------|--------|---------|------|
| Phase 1 策划 | story-outline.md + episodes-plan.md | Markdown | 2个 |
| Phase 2 设计 | {角色}.json + {场景}.json + {道具}.json + style-guide.json | JSON | 按角色/场景/道具数量 |
| Phase 3 剧本 | script.json + ep{NN}-state.json + script.md（可选） | JSON + Markdown | 每集2-3个 |
| Phase 4 诊断 | diagnosis-ep{NN}.md | Markdown | 每集1个 |
| Phase 5 组装 | project-manifest.json + ep{NN}-prompt-package.json | JSON | 1 + 每集1个 |

---

## 特殊模式

### 单镜头调试
```
用户："预览第1集镜头3的提示词"
→ 输出该镜头的完整链路：
  1. 涉及角色的立绘提示词
  2. 涉及场景的场景提示词
  3. 分镜图片提示词
  4. 视频提示词
  5. 音频描述
```

### 续写模式
```
用户："继续生成下一集"
→ 读取最近一集的 ep{NN}-state.json
→ 从 Phase 3 开始（→4→5）
```

### 补建模式
```
用户已有剧本，只需要提示词
→ 跳过Phase 1/3，先确认Phase 2设计件是否齐全
→ 如缺少设计件，从剧本描述中自动提取生成（降级模式）
→ 进入Phase 5组装
```
