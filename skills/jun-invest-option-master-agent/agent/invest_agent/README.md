# Invest Agent 团队（invest_agent）

本目录是一套“独立投资 Agent 团队”的**可落地闭环**：
- 目标：输出给生哥审批的《审批包》（不自动下单）
- 策略边界：不杠杆；期权仅 CSP / Covered Call（30–45DTE 为主）
- 数据原则：**富途 OpenAPI 优先**（尤其期权链）；取不到再用公开数据兜底（yfinance）

---

## 1) 一句话用法（聊天触发）
在聊天里发：
- `审批包 AMZN`

系统会在后台完成：Data→各角色输出→校验→生成审批包，并把审批包回给你。

---

## 2) CLI 用法（本地可重复执行）
进入仓库：
```bash
cd /Users/lijunsheng/.openclaw/workspace-invest-master
```

### 2.1 生成 Data 快照（富途期权 + yfinance 兜底）
```bash
PYTHONPATH=. invest_agent/.venv/bin/python invest_agent/bin/data_snapshot --tickers AMZN
```
产物：`invest_agent/outputs/Data.json`

### 2.2 一键生成审批包 + 校验报告
```bash
PYTHONPATH=. python3 invest_agent/bin/invest build --inputs invest_agent/outputs
```
产物：
- `invest_agent/outputs/approval_packet.md`
- `invest_agent/outputs/validation_report.json`

### 2.3 用 fixtures 做回归验证（推荐）
通过样例：
```bash
PYTHONPATH=. python3 invest_agent/bin/invest build --inputs invest_agent/examples/fixtures/pass/outputs
```
失败样例（应返回非 0，并在 report 里列 violations）：
```bash
PYTHONPATH=. python3 invest_agent/bin/invest validate --inputs invest_agent/examples/fixtures/fail/outputs
```

---

## 3) 团队角色（9 个）与职责
角色配置文件：`config/agents.yaml`；硬约束：`config/policy.yaml`。

1) **PM**：汇总输出审批包（不下单）
2) **Data**：事实快照（价格/波动/期权链/事件窗口）+ 数据可信度
3) **Regime**：市场状态与策略倾向
4) **EquityAlpha**：标的研究（催化剂/关键价位/交易性）
5) **Options**：期权结构（仅 CSP/CC）+ 管理/滚动规则
6) **Portfolio**：资金分配/集中度/现金覆盖
7) **Risk**：独立风控（可否决）
8) **Execution**：执行计划（限价/时段/滑点）
9) **Postmortem**：复盘归因（PnL 拆解/规则迭代）

每个角色输出必须包含：
- `assumptions / confidence / invalidation_conditions / risks`

字段级契约：`config/contracts.yaml`

---

## 4) 数据源与接入
### 4.1 富途（优先）
- OpenD：本机 `127.0.0.1:11111`
- 适配器：`integrations/futu/futu_adapter.py`
- 健康检查：`bin/futu_healthcheck`（或 `bin/futu_healthcheck_venv`）

### 4.2 公开数据兜底（yfinance）
- 适配器（库方式）：`integrations/public/yfinance_fallback.py`
- 已安装 skill（Clawhub）：`skills/yfinance-mcp-server`（工具更全，可作为后续统一入口）

---

## 5) 输出物（你最终看的）
- 审批包模板：`templates/approval_packet.md`
- 最终审批包：`outputs/approval_packet.md`
- 校验报告：`outputs/validation_report.json`

---

## 6) 纪律与审批
- 系统**不自动下单**；所有交易必须由生哥审批
- Validator 会检查关键章程项（如：策略类型、永久现金缓冲、集中度、现金覆盖等）

---

## 7) 文件索引
- `config/policy.yaml`：章程（唯一真相）
- `config/agents.yaml`：角色 I/O 与质量门槛
- `config/contracts.yaml`：字段级输出契约
- `prompts/*.md`：角色 SOP/prompt
- `tools/validator.py`：校验器
- `tools/assembler.py`：拼装器
- `bin/invest`：统一 CLI
- `bin/data_snapshot`：Data 快照生成
- `examples/fixtures/*`：回归用例
- `STATUS.md`：单一进度源
- `PROJECT_PLAN.md`：项目计划（DoD/里程碑/节奏）
