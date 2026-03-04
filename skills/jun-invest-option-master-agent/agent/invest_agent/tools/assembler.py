from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _fmt(x: Any) -> str:
    if x is None:
        return "TODO"
    if isinstance(x, (int, float, str)):
        return str(x)
    return json.dumps(x, ensure_ascii=False)


def _section_fill(template: str, heading: str, body: str) -> str:
    pat = re.compile(rf"(^##\s+{re.escape(heading)}\s*\n)(.*?)(?=^##\s+|\Z)", re.M | re.S)
    m = pat.search(template)
    if not m:
        return template
    return template[: m.start(2)] + body.rstrip() + "\n\n" + template[m.end(2) :]


def assemble(inputs_dir: Path, out_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    tmpl_path = repo_root / "invest_agent/templates/approval_packet.md"
    tmpl = tmpl_path.read_text() if tmpl_path.exists() else ""

    data = _read_json(inputs_dir / "Data.json")
    regime = _read_json(inputs_dir / "Regime.json")
    alpha = _read_json(inputs_dir / "EquityAlpha.json")
    opt = _read_json(inputs_dir / "Options.json")
    port = _read_json(inputs_dir / "Portfolio.json")
    risk = _read_json(inputs_dir / "Risk.json")
    exe = _read_json(inputs_dir / "Execution.json")

    # 0) Audit metadata
    gen = _utc_now_iso()
    snap = (data or {}).get("snapshot") if data else None
    data_asof = (snap or {}).get("asof") if isinstance(snap, dict) else None

    # Data sources summary (best-effort)
    sources = {}
    try:
        prices = (snap or {}).get("prices")
        if isinstance(prices, list) and prices:
            sources["benchmarks"] = sorted(list({p.get("source") for p in prices if isinstance(p, dict) and p.get("source")}))
        ocs = (snap or {}).get("options_chain_summary")
        if isinstance(ocs, list) and ocs:
            sources["options"] = sorted(list({o.get("source") for o in ocs if isinstance(o, dict) and o.get("source")}))
        vix = ((snap or {}).get("implied_vol_proxy") or {}).get("vix_or_proxy")
        if isinstance(vix, dict) and vix.get("source"):
            sources["iv_proxy"] = vix.get("source")
    except Exception:
        pass

    # Installed skills versions (from skills/*/_meta.json)
    skills_versions = []
    try:
        skills_dir = repo_root / "skills"
        if skills_dir.exists():
            for meta in skills_dir.glob("*/_meta.json"):
                try:
                    j = json.loads(meta.read_text())
                    skills_versions.append({
                        "skill": meta.parent.name,
                        "name": j.get("name"),
                        "version": j.get("version"),
                    })
                except Exception:
                    continue
    except Exception:
        pass

    audit_body = (
        f"- generated_at: {gen}\n"
        f"- inputs_dir: {inputs_dir}\n"
        f"- data_asof: {_fmt(data_asof)}\n"
        f"- data_sources_summary: {_fmt(sources)}\n"
        f"- opend_endpoint: 127.0.0.1:11111 (not checked at assemble time)\n"
        f"- skills_versions: {_fmt(skills_versions)}\n"
    )
    tmpl = _section_fill(tmpl, "0) Audit metadata（审计元信息）", audit_body)

    # Precompute common derived fields for TL;DR and later sections
    payoff = (opt or {}).get("payoff") if opt else None
    chosen = ((opt or {}).get("strikes_dte") or {}).get("chosen") if opt else None
    credit = (payoff or {}).get("credit_estimate") if isinstance(payoff, dict) else None
    ann_ret = (payoff or {}).get("annualized_return_pct") if isinstance(payoff, dict) else None
    breakeven = (payoff or {}).get("breakeven") if isinstance(payoff, dict) else None

    chain_sum = None
    try:
        ocs = (snap or {}).get("options_chain_summary")
        if isinstance(ocs, list) and ocs:
            chain_sum = ocs[0]
    except Exception:
        chain_sum = None

    alloc = (port or {}).get("allocation") if port else None
    positions = (alloc or {}).get("positions") if isinstance(alloc, dict) else None
    pos0 = positions[0] if isinstance(positions, list) and positions else None

    limit = (exe or {}).get("limit_prices") if exe else None

    # TL;DR
    verdict = (risk or {}).get("verdict") if risk else None
    decision = (verdict or {}).get("decision") if isinstance(verdict, dict) else None
    qty = (pos0 or {}).get("contracts_or_shares") if isinstance(pos0, dict) else None
    ticker = (opt or {}).get("structure", {}).get("ticker") if isinstance((opt or {}).get("structure"), dict) else None
    strat = (opt or {}).get("structure", {}).get("strategy_type") if isinstance((opt or {}).get("structure"), dict) else None
    expiry = (chosen or {}).get("dte") if isinstance(chosen, dict) else None
    strike = (chosen or {}).get("strike") if isinstance(chosen, dict) else None
    cash_reserved = (pos0 or {}).get("cash_reserved") if isinstance(pos0, dict) else None

    reasons = []
    if isinstance(chain_sum, dict) and chain_sum.get("atm_iv") is not None:
        reasons.append(f"ATM IV={chain_sum.get('atm_iv')} / skew={chain_sum.get('put_skew_note')}")
    if isinstance(limit, dict) and limit.get("guidance"):
        reasons.append(f"Execution: {limit.get('guidance')}")
    if decision:
        reasons.append(f"Risk verdict={decision}")

    tldr_body = (
        f"- Verdict (PASS/LIMIT/VETO): {decision or 'TODO'}\n"
        f"- Trade A:\n"
        f"  - ticker/strategy/expiry/strike/qty: {_fmt(ticker)}/{_fmt(strat)}/{_fmt(expiry)}/{_fmt(strike)}/{_fmt(qty)}\n"
        f"  - credit/annualized/breakeven: {_fmt(credit)}/{_fmt(ann_ret)}/{_fmt(breakeven)}\n"
        f"  - cash_reserved: {_fmt(cash_reserved)}\n"
        f"- Key reasons:\n  - " + "\n  - ".join(reasons[:3] or ["TODO"]) + "\n"
        f"- Approval questions:\n"
        f"  - Approve Trade A? (Y/N)\n"
        f"  - Allowed limit range / max concession: TODO\n"
        f"  - Accept management rules (50% TP / 21DTE roll)? (Y/N)\n"
    )
    tmpl = _section_fill(tmpl, "1) TL;DR（一页摘要）", tldr_body)

    # Summary
    summary_body = (
        f"- 是否建议交易：{decision or 'TODO'}\n"
        f"- 本次结论一句话：TODO\n"
        f"- 方案类型：CSP / CC / 组合\n"
    )
    tmpl = _section_fill(tmpl, "2) Summary（PM 汇总结论）", summary_body)

    # Data snapshot
    snap = (data or {}).get("snapshot") if data else None
    dqs = (data or {}).get("data_quality_score") if data else None
    anom = (data or {}).get("anomalies") if data else None
    data_body = (
        f"- asof：{_fmt((snap or {}).get('asof'))}\n"
        f"- 数据可信度（0-100）& 理由：{_fmt(dqs)}\n"
        f"- 基准：{_fmt((snap or {}).get('prices'))}\n"
        f"- rv20：{_fmt((snap or {}).get('realized_vol_20d'))}\n"
        f"- IV proxy：{_fmt((snap or {}).get('implied_vol_proxy'))}\n"
        f"- 期权链概况：{_fmt((snap or {}).get('options_chain_summary'))}\n"
        f"- 未来 2 周事件窗口：{_fmt((snap or {}).get('calendar_2w'))}\n"
        f"- 异常与缺失：{_fmt(anom)}\n"
    )
    tmpl = _section_fill(tmpl, "2) Data snapshot（Data：事实快照）", data_body)

    # Decision basis (auto-generate from Data + Options + Portfolio + Execution)
    payoff = (opt or {}).get("payoff") if opt else None
    chosen = ((opt or {}).get("strikes_dte") or {}).get("chosen") if opt else None
    credit = (payoff or {}).get("credit_estimate") if isinstance(payoff, dict) else None
    cash_ret = (payoff or {}).get("cash_return_pct") if isinstance(payoff, dict) else None
    ann_ret = (payoff or {}).get("annualized_return_pct") if isinstance(payoff, dict) else None
    breakeven = (payoff or {}).get("breakeven") if isinstance(payoff, dict) else None

    # Pull options chain summary metrics
    chain_sum = None
    try:
        ocs = (snap or {}).get("options_chain_summary")
        if isinstance(ocs, list) and ocs:
            chain_sum = ocs[0]
    except Exception:
        chain_sum = None

    # Portfolio constraints
    alloc = (port or {}).get("allocation") if port else None
    positions = (alloc or {}).get("positions") if isinstance(alloc, dict) else None
    pos0 = positions[0] if isinstance(positions, list) and positions else None

    # Execution
    limit = (exe or {}).get("limit_prices") if exe else None

    decision_basis_body = (
        f"- 回报指标：credit={_fmt(credit)}；cash_return={_fmt(cash_ret)}；annualized={_fmt(ann_ret)}；break-even={_fmt(breakeven)}\n"
        f"- 风险补偿：ATM_IV={_fmt((chain_sum or {}).get('atm_iv') if isinstance(chain_sum, dict) else None)}；skew={_fmt((chain_sum or {}).get('put_skew_note') if isinstance(chain_sum, dict) else None)}\n"
        f"- 可执行性：spread_typical={_fmt((chain_sum or {}).get('bid_ask_spread_typical') if isinstance(chain_sum, dict) else None)}；OI/Vol={_fmt((chain_sum or {}).get('oi_volume_note') if isinstance(chain_sum, dict) else None)}；limit_guidance={_fmt((limit or {}).get('guidance') if isinstance(limit, dict) else None)}\n"
        f"- 事件窗口：{_fmt(((alpha or {}).get('catalysts') if alpha else None))}\n"
        f"- 组合约束：position={_fmt(pos0)}；permanent_cash_buffer={_fmt((alloc or {}).get('permanent_cash_buffer') if isinstance(alloc, dict) else None)}\n"
        f"- 最坏情景动作：{_fmt(((port or {}).get('scenario_notes') if port else None))}\n"
    )
    tmpl = _section_fill(tmpl, "3) Decision basis（决策依据：你审批时看的核心）", decision_basis_body)

    # Regime
    if regime:
        rb = (
            f"- regime_label：{_fmt((regime or {}).get('regime_label'))}\n"
            f"- evidence：{_fmt((regime or {}).get('evidence'))}\n"
            f"- strategy_tilts：{_fmt((regime or {}).get('strategy_tilts'))}\n"
            f"- source_file: {inputs_dir / 'Regime.json'}\n"
        )
        tmpl = _section_fill(tmpl, "4) Regime（Regime：市场状态与策略倾向）", rb)

    # Equity thesis
    if alpha:
        ab = (
            f"- thesis：{_fmt((alpha or {}).get('thesis'))}\n"
            f"- catalysts：{_fmt((alpha or {}).get('catalysts'))}\n"
            f"- key_levels：{_fmt((alpha or {}).get('key_levels'))}\n"
            f"- liquidity_checks：{_fmt((alpha or {}).get('liquidity_checks'))}\n"
            f"- source_file: {inputs_dir / 'EquityAlpha.json'}\n"
        )
        tmpl = _section_fill(tmpl, "4) Equity thesis（EquityAlpha：标的与关键价位）", ab)

    # Proposed trades (Trade A best-effort)
    if opt:
        tradeA = (
            f"- Trade A:\n"
            f"  - ticker: {_fmt((opt or {}).get('structure',{}).get('ticker') if isinstance((opt or {}).get('structure'), dict) else None)}\n"
            f"  - strategy: {_fmt((opt or {}).get('structure',{}).get('strategy_type') if isinstance((opt or {}).get('structure'), dict) else None)}\n"
            f"  - qty: {_fmt((pos0 or {}).get('contracts_or_shares') if isinstance(pos0, dict) else None)}\n"
            f"  - dte/expiry: {_fmt((chosen or {}).get('dte') if isinstance(chosen, dict) else None)}\n"
            f"  - strike: {_fmt((chosen or {}).get('strike') if isinstance(chosen, dict) else None)}\n"
            f"  - approx_delta: {_fmt((chosen or {}).get('approx_delta') if isinstance(chosen, dict) else None)}\n"
            f"  - limit_price / credit: {_fmt((payoff or {}).get('credit_estimate') if isinstance(payoff, dict) else None)}\n"
            f"  - rationale: {_fmt((opt or {}).get('structure',{}).get('rationale') if isinstance((opt or {}).get('structure'), dict) else None)}\n"
        )
        tmpl = _section_fill(tmpl, "5) Proposed trades（Options：待生哥审批）", tradeA)

    # Portfolio section
    if port:
        pb = (
            f"- allocation: {_fmt((port or {}).get('allocation'))}\n"
            f"- concentration_checks: {_fmt((port or {}).get('concentration_checks'))}\n"
            f"- cash_coverage: {_fmt((port or {}).get('cash_coverage'))}\n"
            f"- scenario_notes: {_fmt((port or {}).get('scenario_notes'))}\n"
        )
        tmpl = _section_fill(tmpl, "6) Portfolio & cash coverage（Portfolio：资金与一致性）", pb)

    # Risk checks
    risk_body = (
        f"- 结论：{_fmt((verdict or {}).get('decision')) if isinstance(verdict, dict) else _fmt(verdict)}\n"
        f"- blocking_issues：{_fmt((risk or {}).get('blocking_issues') if risk else None)}\n"
        f"- mitigations：{_fmt((risk or {}).get('mitigations') if risk else None)}\n"
        f"- monitoring_triggers：{_fmt((risk or {}).get('monitoring_triggers') if risk else None)}\n"
    )
    tmpl = _section_fill(tmpl, "7) Risk checks（Risk：独立风控结论，可否决）", risk_body)

    # Execution plan
    if exe:
        eb = (
            f"- order_plan: {_fmt((exe or {}).get('order_plan'))}\n"
            f"- limit_prices: {_fmt((exe or {}).get('limit_prices'))}\n"
            f"- timing: {_fmt((exe or {}).get('timing'))}\n"
            f"- slippage_estimate: {_fmt((exe or {}).get('slippage_estimate'))}\n"
        )
        tmpl = _section_fill(tmpl, "8) Execution plan（Execution：执行要点）", eb)

    # Management plan: take from Options.management_rules
    if opt:
        mb = _fmt((opt or {}).get("management_rules"))
        tmpl = _section_fill(tmpl, "9) Management plan（管理规则）", mb + "\n")

    # What could go wrong: take from Risk.risks
    if risk:
        wc = _fmt((risk or {}).get("risks"))
        tmpl = _section_fill(tmpl, "10) What could go wrong（最坏情景清单）", wc + "\n")

    # Contract fields: prefer PM-level; fallback to Data
    contract_src = risk or opt or alpha or regime or data or {}
    contract_body = (
        f"## assumptions\n{_fmt(contract_src.get('assumptions'))}\n\n"
        f"## confidence\n{_fmt(contract_src.get('confidence'))}\n\n"
        f"## invalidation_conditions\n{_fmt(contract_src.get('invalidation_conditions'))}\n\n"
        f"## risks\n{_fmt(contract_src.get('risks'))}\n"
    )
    tmpl = _section_fill(tmpl, "11) Contract fields（必须包含）", contract_body)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(tmpl)
