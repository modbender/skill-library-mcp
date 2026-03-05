# 团队学习升级简报（示例）

## 0) 一句话结论
当前团队执行稳定，但跨 Agent 证据归并仍有缺口；优先补齐覆盖率与技能分配闭环。

## 1) 覆盖率报告
- 已覆盖：main / qin / qianxuesen / miaoji
- 未覆盖：kongming（无可读会话文件）
- 覆盖率：80%
- 缺失原因：未产生日志或不可见

## 2) CEO 决策面板
- 立即批准：高适配 skills 先试点 2 个
- 条件批准：中适配 skills 先隔离试用
- 暂缓：低适配或高风险且无回滚方案

## 3) 组织能力雷达 Top3
1. 数据覆盖缺口（中）
2. 采纳效果量化缺口（中高）
3. 技能治理产品化缺口（高）

## 4) 双线补强建议
### 给CEO
- 学习“三级决策法”：高先批，中附条件，低暂缓
- 学习“审批卡”：目标/收益/风险/回滚

### 给Agent
- 新增：context7（文档时效）
- 新增：analytics（结构化分析）
- 保留：self-improving-agent（复盘沉淀）

## 5) 执行分层（A1）
- 自动：分析、草案、分层建议
- 审批：安装/更新技能、配置变更

## 6) 外部前沿机会
- MCP 基础设施热度高，优先选“可治理、可观测”的能力

## 7) 明日行动清单
1. 输出可批 Top10（高适配优先）
2. 给每条建议补回滚方案
3. 更新 Agent × Skill 分配表

## 8) Suspicious 候选（待审批）
- openclaw-skill-auditor：隔离试用
- analytics（若跨范围采集）：限定场景

## 9) 适配分层
- 高：context7 / analytics / openclaw-github-assistant
- 中：mcp-skill / openclaw-mcp-plugin
- 低：与当前目标弱相关的垂类连接器

## 10) Agent × Skill 盘点分配
- qianxuesen：新增 context7 / analytics
- qin：新增 playwright-mcp / context7
- main：新增 analytics / openclaw-mcp-plugin
