#!/usr/bin/env python3
"""
Generate visually appealing HTML reports for LLM cost monitoring - Vertical Stacked PPT Style V5 (Fixed Logic)
"""
import argparse
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from store import UsageStore


def generate_html_report(
    store: UsageStore,
    start_date: str = None,
    end_date: str = None,
    title: str = "AI 消耗"
) -> str:
    """Generate a horizontal PPT-style HTML report with improved Top-N logic and detailed labels"""
    
    today_dt = datetime.now()
    if not start_date:
        # Default start to the beginning of the week or month
        start_date = today_dt.replace(day=1).strftime("%Y-%m-%d")
    if not end_date:
        end_date = today_dt.strftime("%Y-%m-%d")
    
    # Trend ranges (Fixed 30 days)
    last_30_dates = [(today_dt - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(29, -1, -1)]
    trend_start_date = last_30_dates[0]
    
    # Comparison range (Previous period of same length)
    requested_start = datetime.strptime(start_date, "%Y-%m-%d")
    requested_end = datetime.strptime(end_date, "%Y-%m-%d")
    period_days = (requested_end - requested_start).days + 1
    prev_start_date = (requested_start - timedelta(days=period_days)).strftime("%Y-%m-%d")
    prev_end_date = (requested_start - timedelta(days=1)).strftime("%Y-%m-%d")

    # Fetch data
    all_data = store.get_usage(min(trend_start_date, prev_start_date), end_date)
    
    daily_total = {}
    daily_models = {}
    period_model_tokens = {}
    period_model_cost = {}
    total_savings = 0
    prev_period_cost = 0
    trend_model_tokens = {} # For selecting Top N models over 30 days

    for record in all_data:
        date = record['date']
        model = record['model']
        
        # Daily aggregations for trends
        if date not in daily_total: daily_total[date] = {'cost': 0, 'tokens': 0}
        daily_total[date]['cost'] += record['cost']
        daily_total[date]['tokens'] += record['input_tokens'] + record['output_tokens']
        
        if date not in daily_models: daily_models[date] = {}
        if model not in daily_models[date]: daily_models[date][model] = {'cost': 0, 'tokens': 0}
        daily_models[date][model]['cost'] += record['cost']
        daily_models[date][model]['tokens'] += record['input_tokens'] + record['output_tokens']
        
        # Requested period stats
        if start_date <= date <= end_date:
            period_model_tokens[model] = period_model_tokens.get(model, 0) + record['input_tokens'] + record['output_tokens']
            period_model_cost[model] = period_model_cost.get(model, 0) + record['cost']
            total_savings += record.get('savings', 0)
            
        # 30-day Trend period stats (for picking Top models to show as lines)
        if trend_start_date <= date <= end_date:
            trend_model_tokens[model] = trend_model_tokens.get(model, 0) + record['input_tokens'] + record['output_tokens']
            
        # Previous period stats
        if prev_start_date <= date <= prev_end_date:
            prev_period_cost += record['cost']

    total_cost = sum(period_model_cost.values())
    total_tokens = sum(period_model_tokens.values())
    days_count = len(set(r['date'] for r in all_data if start_date <= r['date'] <= end_date)) or 1
    
    # Increase to Top 5 for Trend lines
    top_trend_models = sorted(trend_model_tokens.keys(), key=lambda x: -trend_model_tokens[x])[:5]
    colors = ["#10b981", "#3b82f6", "#f59e0b", "#a855f7", "#ec4899", "#06b6d4"]

    def fmt_tokens(t):
        if t >= 1000000: return f"{t/1000000:.1f}M"
        if t >= 1000: return f"{t/1000:.1f}K"
        return str(int(t))
    def fmt_cost(c): return f"${c:.2f}"

    def get_trend_svg(dates, key, width=580, height=140):
        max_val = max([daily_total.get(d, {}).get(key, 0) for d in dates] or [1]) or 1
        svg = f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="overflow:visible;display:block">'
        svg += f'<defs><linearGradient id="g-{key}" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" style="stop-color:{colors[0]};stop-opacity:0.2"/><stop offset="100%" style="stop-color:{colors[0]};stop-opacity:0"/></linearGradient></defs>'
        pts = [f"{(i/(len(dates)-1))*width:.1f},{height-(daily_total.get(d,{}).get(key,0)/max_val*height):.1f}" for i, d in enumerate(dates)]
        path = "L".join(pts)
        svg += f'<path d="M{path} L{width},{height} L0,{height} Z" fill="url(#g-{key})" /><path d="M{path}" fill="none" stroke="{colors[0]}" stroke-width="3" />'
        for idx, m in enumerate(top_trend_models):
            m_pts = [f"{(i/(len(dates)-1))*width:.1f},{height-(daily_models.get(d,{}).get(m,{}).get(key,0)/max_val*height):.1f}" for i, d in enumerate(dates)]
            svg += f'<path d="M{"L".join(m_pts)}" fill="none" stroke="{colors[(idx+1)%len(colors)]}" stroke-width="1.2" stroke-dasharray="3,2" opacity="0.7" />'
        return svg + '</svg>'

    last_7_dates = [(today_dt - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
    avg_unit_cost = (total_cost / total_tokens * 1000000) if total_tokens > 0 else 0
    daily_avg_cost = (total_cost / days_count) if days_count > 0 else 0
    
    growth_html = ""
    if prev_period_cost > 0:
        growth_pct_val = ((total_cost - prev_period_cost) / prev_period_cost * 100)
        # Use high-contrast colors for visibility on gradient background
        # White text on translucent dark background for maximum readability
        color = "#ff4d4f" if growth_pct_val > 0 else "#b7eb8f"
        symbol = "↑" if growth_pct_val > 0 else "↓"
        growth_html = f'<span style="background:rgba(0,0,0,0.25);color:{color};padding:2px 10px;border-radius:100px;font-size:14px;margin-left:12px;font-weight:700;display:inline-flex;align-items:center">{symbol}{abs(growth_pct_val):.1f}%</span>'

    def clean_m(m):
        for k in ['MiniMax', 'Claude', 'Gemini', 'GPT']:
            if k.lower() in m.lower(): return k
        return (m[:10]+'..') if len(m)>10 else m

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>{title}</title></head>
<body style="margin:0;padding:0;font-family:-apple-system,sans-serif;background:#0d0d0d;color:#fff">
    <div style="width:1100px;margin:0 auto;padding:40px;display:flex;gap:24px;align-items:stretch">
        
        <!-- Left Column -->
        <div style="width:380px;display:flex;flex-direction:column;gap:20px">
            <div style="background:linear-gradient(135deg,#059669,#10b981);border-radius:24px;padding:32px;box-shadow:0 10px 15px rgba(0,0,0,0.3)">
                <div style="font-size:16px;opacity:0.9;margin-bottom:8px">Usage Summary</div>
                <div style="font-size:56px;font-weight:800;line-height:1">{fmt_tokens(total_tokens)} <span style="font-size:20px;opacity:0.8;font-weight:600">Tokens</span></div>
                <div style="display:flex;align-items:baseline;margin-top:12px">
                    <span style="font-size:28px;font-weight:700">{fmt_cost(total_cost)}</span>{growth_html}
                </div>
                {f'<div style="margin-top:16px;font-size:14px;font-weight:600;color:#f0fdf4;display:flex;align-items:center"><span style="background:rgba(255,255,255,0.2);width:18px;height:18px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;margin-right:8px;font-size:10px">⚡</span>Saved {fmt_cost(total_savings)}</div>' if total_savings > 0 else ""}
            </div>

            <div style="background:#1a1a1a;border-radius:24px;padding:28px;border:1px solid #2a2a2a;flex-grow:1;display:flex;flex-direction:column">
                <div style="font-size:16px;font-weight:700;margin-bottom:20px;color:#10b981">Model Efficiency (Period)</div>
                <div style="flex-grow:1">
                """
    
    # Efficiency list: models used in CURRENT PERIOD
    sorted_period_models = sorted(period_model_tokens.keys(), key=lambda x: -period_model_tokens[x])
    for m in sorted_period_models[:6]:
        tokens = period_model_tokens[m]
        cost = period_model_cost[m]
        pct = (tokens / total_tokens * 100) if total_tokens > 0 else 0
        u_cost = (cost / tokens * 1000000) if tokens > 0 else 0
        html += f"""<div style="margin-bottom:24px">
                <div style="display:flex;justify-content:space-between;margin-bottom:8px;font-size:13px"><span style="color:#10b981;font-weight:600">{m[:18]}</span><span>{fmt_tokens(tokens)}</span></div>
                <div style="height:6px;background:#2a2a2a;border-radius:3px;overflow:hidden;margin-bottom:6px"><div style="height:100%;width:{pct:.1f}%;background:#10b981"></div></div>
                <div style="font-size:10px;color:#6b7280;display:flex;justify-content:space-between"><span>Unit Cost: ${u_cost:.2f}/M</span><span>Cost: {fmt_cost(cost)}</span></div></div>"""
    
    html += f"""
                </div>
            </div>

            <div style="background:#1a1a1a;border-radius:24px;padding:28px;border:1px solid #2a2a2a;display:flex;flex-direction:column;gap:16px">
                <div style="display:flex;justify-content:space-between;align-items:center"><span style="font-size:12px;color:#6b7280">Unit Cost</span><span style="font-size:20px;font-weight:700;color:#10b981">${avg_unit_cost:.2f}/M</span></div>
                <div style="height:1px;background:#2a2a2a"></div>
                <div style="display:flex;justify-content:space-between;align-items:center"><span style="font-size:12px;color:#6b7280">Daily Avg</span><span style="font-size:20px;font-weight:700;color:#10b981">{fmt_cost(daily_avg_cost)}</span></div>
            </div>
        </div>

        <!-- Right Column -->
        <div style="flex:1;display:flex;flex-direction:column;gap:24px">
            <div style="background:#1a1a1a;border-radius:24px;padding:32px;border:1px solid #2a2a2a">
                <div style="font-size:18px;font-weight:700;margin-bottom:24px;color:#10b981">Last 7 Days Activity</div>
                <div style="display:flex;gap:12px;align-items:flex-end;height:140px;padding-top:20px">
                """
    
    max_day_tok = max([daily_total.get(d,{}).get('tokens',0) for d in last_7_dates] or [1]) or 1
    for d in last_7_dates:
        tokens = daily_total.get(d,{}).get('tokens',0)
        h_pct = (tokens / max_day_tok * 100)
        label = datetime.strptime(d,"%Y-%m-%d").strftime("%m/%d")
        html += f"""<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:10px">
                    <div style="font-size:10px;color:#10b981;font-weight:600">{fmt_tokens(tokens) if tokens>0 else ''}</div>
                    <div style="width:100%;background:#2a2a2a;border-radius:8px;height:120px;position:relative;overflow:hidden">
                    <div style="position:absolute;bottom:0;width:100%;height:{h_pct:.1f}%;background:linear-gradient(0deg,#059669,#10b981);border-radius:4px"></div></div>
                    <span style="font-size:11px;color:#6b7280">{label}</span></div>"""
                    
    html += f"""
                </div>
            </div>

            <div style="background:#1a1a1a;border-radius:24px;padding:32px;border:1px solid #2a2a2a;flex-grow:1;display:flex;flex-direction:column">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px">
                    <div style="font-size:18px;font-weight:700;color:#10b981">Trends (30D)</div>
                    <div style="display:flex;flex-wrap:wrap;justify-content:flex-end;gap:8px;font-size:10px;max-width:350px">
                        <div style="display:flex;align-items:center;gap:4px"><span style="width:10px;height:2px;background:{colors[0]}"></span>Total</div>
                        {" ".join([f'<div style="display:flex;align-items:center;gap:4px"><span style="width:10px;height:0;border-top:1.5px dashed {colors[i+1]}"></span>{clean_m(m)}</div>' for i, m in enumerate(top_trend_models)])}
                    </div>
                </div>
                <div style="margin-bottom:40px;flex-grow:1">
                    <div style="display:flex;justify-content:space-between;font-size:11px;color:#6b7280;margin-bottom:12px"><span>Token Trends</span><span>Peak: {fmt_tokens(max([daily_total.get(d,{}).get('tokens',0) for d in last_30_dates] or [0]))}</span></div>
                    {get_trend_svg(last_30_dates, 'tokens', width=620, height=140)}
                </div>
                <div style="flex-grow:1">
                    <div style="display:flex;justify-content:space-between;font-size:11px;color:#6b7280;margin-bottom:12px"><span>Cost Trends (USD)</span><span>Peak: {fmt_cost(max([daily_total.get(d,{}).get('cost',0) for d in last_30_dates] or [0]))}</span></div>
                    {get_trend_svg(last_30_dates, 'cost', width=620, height=140)}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html


def main():
    parser = argparse.ArgumentParser(description="Generate HTML report")
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--output", type=str, default="/tmp/llm-cost-report.html", help="Output HTML file")
    parser.add_argument("--title", type=str, default="AI Usage", help="Report title")
    args = parser.parse_args()
    store = UsageStore()
    html = generate_html_report(store, args.start, args.end, args.title)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"HTML report saved to: {args.output}")


if __name__ == "__main__":
    main()
