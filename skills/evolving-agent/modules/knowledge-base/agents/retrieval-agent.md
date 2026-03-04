# Knowledge Retrieval Agent

异步检索知识，不阻塞主任务。

## 输入

- `user_input`: 用户原始输入
- `project_dir`: 项目目录（可选）

## 执行

```bash
SKILLS_DIR=$([ -d ~/.config/opencode/skills/evolving-agent ] && echo ~/.config/opencode/skills || echo ~/.claude/skills)

python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge trigger \
  --input "{user_input}" \
  --project "{project_dir}" \
  --format context > .opencode/.knowledge-context.md
```

## 输出

写入 `.opencode/.knowledge-context.md`:

```markdown
## 相关知识
### [category] Name
**关键信息**: ...

## 可能相关
- [category] Name
```

## 调用方式

```python
Task(
  subagent_type="general",
  description="Knowledge retrieval",
  prompt="执行知识检索，输出到 .opencode/.knowledge-context.md"
)
```

## 约束

- 快速执行（< 5秒）
- 不询问用户
- 出错时写入空文件
