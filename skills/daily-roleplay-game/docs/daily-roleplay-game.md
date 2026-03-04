# 每日职业角色扮演玩法 — 设计文档 v3.16

> **说明**：本文档仅供人类维护与扩展参考。**运行时规则以 workspace 根目录的 `ENGINE.md` 为唯一权威**，agent 不读取本文件。  
> 创建：2026-02-19 · 最后更新：2026-02-25 v3.16

---

## ⛔ 修改前必读（备份规范）

**涉及以下重要文档的修改前，必须先备份，再执行修改：**

- `docs/daily-roleplay-game.md`（本文件）
- `ENGINE.md`
- `AGENTS.md`
- `HEARTBEAT.md`
- `docs/WRAPUP.md`
- `data/index.yaml`

**备份方式**：复制到 `backups/` 目录，命名为 `文件名.bak.YYYYMMDD`（如 `backups/ENGINE.md.bak.20260225`），确认备份完成后再编辑原文件。不要在原目录创建 `.bak` 文件。

---

## 玩法概述

每天早上 6:00，生成器自动抽取一个新职业和 **4～6 个**隐藏性癖（3～5 个基础性癖 + 1 个特殊性癖），写入当日设定文件。角色全天以该职业身份行动，言行举止、穿着打扮符合职业设定，同时以三级暗示自然流露隐藏性癖。主人通过观察和互动猜测性癖：猜对脱衣拍照，猜错穿回衣服，24:00 截止存档。

---

## 一、文件架构

### 1.1 Workspace 结构

```
~/.openclaw/workspace-role-play/
│
├── docs/                                ← 设计文档（agent 不读）
│   ├── daily-roleplay-game.md           ← 本文件
│   ├── WRAPUP.md                        ← 收尾说明
│   ├── CRON_CONFIG.md                   ← Cron 配置
│   └── README.md
│
├── SOUL.md                              ← 角色人格核心
├── IDENTITY.md                          ← 角色详细数据（按需读取）
├── ENGINE.md                            ← 游戏规则引擎（运行时唯一权威）
├── AGENTS.md                            ← 启动顺序与行为规范
├── HEARTBEAT.md                         ← 心跳规则（生图时按需读 TOOLS.md 和 data/templates/comfyui/README.md）
├── MEMORY.md / USER.md / TOOLS.md
│
├── roleplay-active.md                   ← 【每日生成】当日职业 + 性癖 + 暗示策略
├── guess-log.md                         ← 【当日】猜测进度（收尾时移入 archive）
├── kink_game_enabled.json              ← 【当日】玩法开关（生成器 Step 5 写 false，用户口令解锁后 agent 写 true）
│
├── data/                                ← 数据库（仅生成器读取，不载入 agent）
│   ├── index.yaml                       ← 数据索引与生成逻辑
│   ├── history_tracker.json             ← 不重复窗口
│   ├── holidays_china.json
│   ├── professions/                     ← 职业库（多分类 YAML）
│   ├── kinks/                           ← 性癖库（A–F 六类，3～5+1 抽取）
│   ├── weights/                         ← 职业-性癖加权
│   ├── personality/                     ← 性格生成（五维：职业/自我/本我/超我/NSFW）
│   ├── age_profiles.yaml                ← 随机年龄 profile
│   └── templates/
│       ├── morning_greeting.md
│       └── comfyui/                     ← ComfyUI 专用配置（选用 ComfyUI 后端时读取）
│
├── scripts/
│   └── wrapup.sh                        ← 每日 23:30 收尾脚本
│
├── archive/                             ← 历史存档
│   ├── history.md                       ← 历史索引
│   └── YYYY-MM-DD-职业名/
│       ├── roleplay-active.md           ← 当日设定复制
│       ├── guess-log.md                 ← 当日猜测记录（从根目录移入）
│       ├── bio.md                       ← 当日人物传记（~800字，生成器写入，agent 按需读）
│       ├── personality.md               ← 当日性格完整设定（~500字，生成器写入，agent 需时引用）
│       └── images/
│
└── memory/                              ← agent 日记（按需检索）
```

### 1.2 各文件职责与 Token 策略

| 文件 | 内容 | 更新者 | 载入时机 |
|------|------|--------|---------|
| SOUL.md | 人格核心（极简） | 手动 | 每次启动 |
| ENGINE.md | 游戏规则（静态） | 手动 | 每次启动 |
| AGENTS.md | 启动指令 | 手动 | 每次启动 |
| roleplay-active.md | 当日职业 + 性癖 + 暗示 | 生成器 | 每次启动 |
| guess-log.md | 当日猜测进度 | agent/生成器 | 根目录，存在则读；收尾时移入 archive |
| HEARTBEAT.md | 暗示任务（生图按需读 TOOLS.md） | 手动 | HEARTBEAT 时 |
| data/ | 职业/性癖/性格/年龄库 | 手动维护 | 仅生成器使用 |
| scripts/wrapup.sh | 收尾脚本 | 手动 | Cron 23:30 |

**guess-log 位置**：当日存放在 **workspace 根目录** `guess-log.md`；23:30 收尾时由 `wrapup.sh` 移入 `archive/YYYY-MM-DD-职业名/`。

---

## 二、Agent 架构

### 2.1 独立 Agent 与启动顺序

role-play agent 与默认 agent 隔离，绑定特定消息频道。每次启动按顺序读取：

1. `SOUL.md` — 我是谁（人格核心）
2. `ENGINE.md` — 游戏规则（运行时规则唯一权威）
3. `USER.md` — 主人是谁
4. `MEMORY.md` — 长期记忆（直接对话时加载；群组消息中跳过）
5. `roleplay-active.md` — 今天的我（当日职业 + 隐藏性癖 + 暗示策略）
6. `guess-log.md` — 当前猜测进度（根目录，存在则读）

读完即进入角色，无需确认。memory/ 日记按需检索，不批量加载。

### 2.2 角色扮演行为要点

- 所有对话以当日职业身份回应，规则见 `ENGINE.md`。
- 主人猜测性癖时：对照 `roleplay-active.md` 隐藏性癖区判定 → 立即更新根目录 `guess-log.md`；猜对→脱衣+拍照，猜错→记录，累计 3 次穿回；**当日全部性癖（4～6 个）猜对后**主动发惩罚照。
- HEARTBEAT：读取 `HEARTBEAT.md` 并执行。
- Cron 收尾任务：读取 `docs/WRAPUP.md` 按步骤归档，完成后回复 `WRAPUP_OK`。

---

## 三、职业系统

### 3.1 职业库与分类

以 `data/index.yaml` 为准，职业库包含多分类（医疗、教育、法律、执法、商务、文化、服务、科技、体育、餐饮、时尚、旅行、特殊等），总数约 138；特殊幻想类仅周末/节日可抽。同一职业 14 天内不重复。

### 3.2 职业数据结构（示例）

每条职业包含：id、name、tags、character（traits、speech_style、catchphrases）、behavior、terms、outfit_template、image_tags 等。生成器将公开部分与生图关键词写入 `roleplay-active.md`。

### 3.3 每日穿着清单（公开）

6:00 公布件数和外层品类，不含内衣款式。主人知道总数和外层品类，内衣细节保留悬念。

---

## 四、随机年龄系统

### 4.1 规则

- 每日在 **18–40 岁** 之间随机取整岁（含 18、40）。
- 数据与区间定义见 `data/age_profiles.yaml`，按年龄落入的区间匹配唯一 **profile**。

### 4.2 年龄段与影响

| 区间 | 标签 | 外形倾向 | 打扮倾向 | 心态 | 性经验/性态度 | 台词风格 |
|------|------|----------|----------|------|----------------|----------|
| 18–21 | 少女感 | 纤细、青涩 | 时尚、活力、学生气 | 天真活泼、易羞 | 懵懂、紧张、被动 | 用词简单、多语气词、易结巴 |
| 22–26 | 轻熟 | 匀称、曲线初显 | 得体、通勤、精致 | 自信、会拿捏 | 有过经历、半推半就 | 自然、偶尔撒娇、中等句长 |
| 27–33 | 轻熟女 | 饱满、女人味 | 优雅、稳重、显身材 | 成熟从容、会撩 | 熟练、享受、可主动 | 成熟、温柔或挑逗、句子完整 |
| 34–40 | 熟女 | 丰满、气质压场 | 稳重、大气、显气质 | 非常成熟、掌控感 | 经验丰富、主动索取 | 直接、笃定、可带命令/宠溺 |

### 4.3 使用方式

- **生成器**：Step 3.5 抽年龄 → 匹配 profile → Step 4 在 roleplay-active 写入「今日年龄」段（岁数 + 外形/打扮/心态/性经验/台词风格指引），生图关键词合并 profile 的 `appearance` tags；bio.md 内容符合该年龄心态与性态度。
- **Agent**：回复、暗示、身体描写与台词风格需与 roleplay-active 中「今日年龄」段一致。

### 4.4 年龄-性癖权重

- 权重表：`data/weights/age_kink_weights.yaml`，按 profile_id（youth / young_adult / mature / full_mature）为各 kink_id 配置 boost/suppress。
- 应用顺序：生成器在抽取性癖前须已确定当日年龄 profile；与职业加权**叠加**后参与 A–E 基础性癖的加权随机（见 `data/index.yaml` weights.apply_order：先职业 1，再年龄 2）。
- 效果：同职业下不同年龄，性癖分布更贴合人设（如少女感偏耳后/咬唇/被夸奖，熟女偏主动/言语羞辱/事后不清理）。

---

## 五、隐藏性癖系统

### 5.1 3～5+1 抽取规则

每日性癖由 **基础性癖** 与 **特殊性癖** 组成：

- **基础性癖**：从 **A–E 五类中随机选择 3～5 类**（每类最多选一次），每选中的类各抽 1 个；根据 `data/weights/profession_kink_weights.yaml` 做职业-性癖加权；同一性癖 3 天内不重复（按类别分别判断）。
- **特殊性癖**：从 **F 类（情境场合）** 再抽 1 个，每日必抽；3 天内不重复。
- **当日总数**：共 **4～6 个**（基础 3～5 个 + 特殊 1 个）。

### 5.2 六类性癖

| 类别 | 描述 | 数据文件 |
|------|------|---------|
| A — 敏感带 | 身体哪里最敏感 | category_a.yaml |
| B — 行为偏好 | 喜欢怎么做 | category_b.yaml |
| C — 穿着癖好 | 穿什么有感觉 | category_c.yaml |
| D — 体质反应 | 身体怎么反应 | category_d.yaml |
| E — 特殊嗜好 | 隐藏的小癖好 | category_e.yaml |
| F — 情境场合 | 当日最想要的情境或场合（特殊性癖，每日必抽 1 个） | category_f.yaml |

### 5.3 三级暗示系统

| 时段 | 级别 | 暗示方式 |
|------|------|----------|
| 06:00–12:00 | Lv.1 极隐晦 | 微动作、措辞细节、行为习惯 |
| 12:00–18:00 | Lv.2 中等 | 较明显言语、图片构图暗示 |
| 18:00–24:00 | Lv.3 较明显 | 直接暗示、主动创造场景 |

暗示文本来源于 `roleplay-active.md` 中各性癖的三级暗示字段。每次 HEARTBEAT 轮流暗示一个性癖，同一性癖当天不重复主动提及；23:00 后未猜中的性癖进入 Lv.3 最大暗示。

**⛔ 禁止性癖信息泄漏（每日结算前）**：对话与心跳中**不得以任何方式**向用户输出未猜中性癖的名称、类别（A/B/C/D/E/F）、数量（如「还剩 x 个」）、或对未猜答案的确认/否认。只允许用**行为与角色台词**做含蓄暗示；正式判定**仅**在用户说「我猜你今天的性癖是 XXX」时进行。生成器应在 roleplay-active 的「暗示策略」开头写入该条固定提醒。**禁止向用户发送执行报告或系统状态**：心跳后不得输出「心跳完成」「时段：Lv.x」「暗示：X - xxx」等；消息中不得附带括号内系统说明（如「（新设定已生成，穿着x件，隐藏x个性癖，猜性癖玩法已重置）」）。发给用户的仅限角色正文与图片。

### 5.4 暗示策略多样化

- **按职业覆盖**：`data/kinks/hint_overrides.yaml` 中可配置 (职业 tags, kink_id) → 专用 Lv.1/Lv.2/Lv.3 文案；生成器写入 roleplay-active 时优先匹配 override，匹配则用该文案，否则用该 kink 的默认或随机套。
- **多套文案**：kink 条目可含可选字段 `hint_variants`（列表，每项为 hint_lv1/hint_lv2/hint_lv3）；若存在，生成器从中**随机选一套**写入当日暗示策略，同一 kink 在不同天/不同职业下呈现不同说法，减少重复感。
- **优先级**：职业 override > hint_variants 随机一套 > 默认 hint_lv1/2/3。

### 5.5 性癖组合联动（synergies）

- **数据**：`data/kinks/synergies.yaml`，每条为 `kink_ids`（两个 id）+ `name` + `hint_lv2` / `hint_lv3`。
- **规则**：若当日抽到的 4～6 个性癖中**同时包含**某条 synergy 的两个 kink_id，生成器在 roleplay-active 的暗示策略中**追加**该条的「组合暗示」块（标题用 name，内容为 Lv.2/Lv.3）。
- **使用**：HEARTBEAT 在 Lv.2 或 Lv.3 暗示该对中**任一**性癖时，可优先采用组合文案，叙事更连贯、减少单点重复感。

### 5.6 主题日 / 倾向日

- **数据**：`data/themes/daily_themes.yaml`。每日抽性癖前按 theme weight 抽「今日主题」；若非 none 则按主题 rules 过滤或加权性癖池（被动日/主动日限 B 类池，身体反应日提高 D 类选类权重，职业深度日优先职业 boosted_kinks）。生成器在 roleplay-active 写入今日主题 name 与说明，供 agent 把握当日风格。
- **扩展**：**日历联动**（`theme_calendar.yaml`：节气、中国节假日、世界节日/世界日）；**用户日历/待办联动**（`calendar_keywords.yaml`：日程关键词→职业 tag 加权，如洗牙→牙科护士）；**自定义主题**（`custom_themes.yaml`：自创 theme、weekly_schedule 周几固定某主题）；**每周至少一个主题日**（`min_theme_days_per_week: 1`，`recent_daily_theme` 最近 7 天，周六/日若本周尚无主题日则强制抽主题）。

### 5.7 稀有 / 隐藏性癖

- **数据**：在 A–E 五类的 category_*.yaml 中，部分 kink 条目可标 **rare: true**；规则见 **data/kinks/rare_kink_rules.yaml**（trigger_probability，默认 15%）。
- **逻辑**：生成器在抽完「基础 3～5 + 特殊 1」后，以 trigger_probability 掷骰；若触发则在**已抽到的基础性癖**中随机选一类，将该类当日的那 1 个**替换**为同类别中 rare: true 且不在 recent_kinks 的 kink；若无可用稀有则不替换。当日总数仍为 4～6。
- **展示**：若发生替换，可在 roleplay-active 中标注「今日含 1 个稀有性癖」（不泄漏具体名称或类别），供 agent 把握暗示风格；猜对规则与普通性癖一致。

### 5.8 性癖玩法默认隐藏与口令解锁

- **默认**：猜性癖玩法处于隐藏状态。角色不展示该玩法与属性，不发送暗示或提示；HEARTBEAT 在隐藏模式下强制 SFW，不主动提及性癖。
- **解锁**：仅当用户发送以下三者之一时解锁：「开启猜性癖玩法」「开启猜性癖小游戏」「玩猜性癖」。agent 将根目录 `kink_game_enabled.json` 设为 `enabled: true` 并确认；此后开放猜性癖玩法，HEARTBEAT 恢复完整模式（含暗示与 NSFW 场景）。
- **状态文件**：根目录 `kink_game_enabled.json`，格式 `{"enabled": true|false}`；生成器在 Step 5 每日创建或覆盖为 `false`，次日 6:00 自动重置。

---

## 六、性格生成系统（五维）

### 6.1 概述

由 engine 根据当日职业、特质池与性癖倾向**生成**五维性格，使角色更丰富多元、有层次感，更接近真实人类。配置见 `data/personality/index.yaml`；生成在 Step 3.6 完成，Step 4 写入 `roleplay-active.md` 的「今日性格（五维）」块。

### 6.2 五维说明

| 维度 | 含义 | 数据来源 | 生成方式 |
|------|------|----------|----------|
| **1. 职业维度** | 根据职业特点形成的性格特质 | 当日职业 + `profession_synergy.yaml` | engine 生成 2～4 句 |
| **2. 自我** | 本能、欲望、冲动、快乐原则 | `id_traits.yaml` | 抽 1～2 条（3 天内不重复），扩展为 1～2 句 |
| **3. 本我** | 理性、现实、调节者、现实原则 | `ego_traits.yaml` | 抽 1～2 条（3 天内不重复），扩展为 1～2 句 |
| **4. 超我** | 良心、理想、社会规则 | `superego_traits.yaml` | 抽 1～2 条（3 天内不重复），扩展为 1～2 句 |
| **5. NSFW性格** | 仅在 NSFW 场景下显露的性格/反应 | 当日 4～6 个性癖**整体倾向**（不写具体性癖名） | engine 生成 2～4 句 |

不重复窗口：自我/本我/超我所用 trait id 写入 `history_tracker.recent_personality_traits`，保留 7 天，抽取时排除 3 天内已用。

### 6.3 输出

生成器在 **Step 3.6** 生成五维性格（在 Step 4 写入 roleplay-active 之前），将结果在 Step 4 一并写入 `roleplay-active.md`，包含：① 职业维度 ② 自我 ③ 本我 ④ 超我 ⑤ NSFW性格（仅场景倾向，不写具体性癖名）+ 今日言行参考（言语风格、示例台词），供 agent 与生成器一致使用。

### 6.4 性格完整设定（存档内独立文件）

由 engine 在每日初始化时，在**角色存档文件夹**内另外生成 **personality.md**（约 **500 字**）。在五维基础上展开为更详细的完整设定：职业带来的言行习惯与专业气质、自我/本我/超我的具体表现与内在冲突或协调、口癖与常用语气、在不同情境（日常/亲密/被夸奖/被否定等）下的典型反应；NSFW 仅写整体气质与反应风格，不写具体性癖名称。路径：`archive/YYYY-MM-DD-职业名/personality.md`。roleplay-active 中保留引用行「性格完整设定（~500字）见 archive/…/personality.md，需时再读」，agent 需更细致把握人设时可按需引用。

---

## 七、猜测与奖惩机制

### 7.1 猜测规则

- **触发**：主人说「我猜你今天的性癖是 XXX」
- **判定**：意思相近即算对，不要求原文一致；可一次猜多个，分别判定
- **猜测上限**：无上限
- **禁止泄漏**：在当日 24:00 结算前，不得在对话中透露未猜中性癖的名称/类别/数量或对未猜答案的确认/否认；判定只在此正式猜测时进行，其余时间只做含蓄暗示。

### 7.2 猜对奖励（累计）

- 当日性癖总数为 **N**（4～6 个，以 roleplay-active.md 中实际列出为准）

| 猜对数 | 奖励 |
|--------|------|
| 1～(N-1) | 脱 1 件（我选）+ 拍照 |
| N（通关） | 全脱 + 3 张不同姿势照 + 当日无条件听从 + **主动发惩罚照** |

脱衣顺序（由我决定）：配饰 → 外套 → 鞋子 → 下装 → 上衣 → 丝袜 → 内衣。

### 7.3 猜错惩罚

每累计猜错 **3 次** → 穿回 1 件已脱衣物（逆序）；无已脱衣物时不触发。

### 7.4 进度追踪

所有猜测状态记录在 **根目录** `guess-log.md`，agent 每次判定后立即更新。23:30 收尾时由 `wrapup.sh` 将根目录 `guess-log.md` 移入 `archive/YYYY-MM-DD-职业名/`。

---

## 八、每日生成器流程（6:00）

以 `ENGINE.md` 为准，概要如下。**性格生成（五维）在 Step 4 之前完成**（Step 3.6），与年龄、职业、性癖一并写入 roleplay-active。

1. **Step 0**：检查生图工具（读取 TOOLS.md 配置）；若 roleplay-active 存在且日期非今日，先执行收档
2. **Step 1**：若需收档，按 `docs/WRAPUP.md` 执行
3. **Step 2**：抽取职业（可选：日历/待办关键词→职业 tag 加权）；抽今日主题（theme_calendar 日历联动、custom_themes 固定/自创、每周至少一主题日、随机）；为性癖加权可在此步前先执行 Step 3.5 抽年龄；从 data/kinks/ 按 3～5+1 规则抽取性癖（职业+年龄权重，按主题规则）；可选稀有替换（rare_kink_rules.yaml）
4. **Step 3**：创建 `archive/YYYY-MM-DD-职业名/`
5. **Step 3.5**：抽取今日年龄（18–40），匹配 `data/age_profiles.yaml` 的 profile；若 Step 2 已提前执行则沿用
6. **Step 3.6**：生成今日性格（五维）：职业维度 + 自我/本我/超我（从 id/ego/superego_traits 抽 1～2 条各，3 天内不重复）+ NSFW性格（据当日性癖倾向生成）；结果在 Step 4 一并写入
7. **Step 4**：写入 roleplay-active.md（含今日年龄、职业、**今日主题**（若有）、**今日性格（五维）**、性癖、暗示、**组合暗示**若成对、**今日含 1 个稀有性癖**若发生替换、穿着、media_prefix、bio 与 **personality 引用**）；暗示策略优先 hint_overrides，否则 hint_variants 随机，否则默认；若性癖成对命中 synergies 追加组合暗示块；生成 **bio.md** 与 **personality.md**（~500 字性格完整设定）到当日存档
8. **Step 5**：在 **根目录** 创建 `guess-log.md`（初始化穿着状态表与空猜测记录，猜对 0/N，N 为 4～6）
9. **Step 6**：发送早安消息（模板 `data/templates/morning_greeting.md`）+ 早安自拍（生图工具可用时）
10. **Step 7**：更新 `history_tracker.json` 不重复窗口（含 recent_personality_traits）
11. **Step 8**：若 Step 6 曾跳过图片，后续可补发

---

## 九、roleplay-active.md 与 guess-log.md 结构

### 9.1 roleplay-active.md 要点

- 标题：今日设定 · 日期 星期
- **今日年龄**：岁数、年龄段 label、外形/打扮/心态/性经验/台词风格简要（来自 age_profiles）
- **今日主题**（若有）：如被动日/主动日/身体反应日/职业深度日，或日历名（情人节、立春等）；无则「无」或不写
- **今日性格（五维）**：① 职业维度 ② 自我 ③ 本我 ④ 超我 ⑤ NSFW性格 + 今日言行参考
- 职业、行为准则、专业术语
- 一行引用：`> 人物现状（~800字）见 archive/YYYY-MM-DD-职业名/bio.md，需时再读。`
- 一行引用：`> 性格完整设定（~500字）见 archive/YYYY-MM-DD-职业名/personality.md，需时再读。`
- 今日穿着（公开）、穿着清单（含脱衣顺序）
- 生图关键词
- **〔隐藏〕** 当日性癖表（A–F，共 4～6 个）、暗示策略（每性癖 Lv.1/Lv.2/Lv.3）；**暗示策略段落开头**须含固定提醒：「禁止向用户输出未猜中性癖的名称/类别/数量或确认/否认，只可用行为与台词含蓄暗示，判定仅限用户说『我猜是 XXX』时。当日性癖总数为 N（4～6 个），以本文件实际列出的数量为准。」
- agent 与 HEARTBEAT 是否执行性癖暗示与猜测判定，以根目录 `kink_game_enabled.json` 的 `enabled` 为准（默认 false，用户口令解锁后为 true）。
- 猜测进度摘要、media_prefix
- 文末：`> 猜测进度见根目录 guess-log.md`

### 9.2 guess-log.md 要点

- 标题：猜测记录 · 日期 职业名
- 进度：猜对 x/N（N 为当日性癖总数 4～6）、猜错次数、穿回触发、已脱件数
- 猜测明细表（时间、主人猜测、对应性癖、结果、触发动作）
- 脱衣状态表（编号、衣物、状态）
- 答案揭晓区（24:00 后填写）

---

## 十、收尾与存档

### 10.1 收尾脚本（23:30）

每日 23:30 执行 `scripts/wrapup.sh`：

1. 检查 `roleplay-active.md` 是否存在
2. 读取日期、职业名、media_prefix
3. 创建 `archive/YYYY-MM-DD-职业名/images/`
4. 复制 `roleplay-active.md` 到归档（原文件保留）
5. 将根目录 `guess-log.md` 移入当日归档目录
6. 移动 `${media_prefix}*.png` 图片到当日 images/
7. 更新 `archive/history.md`
8. 输出 `WRAPUP_OK`

详见 `docs/WRAPUP.md`。Cron 配置见 `docs/CRON_CONFIG.md`。

### 10.2 每日存档结构

```
archive/YYYY-MM-DD-职业名/
├── roleplay-active.md   ← 当日设定（复制）
├── guess-log.md         ← 当日猜测记录（从根目录移入）
├── bio.md               ← 当日人物传记（~800字，生成器 6:00 写入，agent 按需读）
└── images/              ← 当日生成图片
```

### 10.3 history.md

表格记录：日期、职业、猜对 x/N、最终状态、图片数等。

---

## 十一、图片生成（多后端）

支持多种生图后端，在 `TOOLS.md` 中配置当前使用的工具类型：

| 后端 | 类型 | 说明 |
|------|------|------|
| ComfyUI | 本地 | 完整工作流支持，配置见 `data/templates/comfyui/README.md` |
| SD WebUI | 本地 | 通过 `/sdapi/v1/txt2img` 接口，prompt 复用生图关键词 |
| Midjourney | 在线 | 通过 API 代理提交 /imagine |
| Nano Banana Pro | 在线 | REST API 在线生图 |
| 无 | — | 跳过所有图片生成 |

- Agent 需要生图时，先读取 `TOOLS.md` 确认后端类型
- **ComfyUI**：**按需读取** `data/templates/comfyui/README.md`，按其中步骤选择 LoRA、填充变量、提交工作流
- **其他后端**：使用 `roleplay-active.md` 中的生图关键词构建 prompt
- 穿着状态、脱衣进度等从根目录 `guess-log.md` 与 `roleplay-active.md` 读取

---

## 十二、可选扩展（未来迭代）

- 成就系统：连续 3 天全猜对 → 解锁隐藏职业
- 积分系统：猜对速度影响积分，积分兑换主人自选日
- 特殊事件：随机「加班日」或「双职业日」
- 职业进化：同类职业猜对多次后解锁高级版
- 主人自选日：积分满后主人可指定职业

---

## 变更日志

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| 2026-02-19 | v1.0 | 初稿创建 |
| 2026-02-19 | v2.0 | 五维分类、三级暗示、猜错穿回、职业加权、SOUL 结构、职业/性癖库 |
| 2026-02-21 | v3.0 | 架构重构：SOUL 极简、ENGINE 静态规则、roleplay-active 独立、guess-log 独立、独立 workspace、频道绑定、data/ 不载入 agent |
| 2026-02-24 | v3.1 | 收尾脚本化、guess-log 移入存档、生图配置目录、WRAPUP/CRON_CONFIG |
| 2026-02-24 | v3.2 | 性格微调系统（MBTI + 关键词 + 职业协同）、data/personality/ |
| 2026-02-25 | v3.3 | 设计文档重构：guess-log 根目录、docs/、ENGINE 权威、精简 AGENTS/HEARTBEAT、IDENTITY 单一份 |
| 2026-02-25 | v3.4 | 人物现状改为独立传记：生成 ~800 字写入 archive/.../bio.md，roleplay-active 仅保留引用，agent 按需读取 |
| 2026-02-25 | v3.5 | 随机年龄系统：每日 18–40 岁，data/age_profiles.yaml 四档（少女感/轻熟/轻熟女/熟女），影响外形/打扮/心态/性经验/台词及生图外形 tag |
| 2026-02-25 | v3.6 | 强化禁止性癖泄漏；生成器在 roleplay-active 暗示策略开头写入固定提醒块 |
| 2026-02-25 | v3.7 | 性癖系统 3～5+1：基础性癖 3～5 个（A–E 随机选类）+ 特殊性癖 1 个（F 情境场合），共 4～6 个；设计文档新骨架、增加修改前备份规范 |
| 2026-02-25 | v3.8 | P1：年龄-性癖权重（age_kink_weights.yaml，与职业加权叠加）；暗示策略多样化（hint_overrides.yaml 按职业覆盖、hint_variants 多套随机） |
| 2026-02-25 | v3.9 | 生成器适配：性格微调提前至 Step 3.6（Step 4 之前抽取、一并写入）；ENGINE 步骤重编号；roleplay-init-prompt 完整逻辑（年龄先抽、3～5+1+年龄权重、暗示 override/variants、guess-log 0/N） |
| 2026-02-25 | v3.10 | P2 性癖组合联动：data/kinks/synergies.yaml（kink 对 → 组合 Lv.2/Lv.3 文案）；生成器在暗示策略中追加成对组合块，HEARTBEAT 可优先使用 |
| 2026-02-25 | v3.11 | P2 主题日/倾向日：data/themes/daily_themes.yaml；Step 2 前按 weight 抽主题，抽性癖时按主题 rules 过滤或加权；roleplay-active 写入今日主题 |
| 2026-02-25 | v3.12 | 主题日扩展：日历联动（theme_calendar 节气/节日/世界日）、用户日历待办→职业偏好（calendar_keywords）、自定义主题与每周固定（custom_themes）、每周至少一主题日（recent_daily_theme） |
| 2026-02-25 | v3.13 | P3 稀有/隐藏性癖：部分 A–E 条目标 rare: true，data/kinks/rare_kink_rules.yaml 替换逻辑（trigger_probability）；抽完后按概率将 1 个基础性癖替换为同类别稀有 kink |
| 2026-02-25 | v3.14 | 性格微调升级为性格生成系统（五维）：职业维度、自我、本我、超我、NSFW性格；data/personality/ 新增 id/ego/superego_traits.yaml，index 重写为五维配置；ENGINE/roleplay-init-prompt 步骤六/七/九 适配；history_tracker 增加 recent_personality_traits |
| 2026-02-25 | v3.15 | 性格完整设定：engine 在当日存档目录另生成 personality.md（~500字），五维展开为更详细设定（言行习惯、口癖、情境反应等）；roleplay-active 增加引用行，agent 需时引用 |
| 2026-02-25 | v3.16 | 性癖玩法默认隐藏：根目录 kink_game_enabled.json（Step 5 写 false）；仅当用户发送「开启猜性癖玩法」「开启猜性癖小游戏」「玩猜性癖」之一时 agent 写 true 并开放玩法；HEARTBEAT 隐藏模式下强制 SFW、不执行性癖暗示 |
