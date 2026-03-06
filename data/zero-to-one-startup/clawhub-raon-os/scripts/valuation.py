#!/usr/bin/env python3
"""
Raon OS — 스타트업 밸류에이션 엔진
Pre-Seed ~ Series A 밸류에이션 자동 산출

방법론:
1. Scorecard Method
2. Berkus Method
3. Revenue Multiple Method

한국 스타트업 시장 보정 적용
"""

import json
import math

# --- 상수 ---

# 한국 스타트업 평균 밸류에이션 (억원)
KR_STAGE_VALUATION = {
    "pre-seed": {"low": 5, "mid": 7.5, "high": 10},
    "seed": {"low": 10, "mid": 20, "high": 30},
    "series-a": {"low": 30, "mid": 65, "high": 100},
}

# Scorecard 가중치
SCORECARD_WEIGHTS = {
    "team": 0.30,
    "market": 0.25,
    "product": 0.15,
    "competition": 0.10,
    "marketing": 0.10,
    "other": 0.10,
}

# Berkus 항목별 최대값 (USD)
BERKUS_MAX_PER_ITEM = 500_000
BERKUS_ITEMS = ["idea", "prototype", "team", "strategic_relations", "revenue"]

# Revenue Multiple 업종별 배수
REVENUE_MULTIPLES = {
    "ai": {"low": 10, "high": 20},
    "saas": {"low": 10, "high": 20},
    "ai/saas": {"low": 10, "high": 20},
    "fintech": {"low": 8, "high": 15},
    "biotech": {"low": 5, "high": 12},
    "healthcare": {"low": 5, "high": 12},
    "ecommerce": {"low": 3, "high": 8},
    "commerce": {"low": 3, "high": 8},
    "general": {"low": 3, "high": 5},
    "default": {"low": 3, "high": 5},
}

# 환율
USD_TO_KRW = 1350
KRW_억 = 100_000_000


def _to_억(krw_amount):
    """원 → 억원"""
    return round(krw_amount / KRW_억, 1)


def _억_to_원(억):
    return 억 * KRW_억


def scorecard_method(stage="seed", scores=None):
    """
    Scorecard Method (Bill Payne)
    
    scores: dict with keys from SCORECARD_WEIGHTS, values 0.0~2.0
            (1.0 = average, >1 = above average, <1 = below)
    Returns valuation in 억원
    """
    if scores is None:
        scores = {k: 1.0 for k in SCORECARD_WEIGHTS}

    stage_key = stage.lower().replace(" ", "-")
    base = KR_STAGE_VALUATION.get(stage_key, KR_STAGE_VALUATION["seed"])
    base_val = base["mid"]

    weighted_factor = sum(
        SCORECARD_WEIGHTS[k] * scores.get(k, 1.0) for k in SCORECARD_WEIGHTS
    )

    valuation = base_val * weighted_factor
    
    details = {}
    for k, w in SCORECARD_WEIGHTS.items():
        s = scores.get(k, 1.0)
        details[k] = {
            "weight": f"{w*100:.0f}%",
            "score": round(s, 2),
            "contribution": round(w * s, 3),
        }

    return {
        "method": "Scorecard",
        "valuation_억": round(valuation, 1),
        "valuation_krw": int(_억_to_원(valuation)),
        "base_valuation_억": base_val,
        "stage": stage_key,
        "weighted_factor": round(weighted_factor, 3),
        "details": details,
    }


def berkus_method(scores=None):
    """
    Berkus Method
    
    scores: dict with keys from BERKUS_ITEMS, values 0.0~1.0
            (proportion of max $500K per item)
    Returns valuation in 억원 and USD
    """
    if scores is None:
        scores = {k: 0.5 for k in BERKUS_ITEMS}

    total_usd = 0
    details = {}
    for item in BERKUS_ITEMS:
        s = scores.get(item, 0.5)
        s = max(0.0, min(1.0, s))
        val = BERKUS_MAX_PER_ITEM * s
        total_usd += val
        details[item] = {
            "score": round(s, 2),
            "value_usd": int(val),
        }

    total_krw = total_usd * USD_TO_KRW
    return {
        "method": "Berkus",
        "valuation_usd": int(total_usd),
        "valuation_krw": int(total_krw),
        "valuation_억": _to_억(total_krw),
        "max_usd": BERKUS_MAX_PER_ITEM * len(BERKUS_ITEMS),
        "details": details,
    }


def revenue_multiple_method(annual_revenue_krw=0, mrr_krw=0, industry="default"):
    """
    Revenue Multiple Method
    
    annual_revenue_krw: 연간 매출(원) or ARR
    mrr_krw: 월간 반복 매출(원) - ARR 계산용
    industry: 업종
    Returns valuation in 억원
    """
    arr = annual_revenue_krw
    if mrr_krw > 0 and arr == 0:
        arr = mrr_krw * 12

    if arr <= 0:
        return {
            "method": "Revenue Multiple",
            "valuation_억": None,
            "valuation_krw": None,
            "note": "매출 데이터 없음 - Revenue Multiple 적용 불가",
            "industry": industry,
        }

    ind = industry.lower().replace(" ", "")
    multiples = REVENUE_MULTIPLES.get(ind, REVENUE_MULTIPLES["default"])

    low_val = arr * multiples["low"]
    high_val = arr * multiples["high"]
    mid_val = (low_val + high_val) / 2

    return {
        "method": "Revenue Multiple",
        "valuation_low_억": _to_억(low_val),
        "valuation_high_억": _to_억(high_val),
        "valuation_억": _to_억(mid_val),
        "valuation_krw": int(mid_val),
        "arr_억": _to_억(arr),
        "multiple_range": f"{multiples['low']}x - {multiples['high']}x",
        "industry": industry,
    }


def apply_kr_adjustments(base_valuation_억, tips=False, gov_rnd_억=0, stage="seed"):
    """한국 시장 보정"""
    adjusted = base_valuation_억
    adjustments = []

    # TIPS 프리미엄
    if tips:
        premium = adjusted * 0.20
        adjusted += premium
        adjustments.append({"factor": "TIPS 선정", "premium": "+20%", "added_억": round(premium, 1)})

    # 정부 R&D 실적
    if gov_rnd_억 > 0:
        # R&D 수주 실적의 10~15% 반영
        premium = gov_rnd_억 * 0.125
        adjusted += premium
        adjustments.append({
            "factor": "정부 R&D 수주",
            "amount_억": gov_rnd_억,
            "premium": "~12.5%",
            "added_억": round(premium, 1),
        })

    # 스테이지 범위 클램핑
    stage_key = stage.lower().replace(" ", "-")
    bounds = KR_STAGE_VALUATION.get(stage_key)
    clamped = False
    if bounds:
        if adjusted < bounds["low"]:
            adjusted = bounds["low"]
            clamped = True
        elif adjusted > bounds["high"] * 1.5:  # 150% cap
            adjusted = bounds["high"] * 1.5
            clamped = True
        if clamped:
            adjustments.append({
                "factor": "한국 시장 범위 보정",
                "range": f"{bounds['low']}~{bounds['high']}억",
            })

    return {
        "adjusted_valuation_억": round(adjusted, 1),
        "adjustments": adjustments,
    }


def estimate_valuation(
    stage="seed",
    industry="default",
    revenue=0,
    mrr=0,
    tips=False,
    gov_rnd=0,
    scorecard_scores=None,
    berkus_scores=None,
):
    """
    종합 밸류에이션 산출
    
    Args:
        stage: pre-seed, seed, series-a
        industry: ai, saas, fintech, biotech, etc.
        revenue: 연간 매출 (원)
        mrr: 월간 반복 매출 (원)
        tips: TIPS 선정 여부
        gov_rnd: 정부 R&D 수주 누적액 (억원)
        scorecard_scores: Scorecard 항목별 점수 dict
        berkus_scores: Berkus 항목별 점수 dict
    
    Returns: dict with all methods + recommendation
    """
    sc = scorecard_method(stage, scorecard_scores)
    bk = berkus_method(berkus_scores)
    rm = revenue_multiple_method(revenue, mrr, industry)

    # 유효한 밸류에이션 수집
    valuations = []
    if sc["valuation_억"]:
        valuations.append(sc["valuation_억"])
    if bk["valuation_억"]:
        valuations.append(bk["valuation_억"])
    if rm.get("valuation_억"):
        valuations.append(rm["valuation_억"])

    if not valuations:
        avg = KR_STAGE_VALUATION.get(stage.lower().replace(" ", "-"), KR_STAGE_VALUATION["seed"])["mid"]
    else:
        avg = sum(valuations) / len(valuations)

    # 한국 시장 보정
    adj = apply_kr_adjustments(avg, tips=tips, gov_rnd_억=gov_rnd, stage=stage)

    final = adj["adjusted_valuation_억"]
    # 추천 레인지: ±20%
    range_low = round(final * 0.8, 1)
    range_high = round(final * 1.2, 1)

    # 근거 생성
    rationale = []
    rationale.append(f"Scorecard: {sc['valuation_억']}억 (기준: {stage} 평균 {sc['base_valuation_억']}억, 보정계수 {sc['weighted_factor']})")
    rationale.append(f"Berkus: {bk['valuation_억']}억 (${bk['valuation_usd']:,} USD)")
    if rm.get("valuation_억"):
        rationale.append(f"Revenue Multiple: {rm['valuation_억']}억 ({rm['multiple_range']}, ARR {rm['arr_억']}억)")
    else:
        rationale.append("Revenue Multiple: 매출 데이터 없어 미적용")
    if tips:
        rationale.append("TIPS 선정 프리미엄 +20% 적용")
    if gov_rnd > 0:
        rationale.append(f"정부 R&D {gov_rnd}억 실적 반영")

    return {
        "status": "ok",
        "recommendation": {
            "valuation_억": final,
            "range_low_억": range_low,
            "range_high_억": range_high,
            "valuation_krw": int(_억_to_원(final)),
        },
        "methods": {
            "scorecard": sc,
            "berkus": bk,
            "revenue_multiple": rm,
        },
        "adjustments": adj,
        "rationale": rationale,
        "stage": stage,
        "industry": industry,
        "tips": tips,
        "gov_rnd_억": gov_rnd,
    }


def format_report(result):
    """밸류에이션 결과를 사람이 읽기 좋은 형식으로"""
    r = result
    rec = r["recommendation"]
    sc = r["methods"]["scorecard"]
    bk = r["methods"]["berkus"]
    rm = r["methods"]["revenue_multiple"]

    lines = []
    lines.append("### 🌅 라온의 밸류에이션 리포트\n")
    lines.append(f"**스테이지:** {r['stage']}  |  **업종:** {r['industry']}")
    if r["tips"]:
        lines.append("**TIPS 선정:** ✅ (+20% 프리미엄)")
    if r["gov_rnd_억"] > 0:
        lines.append(f"**정부 R&D 실적:** {r['gov_rnd_억']}억원")
    lines.append("")

    lines.append("---\n")
    lines.append("#### 📊 방법론별 밸류에이션\n")

    # Scorecard
    lines.append(f"**1. Scorecard Method: {sc['valuation_억']}억원**")
    lines.append(f"   기준: {sc['stage']} 평균 {sc['base_valuation_억']}억 × 보정계수 {sc['weighted_factor']}")
    lines.append("   | 항목 | 가중치 | 점수 | 기여도 |")
    lines.append("   |------|--------|------|--------|")
    label_map = {"team": "팀", "market": "시장", "product": "제품", "competition": "경쟁환경", "marketing": "마케팅", "other": "기타"}
    for k, d in sc["details"].items():
        lines.append(f"   | {label_map.get(k, k)} | {d['weight']} | {d['score']} | {d['contribution']} |")
    lines.append("")

    # Berkus
    lines.append(f"**2. Berkus Method: {bk['valuation_억']}억원** (${bk['valuation_usd']:,})")
    label_map2 = {"idea": "아이디어", "prototype": "프로토타입", "team": "팀", "strategic_relations": "전략적관계", "revenue": "매출"}
    for k, d in bk["details"].items():
        bar = "█" * int(d["score"] * 10) + "░" * (10 - int(d["score"] * 10))
        lines.append(f"   {label_map2.get(k, k)}: [{bar}] {d['score']} → ${d['value_usd']:,}")
    lines.append("")

    # Revenue Multiple
    if rm.get("valuation_억"):
        lines.append(f"**3. Revenue Multiple: {rm['valuation_억']}억원**")
        lines.append(f"   ARR: {rm['arr_억']}억 × {rm['multiple_range']}")
    else:
        lines.append(f"**3. Revenue Multiple: 미적용** ({rm.get('note', '')})")
    lines.append("")

    lines.append("---\n")
    lines.append("#### 🎯 종합 추천 밸류에이션\n")
    lines.append(f"**{rec['range_low_억']}억 ~ {rec['range_high_억']}억원**")
    lines.append(f"(중심값: **{rec['valuation_억']}억원**)\n")

    lines.append("#### 📝 근거")
    for rationale in r["rationale"]:
        lines.append(f"- {rationale}")

    return "\n".join(lines)


def cli_main(args=None):
    """CLI 엔트리포인트 (evaluate.py에서 호출)"""
    import argparse

    parser = argparse.ArgumentParser(description="🌅 Raon OS — 밸류에이션 산출")
    parser.add_argument("command", choices=["estimate"], help="명령")
    parser.add_argument("--stage", default="seed", choices=["pre-seed", "seed", "series-a"])
    parser.add_argument("--industry", default="default")
    parser.add_argument("--revenue", type=float, default=0, help="연간 매출 (원)")
    parser.add_argument("--mrr", type=float, default=0, help="월간 반복 매출 (원)")
    parser.add_argument("--tips", action="store_true", help="TIPS 선정 여부")
    parser.add_argument("--gov-rnd", type=float, default=0, help="정부 R&D 수주 누적 (억원)")
    parser.add_argument("--file", "-f", help="사업계획서 PDF (향후 LLM 연동)")
    parser.add_argument("--json", action="store_true", help="JSON 출력")
    # Scorecard scores
    parser.add_argument("--team", type=float, default=1.0, help="팀 점수 0~2 (기본 1.0)")
    parser.add_argument("--market", type=float, default=1.0, help="시장 점수 0~2")
    parser.add_argument("--product", type=float, default=1.0, help="제품 점수 0~2")
    parser.add_argument("--competition", type=float, default=1.0, help="경쟁환경 점수 0~2")
    parser.add_argument("--marketing", type=float, default=1.0, help="마케팅 점수 0~2")
    # Berkus scores
    parser.add_argument("--idea", type=float, default=0.5, help="아이디어 점수 0~1")
    parser.add_argument("--prototype", type=float, default=0.5, help="프로토타입 점수 0~1")
    parser.add_argument("--team-quality", type=float, default=0.5, help="팀 퀄리티 점수 0~1 (Berkus)")
    parser.add_argument("--strategic", type=float, default=0.5, help="전략적관계 점수 0~1")
    parser.add_argument("--revenue-traction", type=float, default=0.5, help="매출 트랙션 점수 0~1")

    parsed = parser.parse_args(args)

    scorecard_scores = {
        "team": parsed.team,
        "market": parsed.market,
        "product": parsed.product,
        "competition": parsed.competition,
        "marketing": parsed.marketing,
        "other": 1.0,
    }

    berkus_scores = {
        "idea": parsed.idea,
        "prototype": parsed.prototype,
        "team": parsed.team_quality,
        "strategic_relations": parsed.strategic,
        "revenue": parsed.revenue_traction,
    }

    result = estimate_valuation(
        stage=parsed.stage,
        industry=parsed.industry,
        revenue=parsed.revenue,
        mrr=parsed.mrr,
        tips=parsed.tips,
        gov_rnd=parsed.gov_rnd,
        scorecard_scores=scorecard_scores,
        berkus_scores=berkus_scores,
    )

    if parsed.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_report(result))


if __name__ == "__main__":
    cli_main()
