# AGENTS Guide for `calorie-lookup` / `calorie-lookup` Agent 指南
Practical instructions for coding agents working in this repository.
本文档为在此仓库中工作的编码 Agent 提供实用指引。

Everything below is based on files currently present in this repo.
以下内容基于本仓库中当前存在的文件。

## 1) Project Snapshot / 项目概览
- Language / 语言: Python
- Dependency / 依赖 in `requirements.txt`: `requests>=2.31.0`
- Domain / 领域: USDA FoodData Central nutrition lookup + meal calorie estimation / USDA FoodData Central 营养查询与热量估算
- Main code folder / 主代码目录: `scripts/`
- Main docs / 主要文档: `SKILL.md`, `WORKFLOW.md`, `HOOKS.md`, `references/usda_fdc.md`

## 2) Key Files and Entry Points / 关键文件与入口
- `scripts/core.py`: orchestration (`lookup_food`, `lookup_meal`) + Spoonacular routing / 主编排逻辑 + Spoonacular 路由
- `scripts/spoonacular.py`: Spoonacular API calls + wrapper / Spoonacular API 调用 + 币窗
- `scripts/usda_fdc.py`: USDA API calls + `USDAError` / USDA API 调用 + 错误类
- `scripts/usda_fdc.py`: USDA API calls + `USDAError` / USDA API 调用 + 错误类
- `scripts/parser.py`: text splitting and amount parsing (`ParsedItem`) / 文本分割与份量解析
- `scripts/units.py`: unit normalization + portion-based gram conversion / 单位标准化 + 基于份量的克数换算
- `scripts/translate.py`: Chinese→English food name dictionary (acceleration cache, not primary translation path) / 中英食物名字典（加速缓存，非主翻译路径）
- `scripts/cache.py`: sqlite cache read/write with TTL / SQLite 缓存读写（含 TTL）
- `scripts/config.py`: runtime config and env var reads / 运行时配置与环境变量读取
- `agents/calorie-lookup-decomposer.md`: sub-agent contract for decomposition + translation / Sub-agent 合约（分解 + 翻译）
- `scripts/cooking.py`: calorie modifiers for 8 cooking methods (steamed, grilled, fried, etc.) / 8 种烹饪方式的热量修正系数
- `agents/calorie-lookup-image-recognizer.md`: multimodal sub-agent contract for food photo recognition / 图像识别 Sub-agent 合约

Programmatic smoke entry / 编程式冒烟测试入口:
```bash
python -c "from scripts.core import lookup_meal; print(lookup_meal('鸡胸肉200g+米饭1碗'))"
```

## 3) Environment Setup / 环境搭建
- Recommended Python / 推荐 Python: 3.10+
- Use a virtual environment before running commands / 运行命令前请使用虚拟环境
- Install deps / 安装依赖: `python -m pip install -r requirements.txt`
- Spoonacular key / Spoonacular API 密钥: `SPOONACULAR_API_KEY` (optional / 可选)
- USDA key / USDA API 密钥: `USDA_FDC_API_KEY` (optional / 可选)
- Cache DB env var / 缓存数据库环境变量: `CALORIE_SKILL_CACHE_DB` (optional / 可选)
- Cross-validation toggle / 交叉验证开关: `CROSS_VALIDATE_DEFAULT` (optional / 可选, default `False`)

Example / 示例:
```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export SPOONACULAR_API_KEY="<your-spoonacular-key>"
export USDA_FDC_API_KEY="<your-usda-key>"
export CALORIE_SKILL_CACHE_DB="./calorie_skill_cache.sqlite3"
```

## 4) Build, Lint, and Test Commands / 构建、检查与测试命令
There is no formal build system or committed test suite/config in this repo.
本仓库暂无正式构建系统或已提交的测试套件/配置。

Use the commands below as the default execution workflow.
请使用以下命令作为默认执行工作流。

### Install / 安装
- `python -m pip install -r requirements.txt`

### Build / sanity / 构建/健全性检查
- `python -m compileall scripts`

### Lint / format (optional / 可选)
- `python -m ruff check scripts`
- `python -m black --check scripts`

If `ruff`/`black` are not installed, either install them in the venv, or skip lint and report that lint tooling is not configured in-repo.
若未安装 `ruff`/`black`，可在虚拟环境中安装，或跳过检查并报告仓库内未配置 lint 工具。

### Tests (preferred style when tests are added) / 测试（添加测试时的推荐风格）
- All tests / 全部测试: `python -m pytest`
- Verbose / 详细输出: `python -m pytest -v`
- Keyword subset / 按关键字: `python -m pytest -k "lookup and not cache"`

Single test execution (important) / 单个测试执行（重要）:
- One file / 单文件: `python -m pytest tests/test_core.py`
- One function / 单函数: `python -m pytest tests/test_core.py::test_lookup_food_success`
- One class method / 单方法: `python -m pytest tests/test_core.py::TestCore::test_lookup_meal`

Unittest fallback / Unittest 后备:
- All tests / 全部测试: `python -m unittest discover -s tests -p "test_*.py"`
- One module / 单模块: `python -m unittest tests.test_core`
- One class method / 单方法: `python -m unittest tests.test_core.TestCore.test_lookup_meal`

### Runtime smoke checks (no framework required) / 运行时冒烟检查（无需框架）
- Parser / 解析器: `python -c "from scripts.parser import parse_meal_text; print(parse_meal_text('鸡胸肉200g+米饭1碗'))"`
- Units / 单位换算: `python -c "from scripts.units import to_grams; print(to_grams('米饭',1,'碗'))"`

## 5) Code Style Conventions / 代码风格约定
These reflect existing patterns in `scripts/` and should be preserved.
以下反映 `scripts/` 中的现有模式，应予以保留。

### Imports / 导入
- Keep imports at module top / 保持导入在模块顶部
- Order as: standard library -> third-party -> local modules / 顺序：标准库 → 第三方 → 本地模块
- Prefer explicit imports, never wildcard imports / 使用显式导入，禁止通配符导入
- Preserve local import style used in repo / 保持仓库中使用的本地导入风格（for example / 例如 `from parser import ...` in `scripts/core.py`）

### Formatting / 格式
- Follow PEP 8 and 4-space indentation / 遵循 PEP 8，4 空格缩进
- Keep functions focused and small / 函数保持专注和简短
- Avoid unnecessary comments for obvious code / 避免对显而易见的代码添加不必要注释
- Keep lines Black-compatible where practical / 尽量保持行与 Black 兼容

### Types / 类型
- Add type hints for public functions and key helpers / 为公开函数和关键辅助函数添加类型注解
- Use `Dict[str, Any]` at flexible JSON boundaries only / 仅在灵活的 JSON 边界使用 `Dict[str, Any]`
- Prefer dataclasses for structured values (`ParsedItem`, `Portion`) / 结构化值优先使用 dataclass
- Use `Optional[T]` when `None` is a valid path / 当 `None` 是合法值时使用 `Optional[T]`

### Naming / 命名
- `snake_case`: functions, variables / 函数、变量
- `UPPER_SNAKE_CASE`: constants / 常量（`QUERY_TTL`, `ITEM_TTL`, `NUTRIENT_IDS`）
- `PascalCase`: classes/dataclasses / 类/数据类
- Keep nutrition keys explicit / 营养键保持显式: `kcal`, `protein_g`, `carb_g`, `fat_g`, `fiber_g`

### Error handling / 错误处理
- Use `USDAError` for API-layer failures in `scripts/usda_fdc.py` / API 层失败使用 `USDAError`
- Map known HTTP statuses to actionable messages (401/403/429/5xx) / 将已知 HTTP 状态码映射为可操作的消息
- In orchestration (`lookup_food`, `lookup_meal`), prefer structured payloads over raw tracebacks / 编排层优先返回结构化负载而非原始堆栈
- Keep boundary error shape stable (`ok`, `error`, `status`) / 保持边界错误结构稳定

### Data contracts / 数据契约
- Do not break response shape from `lookup_food` / `lookup_meal` / 不要破坏响应结构
- Keep keys stable / 保持键名稳定: `items`, `totals`, `questions`, `ok`, `error`, `status`
- Keep follow-up questions concise and capped (current cap is 2) / 追问保持简洁，上限 2 条
- Preserve question object shape (`field`, `ask`) / 保持问题对象结构

### Parsing and units / 解析与单位
- Parser must remain tolerant of mixed Chinese/English separators / 解析器必须兼容中英混合分隔符
- Missing amount/unit should trigger follow-up questions, not silent guesses / 缺少数量/单位应触发追问，而非静默猜测
- Unit conversion failures should return clear reasons / 单位换算失败应返回明确原因
- Assumption-based conversions should be reflected in `notes` / 基于假设的换算应在 `notes` 中说明

### Caching and API behavior / 缓存与 API 行为
- Respect configured request timeout (`HTTP_TIMEOUT_SEC`) / 遵守配置的请求超时
- Keep cache keys deterministic and normalized / 缓存键保持确定性和标准化
- Cache serializable payloads only / 仅缓存可序列化的负载
- Keep item-level and meal-level TTL semantics distinct / 保持食材级和餐食级 TTL 语义分离

### Language and i18n / 语言与国际化
- User-facing prompts/errors are primarily Chinese in current code / 面向用户的提示/错误目前以中文为主
- Keep tone and language consistent with surrounding UX text / 保持语调和语言与周围 UX 文本一致
- Preserve Chinese serialization behavior (`ensure_ascii=False` in cache writes) / 保留中文序列化行为

## 6) Agent Workflow Rules (from repo docs) / Agent 工作流规则（源自仓库文档）
From `WORKFLOW.md`, `HOOKS.md`, and `agents/README.md` / 来自 `WORKFLOW.md`、`HOOKS.md` 和 `agents/README.md`：
- **Non-English input → always trigger Decomposer sub-agent / 非英语输入 → 始终触发 Decomposer sub-agent** (LLM translation is the primary path / LLM 翻译是主路径)
- Decomposer also handles: composite dishes, set meals, ambiguous inputs / Decomposer 还处理：复合菜、套餐、模糊输入
- Decomposer contract / 合约: `items[{name(English), name_zh, qty, unit}]` plus `notes[]`
- Decomposer must output English `name` for USDA API; `name_zh` preserves original / `name` 必须为英文（USDA API 要求）；`name_zh` 保留原文
- After decomposition, run `lookup_food` per item (with English name) and aggregate totals / 分解后逐条调用 `lookup_food`（英文名）并汇总
- Pure English simple input → can skip decomposer, call `lookup_meal` directly / 纯英语简单输入 → 可跳过 decomposer，直接调用 `lookup_meal`
- `scripts/translate.py` dictionary is an **acceleration cache** only, not the primary translator / 字典仅为**加速缓存**，非主翻译器
- If key quantity data is missing, ask follow-up questions (max 2) / 缺少关键量化数据时追问（最多 2 条）
- Prefer ingredient-level food names that USDA can match directly / 优先使用 USDA 可直接匹配的食材级名称

## 7) Cursor / Copilot Rules Status / 编辑器规则状态
- `.cursorrules`: not found / 未找到
- `.cursor/rules/`: not found / 未找到
- `.github/copilot-instructions.md`: not found / 未找到

There are currently no additional editor-specific rule files in this repo.
本仓库目前没有额外的编辑器专用规则文件。

## 8) Known Repository Caveat / 已知仓库注意事项
- **Spoonacular is the primary data source** / **Spoonacular 是主数据源**—USDA is automatic fallback / USDA 是自动后备
- `scripts/config.py` env vars: `SPOONACULAR_API_KEY` (optional / 可选), `USDA_FDC_API_KEY` (optional / 可选) — at least one should be set / 至少配置其中一个
- If changing runtime config, align code and docs together in one change / 修改运行时配置时，代码和文档须在同一变更中对齐
- Both Spoonacular and USDA APIs support English queries only / Spoonacular 和 USDA API 都仅支持英文查询
- **LLM translation (via Decomposer sub-agent) is the primary translation path** for non-English input / **LLM 翻译（通过 Decomposer sub-agent）是非英语输入的主翻译路径**
- `scripts/translate.py` provides a built-in ~200-entry Chinese→English dictionary as acceleration cache / 提供内置 ~200 条中英字典作为加速缓存
- The dictionary cannot cover all foods — non-English input should always go through the Decomposer / 字典无法覆盖所有食材，非英语输入应始终走 Decomposer
- The decomposer contract requires `name` (English) + `name_zh` (original language) in output items / 合约要求输出项包含 `name`（英文）+ `name_zh`（原文）
- Spoonacular wraps USDA data with better search algorithms—data overlap is expected / Spoonacular 用更好的搜索算法包装 USDA 数据，数据重叠是预期的
### v0.3 Features / v0.3 新特性
- **Search Optimization** / **搜索优化**: Added `search_hint` field to Decomposer output and implemented search fallback (Spoonacular → USDA).
- **Cooking Modifiers** / **烹饪修正**: Integrated `cooking.py` with 8 USDA-cited cooking methods (e.g., fried, roasted).
- **Cross-Validation** / **交叉验证**: Optional multi-source validation (Spoonacular vs USDA) with 30% warning threshold.
- **Multimodal Recognition** / **多模态识别**: New Image Recognizer sub-agent using Gemini 3 Pro (primary) / GPT-5.2 (fallback).

## 9) Change Management Checklist / 变更管理清单
- Keep edits minimal and scoped to the request / 编辑保持最小化，限定在请求范围内
- Do not rename public response keys without updating all call sites / 不要在未更新所有调用处的情况下重命名公开响应键
- Avoid new dependencies unless necessary / 除非必要，避免新增依赖
- If adding tests, prefer `pytest` and include at least one single-test runnable example / 添加测试时优先使用 `pytest`，并包含至少一个可单独运行的测试示例
- Never commit secrets or API keys / 永远不要提交密钥或 API key
- Update this file when workflow/tooling/contracts change / 工作流/工具链/合约变更时更新本文件
