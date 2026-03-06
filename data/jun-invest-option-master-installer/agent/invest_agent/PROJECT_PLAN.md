# Invest Agent 项目计划（执行版）

Last updated: 2026-02-28 (America/Los_Angeles)

## 0. 项目目标（Definition of Done）
交付一套“可重复、可校验、可拼装”的投资审批包流水线：
- 输入：各角色结构化输出（JSON/YAML）+ 数据快照（Data.json）
- 处理：校验（contracts+policy）+ 拼装（approval_packet.md）
- 输出：单份可审批 Markdown 包 + 校验报告
- 约束：不下单；不杠杆；期权仅 CSP/CC；CSP 100% 现金覆盖；永久现金缓冲 25% 不占用。

## 1. 范围与优先级（先框架后细节）
P0（先完成闭环）
1) Data 快照生成器（已完成）
2) 审批包拼装器（Assembler）
3) 校验器（Validator：contracts + policy 的硬检查）
4) 单一 CLI：build=assemble+validate

P1（质量增强，不阻塞 P0）
5) 富途期权链指标精算：ATM IV/skew/典型点差/OI量化
6) 公共数据成熟 skill 替换（yfinance/yfinancial）；目前用 stooq/web 临时兜底

## 2. 里程碑与可验收交付物
M1（Data pipeline 可用）✅
- 交付：Futu OpenD adapter + public fallback + data_snapshot 脚本

M2（审批包可自动生成）
- 交付：assembler 将 outputs/*.json -> approval_packet_filled.md
- 验收：对 examples/fixtures 一键生成文件成功

M3（可自动校验+一键闭环）
- 交付：validator（缺字段/违规）+ CLI(build)
- 验收：fixtures 正常通过；刻意违规 fixtures 能被抓出并返回非 0

M4（数据质量增强）
- 交付：期权链指标精算（P1）

## 3. 工作分解（WBS）
### 3.1 Assembler
- 解析 role outputs（JSON/YAML）
- 映射到 templates/approval_packet.md 各章节
- 输出 filled markdown + 元信息（生成时间、来源）

### 3.2 Validator
- contracts.yaml：必填字段检查
- policy.yaml：硬约束检查（杠杆/策略类型/现金覆盖/缓冲/集中度/回撤）
- 输出：machine-readable report + human summary

### 3.3 CLI
- 子命令：assemble / validate / build
- 默认目录：invest_agent/outputs

## 4. 质量与节奏（执行纪律）
- 时间盒：每 60–90 分钟必须产出一个可验收增量（代码 + STATUS.md + git commit）
- 每次“进度汇报”必须包含：最新 commit hash + STATUS 变化点
- 不允许长时间停留在思考/查资料；遇到阻塞即降级为骨架实现

## 5. 风险与应对
- 外部 skill 不稳定：先用 stooq/web 临时兜底，后续替换
- 富途权限不齐：期权走富途；ETF spot 走 public
- OpenD 不在线：healthcheck fast-fail + 清晰错误
