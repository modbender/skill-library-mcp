# Knowledge Summarize Agent

异步分析会话提取知识，不阻塞主任务。

## ⚠️ 重要：长会话和大任务需要先压缩

对于复杂任务，在归纳经验前**必须先使用 `/compact` 压缩会话**：

**触发条件**：
- `.opencode/feature_list.json` 中任务数 > 10，或
- 会话轮数 > 50

**重要**：`.opencode/progress.txt` 只保存当前任务信息，不包含历史任务。对于多任务项目，需要结合会话历史进行经验提取。

## 输入

- `session_content`: 会话内容
- `session_id`: 会话标识符

## 执行

### 方式1：简单任务（从 progress.txt 提取）

适用于任务数 ≤ 10 的简单项目。`.opencode/progress.txt` 包含当前任务的结构化经验：

```bash
SKILLS_DIR=$([ -d ~/.config/opencode/skills/evolving-agent ] && echo ~/.config/opencode/skills || echo ~/.claude/skills)

# 检查任务数
TASK_COUNT=0
if [ -f .opencode/feature_list.json ]; then
  TASK_COUNT=$(jq '.features | length' .opencode/feature_list.json 2>/dev/null || echo 0)
fi

# 简单任务（任务数 ≤ 10）：直接从 progress.txt 提取
if [ "$TASK_COUNT" -le 10 ] && [ -f .opencode/progress.txt ]; then
  {
    echo "## 经验总结"
    sed -n '/## 遇到的问题/,/^$/p' .opencode/progress.txt
    sed -n '/## 关键决策/,/^$/p' .opencode/progress.txt
  } | python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge summarize --auto-store
else
  echo "任务数 > 10，建议先执行 /compact，然后结合会话历史归纳总结"
fi
```

**`.opencode/progress.txt` 示例格式**：
```
## 当前任务
- [ ] 添加 JWT 中间件

## 遇到的问题
- bcrypt 编译失败 → 改用 @node-rs/bcrypt
- CORS 跨域报错 → Vite配置 server.proxy

## 关键决策
- JWT secret 存储在环境变量
- 使用 httpOnly cookie 提高安全性
```

### 方式2：复杂任务（结合会话历史）

适用于任务数 > 10 或会话轮数 > 50 的复杂项目：

```bash
# 步骤1: 先执行 /compact 压缩会话历史
# 步骤2: 结合压缩后的摘要 + progress.txt 归纳
# 注意：不要只读 progress.txt，因为它只包含当前任务信息

echo "基于压缩后的会话摘要，归纳所有任务的关键经验：
- 问题1: ...
- 问题2: ...
- 决策1: ...
- 决策2: ...
" | python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge summarize --auto-store
```

### 其他方式

```bash
# 方式4: 从压缩后的摘要归纳
echo "{/compact 后的摘要}" | \
  python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge summarize --auto-store

# 方式5: 手动输入关键经验
echo "问题：跨域报错 → 解决：Vite配置proxy" | \
  python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge summarize --auto-store

# 方式6: 从文件读取
cat experience.txt | \
  python $SKILLS_DIR/evolving-agent/scripts/run.py knowledge summarize --auto-store --session-id "session-123"
```

**建议优先级**:
1. **检查任务复杂度**（任务数 > 10 或会话轮数 > 50）
2. **简单任务**（任务数 ≤ 10）：从 `.opencode/progress.txt` 提取
3. **复杂任务**（任务数 > 10）：先执行 `/compact`，然后结合会话历史 + `.opencode/progress.txt` 归纳
4. **重要**：不要只依赖 `progress.txt`，它只包含当前任务信息

## 知识类型映射

| 内容 | 分类 |
|------|------|
| 问题-解决方案 | problem |
| 最佳实践 | experience |
| 注意事项/坑 | experience |
| 技术模式 | pattern/tech-stack |

## 输出

写入 `.knowledge-summary.md`:

```markdown
## 提取的知识
| 分类 | 名称 | ID |
|------|------|-----|
| problem | CORS问题 | problem-cors-xxx |

## 统计
- 提取条目: 3
- 已存储: 3
```

## 调用方式

```python
Task(
  subagent_type="general",
  description="Knowledge summarization",
  prompt="分析会话并归纳知识"
)
```

## 触发时机

1. **自动**: 进化模式激活时
2. **手动**: 用户说"记住"、"/evolve"

## 约束

- 异步执行
- 不询问用户
- 自动去重
