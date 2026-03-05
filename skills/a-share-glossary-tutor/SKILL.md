---
name: a-share-glossary-tutor
description: A股/炒股新手概念与指标的结构化讲解与笔记沉淀。用在：解释PE/PB/ROE/现金流/财报口径、板块与题材、政策术语；把零散问题整理成可复习的知识体系（中文优先）。
user-invocable: true
metadata: {"openclaw": {"emoji": "📚"}}
---

# A-Share Glossary Tutor

## Inputs
- concept（必填）：字符串或字符串数组。例："市盈率PE" / ["ROE","自由现金流"]
- context（可选）：你看到这个概念的场景/原句/链接
- level（可选）："beginner" | "intermediate"（默认 beginner）

## Output（固定结构）
对每个 concept 输出：
1) 一句话解释
2) 在 A 股语境下怎么看（常见用法/口径差异提醒）
3) 新手常见误区（至少 1 条）
4) 关联指标/下一步要看的数据（给出 2–5 条清单）
5) 可选：一个小例子（用通俗数字演示）

## Notes / Persistence
- 将整理结果追加写入：`notes/stocks/glossary.md`
- 写入时按标题分组（概念名作为二级标题），避免重复；如已存在则补充“误区/例子/下一步”。

## Boundaries
- 不给具体买卖建议；不承诺收益；强调数据口径与滞后。
- 涉及新闻/政策时，先区分“事实/推断/情绪”。

## Failure modes
- concept 为空：指出缺参数并给示例输入。
- 无法判断口径：明确提出需要的口径（TTM/静态、报告期等）。
