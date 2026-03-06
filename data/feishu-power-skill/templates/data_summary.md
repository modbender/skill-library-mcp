# {{title}}

> 生成时间：{{NOW}} | 数据范围：{{WEEK_START}} ~ {{WEEK_END}}

## 概览

- 总记录数：{{summary.total}}
## 状态分布

{{#each records}}
{{#if 状态}}- {{状态}}：{{名称}}
{{/if}}{{/each}}

## 数据明细

{{#each records}}
### {{@index}}. {{名称}}

{{#if 价格}}- 价格：{{价格}}{{/if}}
{{#if 状态}}- 状态：{{状态}}{{/if}}
{{#if 标签}}- 标签：{{标签}}{{/if}}

---
{{/each}}

## 备注

本报告由 Feishu Power Skill 自动生成，数据来源于多维表格。
