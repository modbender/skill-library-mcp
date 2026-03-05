#!/usr/bin/env python3
"""
FireAnt Stock Checker - Automated Vietnamese stock price lookup using Agent Browser
Usage: python3 check_stock.py <SYMBOL1> [SYMBOL2] ...
Example: python3 check_stock.py DPM VCB FPT
"""

import sys
import re
import subprocess
import json
from typing import List, Dict, Optional

def run_agent_browser(args: List[str]) -> str:
    """Run agent-browser command and return output"""
    try:
        result = subprocess.run(
            ['/Users/loc/Library/pnpm/agent-browser'] + args,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""
    except Exception as e:
        print(f"Error running agent-browser: {e}")
        return ""

def extract_stock_data(symbol: str) -> Dict:
    """Extract stock data from FireAnt page using agent-browser"""
    
    stock_data = {'symbol': symbol}
    
    try:
        # Open FireAnt stock page
        url = f"https://fireant.vn/ma-chung-khoan/{symbol}"
        print(f"Opening {url}...")
        run_agent_browser(['open', url])
        
        # Wait for page to load
        run_agent_browser(['wait', '--load', 'networkidle'])
        
        # Close any popup dialogs if present
        run_agent_browser(['dialog', 'dismiss'])
        
        # Get page snapshot
        snapshot = run_agent_browser(['snapshot'])
        
        if not snapshot:
            return {"error": "Failed to get page snapshot"}
        
        # Extract company name
        company_match = re.search(r'(Ngân hàng|Tổng Công ty|Công ty)\s+([^\n]+)', snapshot)
        if company_match:
            stock_data['company_name'] = (company_match.group(1) + ' ' + company_match.group(2)).strip()
        
        # Extract current price (large display price)
        price_match = re.search(r'"([0-9]+\.[0-9]{2})"', snapshot)
        if price_match:
            stock_data['current_price'] = price_match.group(1)
        
        # Extract price change
        change_match = re.search(r'([0-9.]+)\s*/\s*([0-9.]+)%', snapshot)
        if change_match:
            stock_data['change_amount'] = change_match.group(1)
            stock_data['change_percent'] = change_match.group(2)
        
        # Extract reference price
        ref_match = re.search(r'Tham chiếu["\s]+([0-9.]+)', snapshot)
        if ref_match:
            stock_data['reference_price'] = ref_match.group(1)
        
        # Extract open price
        open_match = re.search(r'Mở cửa["\s]+([0-9.]+)', snapshot)
        if open_match:
            stock_data['open_price'] = open_match.group(1)
        
        # Extract high-low range
        range_match = re.search(r'Thấp - Cao["\s]+([0-9.]+)\s*-\s*([0-9.]+)', snapshot)
        if range_match:
            stock_data['low'] = range_match.group(1)
            stock_data['high'] = range_match.group(2)
        
        # Extract volume
        vol_match = re.search(r'Khối lượng["\s]+([0-9,]+)', snapshot)
        if vol_match:
            stock_data['volume'] = vol_match.group(1)
        
        # Extract value
        val_match = re.search(r'Giá trị["\s]+([0-9.,]+\s*tỷ)', snapshot)
        if val_match:
            stock_data['value'] = val_match.group(1).strip()
        
        # Extract market cap
        cap_match = re.search(r'Thị giá vốn["\s]+([0-9.,]+\s*tỷ)', snapshot)
        if cap_match:
            stock_data['market_cap'] = cap_match.group(1).strip()
        
        # Extract P/E
        pe_match = re.search(r'P/E["\s]+([0-9.]+)', snapshot)
        if pe_match:
            stock_data['pe'] = pe_match.group(1)
        
        # Extract EPS
        eps_match = re.search(r'EPS["\s]+([0-9,]+)', snapshot)
        if eps_match:
            stock_data['eps'] = eps_match.group(1)
        
        # Extract Beta
        beta_match = re.search(r'Beta["\s]+([0-9.]+)', snapshot)
        if beta_match:
            stock_data['beta'] = beta_match.group(1)
        
        return stock_data
        
    except Exception as e:
        return {"error": f"Failed to extract data: {str(e)}"}

def format_stock_output(symbol: str, data: Dict) -> str:
    """Format stock data for readable output"""
    
    if 'error' in data:
        return f"❌ {symbol}: {data['error']}"
    
    if not data or len(data) <= 1:  # Only symbol
        return f"❌ {symbol}: No data found"
    
    output = [f"📊 **{symbol.upper()}**"]
    
    if 'company_name' in data:
        output.append(f"🏢 {data['company_name']}")
    
    if 'current_price' in data:
        price = data['current_price']
        change = data.get('change_amount', '')
        percent = data.get('change_percent', '')
        
        if change and percent:
            try:
                direction = "⬆️" if float(percent) >= 0 else "⬇️"
                output.append(f"💰 Price: **{price}** VND {direction} {change} ({percent}%)")
            except:
                output.append(f"💰 Price: **{price}** VND")
        else:
            output.append(f"💰 Price: **{price}** VND")
    
    if 'reference_price' in data:
        output.append(f"📍 Reference: {data['reference_price']} VND")
    
    if 'open_price' in data:
        output.append(f"🔓 Open: {data['open_price']} VND")
    
    if 'low' in data and 'high' in data:
        output.append(f"📉📈 Range: {data['low']} - {data['high']} VND")
    
    if 'volume' in data:
        output.append(f"📊 Volume: {data['volume']}")
    
    if 'value' in data:
        output.append(f"💵 Value: {data['value']}")
    
    if 'market_cap' in data:
        output.append(f"🏦 Market Cap: {data['market_cap']}")
    
    if 'pe' in data:
        output.append(f"📈 P/E: {data['pe']}")
    
    if 'eps' in data:
        output.append(f"💹 EPS: {data['eps']}")
    
    if 'beta' in data:
        output.append(f"📊 Beta: {data['beta']}")
    
    return "\n".join(output)

def check_stocks(symbols: List[str]) -> str:
    """Main function to check multiple stocks using agent-browser"""
    
    if not symbols:
        return "❌ No stock symbols provided"
    
    results = []
    
    for symbol in symbols:
        print(f"🔍 Checking {symbol.upper()}...")
        
        # Extract stock data
        data = extract_stock_data(symbol.upper())
        
        # Format output
        formatted = format_stock_output(symbol.upper(), data)
        results.append(formatted)
    
    # Close browser
    run_agent_browser(['close'])
    
    return "\n\n".join(results)

def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        print("Usage: python3 check_stock.py <SYMBOL1> [SYMBOL2] ...")
        print("Example: python3 check_stock.py DPM VCB FPT")
        sys.exit(1)
    
    symbols = [arg.upper() for arg in sys.argv[1:]]
    
    print(f"🚀 Checking {len(symbols)} stock(s): {', '.join(symbols)}")
    print("=" * 50)
    
    results = check_stocks(symbols)
    print(results)

if __name__ == "__main__":
    main()
