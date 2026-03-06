# Knowledge Base

知识存储、查询、归纳系统。

## 知识分类

| 分类 | 目录 | 触发场景 |
|------|------|----------|
| experience | `experiences/` | 优化、重构、最佳实践 |
| tech-stack | `tech-stacks/` | 框架相关 |
| scenario | `scenarios/` | 创建、实现功能 |
| problem | `problems/` | 修复、调试、报错 |
| testing | `testing/` | 测试相关 |
| pattern | `patterns/` | 架构、设计模式 |
| skill | `skills/` | 通用技巧 |

## 核心命令

```bash
# 设置路径变量
SKILLS_DIR=$([ -d ~/.config/opencode/skills/evolving-agent ] && echo ~/.config/opencode/skills || echo ~/.claude/skills)

# 查询
python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge query --stats           # 统计
python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge query --trigger "react,hooks"  # 按触发词
python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge query --category problem       # 按分类
python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge query --search "跨域"          # 全文搜索

# 触发检测
python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge trigger --input "修复CORS问题"
python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge trigger --input "..." --project .

# 归纳存储
echo "内容" | python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge summarize --auto-store

# 存储
python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge store --category experience --name "xxx"
```

## 工作流程

### 检索流程（任务开始时）

```python
Task(
    subagent_type="general",
    description="Knowledge retrieval",
    prompt="SKILLS_DIR=$([ -d ~/.config/opencode/skills/evolving-agent ] && echo ~/.config/opencode/skills || echo ~/.claude/skills) && python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge trigger --input '...' --format context > .opencode/.knowledge-context.md"
)
```

### 归纳流程（任务结束后）

检查 `.opencode/.evolution_mode_active`，满足条件则：

```python
Task(
    subagent_type="general",
    description="Knowledge summarization",
    prompt="SKILLS_DIR=$([ -d ~/.config/opencode/skills/evolving-agent ] && echo ~/.config/opencode/skills || echo ~/.claude/skills) && echo '{summary}' | python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge summarize --auto-store"
)
```

## 知识条目 Schema

```json
{
  "id": "category-name-hash",
  "category": "experience|tech-stack|scenario|problem|testing|pattern|skill",
  "name": "名称",
  "triggers": ["触发词"],
  "content": {},
  "sources": ["来源"],
  "created_at": "ISO-8601",
  "effectiveness": 0.5
}
```

## 数据位置

```
~/.config/opencode/knowledge/   # OpenCode
~/.claude/knowledge/            # Claude Code / Cursor
```

## 子代理

| 代理 | 文件 | 用途 |
|------|------|------|
| retrieval | `agents/retrieval-agent.md` | 异步检索 |
| summarize | `agents/summarize-agent.md` | 异步归纳 |
