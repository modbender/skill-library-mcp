from __future__ import annotations

from typing import Any

# v0.1 required fields per doc_type (minimal, conservative)
REQUIRED: dict[str, list[str]] = {
    "w2": [
        "employer_name",
        "employer_ein",
        "employee_ssn",
        "wages",
    ],
    "1099_nec": ["payer_name", "recipient_tin", "nonemployee_comp"],
    "1099_int": ["payer_name", "recipient_tin", "interest_income"],
    "1099_div": ["payer_name", "recipient_tin", "ordinary_dividends"],
    "1099_r": ["payer_name", "recipient_tin"],
    "1099_b": ["payer_name", "recipient_tin"],
    "1099_misc": ["payer_name", "recipient_tin"],
    "1099_g": ["payer_name", "recipient_tin"],
    "1099_k": ["payer_name", "recipient_tin"],
    "k1": ["partner_name"],
    "1040": ["taxpayer_name"],
    "consolidated_1099": ["payer_name"],
    "1099_da": [
        "header.payer_name",
        "header.recipient_name",
        "transactions[0].asset_name",
        "transactions[0].proceeds",
    ],
}


def normalize_doc_type(doc_type: str | None) -> str:
    if not doc_type:
        return "unknown"
    t = doc_type.strip().lower()
    t = t.replace("-", "_")
    return t


def _get_path(obj: Any, path: str) -> Any:
    cur: Any = obj
    # supports simple dotted paths and [idx]
    parts = path.replace("]", "").split(".")
    for part in parts:
        if "[" in part:
            key, idx_s = part.split("[", 1)
            if key:
                if not isinstance(cur, dict):
                    return None
                cur = cur.get(key)
            if not isinstance(cur, list):
                return None
            try:
                idx = int(idx_s)
            except ValueError:
                return None
            if idx < 0 or idx >= len(cur):
                return None
            cur = cur[idx]
        else:
            if not isinstance(cur, dict):
                return None
            cur = cur.get(part)
        if cur is None:
            return None
    return cur


def missing_required_fields(doc_type: str, extraction: Any) -> list[str]:
    t = normalize_doc_type(doc_type)
    req = REQUIRED.get(t, [])
    if not req:
        return []
    missing: list[str] = []
    for p in req:
        v = _get_path(extraction, p)
        if v is None or (isinstance(v, str) and not v.strip()):
            missing.append(p)
    return missing


def compute_overall_confidence(*, doc_type: str, extraction: Any, classification_confidence: float | None) -> float:
    base = float(classification_confidence or 0.5)
    missing = missing_required_fields(doc_type, extraction)
    if not REQUIRED.get(normalize_doc_type(doc_type)):
        # if we don't have required rules, don't tank it
        return min(0.95, max(0.1, base))

    coverage = 1.0
    if REQUIRED.get(normalize_doc_type(doc_type)):
        coverage = 1.0 - (len(missing) / max(1, len(REQUIRED[normalize_doc_type(doc_type)])))

    # weight: required field coverage dominates in v0.1
    overall = 0.35 * base + 0.65 * coverage
    return max(0.0, min(1.0, overall))


def compute_needs_review(*, classification_confidence: float | None, overall_confidence: float | None, missing_required: list[str]) -> bool:
    cc = float(classification_confidence or 0.0)
    oc = float(overall_confidence or 0.0)
    if cc < 0.80:
        return True
    if oc < 0.70:
        return True
    if missing_required:
        return True
    return False
