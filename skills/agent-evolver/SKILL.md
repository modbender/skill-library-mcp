---
name: agent-evolver
description: AI Agent self-evolution engine that enables agents to learn from experience, detect problems, extract insights, and optimize strategies autonomously. Invoke when users need to improve agent performance, analyze execution errors, or implement continuous learning capabilities.
triggers:
  keywords:
    - "进化"
    - "优化策略"
    - "学习经验"
    - "改进"
    - "错误分析"
    - "自学习"
    - "经验"
    - "策略优化"
    - "持续学习"
    - "性能改进"
  conditions:
    - "任务执行失败超过3次"
    - "用户要求改进性能"
    - "需要分析历史错误"
    - "需要从经验中学习"
---

# Agent Evolver Skill

AI Agent 自进化引擎，让 Agent 具备自学习和持续改进能力。

## 何时使用此技能

### 自动触发条件

1. **错误分析场景**
   - 当任务执行失败时
   - 当需要分析错误原因时
   - 当需要查找相似历史错误时

2. **性能优化场景**
   - 当用户要求改进 Agent 性能时
   - 当需要优化执行策略时
   - 当需要提高成功率时

3. **学习进化场景**
   - 当需要从历史经验学习时
   - 当需要积累知识时
   - 当需要持续改进时

## 使用方法

### 1. 分析执行结果并提取经验

```bash
python3 scripts/evolution_cli.py analyze --result "<错误信息>"
python3 scripts/evolution_cli.py analyze --result-file result.json
```

### 2. 搜索相似历史经验

```bash
python3 scripts/evolution_cli.py search --query "负数平方计算错误"
python3 scripts/evolution_cli.py search --query "ValueError" --limit 10
```

### 3. 查看进化统计

```bash
python3 scripts/evolution_cli.py stats
python3 scripts/evolution_cli.py stats --agent-id my_agent --json
```

### 4. 查看进化历史

```bash
python3 scripts/evolution_cli.py history --limit 20
python3 scripts/evolution_cli.py history --task-type code_generation
```

### 5. 执行进化周期

```bash
python3 scripts/evolution_cli.py evolve "计算 -5 的平方" --task-type calculation
```

## 集成示例

### Python API

```python
from evolver_core import EvolutionManager

# 初始化进化管理器
evolver = EvolutionManager(agent_id="main_agent")

# 执行任务后自动进化
def execute_with_evolution(task):
    result = execute_task(task)
    
    # 自动分析并学习
    evolver.run_evolution(
        task_input=task,
        task_type="general"
    )
    
    return result

# 搜索历史经验
def find_similar_solutions(error_description):
    similar = evolver.search_similar(error_description)
    return similar

# 获取进化统计
def get_evolution_stats():
    return evolver.get_stats()
```

### 自动触发示例

```python
# 主 Agent 执行任务
result = execute_task("计算 -5 的平方")

# 失败后自动触发进化
if result.status == "failed":
    # 自动调用 agent-evolver 技能
    evolver = get_skill("agent-evolver")
    evolver.analyze(result.error)
    
    # 搜索相似解决方案
    similar = evolver.search_similar(result.error.message)
    
    # 应用建议的解决方案
    if similar:
        apply_solution(similar[0].solution)
```

## 功能特性

### 1. 智能经验提取
- 使用 LLM 自动分析错误原因
- 生成针对性的解决方案
- 提取关键词标签便于搜索

### 2. 经验库持久化
- SQLite 存储所有经验
- 支持按类型、错误类型查询
- 自动统计成功率、改进率

### 3. 经验向量化
- 使用 Embedding 模型向量化经验
- 支持语义搜索相似经验
- ChromaDB 向量存储

### 4. 动态策略优化
- 根据历史经验优化策略
- 支持策略版本管理
- 自动回滚机制

### 5. 多任务类型支持
- 代码生成 (code_generation)
- 数据分析 (data_analysis)
- 文档处理 (document_processing)
- 数值计算 (calculation)
- 通用任务 (general)

## 输出格式

所有命令支持 `--json` 参数输出 JSON 格式：

```bash
python3 scripts/evolution_cli.py stats --json
```

## 配置

### 环境变量

- `OPENAI_API_KEY` - OpenAI API 密钥（用于 LLM 分析和向量化）
- `OPENAI_API_BASE` - API 基础 URL（可选，用于自定义端点）
- `EVOLVER_DB_PATH` - 数据库路径（默认：~/.evolver/evolution.db）

### 配置文件

配置文件位于 `config/evolver_config.yaml`：

```yaml
llm:
  model: gpt-3.5-turbo
  temperature: 0.7

vector:
  model: text-embedding-3-small
  enabled: true

storage:
  db_path: ~/.evolver/evolution.db
  vector_path: ~/.evolver/chroma
```

## 数据模型

### 经验胶囊 (ExperienceCapsule)

```json
{
  "id": "exp_20260224_001",
  "task_type": "code_generation",
  "status": "failed",
  "error_type": "ValueError",
  "error_message": "不支持负数输入",
  "solution": "使用绝对值处理负数",
  "keywords": ["负数", "平方计算", "ValueError"]
}
```

## 示例场景

### 场景 1：任务失败分析

```
用户: "这个任务总是失败，帮我分析一下"
Agent: 我来使用 agent-evolver 技能分析错误...
       [调用] python3 scripts/evolution_cli.py analyze --result "ValueError: 不支持负数输入"
       [结果] 发现类似历史错误 3 次
              建议解决方案：使用绝对值处理负数
```

### 场景 2：性能优化

```
用户: "帮我优化一下 Agent 的性能"
Agent: 我来分析 Agent 的进化统计...
       [调用] python3 scripts/evolution_cli.py stats
       [结果] 成功率：85%，改进率：15%
              常见错误：ValueError (5次), TypeError (3次)
              建议：优先处理 ValueError 类型错误
```

### 场景 3：经验搜索

```
用户: "之前遇到过类似的负数计算问题吗？"
Agent: 我来搜索历史经验...
       [调用] python3 scripts/evolution_cli.py search --query "负数计算"
       [结果] 找到 2 条相似经验：
              1. 使用绝对值处理负数 (相似度: 95%)
              2. 添加负数检查逻辑 (相似度: 87%)
```

## 技能发现机制

当此技能安装后，主 Agent 会自动：
1. 识别关键词触发（进化、优化、学习、改进等）
2. 在任务失败时自动调用分析
3. 定期检查进化统计
4. 主动推荐优化建议

## 依赖

- Python 3.8+
- OpenAI API（可选，用于 LLM 分析）
- ChromaDB（可选，用于向量搜索）

## 注意事项

1. 首次使用需要设置 `OPENAI_API_KEY` 环境变量
2. 经验库存储在 `~/.evolver/` 目录
3. 向量搜索需要安装 `chromadb`
4. 无 API 密钥时使用后备分析方案
