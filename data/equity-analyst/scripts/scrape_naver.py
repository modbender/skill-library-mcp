#!/usr/bin/env python3
"""
Scrape Naver Finance page for stock data.

Usage:
    python scrape_naver.py <ticker> [--output data.json]

Example:
    python scrape_naver.py 251270 --output netmarble_data.json
"""

import argparse
import json
import sys
import re
from typing import Dict, Any, Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: requests and beautifulsoup4 are required. Install with: pip install requests beautifulsoup4")
    sys.exit(1)


def fetch_naver_finance(ticker: str) -> str:
    """Fetch the HTML content from Naver Finance."""
    url = f"https://finance.naver.com/item/main.naver?code={ticker}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text


def extract_financial_data(html: str) -> Dict[str, float]:
    """Extract financial metrics from Naver Finance HTML."""
    soup = BeautifulSoup(html, 'html.parser')

    data = {}

    # Find the table with financial data (typically "재무정보" table)
    # Naver Finance structure: there are multiple tables, we need to find the right one
    tables = soup.find_all('table')

    # Look for table containing PER, PBR, ROE etc.
    for table in tables:
        text = table.get_text()
        if 'PER' in text and 'PBR' in text and 'ROE' in text:
            # Found candidate table
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['th', 'td'])
                if len(cols) >= 2:
                    label = cols[0].get_text(strip=True)
                    value = cols[1].get_text(strip=True)
                    # Clean value (remove commas, convert to float)
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

    # If some data is missing, try alternative parsing (e.g., from summary section)
    if 'PER' not in data or 'PBR' not in data or 'ROE' not in data:
        # Look for '시가총액' section or other areas
        # Sometimes data is in a different format with spans/classes
        # This is a fallback heuristics
        for element in soup.find_all(['span', 'div', 'p']):
            text = element.get_text()
            if 'PER' in text:
                match = re.search(r'(\d+\.?\d*)\s*배', text)
                if match:
                    data['PER'] = float(match.group(1))
            if 'PBR' in text:
                match = re.search(r'(\d+\.?\d*)\s*배', text)
                if match:
                    data['PBR'] = float(match.group(1))
            if 'ROE' in text:
                match = re.search(r'(\d+\.?\d*)\s*%', text)
                if match:
                    data['ROE'] = float(match.group(1))
            if '영업이익률' in text:
                match = re.search(r'(\d+\.?\d*)\s*%', text)
                if match:
                    data['operating_margin'] = float(match.group(1))
            if '부채비율' in text:
                match = re.search(r'(\d+\.?\d*)\s*%', text)
                if match:
                    data['debt_ratio'] = float(match.group(1))
            if '매출성장률' in text:
                match = re.search(r'(\d+\.?\d*)\s*%', text)
                if match:
                    data['revenue_growth'] = float(match.group(1))

    # Ensure all fields exist (set to 0 or None if missing)
    defaults = {
        'PER': 0.0,
        'PBR': 0.0,
        'ROE': 0.0,
        'operating_margin': 0.0,
        'debt_ratio': 0.0,
        'revenue_growth': 0.0
    }
    for key, default in defaults.items():
        data.setdefault(key, default)

    return data


def extract_news_summary(soup: BeautifulSoup) -> str:
    """Extract recent news headlines or summary from the page."""
    # Look for news section - often in a div with class 'news_section' or similar
    news_list = []
    news_section = soup.find('div', {'class': re.compile(r'news|press|article')})
    if news_section:
        links = news_section.find_all('a', limit=5)
        for link in links:
            title = link.get_text(strip=True)
            if title and len(title) > 10:
                news_list.append(title)
    if news_list:
        return "Recent news: " + "; ".join(news_list[:3])
    return "No recent news found."


def extract_chart_description(soup: BeautifulSoup) -> str:
    """Extract simple chart/trend information."""
    # Look for price trend indicators, maybe from a chart img alt text or summary
    # Naver Finance often shows a small chart image, we can look for alt text
    chart_img = soup.find('img', {'alt': re.compile(r'차트|추세|일간|주간|월간')})
    if chart_img:
        alt_text = chart_img.get('alt', '')
        return f"Chart shows: {alt_text}" if alt_text else "Chart: trend not specified"
    # Fallback: check if current price is above/below moving averages mentioned
    price_section = soup.find('div', {'class': re.compile(r'price|current')})
    if price_section:
        price_text = price_section.get_text()
        if '상승' in price_text:
            return "Current trend: 상승 (rising)"
        elif '하락' in price_text:
            return "Current trend: 하락 (falling)"
    return "Chart: neutral/no explicit trend info"


def scrape_stock(ticker: str) -> Dict[str, Any]:
    """Main function to scrape all data for a given ticker."""
    try:
        html = fetch_naver_finance(ticker)
    except requests.RequestException as e:
        print(f"Error fetching data for {ticker}: {e}", file=sys.stderr)
        sys.exit(1)

    soup = BeautifulSoup(html, 'html.parser')

    financials = extract_financial_data(html)
    news_summary = extract_news_summary(soup)
    chart_description = extract_chart_description(soup)

    # Get company name
    title_tag = soup.find('title')
    company_name = title_tag.get_text().split('-')[0].strip() if title_tag else "Unknown"

    return {
        "ticker": ticker,
        "company_name": company_name,
        "financials": financials,
        "news_summary": news_summary,
        "chart_description": chart_description
    }


def main():
    parser = argparse.ArgumentParser(description='Scrape Naver Finance for stock data')
    parser.add_argument('ticker', help='Stock ticker (e.g., 251270)')
    parser.add_argument('--output', help='Output JSON file path', default=None)

    args = parser.parse_args()

    data = scrape_stock(args.ticker)

    output_json = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"Data saved to {args.output}")
    else:
        print(output_json)

    return data


if __name__ == '__main__':
    main()
