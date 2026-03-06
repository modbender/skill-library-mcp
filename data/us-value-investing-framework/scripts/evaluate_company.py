#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def consecutive_roe_pass(financials, threshold=0.15, need_years=3):
    # assume already sorted by year ascending
    streak = 0
    best = 0
    for row in financials:
        if row.get("roe", 0) > threshold:
            streak += 1
            best = max(best, streak)
        else:
            streak = 0
    return best >= need_years, best


def debt_ratio_pass(financials, threshold=0.50):
    latest = financials[-1]
    v = latest.get("debt_ratio", 1)
    return v < threshold, v


def fcf_to_ni_pass(financials, threshold=0.80):
    latest = financials[-1]
    ni = latest.get("net_income", 0)
    fcf = latest.get("free_cash_flow", 0)
    ratio = 0 if ni == 0 else fcf / ni
    return ratio > threshold, ratio


def moat_pass(moat):
    b = moat.get("brand_0_10", 0)
    n = moat.get("network_effect_0_10", 0)
    c = moat.get("cost_advantage_0_10", 0)
    strong_count = sum(1 for x in [b, n, c] if x >= 7)
    avg = (b + n + c) / 3
    passed = strong_count >= 2 or avg >= 7
    return passed, {"brand": b, "network_effect": n, "cost_advantage": c, "strong_dimensions": strong_count, "avg": round(avg, 2)}


def to_rating(pass_count):
    if pass_count == 4:
        return "A"
    if pass_count == 3:
        return "B"
    if pass_count == 2:
        return "C"
    return "D"


def evaluate(payload):
    fin = sorted(payload.get("financials", []), key=lambda x: x.get("year", 0))
    if len(fin) < 3:
        raise ValueError("Need at least 3 years of financial data")

    r1, streak = consecutive_roe_pass(fin)
    r2, debt = debt_ratio_pass(fin)
    r3, ratio = fcf_to_ni_pass(fin)
    r4, moat_detail = moat_pass(payload.get("moat", {}))

    checks = [r1, r2, r3, r4]
    pass_count = sum(1 for x in checks if x)
    rating = to_rating(pass_count)

    reasons = [
        f"ROE > 15% for 3+ years: {'PASS' if r1 else 'FAIL'} (best streak={streak})",
        f"Debt ratio < 50%: {'PASS' if r2 else 'FAIL'} (latest={debt:.2%})",
        f"FCF > 80% of Net Income: {'PASS' if r3 else 'FAIL'} (latest ratio={ratio:.2f})",
        f"Moat (brand/network effect/cost advantage): {'PASS' if r4 else 'FAIL'} (detail={moat_detail})",
    ]

    cn_reasons = [
        f"ROE连续3年以上大于15%：{'通过' if r1 else '未通过'}（最长连续={streak}年）",
        f"负债率低于50%：{'通过' if r2 else '未通过'}（最新={debt:.2%}）",
        f"自由现金流>净利润80%：{'通过' if r3 else '未通过'}（最新比值={ratio:.2f}）",
        f"护城河（品牌/网络效应/成本优势）：{'通过' if r4 else '未通过'}",
    ]

    return {
        "symbol": payload.get("symbol"),
        "company_name": payload.get("company_name"),
        "as_of": payload.get("as_of"),
        "rating": rating,
        "pass_count": pass_count,
        "reasons_en": reasons,
        "reasons_zh": cn_reasons,
        "rule_results": {
            "roe_3y_gt_15pct": r1,
            "debt_ratio_lt_50pct": r2,
            "fcf_gt_80pct_net_income": r3,
            "moat_pass": r4,
        },
    }


def to_markdown(res):
    en = "\n".join([f"- {x}" for x in res["reasons_en"]])
    zh = "\n".join([f"- {x}" for x in res["reasons_zh"]])
    return f"""# {res.get('symbol','N/A')} US Stock Valuation Result

## English Result
- Investment Rating: **{res['rating']}**
- Passed Rules: **{res['pass_count']} / 4**

### Reasons
{en}

## 中文结论（摘要）
- 投资评级：**{res['rating']}**
- 通过规则：**{res['pass_count']} / 4**

### 理由
{zh}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--markdown")
    args = ap.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    res = evaluate(payload)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.markdown:
        md = Path(args.markdown)
        md.parent.mkdir(parents=True, exist_ok=True)
        md.write_text(to_markdown(res), encoding="utf-8")

    print(f"{res['symbol']} => rating {res['rating']} ({res['pass_count']}/4)")


if __name__ == "__main__":
    main()
