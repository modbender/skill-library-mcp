#!/usr/bin/env python3
"""
Finnhub CLI - 全功能金融数据工具
用法: finnhub <command> [args] [--json]

免费层支持的命令:
  quote <symbol>                     实时报价
  profile <symbol>                   公司档案/基本信息
  news <symbol> [from] [to]          公司新闻
  recommend <symbol>                 分析师推荐趋势
  insiders <symbol> [from] [to]      内部人交易记录
  earnings [symbol] [from] [to]      盈利日历
  financials <symbol> [metric]       基本面财务指标
  market <exchange>                  市场状态 (US/NYSE/NASDAQ等)
  peers <symbol>                     同行公司
  search <query>                     股票代码搜索
"""

import sys
import os
import json
import argparse
from datetime import datetime, timedelta

try:
    import finnhub
except ImportError:
    print("❌ 需要安装 finnhub-python: pip install finnhub-python", file=sys.stderr)
    sys.exit(1)

API_KEY = os.environ.get("FINNHUB_API_KEY", "YOUR_FINNHUB_API_KEY")
client = finnhub.Client(api_key=API_KEY)


def fmt_num(n, decimals=2):
    """格式化数字"""
    if n is None:
        return "N/A"
    try:
        return f"{float(n):,.{decimals}f}"
    except:
        return str(n)


def fmt_ts(ts):
    """时间戳转可读时间"""
    if not ts:
        return "N/A"
    try:
        return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
    except:
        return str(ts)


def cmd_quote(symbol, as_json=False):
    """实时报价"""
    q = client.quote(symbol.upper())
    if as_json:
        print(json.dumps(q, indent=2, ensure_ascii=False))
        return
    
    symbol = symbol.upper()
    c = q.get('c', 0)
    d = q.get('d', 0)
    dp = q.get('dp', 0)
    sign = "▲" if d >= 0 else "▼"
    color_start = "\033[32m" if d >= 0 else "\033[31m"
    color_end = "\033[0m"
    
    print(f"\n{'='*45}")
    print(f"  📈 {symbol} 实时报价")
    print(f"{'='*45}")
    print(f"  当前价:  {color_start}{fmt_num(c)} {sign} {fmt_num(d)} ({fmt_num(dp)}%){color_end}")
    print(f"  今开盘:  {fmt_num(q.get('o'))}")
    print(f"  今高/低: {fmt_num(q.get('h'))} / {fmt_num(q.get('l'))}")
    print(f"  昨收盘:  {fmt_num(q.get('pc'))}")
    print(f"  更新时间: {fmt_ts(q.get('t'))}")
    print(f"{'='*45}\n")


def cmd_profile(symbol, as_json=False):
    """公司档案"""
    p = client.company_profile2(symbol=symbol.upper())
    if as_json:
        print(json.dumps(p, indent=2, ensure_ascii=False))
        return
    
    print(f"\n{'='*50}")
    print(f"  🏢 {p.get('name', symbol)} ({symbol.upper()})")
    print(f"{'='*50}")
    print(f"  行业:    {p.get('finnhubIndustry', 'N/A')}")
    print(f"  交易所:  {p.get('exchange', 'N/A')}")
    print(f"  国家:    {p.get('country', 'N/A')}")
    print(f"  货币:    {p.get('currency', 'N/A')}")
    mc = p.get('marketCapitalization')
    if mc:
        print(f"  市值:    ${fmt_num(mc)}M")
    shares = p.get('shareOutstanding')
    if shares:
        print(f"  流通股:  {fmt_num(shares)}M 股")
    ipo = p.get('ipo')
    if ipo:
        print(f"  IPO日期: {ipo}")
    logo = p.get('logo')
    if logo:
        print(f"  Logo:    {logo}")
    website = p.get('weburl')
    if website:
        print(f"  网站:    {website}")
    print(f"{'='*50}\n")


def cmd_news(symbol, from_date=None, to_date=None, limit=10, as_json=False):
    """公司新闻"""
    if not to_date:
        to_date = datetime.now().strftime("%Y-%m-%d")
    if not from_date:
        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    news = client.company_news(symbol.upper(), _from=from_date, to=to_date)
    
    if as_json:
        print(json.dumps(news[:limit], indent=2, ensure_ascii=False))
        return
    
    print(f"\n📰 {symbol.upper()} 新闻 ({from_date} ~ {to_date}) - 共 {len(news)} 条")
    print(f"{'='*60}")
    
    for item in news[:limit]:
        ts = fmt_ts(item.get('datetime'))
        headline = item.get('headline', '')[:80]
        source = item.get('source', '')
        url = item.get('url', '')
        
        print(f"\n  [{ts}] {source}")
        print(f"  {headline}")
        if url:
            print(f"  🔗 {url}")
    
    print(f"\n{'='*60}")
    if len(news) > limit:
        print(f"  ⚡ 共 {len(news)} 条，显示最新 {limit} 条\n")


def cmd_recommend(symbol, as_json=False):
    """分析师推荐趋势"""
    rec = client.recommendation_trends(symbol.upper())
    
    if as_json:
        print(json.dumps(rec, indent=2, ensure_ascii=False))
        return
    
    print(f"\n📊 {symbol.upper()} 分析师推荐趋势")
    print(f"{'='*55}")
    print(f"  {'月份':<12} {'强买':>6} {'买入':>6} {'持有':>6} {'卖出':>6} {'强卖':>6}")
    print(f"  {'-'*50}")
    
    for r in rec[:6]:  # 显示最近6个月
        period = r.get('period', '')[:7]
        sb = r.get('strongBuy', 0)
        b = r.get('buy', 0)
        h = r.get('hold', 0)
        s = r.get('sell', 0)
        ss = r.get('strongSell', 0)
        total = sb + b + h + s + ss
        
        # 计算综合评分 (1=强卖, 5=强买)
        if total > 0:
            score = (sb*5 + b*4 + h*3 + s*2 + ss*1) / total
            score_str = f"⭐{score:.1f}"
        else:
            score_str = "N/A"
        
        print(f"  {period:<12} {sb:>6} {b:>6} {h:>6} {s:>6} {ss:>6}  {score_str}")
    
    print(f"{'='*55}\n")


def cmd_insiders(symbol, from_date=None, to_date=None, limit=20, as_json=False):
    """内部人交易记录"""
    if not to_date:
        to_date = datetime.now().strftime("%Y-%m-%d")
    if not from_date:
        from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    
    data = client.stock_insider_transactions(symbol.upper(), from_date, to_date)
    transactions = data.get('data', [])
    
    if as_json:
        print(json.dumps(transactions[:limit], indent=2, ensure_ascii=False))
        return
    
    print(f"\n👔 {symbol.upper()} 内部人交易 ({from_date} ~ {to_date})")
    print(f"{'='*70}")
    
    if not transactions:
        print("  暂无内部人交易记录\n")
        return
    
    print(f"  {'日期':<12} {'姓名':<20} {'职位':<10} {'类型':<6} {'价格':>8} {'数量':>10} {'价值':>12}")
    print(f"  {'-'*68}")
    
    buys = sells = 0
    for t in transactions[:limit]:
        date = t.get('transactionDate', '')
        name = (t.get('name', '') or '')[:18]
        title = (t.get('officerTitle', '') or 'N/A')[:8]
        tx_type = t.get('transactionCode', '')
        price = t.get('transactionPrice', 0) or 0
        shares = t.get('share', 0) or 0
        value = price * shares
        
        # P=买入, S=卖出
        if tx_type in ['P', 'A']:
            type_str = "\033[32m买入\033[0m"
            buys += 1
        elif tx_type in ['S', 'D']:
            type_str = "\033[31m卖出\033[0m"
            sells += 1
        else:
            type_str = tx_type
        
        print(f"  {date:<12} {name:<20} {title:<10} {type_str:<6} {fmt_num(price):>8} {fmt_num(shares,0):>10} ${fmt_num(value,0):>11}")
    
    print(f"\n  📈 买入: {buys} 笔  📉 卖出: {sells} 笔  共 {len(transactions)} 笔")
    print(f"{'='*70}\n")


def cmd_earnings(symbol="", from_date=None, to_date=None, limit=20, as_json=False):
    """盈利日历"""
    if not to_date:
        to_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    if not from_date:
        from_date = datetime.now().strftime("%Y-%m-%d")
    
    data = client.earnings_calendar(_from=from_date, to=to_date, symbol=symbol, international=False)
    calendar = data.get('earningsCalendar', [])
    
    if as_json:
        print(json.dumps(calendar[:limit], indent=2, ensure_ascii=False))
        return
    
    title = f"📅 盈利日历 {from_date} ~ {to_date}"
    if symbol:
        title += f" [{symbol.upper()}]"
    print(f"\n{title}")
    print(f"{'='*60}")
    print(f"  {'日期':<12} {'代号':<8} {'公司':<25} {'时间':<8} {'EPS预期':>8}")
    print(f"  {'-'*58}")
    
    for item in calendar[:limit]:
        date = item.get('date', '')
        sym = item.get('symbol', '')
        company = (item.get('name', '') or '')[:22]
        hour = item.get('hour', '')  # bmo=开盘前, amc=收盘后
        hour_str = {"bmo": "盘前", "amc": "盘后"}.get(hour, hour or "N/A")
        eps_est = item.get('epsEstimate')
        eps_str = fmt_num(eps_est) if eps_est is not None else "N/A"
        
        print(f"  {date:<12} {sym:<8} {company:<25} {hour_str:<8} {eps_str:>8}")
    
    if len(calendar) > limit:
        print(f"\n  ⚡ 共 {len(calendar)} 条，显��� {limit} 条")
    print(f"{'='*60}\n")


def cmd_financials(symbol, metric="all", as_json=False):
    """基本面财务指标"""
    data = client.company_basic_financials(symbol.upper(), metric)
    
    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    
    metrics = data.get('metric', {})
    
    print(f"\n💰 {symbol.upper()} 关键财务指标")
    print(f"{'='*45}")
    
    # Key metrics summary
    key_fields = [
        ("52周最高", "52WeekHigh"),
        ("52周最低", "52WeekLow"),
        ("市盈率(TTM)", "peBasicExclExtraTTM"),
        ("市净率", "pbAnnual"),
        ("市销率(TTM)", "psTTM"),
        ("EV/EBITDA", "evToEbitda"),
        ("毛利率(TTM)%", "grossMarginTTM"),
        ("净利率(TTM)%", "netMarginTTM"),
        ("ROE(TTM)%", "roeTTM"),
        ("ROA(TTM)%", "roaTTM"),
        ("股息率%", "dividendYieldIndicatedAnnual"),
        ("Beta", "beta"),
        ("流动比率", "currentRatioAnnual"),
        ("资产负债率", "totalDebt/totalEquityAnnual"),
    ]
    
    for label, key in key_fields:
        val = metrics.get(key)
        if val is not None:
            print(f"  {label:<18}: {fmt_num(val)}")
    
    print(f"{'='*45}")
    print(f"  提示: 用 --json 查看全部 {len(metrics)} 个指标\n")


def cmd_market(exchange="US", as_json=False):
    """市场状态"""
    data = client.market_status(exchange=exchange)
    
    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    
    is_open = data.get('isOpen', False)
    status = "\033[32m🟢 开盘中\033[0m" if is_open else "\033[31m🔴 休市\033[0m"
    
    print(f"\n🌐 {exchange} 市场状态")
    print(f"{'='*35}")
    print(f"  状态:     {status}")
    print(f"  时区:     {data.get('timezone', 'N/A')}")
    holiday = data.get('holiday')
    if holiday:
        print(f"  节假日:   {holiday}")
    session = data.get('session')
    if session:
        print(f"  交易时段: {session}")
    print(f"  更新时间: {fmt_ts(data.get('t'))}")
    print(f"{'='*35}\n")


def cmd_peers(symbol, as_json=False):
    """同行公司"""
    peers = client.company_peers(symbol.upper())
    
    if as_json:
        print(json.dumps(peers, indent=2, ensure_ascii=False))
        return
    
    print(f"\n🏭 {symbol.upper()} 同行公司")
    print(f"{'='*35}")
    for p in peers:
        print(f"  • {p}")
    print(f"{'='*35}\n")


def cmd_search(query, limit=10, as_json=False):
    """搜��股票代码"""
    results = client.symbol_lookup(query)
    count = results.get('count', 0)
    items = results.get('result', [])
    
    if as_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return
    
    print(f"\n🔍 搜索 '{query}' - 找到 {count} 个结果")
    print(f"{'='*55}")
    print(f"  {'代号':<12} {'类型':<8} {'公司名称'}")
    print(f"  {'-'*52}")
    
    for item in items[:limit]:
        sym = item.get('symbol', '')
        type_ = item.get('type', '')
        desc = item.get('description', '')[:35]
        print(f"  {sym:<12} {type_:<8} {desc}")
    
    print(f"{'='*55}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Finnhub 金融数据 CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("command", help="命令")
    parser.add_argument("args", nargs="*", help="命令参数")
    parser.add_argument("--json", action="store_true", help="输出原始 JSON")
    parser.add_argument("--limit", type=int, default=20, help="最大显示条数")
    parser.add_argument("--from", dest="from_date", help="开始日期 YYYY-MM-DD")
    parser.add_argument("--to", dest="to_date", help="结束日期 YYYY-MM-DD")
    
    args = parser.parse_args()
    cmd = args.command.lower()
    params = args.args
    
    try:
        if cmd == "quote" and params:
            cmd_quote(params[0], as_json=args.json)
        
        elif cmd == "profile" and params:
            cmd_profile(params[0], as_json=args.json)
        
        elif cmd == "news" and params:
            from_d = args.from_date or (params[1] if len(params) > 1 else None)
            to_d = args.to_date or (params[2] if len(params) > 2 else None)
            cmd_news(params[0], from_d, to_d, args.limit, as_json=args.json)
        
        elif cmd == "recommend" and params:
            cmd_recommend(params[0], as_json=args.json)
        
        elif cmd == "insiders" and params:
            from_d = args.from_date or (params[1] if len(params) > 1 else None)
            to_d = args.to_date or (params[2] if len(params) > 2 else None)
            cmd_insiders(params[0], from_d, to_d, args.limit, as_json=args.json)
        
        elif cmd == "earnings":
            sym = params[0] if params else ""
            from_d = args.from_date or (params[1] if len(params) > 1 else None)
            to_d = args.to_date or (params[2] if len(params) > 2 else None)
            cmd_earnings(sym, from_d, to_d, args.limit, as_json=args.json)
        
        elif cmd == "financials" and params:
            metric = params[1] if len(params) > 1 else "all"
            cmd_financials(params[0], metric, as_json=args.json)
        
        elif cmd == "market":
            exchange = params[0] if params else "US"
            cmd_market(exchange, as_json=args.json)
        
        elif cmd == "peers" and params:
            cmd_peers(params[0], as_json=args.json)
        
        elif cmd == "search" and params:
            cmd_search(" ".join(params), args.limit, as_json=args.json)
        
        else:
            print(__doc__)
            sys.exit(1)
    
    except Exception as e:
        err_str = str(e)
        if "403" in err_str:
            print(f"❌ 此功能需要付费订阅: {err_str}", file=sys.stderr)
        elif "429" in err_str:
            print(f"❌ 请求频率超限（免费层60次/分钟）", file=sys.stderr)
        else:
            print(f"❌ 错误: {err_str}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
