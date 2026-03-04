#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import json
import re
import datetime as dt
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

T_LABELS = {
    "T1": "使用主体",
    "T2": "商标标识",
    "T3": "商品/服务",
    "T4": "使用时间",
    "T5": "使用场景",
    "T6": "交易闭环",
}


def _resolve_rules_dir(base_dir: Path) -> Path:
    candidates = [
        base_dir / "rules",
        base_dir.parent / "Resources" / "rules",
        base_dir.parent / "rules",
        Path.cwd() / "rules",
    ]
    required = ("time_rules.yaml", "score_rules.yaml", "risk_rules.yaml")
    for c in candidates:
        if all((c / name).exists() for name in required):
            return c
    hint = "；".join(str(x) for x in candidates)
    raise FileNotFoundError(f"缺少规则文件目录，候选路径：{hint}")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_rules_and_write_profile(
    *,
    base_dir: Path,
    out_dir: Path,
    run_id: str,
    logger: Any,
    audit: Any,
) -> Dict[str, Any]:
    rules_dir = _resolve_rules_dir(base_dir)
    files = [
        ("time_rules", rules_dir / "time_rules.yaml"),
        ("score_rules", rules_dir / "score_rules.yaml"),
        ("risk_rules", rules_dir / "risk_rules.yaml"),
    ]
    profile: Dict[str, Any] = {
        "run_id": run_id,
        "rules": {},
        "sources": [],
    }
    for key, p in files:
        if not p.exists():
            raise FileNotFoundError(f"缺少规则文件：{p}")
        raw = p.read_text(encoding="utf-8")
        try:
            loaded = yaml.safe_load(raw) or {}
        except Exception as exc:
            logger.exception("规则文件解析失败：%s", p)
            audit({
                "type": "exception",
                "step": "load_rules",
                "file": str(p),
                "error": str(exc),
                "ok": False,
                "reason_code": "rule_parse_error",
            })
            raise
        profile["rules"][key] = loaded
        profile["sources"].append({
            "key": key,
            "path": str(p.resolve()),
            "sha256": sha256_file(p),
            "loaded_keys": sorted(list(loaded.keys())) if isinstance(loaded, dict) else [],
            "content": loaded,
        })

    out_path = out_dir / "rule_profile_used.json"
    out_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    audit({
        "type": "rule_profile_written",
        "step": "write_rule_profile",
        "file": str(out_path),
        "ok": True,
    })
    return profile


def _pick_column(cols: List[str], candidates: List[str]) -> Optional[str]:
    for c in candidates:
        if c in cols:
            return c
    lc = {x.lower(): x for x in cols}
    for c in candidates:
        if c.lower() in lc:
            return lc[c.lower()]
    return None


def _parse_targets(v: Any) -> List[str]:
    src = str(v or "")
    found = re.findall(r"T[1-6]", src.upper())
    out: List[str] = []
    for t in found:
        if t not in out:
            out.append(t)
    return out


def build_reason_chain(
    *,
    casebook_path: Path,
    out_dir: Path,
    run_id: str,
    rule_profile: Dict[str, Any],
    logger: Any,
    audit: Any,
) -> Path:
    try:
        import pandas as pd
    except Exception as exc:
        logger.exception("加载pandas失败，无法生成reason_chain")
        audit({
            "type": "exception",
            "step": "build_reason_chain",
            "file": str(casebook_path),
            "error": str(exc),
            "ok": False,
            "reason_code": "missing_pandas",
        })
        raise

    if not casebook_path.exists():
        raise FileNotFoundError(f"台账不存在：{casebook_path}")

    df = pd.read_excel(casebook_path, sheet_name="DefenseEvidence")
    cols = [str(c) for c in df.columns]
    col_id = _pick_column(cols, ["证据ID", "Evidence ID", "证据编号", "ID"])
    col_name = _pick_column(cols, ["证据名称", "Evidence Name", "Name"])
    col_target = _pick_column(cols, ["要件", "Proof Target (T1-T6)", "Proof Target"])
    col_page = _pick_column(cols, ["页码", "Page", "Pages"])

    score_rules = (rule_profile.get("rules", {}) or {}).get("score_rules", {}) or {}
    risk_rules = (rule_profile.get("rules", {}) or {}).get("risk_rules", {}) or {}
    element_weight = score_rules.get("element_weight", {k: 10 for k in T_LABELS})
    per_evidence = int(score_rules.get("per_evidence_score", 5))
    max_score = int(score_rules.get("max_element_score", 100))
    pass_min_elements = int(risk_rules.get("pass_min_elements", 3))

    buckets: Dict[str, Dict[str, Any]] = {}
    for t, label in T_LABELS.items():
        buckets[t] = {
            "code": t,
            "label": label,
            "score": 0,
            "hit_rules": [],
            "evidence": [],
            "citations": [],
        }

    for _, row in df.fillna("").iterrows():
        targets = _parse_targets(row.get(col_target, "")) if col_target else []
        if not targets:
            continue
        evidence_id = str(row.get(col_id, "") or "").strip()
        evidence_name = str(row.get(col_name, "") or "").strip()
        page = str(row.get(col_page, "") or "").strip()
        evidence_ref = evidence_id or evidence_name
        if not evidence_ref:
            continue
        citation = {
            "file": evidence_name or evidence_ref,
            "page": page,
        }
        for t in targets:
            if t not in buckets:
                continue
            b = buckets[t]
            if evidence_ref not in b["evidence"]:
                b["evidence"].append(evidence_ref)
            if citation not in b["citations"]:
                b["citations"].append(citation)

    for t in sorted(buckets.keys()):
        b = buckets[t]
        count = len(b["evidence"])
        weighted = int(element_weight.get(t, 10))
        score = min(max_score, count * per_evidence + weighted)
        b["score"] = score if count > 0 else 0
        b["hit_rules"] = ["score_rules.element_weight", "score_rules.per_evidence_score"] if count > 0 else []

    covered = sum(1 for t in buckets.values() if t["evidence"])
    final_decision = "PASS" if covered >= pass_min_elements else "WARN"
    element_scores = {k: buckets[k]["score"] for k in sorted(buckets.keys())}
    reason_chain = {
        "run_id": run_id,
        "elements": [buckets[k] for k in sorted(buckets.keys())],
        "final_decision": {
            "level": final_decision,
            "covered_elements": covered,
            "decision_rule": {
                "rule_key": "risk_rules.pass_min_elements",
                "formula": "covered_elements >= pass_min_elements => PASS else WARN",
                "pass_min_elements": pass_min_elements,
            },
            "inputs": {
                "element_scores": element_scores,
                "per_evidence_score": per_evidence,
                "max_element_score": max_score,
            },
            "rationale_pointers": [
                "rule_profile_used.json",
                f"{casebook_path.name}#DefenseEvidence",
            ],
        },
    }

    out_path = out_dir / "reason_chain.json"
    out_path.write_text(json.dumps(reason_chain, ensure_ascii=False, indent=2), encoding="utf-8")
    audit({
        "type": "reason_chain_written",
        "step": "write_reason_chain",
        "file": str(out_path),
        "ok": True,
    })
    return out_path


def _safe_str(v: Any) -> str:
    return str(v or "").strip()


def _norm_yesno(v: Any) -> str:
    s = _safe_str(v).upper()
    if s in ("Y", "YES", "TRUE", "1", "是"):
        return "Y"
    if s in ("N", "NO", "FALSE", "0", "否"):
        return "N"
    return ""


def _norm_conf(v: Any, *, allow_na: bool = True) -> str:
    s = _safe_str(v).upper()
    if s in ("HIGH", "MEDIUM", "LOW"):
        return s
    if allow_na and s in ("N/A", "NA", "UNKNOWN", "UNK"):
        return "N/A"
    return "LOW"


def _norm_valid(v: Any) -> str:
    s = _safe_str(v).upper()
    if s in ("VALID", "INVALID", "N/A"):
        return s
    return ""


def _parse_date_loose(v: Any) -> Optional[dt.date]:
    s = _safe_str(v)
    if not s:
        return None
    m = re.search(r"(20\d{2})[./-](\d{1,2})[./-](\d{1,2})", s)
    if not m:
        m = re.search(r"(20\d{2})年(\d{1,2})月(\d{1,2})日?", s)
    if not m:
        return None
    try:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except Exception:
        return None


def _extract_amount_number(v: Any) -> Optional[float]:
    s = _safe_str(v).replace(",", "")
    if not s:
        return None
    nums = re.findall(r"(\d+(?:\.\d+)?)", s)
    if not nums:
        return None
    try:
        return max(float(x) for x in nums)
    except Exception:
        return None


def _looks_like_trade_type(row: Dict[str, Any]) -> bool:
    t = _safe_str(row.get("Type", ""))
    src = f"{t} {_safe_str(row.get('Evidence Name', ''))} {_safe_str(row.get('Inferred Proof Name', ''))}"
    keys = ("交易", "合同", "发票", "票据", "订单", "物流", "回款", "付款", "支付")
    return any(k in src for k in keys)


def _party_confidence(v: Any) -> Tuple[str, str, str]:
    raw = _safe_str(v)
    if not raw:
        return ("LOW", "INVALID", "party_missing")
    norm = re.sub(r"[^\u4e00-\u9fa5A-Za-z0-9]", "", raw)
    if len(norm) < 2:
        return ("LOW", "INVALID", "party_too_short")
    weak_tokens = {"买家", "卖家", "客户", "商户", "甲方", "乙方", "对方", "个人"}
    if norm in weak_tokens:
        return ("LOW", "INVALID", "party_generic")
    if re.search(r"(公司|企业|集团|事务所|中心|医院|银行|平台|店|厂)$", norm):
        return ("HIGH", "VALID", "party_entity_named")
    return ("MEDIUM", "VALID", "party_named")


def evaluate_field_quality_row(row: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """
    对关键字段给出 confidence/validity，避免低置信字段直接进入核心评分。
    返回字段:
      date / amount / party / goods / mark_presence
    每项包含: value, confidence, validity, reason_code
    """
    out: Dict[str, Dict[str, str]] = {}

    # date
    date_allowed = (_norm_yesno(row.get("Time Anchor Allowed", "")) == "Y")
    if not date_allowed:
        scope = _safe_str(row.get("Time Gate Scope", "Y")).upper()
        evidence_type = _safe_str(row.get("Type", ""))
        date_allowed = scope != "N" and evidence_type != "程序文件"
    d_conf = _norm_conf(row.get("Date Confidence", ""), allow_na=True)
    d_start = _parse_date_loose(row.get("Evidence Date Start", ""))
    d_end = _parse_date_loose(row.get("Evidence Date End", "")) or d_start
    date_has_anchor = bool(d_start and d_end)
    if not date_allowed:
        out["date"] = {
            "value": _safe_str(row.get("Evidence Date Start", "")) or _safe_str(row.get("Time Anchor Text", "")),
            "confidence": "N/A",
            "validity": "N/A",
            "reason_code": "date_not_scored_lane",
        }
    elif date_has_anchor and d_conf in ("HIGH", "MEDIUM"):
        out["date"] = {
            "value": f"{d_start.isoformat()}~{d_end.isoformat()}",
            "confidence": d_conf,
            "validity": "VALID",
            "reason_code": "date_anchor_valid",
        }
    elif date_has_anchor:
        out["date"] = {
            "value": f"{d_start.isoformat()}~{d_end.isoformat()}",
            "confidence": "LOW",
            "validity": "INVALID",
            "reason_code": "date_low_confidence",
        }
    else:
        out["date"] = {
            "value": _safe_str(row.get("Time Anchor Text", "")),
            "confidence": "LOW",
            "validity": "INVALID",
            "reason_code": "date_anchor_missing",
        }

    # amount / party
    trade_like = _looks_like_trade_type(row)
    raw_amount = _safe_str(row.get("Trade Amount", ""))
    raw_party = _safe_str(row.get("Trade Counterparty", "")) or _safe_str(row.get("Entity Names", ""))
    if not trade_like:
        out["amount"] = {"value": raw_amount, "confidence": "N/A", "validity": "N/A", "reason_code": "amount_not_trade"}
        out["party"] = {"value": raw_party, "confidence": "N/A", "validity": "N/A", "reason_code": "party_not_trade"}
    else:
        num = _extract_amount_number(raw_amount)
        if num and num > 0:
            out["amount"] = {
                "value": raw_amount or f"{num:.2f}",
                "confidence": "HIGH",
                "validity": "VALID",
                "reason_code": "amount_parsed",
            }
        elif raw_amount:
            out["amount"] = {
                "value": raw_amount,
                "confidence": "LOW",
                "validity": "INVALID",
                "reason_code": "amount_parse_failed",
            }
        else:
            out["amount"] = {
                "value": "",
                "confidence": "LOW",
                "validity": "INVALID",
                "reason_code": "amount_missing",
            }
        p_conf, p_valid, p_reason = _party_confidence(raw_party)
        out["party"] = {
            "value": raw_party,
            "confidence": p_conf,
            "validity": p_valid,
            "reason_code": p_reason,
        }

    # goods
    g_level = _safe_str(row.get("Goods Match Level", "")).upper()
    if g_level == "G1":
        out["goods"] = {"value": g_level, "confidence": "HIGH", "validity": "VALID", "reason_code": "goods_direct_match"}
    elif g_level == "G2":
        out["goods"] = {"value": g_level, "confidence": "MEDIUM", "validity": "VALID", "reason_code": "goods_synonym_match"}
    elif g_level == "G3":
        out["goods"] = {"value": g_level, "confidence": "LOW", "validity": "INVALID", "reason_code": "goods_unmatched"}
    else:
        out["goods"] = {"value": g_level, "confidence": "LOW", "validity": "INVALID", "reason_code": "goods_missing"}

    # mark presence
    mark_shown = _norm_yesno(row.get("Mark Shown (Y/N)", ""))
    mark_conf = _norm_conf(row.get("Mark Name Confidence", ""), allow_na=True)
    if mark_shown == "Y" and mark_conf in ("HIGH", "MEDIUM"):
        out["mark_presence"] = {
            "value": "Y",
            "confidence": mark_conf,
            "validity": "VALID",
            "reason_code": "mark_present",
        }
    elif mark_shown == "Y":
        out["mark_presence"] = {
            "value": "Y",
            "confidence": "LOW",
            "validity": "INVALID",
            "reason_code": "mark_low_confidence",
        }
    else:
        out["mark_presence"] = {
            "value": mark_shown or "N",
            "confidence": "LOW",
            "validity": "INVALID",
            "reason_code": "mark_not_shown",
        }

    return out


def write_low_confidence_fields(
    *,
    rows: List[Dict[str, Any]],
    out_dir: Path,
    run_id: str,
    logger: Any,
    audit: Any,
) -> Dict[str, Any]:
    """
    1) 对关键字段写入 confidence/validity 到每行;
    2) 输出低置信/无效清单到 low_confidence_fields.json;
    3) 记录审计计数。
    """
    issues: List[Dict[str, Any]] = []
    by_field: Dict[str, int] = {"date": 0, "amount": 0, "party": 0, "goods": 0, "mark_presence": 0}
    by_reason: Dict[str, int] = {}

    for row in rows:
        score = evaluate_field_quality_row(row)
        row["Date Field Confidence"] = score["date"]["confidence"]
        row["Date Validity"] = score["date"]["validity"]
        row["Amount Confidence"] = score["amount"]["confidence"]
        row["Amount Validity"] = score["amount"]["validity"]
        row["Party Confidence"] = score["party"]["confidence"]
        row["Party Validity"] = score["party"]["validity"]
        row["Goods Confidence"] = score["goods"]["confidence"]
        row["Goods Validity"] = score["goods"]["validity"]
        row["Mark Presence Confidence"] = score["mark_presence"]["confidence"]
        row["Mark Presence Validity"] = score["mark_presence"]["validity"]

        eid = _safe_str(row.get("Evidence ID", ""))
        ename = _safe_str(row.get("Evidence Name", ""))
        etype = _safe_str(row.get("Type", ""))
        page = _safe_str(row.get("Page Range", ""))
        for field in ("date", "amount", "party", "goods", "mark_presence"):
            item = score[field]
            conf = _norm_conf(item.get("confidence", ""), allow_na=True)
            valid = _norm_valid(item.get("validity", ""))
            reason = _safe_str(item.get("reason_code", "")) or "unknown"
            if valid == "INVALID" or conf == "LOW":
                by_field[field] += 1
                by_reason[reason] = by_reason.get(reason, 0) + 1
                issues.append({
                    "evidence_id": eid,
                    "evidence_name": ename,
                    "type": etype,
                    "page_range": page,
                    "field": field,
                    "value": _safe_str(item.get("value", "")),
                    "confidence": conf,
                    "validity": valid or "INVALID",
                    "reason_code": reason,
                })

    payload = {
        "run_id": run_id,
        "summary": {
            "total_evidence": len(rows),
            "low_confidence_field_count": len(issues),
            "by_field": by_field,
            "by_reason_code": by_reason,
        },
        "issues": issues,
    }
    out_path = out_dir / "low_confidence_fields.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    audit({
        "type": "low_confidence_fields_written",
        "step": "field_quality_check",
        "file": str(out_path),
        "ok": True,
        "field_issue_count": len(issues),
        "field_issue_by_field": by_field,
    })
    logger.info("低置信字段清单已生成: %s (issues=%s)", out_path, len(issues))
    return {
        "path": str(out_path),
        "count": len(issues),
        "by_field": by_field,
        "by_reason_code": by_reason,
    }
