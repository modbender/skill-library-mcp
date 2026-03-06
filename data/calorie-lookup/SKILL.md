---
name: calorie-lookup
version: 0.3.0
description: Spoonacular 营养查询与热量估算（主数据源，USDA 后备）。支持搜寻优化、烹饪系数、交叉验证及图像识别。需要 API key 环境变量 SPOONACULAR_API_KEY 或 USDA_FDC_API_KEY。
description_en: Spoonacular nutrition lookup & meal calorie estimation (primary, USDA fallback). Supports search optimization, cooking modifiers, cross-validation, and image recognition. Requires env var SPOONACULAR_API_KEY or USDA_FDC_API_KEY.
metadata: {"clawdbot":{"emoji":"🍽️","requires":{"env":["SPOONACULAR_API_KEY","USDA_FDC_API_KEY"],"python":["requests"]}}}
---

# Calorie Lookup (Spoonacular + USDA)

## 使用 / Usage
- 入口函数 / Entry functions：`scripts/core.py` 中的 `lookup_meal(text, meal_type)` / `lookup_food(name, qty, unit)`
- 结果为 JSON / Returns JSON：items + totals + questions（最多 2 个追问 / up to 2 follow-up questions）

## 配置 / Configuration
- 环境变量 / Env var：`SPOONACULAR_API_KEY`（主数据源）/ `USDA_FDC_API_KEY`（后备）/ `SPOONACULAR_API_KEY` (primary) or `USDA_FDC_API_KEY` (fallback)
- 缓存 / Cache：`CALORIE_SKILL_CACHE_DB`（默认本地 sqlite / defaults to local sqlite）

## 结构说明 / Module Structure
- `scripts/core.py`：主逻辑（Spoonacular 主路由 + USDA 后备）/ Main logic (Spoonacular primary routing + USDA fallback)
- `scripts/spoonacular.py`：Spoonacular API 封装 / Spoonacular API wrapper
- `scripts/translate.py`：中英食物名字典（加速缓存，非主翻译路径）/ CN→EN dictionary (acceleration cache, not the primary translation path)
- `scripts/usda_fdc.py`：USDA API 封装 + 错误处理 / USDA API wrapper + error handling
- `scripts/parser.py`：文本解析 / Text parsing
- `scripts/units.py`：默认换算表（常改）/ Unit conversion & portion defaults
- `scripts/cache.py`：SQLite 缓存 / SQLite cache
- `scripts/cooking.py`：烹饪热量修正系数（USDA 数据源）/ Cooking calorie modifiers (USDA source)

## 行为约束 / Behavior Constraints
- 缺单位或无法换算：返回 `questions` 提示补充 / Missing unit or unconvertible: returns `questions` prompting user
- 401/403/429/5xx：返回明确错误信息（适合直接在 Discord 显示）/ Returns clear error messages (suitable for Discord display)

## 工作流（含 Sub-agent 翻译 + 分解）/ Workflow (with Sub-agent Translation + Decomposition)
- sub-agent 描述位于本 skill 的 `agents/` 目录 / Sub-agent contracts are in `agents/`
- `agents/calorie-lookup-image-recognizer.md`：图像识别 Sub-agent 合约 / Image Recognizer Sub-agent contract
- **非英语输入** → 触发 Decomposer Sub-agent（LLM 翻译 + 分解）/ **Non-English input** → triggers Decomposer Sub-agent (LLM translation + decomposition)
- 复合菜/套餐/模糊描述 → 触发 Decomposer Sub-agent / Composite dishes / set meals / ambiguous descriptions → triggers Decomposer
- 纯英语简单食材 → 直接调用 `lookup_meal` / Plain English simple ingredients → calls `lookup_meal` directly
- 见 / See `WORKFLOW.md` 与 / and `HOOKS.md`
- 分解后逐条调用 `lookup_food`（英文 name），再汇总 totals / After decomposition, calls `lookup_food` per item (English name), then aggregates totals
- `scripts/translate.py` 字典仅作为 Python 层的加速缓存，不替代 LLM 翻译 / The dictionary is only an acceleration cache, not a replacement for LLM translation
- 仍缺关键量化 → 追问最多 2 条 / Still missing key quantity data → up to 2 follow-up questions

## 路径规范 / Path Convention
- 本 skill 内所有引用均使用相对路径 / All references within this skill use relative paths（例如 / e.g. `scripts/core.py`、`agents/`、`references/usda_fdc.md`）
