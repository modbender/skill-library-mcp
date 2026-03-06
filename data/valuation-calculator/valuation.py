#!/usr/bin/env python3
"""
Valuation Calculator - 快速估值計算機
支持: PEG, EV/EBITDA, Rule of 40, DCF
"""

import sys
import os

# Add workspace to path
sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace'))

try:
    import yfinance as yf
except ImportError:
    print("Error: yfinance not installed. Run: pip install yfinance")
    sys.exit(1)


def get_valuation(ticker):
    """獲取單一股票的估值數據"""
    # Use regular market price for ETFs
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # If price is None, try history
        if not info.get('currentPrice'):
            hist = stock.history(period='2d')
            if not hist.empty:
                info['currentPrice'] = hist['Close'].iloc[-1]
        
        # Basic data
        price = info.get('currentPrice', 0)
        trailing_pe = info.get('trailingPE', 0)
        forward_pe = info.get('forwardPE', 0)
        peg_ratio = info.get('pegRatio', 0)
        
        # EV/EBITDA
        enterprise_value = info.get('enterpriseValue', 0)
        ebitda = info.get('ebitda', 0)
        ev_ebitda = enterprise_value / ebitda if ebitda and ebitda > 0 else 0
        
        # Revenue growth for Rule of 40
        revenue_growth = info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0
        profit_margin = info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0
        rule_of_40 = revenue_growth + profit_margin
        
        # Implied EPS Growth
        implied_growth = 0
        if trailing_pe and forward_pe and forward_pe > 0:
            implied_growth = (trailing_pe / forward_pe - 1) * 100
        
        # Calculate PEG if not provided
        if peg_ratio == 0 or peg_ratio is None:
            if forward_pe and implied_growth > 0:
                peg_ratio = forward_pe / implied_growth
            elif trailing_pe and implied_growth > 0:
                peg_ratio = trailing_pe / implied_growth
        
        return {
            'price': price,
            'trailing_pe': trailing_pe,
            'forward_pe': forward_pe,
            'peg': peg_ratio,
            'implied_growth': implied_growth,
            'ev_ebitda': ev_ebitda,
            'revenue_growth': revenue_growth,
            'profit_margin': profit_margin,
            'rule_of_40': rule_of_40,
            'ticker': ticker
        }
    except Exception as e:
        return {'error': str(e)}


def get_fcf_data(ticker):
    """獲取 DCF 所需的財務數據"""
    try:
        stock = yf.Ticker(ticker)
        
        # Try to get cash flow data
        cf = stock.cashflow
        info = stock.info
        
        # Get Free Cash Flow
        free_cash_flow = 0
        if cf is not None and not cf.empty:
            # Try different FCF metrics
            if 'Free Cash Flow' in cf.index:
                free_cash_flow = cf.loc['Free Cash Flow'].iloc[0]
            elif 'Operating Cash Flow' in cf.index and 'Capital Expenditure' in cf.index:
                operating_cf = cf.loc['Operating Cash Flow'].iloc[0]
                capex = cf.loc['Capital Expenditure'].iloc[0]
                free_cash_flow = operating_cf - capex if capex else operating_cf
        
        # Get shares outstanding
        shares = info.get('sharesOutstanding', 0)
        
        # Get beta for WACC estimation
        beta = info.get('beta', 1.0)
        
        # Get current price
        price = info.get('currentPrice', 0)
        
        return {
            'free_cash_flow': free_cash_flow,
            'shares_outstanding': shares,
            'beta': beta,
            'price': price,
            'enterprise_value': info.get('enterpriseValue', 0)
        }
    except Exception as e:
        return {'error': str(e)}


def get_risk_free_rate():
    """獲取 10 年期公債利率 (無風險利率)"""
    try:
        treasury = yf.Ticker('^TNX')
        info = treasury.info
        # priceHint is the yield in percentage, divide by 100 for decimal
        rf = info.get('regularMarketPrice', 0) / 100 if info.get('regularMarketPrice') else 0.045
        return rf
    except:
        return 0.045  # Default to 4.5% if unavailable


def calculate_wacc_auto(ticker):
    """自動計算 WACC (CAPM 模型)"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get beta
        beta = info.get('beta', 1.0)
        if beta is None or beta <= 0:
            beta = 1.0
        
        # Get risk-free rate (10-year Treasury)
        rf = get_risk_free_rate()
        
        # Market risk premium (historical average ~5.5%)
        market_risk_premium = 0.055
        
        # Cost of Equity (CAPM) = Rf + Beta × (Rm - Rf)
        cost_of_equity = rf + beta * market_risk_premium
        
        # For simplicity, assume WACC ≈ Cost of Equity (for all-equity firm)
        # More complex version would include debt cost
        wacc = cost_of_equity
        
        return {
            'wacc': wacc,
            'beta': beta,
            'risk_free': rf,
            'market_risk_premium': market_risk_premium,
            'cost_of_equity': cost_of_equity
        }
    except Exception as e:
        return {'wacc': 0.10, 'error': str(e)}  # Default to 10%


def calculate_dcf(ticker, wacc=0.10, growth_rate=0.05, terminal_growth=0.025, years=10):
    """計算 DCF 估值"""
    fcf_data = get_fcf_data(ticker)
    
    if 'error' in fcf_data:
        return fcf_data
    
    fcf = fcf_data.get('free_cash_flow', 0)
    shares = fcf_data.get('shares_outstanding', 1)
    price = fcf_data.get('price', 0)
    beta = fcf_data.get('beta', 1.0)
    
    if fcf <= 0 or shares <= 0:
        return {'error': '無法獲取有效的 FCF 或股數'}
    
    # Calculate FCF per share
    fcf_per_share = fcf / shares
    
    # Project FCF
    projected_fcf = []
    for year in range(1, years + 1):
        fcf_val = fcf_per_share * ((1 + growth_rate) ** year)
        discounted = fcf_val / ((1 + wacc) ** year)
        projected_fcf.append({
            'year': year,
            'fcf': fcf_val,
            'discounted': discounted
        })
    
    # Terminal value
    terminal_fcf = fcf_per_share * (1 + growth_rate) ** years * (1 + terminal_growth)
    terminal_value = terminal_value = terminal_fcf / (wacc - terminal_growth) if wacc > terminal_growth else 0
    terminal_discounted = terminal_value / ((1 + wacc) ** years)
    
    # Sum up
    sum_discounted_fcf = sum(p['discounted'] for p in projected_fcf)
    total_dcf = sum_discounted_fcf + terminal_discounted
    
    # Fair value per share
    fair_value = total_dcf
    
    # Current upside/downside
    upside = (fair_value - price) / price * 100 if price > 0 else 0
    
    return {
        'ticker': ticker,
        'price': price,
        'fcf_per_share': fcf_per_share,
        'wacc': wacc,
        'growth_rate': growth_rate,
        'terminal_growth': terminal_growth,
        'years': years,
        'projected_fcf': projected_fcf,
        'terminal_value': terminal_value,
        'terminal_discounted': terminal_discounted,
        'sum_discounted_fcf': sum_discounted_fcf,
        'fair_value': fair_value,
        'upside': upside,
        'beta': beta
    }


def format_dcf(dcf_data):
    """格式化 DCF 輸出"""
    if 'error' in dcf_data:
        return f"Error: {dcf_data['error']}"
    
    d = dcf_data
    upside_emoji = '📈' if d['upside'] > 0 else '📉'
    
    result = f"""
## {d['ticker']} DCF 估值

### 輸入參數
| 參數 | 數值 |
|------|------|
| 股價 | ${d['price']:.2f} |
| 每股 FCF | ${d['fcf_per_share']:.2f} |
| WACC (折現率) | {d['wacc']*100:.1f}% |
| 成長率 | {d['growth_rate']*100:.1f}% |
| 永續成長率 | {d['terminal_growth']*100:.1f}% |
| 預測年數 | {d['years']} 年 |
| Beta | {d['beta']:.2f} |

### 估值結果
| 項目 | 數值 |
|------|------|
| 10年折現FCF總和 | ${d['sum_discounted_fcf']:.2f} |
| 終端價值 | ${d['terminal_value']:.2f} |
| 終端價值 (折現) | ${d['terminal_discounted']:.2f} |
| **公平價值** | **${d['fair_value']:.2f}** |
| {upside_emoji} **漲跌空間** | **{d['upside']:.1f}%** |

### 敏感度分析 (公平價值)
| WACC \\ 成長率 | {d['growth_rate']*100:.0f}% | {d['growth_rate']*100+2:.0f}% | {d['growth_rate']*100+5:.0f}% |
|---------------|---------|---------|---------|
| {d['wacc']*100-1:.0f}% | ${calculate_dcf(d['ticker'], d['wacc']-0.01, d['growth_rate'], d['terminal_growth'])['fair_value']:.2f} | ${calculate_dcf(d['ticker'], d['wacc']-0.01, d['growth_rate']+0.02, d['terminal_growth'])['fair_value']:.2f} | ${calculate_dcf(d['ticker'], d['wacc']-0.01, d['growth_rate']+0.05, d['terminal_growth'])['fair_value']:.2f} |
| {d['wacc']*100:.0f}% | ${d['fair_value']:.2f} | ${calculate_dcf(d['ticker'], d['wacc'], d['growth_rate']+0.02, d['terminal_growth'])['fair_value']:.2f} | ${calculate_dcf(d['ticker'], d['wacc'], d['growth_rate']+0.05, d['terminal_growth'])['fair_value']:.2f} |
| {d['wacc']*100+1:.0f}% | ${calculate_dcf(d['ticker'], d['wacc']+0.01, d['growth_rate'], d['terminal_growth'])['fair_value']:.2f} | ${calculate_dcf(d['ticker'], d['wacc']+0.01, d['growth_rate']+0.02, d['terminal_growth'])['fair_value']:.2f} | ${calculate_dcf(d['ticker'], d['wacc']+0.01, d['growth_rate']+0.05, d['terminal_growth'])['fair_value']:.2f} |

**評估:** {'✅ 被低估' if d['upside'] > 20 else '⚠️ 合理' if d['upside'] > -20 else '❌ 被高估'}
"""
    return result


def format_peg(data):
    """格式化 PEG 輸出"""
    if 'error' in data:
        return f"Error: {data['error']}"
    
    return f"""
## {data['ticker']} 估值數據

| 指標 | 數值 |
|------|------|
| 股價 | ${data['price']:.2f} |
| Forward P/E | {data['forward_pe']:.2f} |
| Trailing P/E | {data['trailing_pe']:.2f} |
| 隱含EPS成長率 | **{data['implied_growth']:.1f}%** |
| PEG Ratio | **{data['peg']:.2f}** |

**評估:** {'🔥 嚴重低估' if data['peg'] < 0.5 else '👍 低估' if data['peg'] < 1 else '⚠️ 高估' if data['peg'] > 1.5 else '✅ 合理'}
"""


def format_full(data):
    """格式化完整估值輸出"""
    if 'error' in data:
        return f"Error: {data['error']}"
    
    peg_status = '🔥 嚴重低估' if data['peg'] < 0.5 else '👍 低估' if data['peg'] < 1 else '⚠️ 高估' if data['peg'] > 1.5 else '✅ 合理'
    
    return f"""
## {data['ticker']} 完整估值

| 指標 | 數值 | 備註 |
|------|------|------|
| 股價 | ${data['price']:.2f} | |
| Forward P/E | {data['forward_pe']:.2f} | 基於未來12個月預期 |
| Trailing P/E | {data['trailing_pe']:.2f} | 基於過去12個月 |
| 隱含EPS成長 | **{data['implied_growth']:.1f}%** | Trailing ÷ Forward - 1 |
| PEG Ratio | **{data['peg']:.2f}** | {peg_status} |
| EV/EBITDA | {data['ev_ebitda']:.2f} | 企業價值÷EBITDA |
| Rule of 40 | {data['rule_of_40']:.1f}% | 營收成長+毛利率 |
| 營收成長 | {data['revenue_growth']:.1f}% | YoY |
| 毛利率 | {data['profit_margin']:.1f}% | |
"""


def format_holdings(holdings, data_dict):
    """格式化持股估值儀表板"""
    lines = ["| Ticker | 股價 | Forward P/E | Trailing P/E | 隱含成長% | PEG | 評估 |"]
    lines.append("|--------|------|-------------|-------------|----------|-----|------|")
    
    for ticker, shares in holdings.items():
        if ticker in data_dict:
            d = data_dict[ticker]
            peg_status = '🔥' if d['peg'] < 0.5 else '👍' if d['peg'] < 1 else '⚠️' if d['peg'] > 1.5 else '✅'
            lines.append(f"| {ticker} | ${d['price']:.2f} | {d['forward_pe']:.1f} | {d['trailing_pe']:.1f} | {d['implied_growth']:.0f}% | {d['peg']:.2f} | {peg_status} |")
    
    return "\n".join(lines)


def parse_holdings():
    """讀取持股清單"""
    holdings_path = os.path.expanduser('~/.openclaw/workspace/holdings.md')
    holdings = {}
    
    if not os.path.exists(holdings_path):
        return None
    
    with open(holdings_path, 'r') as f:
        for line in f:
            if line.strip().startswith('|') and 'Ticker' not in line and '---' not in line:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 3:
                    ticker = parts[1].upper()
                    if ticker and ticker not in ['Ticker', '']:
                        try:
                            shares = int(parts[2]) if parts[2].isdigit() else 0
                            holdings[ticker] = shares
                        except:
                            pass
    return holdings


def main():
    args = sys.argv[1:]
    
    if not args:
        print("用法:")
        print("  value <ticker>                    - 單一股票所有估值")
        print("  value peg <ticker>                - 僅 PEG")
        print("  value ev <ticker>                 - 僅 EV/EBITDA + Rule of 40")
        print("  value dcf <ticker>               - DCF 估值 (預設參數)")
        print("  value dcf <ticker> --auto        - DCF 估值 (自動計算 WACC)")
        print("  value dcf <ticker> --wacc=0.10   - 自訂 WACC")
        print("  value dcf <ticker> --growth=0.15 - 自訂成長率")
        print("  value                             - 所有持股估值")
        print("  value --index                     - 三大指數 (SPY, QQQ, DIA)")
        return
    
    command = args[0].lower()
    
    # Handle index
    if '--index' in args:
        tickers = ['SPY', 'QQQ', 'DIA']
        data_dict = {}
        for t in tickers:
            data_dict[t] = get_valuation(t)
        
        print("\n## 三大指數估值")
        print("| Index | 股價 | Forward P/E | Trailing P/E | PEG |")
        print("|-------|------|-------------|-------------|-----|")
        for t in tickers:
            d = data_dict[t]
            print(f"| {t} | ${d['price']:.2f} | {d['forward_pe']:.1f} | {d['trailing_pe']:.1f} | {d['peg']:.2f} |")
        return
    
    # Handle all holdings
    if command == 'value' and len(args) == 1:
        holdings = parse_holdings()
        if not holdings:
            print("❌ 無持股清單。請先建立 ~/.openclaw/workspace/holdings.md")
            return
        
        print(f"\n## George 持股估值儀表板 ({len(holdings)} 檔)\n")
        data_dict = {}
        for ticker in holdings:
            data_dict[ticker] = get_valuation(ticker)
        
        print(format_holdings(holdings, data_dict))
        return
    
    # Handle subcommands (peg, ev, dcf)
    subcommands = ['peg', 'ev', 'dcf']
    
    if len(args) >= 2 and args[1].lower() in subcommands:
        # value peg <ticker>, value ev <ticker>, value dcf <ticker>
        subcmd = args[1].lower()
        if len(args) >= 3:
            ticker = args[2].upper()
            data = get_valuation(ticker)
            data['ticker'] = ticker
            
            if subcmd == 'peg':
                print(format_peg(data))
            elif subcmd == 'ev':
                print(f"""
## {ticker} EV/EBITDA & Rule of 40

| 指標 | 數值 |
|------|------|
| 股價 | ${data['price']:.2f} |
| EV/EBITDA | **{data['ev_ebitda']:.2f}** |
| Rule of 40 | **{data['rule_of_40']:.1f}%** |
| 營收成長 (YoY) | {data['revenue_growth']:.1f}% |
| 毛利率 | {data['profit_margin']:.1f}% |

**Rule of 40:** {'✅ 達標' if data['rule_of_40'] >= 40 else '⚠️ 未達標'}
""")
            elif subcmd == 'dcf':
                # Parse custom parameters
                wacc = 0.10  # Default 10%
                growth = 0.05  # Default 5%
                terminal = 0.025  # Default 2.5%
                auto_wacc = False
                
                for arg in args[3:]:
                    if arg == '--auto':
                        auto_wacc = True
                    elif arg.startswith('--wacc='):
                        try:
                            wacc = float(arg.split('=')[1])
                        except:
                            pass
                    elif arg.startswith('--growth='):
                        try:
                            growth = float(arg.split('=')[1])
                        except:
                            pass
                    elif arg.startswith('--terminal='):
                        try:
                            terminal = float(arg.split('=')[1])
                        except:
                            pass
                
                # Auto WACC calculation
                if auto_wacc:
                    wacc_data = calculate_wacc_auto(ticker)
                    wacc = wacc_data.get('wacc', 0.10)
                    print(f"### ⚡ 自動 WACC")
                    print(f"| 參數 | 數值 |")
                    print(f"|------|------|")
                    print(f"| Beta | {wacc_data.get('beta', 'N/A')} |")
                    print(f"| 無風險利率 | {wacc_data.get('risk_free', 0)*100:.2f}% |")
                    print(f"| 市場風險溢價 | {wacc_data.get('market_risk_premium', 0)*100:.1f}% |")
                    print(f"| **計算 WACC** | **{wacc*100:.2f}%** |")
                    print()
                
                dcf_result = calculate_dcf(ticker, wacc=wacc, growth_rate=growth, terminal_growth=terminal)
                print(format_dcf(dcf_result))
        else:
            print("Error: 請指定股票代碼")
        return
    
    # Handle value <ticker>
    if command == 'value' and len(args) >= 2:
        ticker = args[1].upper()
        data = get_valuation(ticker)
        data['ticker'] = ticker
        print(format_full(data))
    else:
        # Assume it's a ticker (backward compatibility)
        ticker = args[0].upper()
        data = get_valuation(ticker)
        data['ticker'] = ticker
        print(format_full(data))


if __name__ == '__main__':
    main()
