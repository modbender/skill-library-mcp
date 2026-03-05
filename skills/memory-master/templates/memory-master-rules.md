# 记忆系统规则 - memory-master v1.2.5

## 写入时机（自动触发）
- 讨论有结论/行动时立刻写
- 学会新技能/解决方法时立刻写
- ⚠️ 不要等用户提醒！

## 格式
- 格式：memory/daily/YYYY-MM-DD.md
- 索引：memory/daily-index.md
- 记录格式：
```
## [日期] 主题
- 因：原因/背景
- 改：做了什么、改了什么
- 待：待办/后续
```
- 索引格式：`- 主题 → daily/日期.md,日期.md`
- 启发式恢复：发现上下文缺失时主动读索引找记忆

## 知识库
- 目录：memory/knowledge/
- 索引：memory/knowledge-index.md（关键字列表）
- 启发式搜索：上下文没有时搜索引 → 读知识库文件执行
- 学到新技能 → 写入 memory/knowledge/ → 更新索引
