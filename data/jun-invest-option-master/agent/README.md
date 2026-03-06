# 独立投资Agent（项目工作空间）

本目录用于维护一套**独立于 main agent**的专业投研/期权现金策略（CSP + Covered Call）工作流。

## 核心约束（必须遵守）
- 账户：USD；资金规模：约 $150,000
- 核心长期：SPY 30% + QQQ 30%
- 永久现金缓冲：25%（绝不占用）
- 战术资金：15%（个股波段 + CSP滚动）
- 最大回撤上限：30%
- 不使用杠杆
- 期权仅允许：Cash-Secured Put、Covered Call（30–45 DTE为主）
- 所有交易必须由生哥审批（本系统只产出“审批包”，不自动下单）

## 目录结构
- `config/policy.yaml`：交易与风控章程（唯一真相）
- `config/agents.yaml`：子agent角色与输出契约
- `prompts/`：各角色提示词（供真实子agent mode=run 调用）
- `templates/approval_packet.md`：给生哥的固定审批包模板
- `logs/`：运行日志与每次产出（按日期归档）

## 运行方式（概念）
每次需要投研/给出交易建议时：
1) 真实拉起子agent（mode=run）分别产出：Data/Regime/Equity/Options/Portfolio/Risk/Exec/Postmortem
2) 将结果落盘到 `logs/YYYY-MM-DD/`
3) PM 汇总成 `approval_packet.md` 给生哥审批
