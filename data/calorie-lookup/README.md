# calorie-lookup v0.3.0

| Spoonacular 与USDA FoodData Central 两重数据源的营养查询与热量估算 Agent Skill。

将自然语言食物输入（支持中文）转化为结构化营养数据：热量、蛋白质、碳水、脂肪、膳食纤维。

Spoonacular (primary) & USDA FoodData Central (fallback) nutrition lookup & meal calorie estimation agent skill.

Converts natural language food input (Chinese supported) into structured nutrition data: calories, protein, carbs, fat, and fiber.
- **Multimodal Recognition** / **多模态识别**: Supports food photo recognition via Image Recognizer sub-agent (Gemini 3 Pro / GPT-5.2).
- **Search Optimization** / **搜索优化**: Improved accuracy with `search_hint` and multi-source fallback logic.
- **Data Quality** / **数据质量**: Added calorie modifiers for 8 cooking methods and optional source cross-validation.

---

## 快速开始 / Quick Start

```bash
# 1. 安装依赖 / Install dependencies
python -m pip install -r requirements.txt

# 2. 填入 API Key / Fill in your API keys
#    Spoonacular 免费签上 / Free sign-up: https://spoonacular.com/food-api
#    或 USDA FDC API Key / or USDA FDC API key: https://fdc.nal.usda.gov/api-key-signup.html
export SPOONACULAR_API_KEY="<your-spoonacular-key>"
# 或第二个 API Key / or use second API Key (fallback)
export USDA_FDC_API_KEY="<your-usda-key>"

# 3. 试运行 / Try it
PYTHONPATH=scripts python -c "
from core import lookup_meal
print(lookup_meal('chicken breast 200g + rice 1 bowl'))
"
```

---

## 项目结构 / Project Structure

```
calorie-lookup/
├── SKILL.md                  # Skill 元数据 / Skill metadata
├── WORKFLOW.md               # 工作流说明 / Workflow description
├── HOOKS.md                  # Sub-agent 触发逻辑 / Sub-agent trigger logic
├── AGENTS.md                 # 开发者/Agent 指南 / Developer/Agent guide
├── agents/
│   ├── README.md             # Sub-agent 概览 / Sub-agent overview
│   ├── calorie-lookup-decomposer.md  # Decomposer 合约 / Decomposer contract
│   └── calorie-lookup-image-recognizer.md # Image Recognizer 合约 / Image Recognizer contract
├── scripts/
│   ├── __init__.py           # 模块导出 / Module exports
│   ├── core.py               # 主逻辑 / Main logic: lookup_meal / lookup_food
│   ├── config_example.py     # 配置模板 / Config template (tracked by git)
│   ├── spoonacular.py        # Spoonacular API 封装 / Spoonacular API wrapper
│   ├── cooking.py            # 烹饪系数 / Cooking modifiers (USDA data)
│   ├── parser.py             # 自然语言文本解析 / NL text parsing
│   ├── units.py              # 单位换算 / Unit conversion & portion defaults
│   ├── translate.py          # 中英食物名字典 / CN→EN dictionary (acceleration cache)
│   ├── usda_fdc.py           # USDA API 封装 / USDA API wrapper + error handling
│   └── cache.py              # SQLite 缓存 / SQLite cache
├── references/
│   └── usda_fdc.md           # USDA API 快速参考 / USDA API quick reference
├── pyproject.toml            # 项目元数据 / Project metadata
├── requirements.txt          # Python 依赖 / Python dependencies
└── LICENSE                   # MIT
```

---

## 架构 / Architecture

### 两条处理路径 / Two Processing Paths

**路径 A — 快速路径 / Path A — Fast Path**
纯英语简单食材 → `lookup_meal(text)` 直接处理—优先查询 Spoonacular。
Plain English simple ingredients → `lookup_meal(text)` directly—prioritizes Spoonacular.

**路径 B — 主路径 / Path B — Primary Path**
非英语/覆合菜/套餐 → Decomposer Sub-agent（LLM 翻译 + 分解）→ 英文食材名 → Spoonacular 查询(或 USDA 后备) → 汇总。
Non-English / composite dishes / set meals → Decomposer Sub-agent (LLM translation + decomposition) → English ingredient names → Spoonacular query (or USDA fallback) → aggregate totals.

### 译业 / Translation Strategy

- **主数据源 / Primary data source**：Spoonacular API
- **后备 / Fallback**：USDA FoodData Central API
- **主语言路径 / Primary language path**：LLM 翻译（通过 Decomposer Sub-agent）
- **加速缓存 / Acceleration cache**：`scripts/translate.py` 内置 ~224 条中英字典
- Spoonacular 和 USDA API 都仅支持英文查询 / Both APIs only accept English queries

### 数据流 / Data Flow

```
用户输入 / User Input
  → [Agent 判断路径 / Path Decision]
  → [解析/翻译 / Parse & Translate]
  → Spoonacular API 查询（主）/ Spoonacular API Query (primary)
  → USDA API 查询（后备）/ USDA API Query (fallback on error)
  → 营养计算 / Nutrition Calculation
  → 结构化输出 / Structured Output
  → SQLite 缓存 / Cache
```

---

## API

### `lookup_meal(text, meal_type="unknown")`

解析多食材文本，逐条查询并汇总。
Parses multi-ingredient text, queries each item, and aggregates totals.

```python
result = lookup_meal("chicken breast 200g + rice 1 bowl")
# {
#   "type": "meal_nutrition",
#   "items": [...],
#   "totals": {"kcal": ..., "protein_g": ..., "carb_g": ..., "fat_g": ..., "fiber_g": ...},
#   "questions": [...]
# }
```

### `lookup_food(name, qty, unit)`

查询单个食材的营养信息。
Queries nutrition info for a single ingredient.

```python
result = lookup_food("chicken breast", 200, "g")
# {"ok": True, "kcal": 330.0, "protein_g": 62.0, ...}
```

---

## 环境变量 / Environment Variables

| 变量 / Variable | 必需 / Required | 说明 / Description |
|------|------|------|
| `SPOONACULAR_API_KEY` | 否 / No | Spoonacular API Key（为空時自动使用 USDA / Auto-fallback to USDA if empty）|
| `USDA_FDC_API_KEY` | 否 / No | USDA FoodData Central API Key |
| `CALORIE_SKILL_CACHE_DB` | 否 / No | SQLite 缓存路径 / Cache DB path（默认 / default: `calorie_skill_cache.sqlite3`）|
|| `CROSS_VALIDATE_DEFAULT` | 否 / No | 开启交叉验证 / Enable cross-validation (default: `False`) |

---

## License

MIT
