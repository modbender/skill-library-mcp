#!/usr/bin/env python3
"""
Daily Popular Stocks Report
- Opens Naver Finance main page via openclaw browser
- Extracts top 5 popular search stocks
- Visits each stock page, scrapes financial data
- Runs equity analysis
- Generates report and sends to LINE
"""

import subprocess, json, re, sys, os, time
from datetime import datetime

def run_cmd(cmd, timeout=30):
    """Run shell command and return output."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result.stdout, result.stderr, result.returncode

def browser_open(url):
    """Open URL in openclaw browser."""
    cmd = f'openclaw browser --browser-profile openclaw open "{url}"'
    out, err, rc = run_cmd(cmd)
    return rc == 0

def browser_snapshot(save_path=None):
    """Get snapshot of current page. Optionally save to file."""
    if save_path:
        cmd = f'openclaw browser --browser-profile openclaw snapshot > "{save_path}" 2>&1'
        out, err, rc = run_cmd(cmd, timeout=20)
        if rc == 0:
            # Read file with cp949 encoding (Windows default)
            try:
                with open(save_path, 'r', encoding='cp949') as f:
                    return f.read()
            except UnicodeDecodeError:
                # Fallback to utf-8
                with open(save_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        else:
            print(f"Snapshot error: {err}", file=sys.stderr)
            return None
    else:
        cmd = 'openclaw browser --browser-profile openclaw snapshot'
        out, err, rc = run_cmd(cmd, timeout=20)
        if rc == 0:
            return out
        else:
            print(f"Snapshot error: {err}", file=sys.stderr)
            return None

def parse_popular_stocks_from_snapshot(snapshot_text):
    """
    Parse the snapshot output to extract top 5 popular search stocks.
    Expected format from earlier snapshot: "인기 검색 종목" table with rows like:
    '1.삼성전자 158,600 하락 700' and link with code 005930.
    We'll extract name and code from the rowheader links.
    """
    stocks = []
    lines = snapshot_text.split('\n')
    in_popular_section = False

    # Patterns for popular stocks table
    # Row pattern: rowheader with link: 'link "삼성전자" ... /code=005930'
    code_pattern = re.compile(r'/item/main\.naver\?code=(\d{6})')
    name_pattern = re.compile(r'link "([^"]+)" \[ref=')

    for line in lines:
        # Detect start of popular stocks section
        if '인기 검색 종목' in line:
            in_popular_section = True
            continue
        if in_popular_section and '더보기' in line:
            break  # End of table

        if in_popular_section:
            # Look for rows with stock codes
            if '/item/main.naver?code=' in line:
                # Extract code
                code_match = code_pattern.search(line)
                if code_match:
                    code = code_match.group(1)
                    # Extract name: look for the link text just before the URL
                    # The pattern typically: link "NAME" ... /url...
                    name_match = name_pattern.search(line)
                    if name_match:
                        name = name_match.group(1)
                    else:
                        # Fallback: maybe the line contains name in quotes earlier
                        # Try another approach: find the text between quotes before the URL
                        alt_match = re.search(r'"([^"]+)"\s+\[ref=', line)
                        if alt_match:
                            name = alt_match.group(1)
                        else:
                            name = "Unknown"

                    # Avoid duplicates
                    if not any(s['code'] == code for s in stocks):
                        stocks.append({"name": name, "code": code})

                    if len(stocks) >= 5:
                        break

    return stocks[:5]

def scrape_stock_data(ticker):
    """
    Visit stock page and scrape required data.
    Returns dict with ticker, company_name, financials, news_summary, chart_description.
    """
    # Use mobile version to avoid bot detection
    url = f"https://m.stock.naver.com/item/main.nhn?code={ticker}"
    if not browser_open(url):
        print(f"Failed to open {url}", file=sys.stderr)
        return None

    time.sleep(4)  # Wait longer for page load (mobile page might be slower)

    snapshot = browser_snapshot()
    if not snapshot:
        return None

    # Parse data from snapshot (simplified)
    # We'll extract PER, PBR, ROE, etc. from the snapshot text
    data = {
        "ticker": ticker,
        "company_name": "",
        "financials": {
            "PER": 0.0,
            "PBR": 0.0,
            "ROE": 0.0,
            "operating_margin": 0.0,
            "debt_ratio": 0.0,
            "revenue_growth": 0.0
        },
        "news_summary": "",
        "chart_description": "neutral"
    }

    # Extract company name from title or heading
    name_match = re.search(r'<strong[^>]*>([^<]+)</strong>', snapshot)
    if name_match:
        data["company_name"] = name_match.group(1).strip()
    else:
        data["company_name"] = ticker  # fallback

    # Extract financial metrics from the snapshot (look for table rows)
    # In the snapshot we saw: 'ROE(지배주주) 8.37' etc.
    # Pattern: label + number + unit (% or 배)
    # We'll search for these labels

    # PER (배), PBR (배), ROE (%), 영업이익률 (%), 부채비율 (%), 매출성장률 (%)
    finance_labels = {
        'PER': (r'PER\(배\)\s*([\d\.]+)', 1.0),
        'PBR': (r'PBR\(배\)\s*([\d\.]+)', 1.0),
        'ROE': (r'ROE\(지배주주\)\s*([\d\.]+)', 1.0),
        'operating_margin': (r'영업이익률\s*([\d\.]+)', 1.0),
        'debt_ratio': (r'부채비율\s*([\d\.]+)', 1.0),
        'revenue_growth': (r'매출성장률\s*([\d\.]+)', 1.0)
    }

    for key, (pattern, scale) in finance_labels.items():
        match = re.search(pattern, snapshot)
        if match:
            try:
                data["financials"][key] = float(match.group(1)) * scale
            except:
                pass

    # Extract news summary (grab a few recent news headlines)
    # Look for news section links or titles
    news_headlines = []
    news_matches = re.findall(r'<a[^>]*>([^<]+)</a>', snapshot)
    for match in news_matches:
        title = match.strip()
        if len(title) > 10 and ('[' in title or '전망' in title or '공급' in title or 'AI' in title):
            news_headlines.append(title)
        if len(news_headlines) >= 3:
            break
    data["news_summary"] = "; ".join(news_headlines) if news_headlines else "No major news."

    # Extract chart description (simple: look for trend keywords in snapshot)
    if '상승' in snapshot and '하락' not in snapshot[-500:]:
        data["chart_description"] = "uptrend"
    elif '하락' in snapshot[-500:]:
        data["chart_description"] = "downtrend"
    else:
        data["chart_description"] = "neutral"

    return data

def analyze_stock_with_script(data):
    """Call analyze.py to compute scores."""
    import tempfile, os

    # Write input to temp JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        input_path = f.name

    script_path = os.path.join(os.path.dirname(__file__), 'analyze.py')
    python_exe = "C:/Users/IM/AppData/Local/Programs/Python/Python310/python.exe"

    try:
        result = subprocess.run(
            [python_exe, script_path, '--input', input_path],
            capture_output=True,
            text=True,
            timeout=15
        )
        # Parse JSON output from stderr
        if result.stderr:
            json_start = result.stderr.find('{')
            if json_start != -1:
                json_str = result.stderr[json_start:]
                return json.loads(json_str)
        return {"error": "No JSON output", "raw": result.stderr}
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            os.unlink(input_path)
        except:
            pass

def generate_report(results, date_str):
    """Format the final report."""
    lines = [f"[{date_str}] 유력종목 아침 리포트 (인기검색 TOP 5)\n"]
    lines.append("순위 | 종목 | 코드 | 점수 | 추천 | 핵심근거")
    lines.append("-" * 60)

    sorted_results = sorted(results, key=lambda x: x.get('final_score', 0), reverse=True)

    for idx, r in enumerate(sorted_results, 1):
        name = r.get('company_name', 'N/A')[:6]
        ticker = r.get('ticker', 'N/A')
        score = r.get('final_score', 0)
        verdict = r.get('verdict', 'N/A')
        reasoning = r.get('reasoning', '')[:30] + "..." if r.get('reasoning') else ''
        lines.append(f"{idx:<4} | {name:<6} | {ticker} | {score:<5.1f} | {verdict:<8} | {reasoning}")

    lines.append("\n=== 상세 analyze 결과는 상위 3개만 표시 ===\n")
    for idx, r in enumerate(sorted_results[:3], 1):
        lines.append(f"{idx}. {r.get('company_name')} ({r.get('ticker')})")
        lines.append(f"   Final Score: {r.get('final_score', 0):.1f} / 100")
        lines.append(f"   Verdict: {r.get('verdict')}")
        fb = r.get('financial_breakdown', {})
        lines.append(f"   재무: Valuation {fb.get('ValuationScore')}, Profit {fb.get('ProfitabilityScore')}, Growth {fb.get('GrowthScore')}, Stability {fb.get('StabilityScore')}")
        lines.append(f"   뉴스: {r.get('news_score')}, 차트: {r.get('chart_score')}")
        lines.append("")

    return "\n".join(lines)

def main():
    print("=== Daily Popular Report Started ===")

    # Step 1: Open Naver Finance main page
    print("1. Opening Naver Finance main page...")
    if not browser_open("https://finance.naver.com/"):
        print("Failed to open browser.", file=sys.stderr)
        return

    time.sleep(3)
    snapshot = browser_snapshot()
    if not snapshot:
        print("Failed to get snapshot.", file=sys.stderr)
        return

    # Step 2: Extract top 5 popular stocks
    print("2. Extracting top 5 popular stocks...")
    top_stocks = parse_popular_stocks_from_snapshot(snapshot)
    if not top_stocks:
        print("No stocks extracted. Using fallback list.", file=sys.stderr)
        top_stocks = [
            {"name": "삼성전자", "code": "005930"},
            {"name": "SK하이닉스", "code": "000660"},
            {"name": "현대차", "code": "005380"},
            {"name": "한화솔루션", "code": "009830"},
            {"name": "두산에너빌리", "code": "034020"}
        ]

    print(f"   Found: {[s['name'] for s in top_stocks]}")

    # Step 3: Scrape each stock and analyze
    results = []
    for stock in top_stocks:
        print(f"3. Analyzing {stock['name']} ({stock['code']})...")
        data = scrape_stock_data(stock['code'])
        if not data:
            print(f"   Skipping {stock['name']} due to scrape failure.")
            continue

        analysis = analyze_stock_with_script(data)
        if 'error' not in analysis:
            # Flatten keys for easier report generation
            analysis['final_score'] = analysis.get('Final Investment Attractiveness Score', 0)
            analysis['verdict'] = analysis.get('Verdict', 'N/A')
            analysis['financial_breakdown'] = analysis.get('financial_breakdown', {})
            analysis['news_score'] = analysis.get('NewsScore', 0)
            analysis['chart_score'] = analysis.get('ChartScore', 0)
            analysis['reasoning'] = analysis.get('Reasoning Summary', '')
            results.append(analysis)
        else:
            print(f"   Analysis error: {analysis.get('error')}")

    # Step 4: Generate report
    today = datetime.now().strftime('%Y-%m-%d')
    report = generate_report(results, today)
    print("\n=== REPORT PREVIEW ===")
    print(report)

    # Save report
    report_path = 'C:/Users/IM/.openclaw/workspace/daily_popular_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport saved to {report_path}")

    # Step 5: Send to LINE via cron delivery (will be handled by cron job systemEvent -> isolated agentTurn)
    # For manual run, we could also send immediately:
    # message send --channel line --to <user_id> --message "$(cat report_path)"
    print("\n=== Report Generation Complete ===")

if __name__ == '__main__':
    main()