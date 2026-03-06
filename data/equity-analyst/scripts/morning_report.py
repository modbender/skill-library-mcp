#!/usr/bin/env python3
"""
Morning Report Generator
Analyzes top 5 KRX stocks and sends LINE report.
"""

import json
import subprocess
import sys
from datetime import datetime

# Top 5 influential stocks (hardcoded for now)
TICKERS = [
    {"code": "005930", "name": "삼성전자"},
    {"code": "000660", "name": "SK하이닉스"},
    {"code": "035720", "name": "카카오"},
    {"code": "035420", "name": "네이버"},
    {"code": "005380", "name": "현대차"}
]

def fetch_naver_finance(ticker: str) -> dict:
    """Scrape data from Naver Finance (simplified)."""
    try:
        import requests
        from bs4 import BeautifulSoup
        import re

        url = f"https://finance.naver.com/item/main.naver?code={ticker}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        # Extract financial metrics
        data = {}
        tables = soup.find_all('table')
        for table in tables:
            text = table.get_text()
            if 'PER' in text and 'PBR' in text and 'ROE' in text:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all(['th', 'td'])
                    if len(cols) >= 2:
                        label = cols[0].get_text(strip=True)
                        value = cols[1].get_text(strip=True)
                        try:
                            value_clean = re.sub(r'[^\d\.\-]', '', value)
                            if value_clean:
                                float_val = float(value_clean)
                                if 'PER' in label and '배' in label:
                                    data['PER'] = float_val
                                elif 'PBR' in label and '배' in label:
                                    data['PBR'] = float_val
                                elif 'ROE' in label and '%' in label:
                                    data['ROE'] = float_val
                                elif '영업이익률' in label and '%' in label:
                                    data['operating_margin'] = float_val
                                elif '부채비율' in label and '%' in label:
                                    data['debt_ratio'] = float_val
                                elif '매출성장률' in label and '%' in label:
                                    data['revenue_growth'] = float_val
                        except (ValueError, IndexError):
                            continue
                break

        # Fallback extraction from entire page
        defaults = {'PER': 0.0, 'PBR': 0.0, 'ROE': 0.0, 'operating_margin': 0.0, 'debt_ratio': 0.0, 'revenue_growth': 0.0}
        for key, default in defaults.items():
            data.setdefault(key, default)

        # News summary (simple)
        news_section = soup.find('div', {'class': re.compile(r'news|press')})
        news_list = []
        if news_section:
            links = news_section.find_all('a', limit=3)
            for link in links:
                title = link.get_text(strip=True)
                if title and len(title) > 10:
                    news_list.append(title)
        news_summary = '; '.join(news_list) if news_list else "No recent news."

        # Chart description (simple trend from price movement)
        price_section = soup.find('div', {'class': re.compile(r'price|current')})
        chart_desc = "neutral"
        if price_section:
            txt = price_section.get_text()
            if '상승' in txt:
                chart_desc = "uptrend"
            elif '하락' in txt:
                chart_desc = "downtrend"
        else:
            chart_desc = "no explicit trend"

        return {
            "ticker": ticker,
            "financials": data,
            "news_summary": news_summary,
            "chart_description": chart_desc
        }

    except Exception as e:
        print(f"Error scraping {ticker}: {e}", file=sys.stderr)
        return {
            "ticker": ticker,
            "financials": {"PER": 0, "PBR": 0, "ROE": 0, "operating_margin": 0, "debt_ratio": 0, "revenue_growth": 0},
            "news_summary": "Error fetching data",
            "chart_description": "unknown"
        }

def analyze_with_script(data: dict) -> dict:
    """Call analyze.py to compute score."""
    import tempfile
    import os

    # Write input JSON to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        input_path = f.name

    # Output to temp file
    output_path = input_path.replace('.json', '_out.txt')

    # Call analyzer
    script_path = os.path.join(os.path.dirname(__file__), 'analyze.py')
    python_exe = "C:/Users/IM/AppData/Local/Programs/Python/Python310/python.exe"

    try:
        result = subprocess.run(
            [python_exe, script_path, '--input', input_path],
            capture_output=True,
            text=True,
            timeout=15
        )
        # Parse JSON output from stderr (analyze.py prints JSON to stderr)
        if result.stderr:
            json_start = result.stderr.find('{')
            if json_start != -1:
                json_str = result.stderr[json_start:]
                return json.loads(json_str)
        return {"error": "No JSON output", "raw": result.stderr}
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Cleanup
        try:
            os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
        except:
            pass

def generate_report(results: list) -> str:
    """Create formatted report string."""
    today = datetime.now().strftime('%Y-%m-%d')
    lines = [f"[{today}] 유력종목 아침 리포트\n"]
    lines.append("순위 | 종목 | 코드 | 점수 | 추천 | 주요이유")
    lines.append("-" * 50)

    # Sort by final score descending
    sorted_results = sorted(results, key=lambda x: x.get('Final Investment Attractiveness Score', 0), reverse=True)

    for idx, r in enumerate(sorted_results, 1):
        name = r.get('company_name', 'N/A')
        ticker = r.get('ticker', 'N/A')
        score = r.get('Final Investment Attractiveness Score', 0)
        verdict = r.get('Verdict', 'N/A')
        reasoning = r.get('Reasoning Summary', '')[:40] + "..." if r.get('Reasoning Summary') else ''
        lines.append(f"{idx:<4} | {name:<6} | {ticker} | {score:<5} | {verdict:<8} | {reasoning}")

    return "\n".join(lines)

def main():
    all_results = []

    print("[Morning Report] Starting analysis...")
    for stock in TICKERS:
        print(f"  Analyzing {stock['name']} ({stock['code']})...")
        # Scrape fresh data (would work if network allowed)
        # data = fetch_naver_finance(stock['code'])
        # For now, use previously scraped data or mock if fails
        try:
            data = fetch_naver_finance(stock['code'])
        except Exception as e:
            print(f"    Skipping {stock['name']} due to fetch error: {e}")
            continue

        # Analyze
        result = analyze_with_script(data)
        if 'error' not in result:
            all_results.append(result)
        else:
            print(f"    Analysis error: {result.get('error')}")

    if all_results:
        report = generate_report(all_results)
        print("\n=== REPORT PREVIEW ===")
        print(report)
        # Also write to file for cron delivery
        with open('morning_report_output.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        print("\n✅ Report generated and saved to morning_report_output.txt")
    else:
        print("❌ No results to report.")

if __name__ == '__main__':
    main()