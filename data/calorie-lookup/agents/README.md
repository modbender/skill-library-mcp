# Sub-agents

## calorie-lookup-decomposer
- 触发 / Trigger：非英语输入 / 复合菜 / 套餐 / 模糊描述 — Non-English input / composite dishes / set meals / ambiguous descriptions
- 目标 / Goal：翻译为英文 + 拆分为可查询食材条目 — Translate to English + decompose into queryable ingredient items
- 输出 / Output：items[{name(英文/English), name_zh, qty, unit}], notes[]

### 使用说明 / Usage
- **非英语输入默认触发 / Triggered by default for non-English input**：主 Agent 检测到非英语字符时必须调用此 sub-agent / Main agent must invoke this sub-agent when non-English characters are detected
- Decomposer 输出的 `name` 字段为英文，可直接传给 `lookup_food(name, qty, unit)` / Decomposer's `name` field is English, can be passed directly to `lookup_food(name, qty, unit)`
- `name_zh` 保留原始非英语名称，用于用户展示 / `name_zh` preserves original non-English name for user display
- LLM 翻译是主路径；`scripts/translate.py` 字典仅作为 Python 层的加速缓存 / LLM translation is the primary path; `scripts/translate.py` dictionary serves only as a Python-layer acceleration cache
