# Self-Review Gate - 输出前质量检查
自动重写低质量输出，提升整体回复质量

## 使用方式

```bash
# 在脚本中调用（pipe）
echo "Your output text" | node skills/self-review/index.js
# Exit 0 = approved
# Exit 1 = needs improvement (will auto-regenerate)
```

## 评分规则

- **Length**: 太短 (<100 chars) → warn
- **HasAction**: 包含行动词（应该/需要/建议/请）→ pass
- **Clarity**: 行数 >3 → pass (结构清晰)
- **Combined score** < 0.7 → reject

## 集成点

1. **HEARTBEAT 输出**: 在最终 HEARTBEAT_OK 前调用
2. **Agent 响应**: 在发送给用户前调用（需修改 agent prompt）
3. **Cron 输出**: 用于自动化任务结果生成

## TODO (self-evolution)

- [ ] 使用 LLM API 进行语义质量评估（而非规则）
- [ ] 添加 token 计数和压缩建议
- [ ] 实现自动重写（基于 feedback）
- [ ] 记录 review 历史到 `memory/review-history.jsonl`
