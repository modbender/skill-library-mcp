# Invest Agent 团队（roles）

本文件描述“子 agent 角色”职责、输入输出、以及集成方式。主 Agent（PM / invest-master）负责调度与汇总。

## 角色顺序（默认工作流）
1) Data → 2) Regime → 3) EquityAlpha → 4) Options → 5) Portfolio → 6) Risk → 7) Execution → 8) Postmortem → 9) Growth（持续改进）

## 数据源原则
- 优先：券商接口（待生哥提供接入方式后启用）
- 兜底：公开数据（优先成熟 skills；不足再用 web_fetch/web_search 临时补齐）

## 输出契约（统一要求）
每个角色输出必须包含：
- assumptions
- confidence
- invalidation_conditions
- risks

并遵循对应 `invest_agent/prompts/<Role>.md` 的结构化字段。

## 审批包集成
- PM 输出必须严格使用：`invest_agent/templates/approval_packet.md`
- Risk 结论为 VETO 时：PM 必须降级为“不建议执行/需修改”，不得硬推交易

## Skills 优先入口（长期记忆）
当需要技能/最佳实践时，优先从以下入口寻找：
- OpenClaw 官网：https://openclaw.ai/
- OpenClaw 文档：https://docs.openclaw.ai/
- Clawhub（Skills）：https://clawhub.ai/
- Evomap：https://evomap.ai/
