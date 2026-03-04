#!/usr/bin/env python3
"""Quick test of morning report pipeline using pre-made JSON data."""
import json, sys, os
from datetime import datetime

# Add skill scripts to path
skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, skill_dir)

from scripts.analyze import analyze_stock, format_output

# Load test data
with open('C:/Users/IM/.openclaw/workspace/test_morning_report.json', 'r', encoding='utf-8') as f:
    stocks = json.load(f)

results = []
for stock in stocks:
    try:
        result = analyze_stock(stock)
        results.append(result)
        print(f"Analyzed {stock['company_name']}: {result['Final Investment Attractiveness Score']} ({result['Verdict']})")
    except Exception as e:
        print(f"Failed {stock['company_name']}: {e}")

# Generate report
today = datetime.now().strftime('%Y-%m-%d')
report_lines = [f"[{today}] 유력종목 아침 리포트\n"]
report_lines.append("순위 | 종목 | 코드 | 점수 | 추천")
report_lines.append("-" * 40)

sorted_results = sorted(results, key=lambda x: x.get('Final Investment Attractiveness Score', 0), reverse=True)

for idx, r in enumerate(sorted_results, 1):
    name = r.get('company_name', 'N/A')
    ticker = r.get('ticker', 'N/A')
    score = r.get('Final Investment Attractiveness Score', 0)
    verdict = r.get('Verdict', 'N/A')
    report_lines.append(f"{idx:<4} | {name:<6} | {ticker} | {score:<5.1f} | {verdict}")

report = "\n".join(report_lines)
print("\n" + report)

with open('C:/Users/IM/.openclaw/workspace/morning_report_output.txt', 'w', encoding='utf-8') as f:
    f.write(report)

print("\nSaved to morning_report_output.txt")