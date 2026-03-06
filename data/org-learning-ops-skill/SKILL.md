---
name: org-learning-ops-skill
description: 全量会话分析 + 每日技能盘点分配 + CEO学习日报与热门skills雷达联动输出。
version: 1.0.0
---

# Org Learning Ops Skill

## 目标
把“团队协作对话”转成可执行的组织能力升级建议，并形成每日可审批的技能分配清单。

## 固定输入
1. 全量会话历史：`~/.openclaw/agents/*/sessions/*.jsonl`
2. 可见会话API：`sessions_list` / `sessions_history`
3. 技能来源：GitHub / ClawHub / SkillsMP / skills.sh
4. 已安装技能与agent配置：当前环境可见配置

## 固定动作（必须按顺序）

### A. 全量覆盖分析
- 覆盖目标agent：main / qin / kongming / qianxuesen / miaoji（若可见）
- 统计字段：
  - session数量
  - 角色消息计数（user/assistant/toolResult）
  - 时间范围
  - 主题命中（技能安装/定时运营/研究情报/协作调度/治理审批）
- 输出覆盖率报告：已覆盖、未覆盖、覆盖率%、缺失原因

### B. 组织诊断
- 输出组织能力雷达Top3（证据化）
- 输出双线建议：
  - CEO学习输入（方法/资料/应用）
  - Agent能力补强（skills/SOP/workflow）

### C. 技能雷达（近3天Top30）
- 每条必须包含：
  1) skill名称
  2) 用途（1-2句）
  3) 数据表现（热度/星标/下载/活跃；缺失标注“数据不可得”）
  4) 来源链接
  5) 适配等级（高/中/低）+ 依据
- 输出“可批Top10（高适配优先）”

### D. 技能盘点与分配（每日必做）
- 盘点：已安装skills + 各agent已配置skills
- 输出 Agent × Skill 分配表：
  - 建议新增
  - 建议保留
  - 建议暂停/移除
- 每条必须附：用途、证据、风险、回滚点

### E. 治理边界（A1）
- 自动：收集、分析、草案、分层、推荐
- 需审批：安装/更新skill、配置变更、正式启用
- suspicious技能：先展示清单并审批；未批不转正

## 输出模板（日报）
1) 一句话结论
2) 覆盖率报告
3) CEO决策面板
4) 组织能力雷达Top3
5) 双线补强建议
6) 执行分层(A1)
7) 外部前沿机会
8) 明日行动清单
9) Suspicious候选清单（待审批）
10) 适配分层（高/中/低）
11) Agent×Skill盘点分配（新增/保留/暂停）

## 质量门槛
- 无证据不建议
- 覆盖率<80%时，先给“补数动作Top3”
- 禁止泛推荐；建议必须能落地
