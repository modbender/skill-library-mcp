# Session README Template

Council 会议记录的 README 模板。

## 基础模板

```markdown
# AI Council Session - YYYY-MM-DD

## 审查目标
- [PR/Issue/决策 描述]
- [相关链接]

## Council 成员

| 角色 | 模型 | 人设 | 关注点 |
|------|------|------|--------|
| 架构师 | opus-4.6 | **[大牛名字]** | [专长领域] |
| 工程师 | sonnet-4.5 | **[大牛名字]** | [专长领域] |
| 批判者 | gpt-5.2 | **[大牛名字]** | [专长领域] |

## 文件清单

| 文件 | 内容 | 行数 |
|------|------|------|
| `council-opus-prompt.txt` | Opus 任务 prompt | XX |
| `council-opus-output.txt` | Opus 完整分析 | XX |
| `council-sonnet-prompt.txt` | Sonnet 任务 prompt | XX |
| `council-sonnet-output.txt` | Sonnet 完整分析 | XX |
| `council-gpt-prompt.txt` | GPT 任务 prompt | XX |
| `council-gpt-output.txt` | GPT 完整分析 | XX |

## 共识矩阵

| 维度 | Opus | Sonnet | GPT |
|------|------|--------|-----|
| [维度1] | [观点] | [观点] | [观点] |
| [维度2] | [观点] | [观点] | [观点] |

## 结论

### 一致同意
- [共识点1]
- [共识点2]

### 存在分歧
- [分歧点及各方观点]

### 最终建议
[综合建议]

## 后续行动

- [ ] [Action 1]
- [ ] [Action 2]

## 相关链接

- [GitHub PR](https://...)
- [GitHub Comment](https://...#issuecomment-...)
```

## PR 审查专用模板

```markdown
# AI Council Session - YYYY-MM-DD - PR Review

## 审查目标

| PR | 标题 | 作者 |
|----|------|------|
| #XXXX | [标题] | @author |
| #YYYY | [标题] | @author |

## Council 成员

| 角色 | 模型 | 人设 | 关注点 |
|------|------|------|--------|
| 架构师 | opus-4.6 | **Joe Armstrong** | 并发安全、进程隔离、Let it crash |
| 工程师 | sonnet-4.5 | **TJ Holowaychuk** | 代码简洁、Node 最佳实践 |
| 批判者 | gpt-5.2 | **Ryan Dahl** | 根因反思、设计问题 |

## 审查结论

| PR | Opus | Sonnet | GPT | 最终建议 |
|----|------|--------|-----|----------|
| #XXXX | ⚠️ | ❌ | ⚠️ | REQUEST CHANGES |
| #YYYY | ✅ | ✅ | ⚠️ | APPROVE with comments |

## 关键发现

### PR #XXXX
- **核心问题**：[问题描述]
- **改进建议**：[建议]

### PR #YYYY  
- **核心问题**：[问题描述]
- **改进建议**：[建议]

## GitHub 评论已提交

- https://github.com/.../pull/XXXX#issuecomment-...
- https://github.com/.../pull/YYYY#issuecomment-...
```

## 快速生成脚本

```bash
#!/bin/bash
# generate-council-readme.sh

DATE=$(date +%Y-%m-%d)
ARCHIVE_DIR=${1:-~/.openclaw/workspace/pr-review/council-$DATE}

cat > "$ARCHIVE_DIR/README.md" << EOF
# AI Council Session - $DATE

## 审查目标
- TODO: 填写审查目标

## Council 成员

| 角色 | 模型 | 人设 | 关注点 |
|------|------|------|--------|
| 架构师 | opus-4.6 | **TODO** | TODO |
| 工程师 | sonnet-4.5 | **TODO** | TODO |
| 批判者 | gpt-5.2 | **TODO** | TODO |

## 文件清单
$(for f in "$ARCHIVE_DIR"/council-*.txt; do
  [ -f "$f" ] && echo "- \`$(basename $f)\` ($(wc -l < "$f") lines)"
done)

## 结论
TODO: 填写结论

## 相关链接
- TODO: 添加链接
EOF

echo "Generated: $ARCHIVE_DIR/README.md"
```
