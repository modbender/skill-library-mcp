from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def _read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _read_yaml_like(path: Path) -> Dict[str, Any]:
    """Minimal YAML reader for our simple policy/contracts.

    Preferred: PyYAML if available.
    Fallback: very small scalar extractor for the few fields we need.
    """
    text = path.read_text() if path.exists() else ""
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text) or {}
    except Exception:
        # Fallback scalar parse (handles `key: value` with indentation).
        out: Dict[str, Any] = {}
        import re

        def pick(key: str, cast=float):
            m = re.search(rf"^\s*{re.escape(key)}\s*:\s*([^#\n]+)", text, re.M)
            if not m:
                return None
            raw = m.group(1).strip().strip('"').strip("'")
            try:
                return cast(raw)
            except Exception:
                return raw

        # policy.yaml scalars
        out.setdefault("risk", {})
        out["risk"].setdefault("concentration", {})
        v = pick("single_stock_max_pct")
        if v is not None:
            out["risk"]["concentration"]["single_stock_max_pct"] = v
        v = pick("aux_single_ticker_max_pct")
        if v is not None:
            out["risk"]["concentration"]["aux_single_ticker_max_pct"] = v
        v = pick("permanent_cash_buffer_pct")
        if v is not None:
            out["risk"]["permanent_cash_buffer_pct"] = v

        # contracts.yaml required_contract_fields (optional)
        m = re.search(r"required_contract_fields\s*:\s*\[([^\]]+)\]", text)
        if m:
            fields = [x.strip() for x in m.group(1).split(",") if x.strip()]
            out.setdefault("common", {})
            out["common"]["required_contract_fields"] = [f.strip('"').strip("'") for f in fields]

        return out


def _has_keys(obj: Dict[str, Any], keys: List[str]) -> List[str]:
    missing = []
    for k in keys:
        if k not in obj:
            missing.append(k)
    return missing


def validate(inputs_dir: Path) -> Dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    contracts = _read_yaml_like(repo_root / "invest_agent/config/contracts.yaml")
    policy = _read_yaml_like(repo_root / "invest_agent/config/policy.yaml")

    required_contract_fields = (
        ((contracts.get("common") or {}).get("required_contract_fields"))
        or ["assumptions", "confidence", "invalidation_conditions", "risks"]
    )

    roles_required = {
        "Data": ["snapshot", "data_quality_score", "anomalies"],
        "Regime": ["regime_label", "evidence", "strategy_tilts"],
        "EquityAlpha": ["thesis", "catalysts", "key_levels", "liquidity_checks"],
        "Options": ["structure", "strikes_dte", "payoff", "management_rules"],
        "Portfolio": ["allocation", "concentration_checks", "cash_coverage"],
        "Risk": ["verdict", "blocking_issues"],
        "Execution": ["order_plan", "limit_prices"],
    }

    report: Dict[str, Any] = {"ok": True, "missing": {}, "violations": []}

    # Contract field checks (per role file)
    for role, fields in roles_required.items():
        data = _read_json(inputs_dir / f"{role}.json")
        if data is None:
            report["ok"] = False
            report["missing"][role] = {"file": "missing"}
            continue
        miss = _has_keys(data, fields + list(required_contract_fields))
        if miss:
            report["ok"] = False
            report["missing"][role] = {"fields": miss}

    # Cross-role consistency checks (auto-downgrade behavior implemented as violations)
    riskj = _read_json(inputs_dir / "Risk.json") or {}
    verdict = riskj.get("verdict") if isinstance(riskj.get("verdict"), dict) else {}
    decision = (verdict or {}).get("decision")

    portj = _read_json(inputs_dir / "Portfolio.json") or {}
    ccov = portj.get("cash_coverage") if isinstance(portj.get("cash_coverage"), dict) else {}
    cov_ok = ccov.get("coverage_ok") if isinstance(ccov, dict) else None
    if decision == "PASS" and cov_ok is False:
        report["ok"] = False
        report["violations"].append({"type": "consistency", "detail": "Risk=PASS but Portfolio.cash_coverage.coverage_ok=false"})

    # Policy checks (best-effort; relies on Portfolio/Options/Risk)

    # 0) Risk verdict must be valid
    if decision is not None and decision not in ("PASS", "LIMIT", "VETO"):
        report["ok"] = False
        report["violations"].append({"type": "risk_verdict", "detail": f"invalid Risk.verdict.decision={decision}"})

    # 1) Allowed strategies
    opt = _read_json(inputs_dir / "Options.json") or {}
    structure = opt.get("structure") if isinstance(opt.get("structure"), dict) else {}
    strat = (structure or {}).get("strategy_type")
    allowed = (((policy.get("options_policy") or {}).get("allowed_strategies")) or [])
    # map allowed strings to our role naming
    if strat is not None:
        if strat not in ("cash-secured put", "covered call", "cash_secured_put", "covered_call"):
            report["ok"] = False
            report["violations"].append({"type": "options_strategy", "detail": f"invalid strategy_type={strat}"})
        elif allowed and strat in ("cash_secured_put", "covered_call"):
            # ok
            pass

    # 2) Permanent cash buffer policy (must exist and be preserved)
    port = _read_json(inputs_dir / "Portfolio.json") or {}
    alloc = port.get("allocation") if isinstance(port.get("allocation"), dict) else {}

    buf_policy = ((policy.get("risk") or {}).get("permanent_cash_buffer_pct"))
    buf_policy = 25 if buf_policy is None else float(buf_policy)

    buf_val = alloc.get("permanent_cash_buffer")
    if buf_val is None:
        report["ok"] = False
        report["violations"].append({"type": "cash_buffer", "detail": "allocation.permanent_cash_buffer missing"})
    else:
        ok_buf = False
        if isinstance(buf_val, str) and buf_val.strip().endswith("%"):
            try:
                ok_buf = abs(float(buf_val.strip().rstrip("%")) - buf_policy) < 1e-9
            except Exception:
                ok_buf = False
        elif isinstance(buf_val, (int, float)):
            # allow 25 or 0.25
            ok_buf = abs(float(buf_val) - buf_policy) < 1e-9 or abs(float(buf_val) - (buf_policy / 100.0)) < 1e-9
        if not ok_buf:
            report["ok"] = False
            report["violations"].append({"type": "cash_buffer", "detail": f"permanent_cash_buffer must be {buf_policy}%"})

    # 3) Concentration checks (best-effort)
    # Expect Portfolio.allocation.positions entries to optionally carry position_pct.
    single_limit = float(((policy.get("risk") or {}).get("concentration") or {}).get("single_stock_max_pct") or 8)
    aux_limit = float(((policy.get("risk") or {}).get("concentration") or {}).get("aux_single_ticker_max_pct") or 5)

    positions = (alloc.get("positions") or []) if isinstance(alloc, dict) else []
    if isinstance(positions, list):
        for p in positions:
            if not isinstance(p, dict):
                continue
            pct = p.get("position_pct")
            if pct is None:
                continue
            try:
                pctf = float(pct)
            except Exception:
                continue
            is_aux = bool(p.get("is_aux"))
            limit = aux_limit if is_aux else single_limit
            if pctf > limit:
                report["ok"] = False
                report["violations"].append({"type": "concentration", "detail": f"{p.get('ticker')} position_pct {pctf}% > limit {limit}%"})

    # 4) CSP cash coverage (best-effort)
    # Expect Portfolio.cash_coverage.coverage_ok boolean.
    ccov = port.get("cash_coverage") if isinstance(port.get("cash_coverage"), dict) else {}
    if ccov:
        cov_ok = ccov.get("coverage_ok")
        if cov_ok is False:
            report["ok"] = False
            report["violations"].append({"type": "cash_coverage", "detail": "CSP cash coverage not OK"})

    # 5) Preferred DTE window (best-effort)
    # Expect Options.strikes_dte.target_dte (days).
    pref = (((policy.get("options_policy") or {}).get("preferred_dte_days")) or [])
    if isinstance(pref, list) and len(pref) >= 2:
        try:
            dmin, dmax = float(pref[0]), float(pref[1])
        except Exception:
            dmin, dmax = 30.0, 45.0
    else:
        dmin, dmax = 30.0, 45.0

    strikes = opt.get("strikes_dte") if isinstance(opt.get("strikes_dte"), dict) else {}
    tdte = strikes.get("target_dte") if isinstance(strikes, dict) else None
    try:
        if tdte is not None:
            td = float(tdte)
            if not (dmin <= td <= dmax):
                report["ok"] = False
                report["violations"].append({"type": "dte_window", "detail": f"target_dte {td} not in preferred window [{dmin},{dmax}]"})
    except Exception:
        pass

    # 6) Leverage not allowed (best-effort)
    lev_allowed = ((policy.get("risk") or {}).get("leverage_allowed"))
    if lev_allowed is False:
        lev_port = None
        if isinstance(alloc, dict):
            lev_port = alloc.get("leverage_used")
        lev_opt = None
        if isinstance(structure, dict):
            lev_opt = structure.get("leverage")
        if lev_port is True or lev_opt is True:
            report["ok"] = False
            report["violations"].append({"type": "leverage", "detail": "leverage_used/leverage must be false"})

    return report
