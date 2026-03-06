# Sub-agent / Hooks

## sub-agent: calorie-lookup-decomposer

- role: 将用户食物输入解析为可查询食材，并翻译为英文 / Parses user food input into queryable ingredients and translates to English
- input: 原始用户文本 / Raw user text
- output: items[{name(英文/English), name_zh, qty, unit}], notes[]

## hook: on_user_food_input

主 Agent 收到食物输入时的判断逻辑：
Decision logic when main agent receives food input:

```
if 输入包含非英语文字 / input contains non-English text:
    触发 decomposer sub-agent（LLM 翻译 + 分解）
    trigger decomposer sub-agent (LLM translation + decomposition)
    用 decomposer 输出的英文 name 调用 lookup_food
    call lookup_food with English name from decomposer output
elif 输入是复合菜/套餐/模糊描述 / input is composite dish / set meal / ambiguous:
    触发 decomposer sub-agent（分解）
    trigger decomposer sub-agent (decomposition)
    用 decomposer 输出调用 lookup_food
    call lookup_food with decomposer output
else:
    直接调用 lookup_meal（快速路径）
    call lookup_meal directly (fast path)
```

### 触发条件汇总（满足任一即触发）/ Trigger Conditions (any one triggers)
1. 输入包含非英语文字（中/日/韩等）/ Input contains non-English text (Chinese / Japanese / Korean, etc.)
2. 复合菜品 / Composite dishes（宫保鸡丁、红烧肉、麻婆豆腐…）
3. 套餐/外卖描述 / Set meals / takeout descriptions
4. 模糊描述无法直接映射到 USDA 食材名 / Ambiguous descriptions that cannot be directly mapped to USDA ingredient names

### 关键原则 / Key Principles
- **LLM 翻译是主路径 / LLM translation is the primary path**，字典只是加速缓存 / dictionary is only an acceleration cache
- 非英语输入不应依赖硬编码字典作为唯一翻译手段 / Non-English input should not rely on the hardcoded dictionary as the sole translation mechanism
