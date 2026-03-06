# FRED Navigator

## 英文版本

Navigate FRED (Federal Reserve Economic Data) categories and series using fredapi, supporting natural-language queries with intent recognition and double validation.

### Purpose

Provide a reliable workflow to navigate FRED categories and series, with support for:
1. Direct `category_id` lookup
2. Direct `series_id` retrieval
3. Natural-language `query` → intent recognition → double validation

### Project Structure

```
fred-navigator/
├── references/              # Reference data files
│   ├── category_paths.json  # Precomputed category paths (optional)
│   ├── fred_categories_flat.json  # Flat category list
│   ├── fred_categories_tree.json  # Hierarchical category tree
│   └── synonyms.json        # Concept synonyms (optional)
├── scripts/                 # Helper scripts
│   ├── build_paths.py       # Build category paths index
│   └── fred_query.py        # FRED API query helper
├── SKILL.md                 # Skill configuration and workflow
├── README.md                # This file
├── requirements.txt         # Python dependencies
└── .gitignore               # Git ignore rules
```

### Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up FRED API key as environment variable:
   ```bash
   export FRED_API_KEY=your_api_key_here
   ```

### Dependencies

- `fredapi`: Python wrapper for FRED API
- `pandas`: Data manipulation library

### Usage

#### Using Helper Scripts

##### List series under a category
```bash
python scripts/fred_query.py category <category_id> [--limit 20] [--output table|json]
```

##### Fetch series data
```bash
python scripts/fred_query.py series <series_id> [--tail 20] [--output table|json]
```

##### Fetch series metadata
```bash
python scripts/fred_query.py series-info <series_id> [--output table|json]
```

##### Show full path for a category
```bash
python scripts/fred_query.py category-path <category_id>
```

##### Check category existence and content
```bash
python scripts/fred_query.py check-category <category_id>
```

##### Build category paths index
```bash
python scripts/build_paths.py
```

#### Skill Inputs

- `category_id`: FRED category id
- `series_id`: FRED series id
- `query`: natural language request
- `limit`: number of candidates to return (default 5)
- `api_key`: read from environment `FRED_API_KEY` only

### Workflow

#### 1. Category Exploration
1. Load `fred_categories_tree.json` for hierarchical browsing
2. Validate `category_id` if provided
3. Fuzzy match `category_name` against flat names if provided

#### 2. Series Discovery
1. Use `search_by_category(category_id)` to list available series
2. Return key columns: `id`, `title`, `frequency`, `units`, `seasonal_adjustment`, `last_updated`

#### 3. Series Retrieval
1. Use `get_series(series_id)` for time series data
2. Use `get_series_info(series_id)` for metadata
3. Provide data head/tail, missing counts, and latest value/date

#### 4. Natural Language Query
1. **Intent Identification**: Interpret natural-language intent and select best-matching category
2. **Double Validation**: 
   - Structural validation: Ensure category exists and has content
   - Semantic validation: Compare query with category name/path
3. **Decision**: Accept category if both validations pass, otherwise return Top-5 candidates

### Failure Handling

- Always provide Top-5 candidates when uncertain
- Never proceed to series retrieval if category validation fails

### Maintenance

- **Update workflow or constraints**: Edit `SKILL.md`
- **Update category data**: Replace files in `references/`
- **Improve natural-language matching**: Add or edit `references/synonyms.json`
- **Regenerate precomputed paths**: Run `scripts/build_paths.py`
- **Add helper scripts**: Place in `scripts/` and document usage

### Notes

- Do not hardcode API keys
- Keep heavy reference data in `references/`, not in `SKILL.md`
- When running Python functions for querying, execute them inside the sandbox environment

## 中文版本

使用 fredapi 导航 FRED（联邦储备经济数据）类别和系列，支持自然语言查询，具有意图识别和双重验证功能。

### 目的

提供可靠的工作流程来导航 FRED 类别和系列，支持：
1. 直接 `category_id` 查找
2. 直接 `series_id` 检索
3. 自然语言 `query` → 意图识别 → 双重验证

### 项目结构

```
fred-navigator/
├── references/              # 参考数据文件
│   ├── category_paths.json  # 预计算的类别路径（可选）
│   ├── fred_categories_flat.json  # 扁平类别列表
│   ├── fred_categories_tree.json  # 层次化类别树
│   └── synonyms.json        # 概念同义词（可选）
├── scripts/                 # 辅助脚本
│   ├── build_paths.py       # 构建类别路径索引
│   └── fred_query.py        # FRED API 查询助手
├── SKILL.md                 # 技能配置和工作流程
├── README.md                # 此文件
├── requirements.txt         # Python 依赖
└── .gitignore               # Git 忽略规则
```

### 安装

1. 克隆此仓库
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 设置 FRED API 密钥作为环境变量：
   ```bash
   export FRED_API_KEY=your_api_key_here
   ```

### 依赖

- `fredapi`: FRED API 的 Python 包装器
- `pandas`: 数据处理库

### 使用

#### 使用辅助脚本

##### 列出类别下的系列
```bash
python scripts/fred_query.py category <category_id> [--limit 20] [--output table|json]
```

##### 获取系列数据
```bash
python scripts/fred_query.py series <series_id> [--tail 20] [--output table|json]
```

##### 获取系列元数据
```bash
python scripts/fred_query.py series-info <series_id> [--output table|json]
```

##### 显示类别的完整路径
```bash
python scripts/fred_query.py category-path <category_id>
```

##### 检查类别是否存在及其内容
```bash
python scripts/fred_query.py check-category <category_id>
```

##### 构建类别路径索引
```bash
python scripts/build_paths.py
```

#### 技能输入

- `category_id`: FRED 类别 ID
- `series_id`: FRED 系列 ID
- `query`: 自然语言请求
- `limit`: 返回的候选数量（默认 5）
- `api_key`: 仅从环境变量 `FRED_API_KEY` 读取

### 工作流程

#### 1. 类别探索
1. 加载 `fred_categories_tree.json` 进行层次浏览
2. 如果提供了 `category_id`，验证其是否存在
3. 如果提供了 `category_name`，对扁平名称进行模糊匹配

#### 2. 系列发现
1. 使用 `search_by_category(category_id)` 列出可用系列
2. 返回关键列：`id`、`title`、`frequency`、`units`、`seasonal_adjustment`、`last_updated`

#### 3. 系列检索
1. 使用 `get_series(series_id)` 获取时间序列数据
2. 使用 `get_series_info(series_id)` 获取元数据
3. 提供数据的头部/尾部、缺失计数以及最新值和日期

#### 4. 自然语言查询
1. **意图识别**：解释自然语言意图并选择最佳匹配类别
2. **双重验证**：
   - 结构验证：确保类别存在且有内容
   - 语义验证：将查询与类别名称/路径进行比较
3. **决策**：如果两个验证都通过，则接受类别；否则返回前 5 个候选

### 故障处理

- 不确定时始终提供前 5 个候选
- 如果类别验证失败，永远不要进行系列检索

### 维护

- **更新工作流程或约束**：编辑 `SKILL.md`
- **更新类别数据**：替换 `references/` 中的文件
- **改进自然语言匹配**：添加或编辑 `references/synonyms.json`
- **重新生成预计算路径**：运行 `scripts/build_paths.py`
- **添加辅助脚本**：放在 `scripts/` 中并记录用法

### 注意事项

- 不要硬编码 API 密钥
- 将大量参考数据保存在 `references/` 中，而不是 `SKILL.md` 中
- 运行用于查询的 Python 函数时，在沙盒环境中执行它们

## License

MIT License
