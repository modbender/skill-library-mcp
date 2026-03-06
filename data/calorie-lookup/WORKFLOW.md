# Calorie Lookup Workflow / 热量查询工作流

## 判断是否需要 Sub-agent（主 Agent 职责）/ Determining Sub-agent Need (Main Agent's Responsibility)

主 Agent 收到用户的食物输入后，按以下规则判断处理路径：
When the main agent receives food input from the user, it determines the processing path by the following rules:

### 路径 A：直接调用 `lookup_meal`（快速路径）/ Path A: Direct `lookup_meal` Call (Fast Path)
- 输入为**纯英语**且是**简单食材列表** / Input is **plain English** and a **simple ingredient list**（如 / e.g. `chicken breast 200g + rice 1 bowl`）
- 可选：输入为中文但所有食材都在 `scripts/translate.py` 字典中能命中（加速缓存）/ Optional: Chinese input where all items hit the dictionary (acceleration cache)
- 字典命中仅作为**加速**，不保证覆盖所有食材 / Dictionary hits serve as **acceleration** only, not guaranteed to cover all foods
- **注：Spoonacular 是主数据源** / **Note: Spoonacular is the primary data source**—对于简单食材需优先使用。任何错误时自动回滚到 USDA / For simple ingredients, prioritize Spoonacular. Falls back to USDA on any error.

### 路径 B：触发 Decomposer Sub-agent（LLM 翻译 + 分解，主路径）/ Path B: Trigger Decomposer Sub-agent (LLM Translation + Decomposition, Primary Path)
**触发条件（满足任一即触发）/ Trigger conditions (any one triggers)：**
1. 输入包含**非英语文字**（中文、日文、韩文等）/ Input contains **non-English text** (Chinese, Japanese, Korean, etc.)
2. 输入是**复合菜** / Input is a **composite dish**（如 / e.g. 宫保鸡丁、鱼香肉丝、咖喱牛肉饭）
3. 输入是**套餐/外卖描述** / Input is a **set meal / takeout description**（如 / e.g. 麦当劳巨无霸套餐、一份黄焖鸡）
4. 输入**描述模糊**，无法直接映射到 USDA 可查询的食材名 / Input is **ambiguous**, cannot be directly mapped to USDA-searchable ingredient names

**Decomposer 职责 / Decomposer Responsibilities：**
- 将复合菜拆分为可独立查询的食材列表 / Split composite dishes into independently queryable ingredients
- **将所有非英语食材名翻译为英文** / **Translate all non-English ingredient names to English**（Spoonacular 和 USDA API 都仅支持英文查询 / Spoonacular and USDA API both only support English queries）
- Spoonacular 优先查询，任何错误自动回滚到 USDA / Spoonacular is tried first; any error falls back to USDA
- 估算缺失的份量，并在 notes 中说明假设 / Estimate missing quantities and note assumptions in `notes`
- 输出格式 / Output format：`{items: [{name, name_zh, qty, unit}], notes: []}`
### 路径 C：触发 Image Recognizer Sub-agent（图像识别 + 分解）/ Path C: Trigger Image Recognizer Sub-agent (Image Recognition + Decomposition)
**触发条件 / Trigger conditions：**
- 用户发送食物照片（含或不含文字描述）/ User sends a food photo (with or without text description)

**Image Recognizer 职责 / Image Recognizer Responsibilities：**
- 识别照片中的食物种类并结合用户提供的文字进行分析 / Identify food types in the photo and analyze them alongside user-provided text
- **输出兼容 Decomposer 的 JSON 格式** / **Output JSON compatible with Decomposer**：包含英文食材名、原始中文名、估算份量及单位 / Contains English ingredient names, original Chinese names, estimated quantities, and units
- 优先识别为可直接查询的单一食材，必要时进行分解 / Prioritize identifying individually queryable ingredients, decomposing where necessary
- 使用 Gemini 3 Pro (主) / GPT-5.2 (后备) 进行多模态识别 / Uses Gemini 3 Pro (primary) / GPT-5.2 (fallback) for multimodal recognition
- 输出格式 / Output format：`{items: [{name, name_zh, qty, unit, search_hint}], notes: []}`


## 处理步骤 / Processing Steps

### 路径 A（纯英语/字典命中）/ Path A (English / Dictionary Hit)
1. 主 Agent 调用 `lookup_meal(text, meal_type)` / Main agent calls `lookup_meal(text, meal_type)`
2. `core.py` 内部解析 → Spoonacular 查询（或 USDA 后备）→ 汇总 / `core.py` internally parses → Spoonacular query (or USDA fallback) → aggregation
3. 返回结果 / Return results

### 路径 B（Sub-agent 主路径）/ Path B (Sub-agent Primary Path)
1. 主 Agent 将原始用户文本发送给 Decomposer Sub-agent / Main agent sends raw user text to Decomposer Sub-agent
2. Decomposer 返回 / Decomposer returns `{items: [{name(英文/English), name_zh, qty, unit}], notes: []}`
3. 主 Agent 对每个 item 调用 `lookup_food(name, qty, unit)`（name 已是英文）/ Main agent calls `lookup_food(name, qty, unit)` per item (name is already English)
4. 汇总 totals / Aggregate totals
5. 若仍缺关键量化信息，最多追问 2 条 / If key quantity data is still missing, ask up to 2 follow-up questions
### 路径 C（Image Recognizer 识别路径）/ Path C (Image Recognizer Path)
1. 主 Agent 将照片（及可选文字）发送给 `calorie-lookup-image-recognizer` Sub-agent / Main agent sends photo (and optional text) to `calorie-lookup-image-recognizer` Sub-agent
2. Image Recognizer 使用多模态 LLM 识别并返回 / Image Recognizer uses multimodal LLM to identify and returns `{items: [{name, name_zh, qty, unit, search_hint}], notes: []}`
3. 主 Agent 对每个 item 调用 `lookup_food(name, qty, unit, search_hint=search_hint)` / Main agent calls `lookup_food(name, qty, unit, search_hint=search_hint)` per item
4. 汇总 totals / Aggregate totals
5. 若识别不确定或关键信息缺失，向用户追问 / If identification is uncertain or key info is missing, ask the user


## 关键原则 / Key Principles
- **LLM 翻译是主路径 / LLM translation is the primary path**：字典只是加速缓存，不可能覆盖所有食材 / The dictionary is only an acceleration cache; it cannot cover all foods
- **非英语输入默认走 Sub-agent / Non-English input defaults to Sub-agent**：不要假设字典能处理 / Do not assume the dictionary can handle it
- **Decomposer 的 `name` 字段必须是英文 / Decomposer's `name` field must be English**：这是 USDA API 的硬性要求 / This is a hard requirement of the USDA API
- **追问上限 2 条 / Follow-up question limit: 2**：避免用户体验过差 / To avoid degrading user experience
- **图像输入必须走 Image Recognizer / Image-based input must go through Image Recognizer**：利用多模态 LLM 进行识别，不依赖外部第三方图像识别 API / Utilizes multimodal LLM for identification without relying on external third-party image recognition APIs
**Spoonacular 是数据查询的主来源** / **Spoonacular is the primary data source**—USDA 仅作为自动后备 / USDA is only automatic fallback
- **搜索优化 / Search Optimization**：支持 `search_hint` 提高复合菜搜索准确度，并具备搜索回退策略 / Supports `search_hint` for better composite dish matching with fallback strategy.
- **数据质量 / Data Quality**：支持 8 种烹饪方式的热量修正（`cooking.py`）及数据源交叉验证（可选） / Supports 8 cooking method calorie modifiers and optional data cross-validation.
