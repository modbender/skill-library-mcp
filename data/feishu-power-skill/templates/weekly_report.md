# 周报 | {{WEEK_START}} ~ {{WEEK_END}}

> 生成时间：{{NOW}}
> 负责人：{{author}}

## 本周概览

共处理 **{{summary.total}}** 条记录。

{{#if highlights}}
## 重点事项

{{#each highlights}}
- {{this}}
{{/each}}
{{/if}}

## 数据汇总

{{#each records}}
- {{名称}}（{{状态}}）
{{/each}}

## 下周计划

{{#if next_week}}
{{#each next_week}}
- {{this}}
{{/each}}
{{/if}}

---
*本报告由 Feishu Power Skill 自动生成*
