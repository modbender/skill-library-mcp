#!/usr/bin/env python3
"""
Equity Analyst - Investment Attractiveness Score Calculator

This script implements the strict evaluation framework described in references/framework.md.
It takes extracted financial data, news summary, and chart description, then outputs
a structured analysis report with scores and verdict.

Usage:
    python analyze.py --input data.json --output report.txt

Input JSON format:
{
  "ticker": "000660",
  "company_name": "SK하이닉스",
  "financials": {
    "PER": 17.11,
    "PBR": 5.79,
    "ROE": 43.20,
    "operating_margin": 46.67,
    "debt_ratio": 64.12,
    "revenue_growth": 43.7
  },
  "news_summary": "Brief news summary...",
  "chart_description": "Brief chart description..."
}

Output format: See SKILL.md for exact structure.
"""

import json
import sys
import argparse
from typing import Dict, Any, Tuple

def score_valuation(per: float, pbr: float, industry_per_avg: float = 23.87) -> Tuple[int, str]:
    """Score valuation based on PER and PBR levels."""
    # PER scoring
    if per < 10:
        per_score = 95
    elif per < 15:
        per_score = 85
    elif per < 20:
        per_score = 75
    elif per < 30:
        per_score = 60
    elif per < 40:
        per_score = 40
    else:
        # PER > 40: very expensive unless growth justifies (handled elsewhere)
        per_score = 20

    # PBR scoring
    if pbr < 0.8:
        pbr_score = 95
    elif pbr < 1.2:
        pbr_score = 85
    elif pbr < 2.0:
        pbr_score = 75
    elif pbr < 3.0:
        pbr_score = 60
    elif pbr < 5.0:
        pbr_score = 40
    else:
        pbr_score = 20

    # Average
    final_score = (per_score + pbr_score) // 2

    reasoning = f"PER {per:.1f}x (score {per_score}), PBR {pbr:.1f}x (score {pbr_score})"
    return final_score, reasoning

def score_profitability(roe: float, operating_margin: float) -> Tuple[int, str]:
    """Score profitability based on ROE and operating margin."""
    # ROE scoring
    if roe > 20:
        roe_score = 95
    elif roe > 15:
        roe_score = 85
    elif roe > 10:
        roe_score = 75
    elif roe > 5:
        roe_score = 60
    elif roe > 3:
        roe_score = 40
    else:
        roe_score = 20

    # Operating margin scoring
    if operating_margin > 20:
        margin_score = 95
    elif operating_margin > 15:
        margin_score = 85
    elif operating_margin > 10:
        margin_score = 75
    elif operating_margin > 5:
        margin_score = 60
    elif operating_margin > 0:
        margin_score = 40
    else:
        margin_score = 20

    final_score = (roe_score + margin_score) // 2
    reasoning = f"ROE {roe:.1f}% (score {roe_score}), OpMargin {operating_margin:.1f}% (score {margin_score})"
    return final_score, reasoning

def score_growth(revenue_growth: float) -> Tuple[int, str]:
    """Score growth based on revenue growth rate."""
    if revenue_growth > 30:
        score = 95
    elif revenue_growth > 20:
        score = 85
    elif revenue_growth > 10:
        score = 75
    elif revenue_growth > 5:
        score = 60
    elif revenue_growth > 0:
        score = 40
    else:
        score = 20

    return score, f"Revenue growth {revenue_growth:.1f}%"

def score_stability(debt_ratio: float, industry_avg: float = 80) -> Tuple[int, str]:
    """Score stability based on debt ratio."""
    # Adjust for industry (semis typically have higher debt than software)
    # But only slight adjustment: max +10 if debt_ratio is reasonable for industry
    if debt_ratio < 30:
        score = 95
    elif debt_ratio < 50:
        score = 85
    elif debt_ratio < 80:
        score = 75
    elif debt_ratio < 100:
        score = 60
    elif debt_ratio < 150:
        score = 40
    else:
        score = 20

    return score, f"Debt ratio {debt_ratio:.1f}%"

def score_news(news_summary: str) -> int:
    """
    Score news and outlook based on qualitative assessment.
    This is a simplified heuristic - in practice would use NLP.
    """
    news_lower = news_summary.lower()

    # Positive keywords
    positive_words = [
        'hbm4', '공급', '기대', 'ai', '수요', '증가', '성장', '호조',
        '상승', '매수', '목표가', '상향', '계약', '협력', '승인',
        'tailwind', 'bullish', 'upgrade', 'beat', 'expansion'
    ]

    # Negative keywords
    negative_words = [
        '매도', '하락', '부진', '위기', '소송', '규제', '하향',
        ' cuts', 'loss', 'lawsuit', 'downgrade', 'bearish', 'headwind',
        'foreign selling', '외국인 매도'
    ]

    positive_count = sum(1 for word in positive_words if word in news_lower)
    negative_count = sum(1 for word in negative_words if word in news_lower)

    # Base score
    if positive_count > negative_count + 2:
        score = 80  # Strong positive
    elif positive_count > negative_count:
        score = 70  # Moderate positive
    elif positive_count == negative_count:
        score = 50  # Neutral
    elif negative_count > positive_count + 2:
        score = 30  # Strong negative
    else:
        score = 40  # Moderate negative

    # Cap hype: if many positive words but no concrete numbers, cap at 60
    # Simple heuristic: if score > 60 but no percentage/numbers in summary, reduce
    if score > 60 and not any(c.isdigit() for c in news_summary):
        score = 60

    return score

def score_chart(chart_description: str) -> int:
    """
    Score technical/chart conditions for timing.
    """
    desc_lower = chart_description.lower()

    # Uptrend keywords
    uptrend_words = ['상승', 'uptrend', ' rising', 'higher high', '상승추세', '강세']
    # Downtrend keywords
    downtrend_words = ['하락', 'downtrend', ' falling', 'lower low', '하락추세', '약세']
    # Consolidation/sideways
    sideways_words = ['조정', '횡보', 'consolidation', 'sideways', '밴드', '봉']

    # High52w reference
    near_high = any(word in desc_lower for word in ['최고', '52주 최고', 'high', ' resistance'])
    near_low = any(word in desc_lower for word in ['최저', '52주 최저', 'low', ' support'])

    # Determine trend score
    if any(word in desc_lower for word in uptrend_words):
        trend_score = 70
    elif any(word in desc_lower for word in downtrend_words):
        trend_score = 30
    else:
        trend_score = 50  # Neutral/unknown

    # Adjust for position
    if near_high and trend_score > 50:
        trend_score -= 10  # Extended from high
    if near_low and trend_score < 50:
        trend_score += 10  # Potential bounce

    # Ensure within range
    trend_score = max(0, min(100, trend_score))

    return trend_score

def analyze_stock(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main analysis function implementing the framework.
    """
    financials = data['financials']

    # Step 1: Financial scores
    valuation_score, val_reason = score_valuation(
        financials['PER'],
        financials['PBR']
    )
    profitability_score, profit_reason = score_profitability(
        financials['ROE'],
        financials['operating_margin']
    )
    growth_score, growth_reason = score_growth(
        financials['revenue_growth']
    )
    stability_score, stabil_reason = score_stability(
        financials['debt_ratio']
    )

    # Calculate FinancialScore
    financial_score = (
        valuation_score * 0.30 +
        profitability_score * 0.30 +
        growth_score * 0.25 +
        stability_score * 0.15
    )

    # Special rule: if both Profitability and Growth below 30, cap FinancialScore at 50
    if profitability_score < 30 and growth_score < 30:
        financial_score = min(financial_score, 50)

    # Step 2: News score
    news_score = score_news(data['news_summary'])

    # Step 3: Chart score
    chart_score = score_chart(data['chart_description'])

    # Final score
    final_score = (
        financial_score * 0.50 +
        news_score * 0.25 +
        chart_score * 0.25
    )

    # Verdict
    if final_score >= 80:
        verdict = "BUY"
    elif final_score >= 65:
        verdict = "BUY_LEAN"
    elif final_score >= 45:
        verdict = "HOLD"
    else:
        verdict = "AVOID"

    # Build reasoning parts separately to avoid nested f-string issues
    financial_strength = 'strong' if financial_score >= 70 else 'moderate' if financial_score >= 50 else 'weak'
    valuation_desc = 'reasonable' if valuation_score >= 60 else 'expensive'
    news_sentiment = 'positive' if news_score >= 60 else 'neutral' if news_score >= 40 else 'negative'
    chart_timing = 'favorable timing' if chart_score >= 60 else 'neutral' if chart_score >= 40 else 'unfavorable timing'

    # Profit/growth message
    if profitability_score >= 70 and growth_score >= 70:
        profit_msg = f'Profitability is excellent (ROE {financials["ROE"]:.1f}%) with solid growth (Revenue growth {financials["revenue_growth"]:.1f}%).'
    else:
        profit_msg = 'Profitability and growth are mixed.'

    reasoning = f"""The stock scores {final_score:.1f}/100 ({verdict}). Financial strength is {financial_strength} (FinancialScore {financial_score:.1f}). {profit_msg} Valuation appears {valuation_desc} (PER {financials['PER']:.1f}x). News sentiment is {news_sentiment} (Score {news_score}). Technical chart shows {chart_timing} (Score {chart_score})."""

    # Build output
    result = {
        "ticker": data['ticker'],
        "company_name": data.get('company_name', ''),
        "financial_breakdown": {
            "ValuationScore": round(valuation_score),
            "ProfitabilityScore": round(profitability_score),
            "GrowthScore": round(growth_score),
            "StabilityScore": round(stability_score),
            "FinancialScore": round(financial_score, 1)
        },
        "NewsScore": round(news_score),
        "ChartScore": round(chart_score),
        "Final Investment Attractiveness Score": round(final_score, 1),
        "Verdict": verdict,
        "Reasoning Summary": reasoning.strip(),
        "detailed_reasoning": {
            "valuation": val_reason,
            "profitability": profit_reason,
            "growth": growth_reason,
            "stability": stabil_reason
        }
    }

    return result

def format_output(result: Dict[str, Any]) -> str:
    """Format result as plain text report."""
    lines = []
    lines.append("1. Financial Breakdown")
    fb = result['financial_breakdown']
    lines.append(f"- ValuationScore: {fb['ValuationScore']}")
    lines.append(f"- ProfitabilityScore: {fb['ProfitabilityScore']}")
    lines.append(f"- GrowthScore: {fb['GrowthScore']}")
    lines.append(f"- StabilityScore: {fb['StabilityScore']}")
    lines.append(f"- FinancialScore: {fb['FinancialScore']}")
    lines.append("")
    lines.append(f"2. NewsScore: {result['NewsScore']}")
    lines.append("")
    lines.append(f"3. ChartScore: {result['ChartScore']}")
    lines.append("")
    lines.append(f"4. Final Investment Attractiveness Score: {result['Final Investment Attractiveness Score']} / 100")
    lines.append("")
    lines.append(f"5. Verdict: {result['Verdict']}")
    lines.append("")
    lines.append("6. Reasoning Summary:")
    lines.append(result['Reasoning Summary'])

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description='Equity Analyst - Stock Analysis Score Calculator')
    parser.add_argument('--input', required=True, help='Input JSON file with stock data')
    parser.add_argument('--output', required=False, help='Output file (defaults to stdout)')

    args = parser.parse_args()

    # Load input data
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Analyze
    result = analyze_stock(data)

    # Format output
    output_text = format_output(result)

    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_text)
    else:
        print(output_text)

    # Also return JSON for programmatic use
    return result

if __name__ == '__main__':
    result = main()
    # Print JSON to stderr for debugging/capturing
    import json
    print("\n--- JSON OUTPUT ---", file=sys.stderr)
    print(json.dumps(result, ensure_ascii=False, indent=2), file=sys.stderr)
