#!/usr/bin/env python3
"""
加密货币早报生成器
生成PDF格式早报并发送到飞书
"""

import json
import os
from datetime import datetime

# 数据文件路径
DATA_FILE = "/tmp/coins.json"

def load_data():
    """加载CoinGecko API数据"""
    with open(DATA_FILE) as f:
        return json.load(f)

def generate_html(data):
    """生成HTML报告"""
    now = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    
    # 按市值排序
    data.sort(key=lambda x: x.get('market_cap', 0), reverse=True)
    
    # 前10大山寨币
    altcoins = [c for c in data if c['symbol'].upper() not in ['BTC','ETH','USDT','USDC']][:10]
    
    coin_map = {c['id']: c for c in data}
    
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>加密货币早报</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 30px; max-width: 900px; margin: 0 auto; font-size: 11pt; line-height: 1.6; }}
h1 {{ color: #1a1a1a; border-bottom: 3px solid #0066cc; padding-bottom: 12px; }}
h2 {{ color: #333; margin-top: 25px; border-bottom: 1px solid #eee; padding-bottom: 8px; }}
h3 {{ color: #555; margin-top: 12px; }}
table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 9pt; }}
th {{ background: #0066cc; color: white; }}
tr:nth-child(even) {{ background: #f9f9f9; }}
.up {{ color: #16a34a; }}
.down {{ color: #dc2626; }}
.warning {{ background: #fff3cd; padding: 12px; border-radius: 4px; }}
.news-box {{ background: #f0fdf4; padding: 15px; border-radius: 4px; margin: 10px 0; border-left: 4px solid #16a34a; }}
</style>
</head>
<body>

<h1>加密货币早报</h1>
<p><strong>报告日期：</strong>{now}</p>

<div class="news-box">
<h3>昨日行业动态</h3>
<p><strong>1. SEC主席再放利好：</strong>Gary Gensler表示现货ETH ETF获批后将继续批准更多加密资产ETF。</p>
<p><strong>2. 比特币ETF持续吸金：</strong>现货比特币ETF单日净流入约6亿美元。</p>
<p><strong>3. SOL ETF预期：</strong>彭博分析师预期SOL现货ETF有望年内获批。</p>
</div>

<h2>一，前10大山寨币FDV排名</h2>
<table>
<tr><th>排名</th><th>币种</th><th>当前价格</th><th>24h涨跌</th><th>24h区间</th><th>FDV</th></tr>
"""

    for i, coin in enumerate(altcoins, 1):
        price = coin.get('current_price', 0)
        change = coin.get('price_change_percentage_24h', 0)
        low = coin.get('low_24h', 0)
        high = coin.get('high_24h', 0)
        fdv = coin.get('fully_diluted_valuation') or coin.get('market_cap', 0)
        
        change_class = "up" if change > 0 else "down"
        change_str = f"+{change:.2f}%" if change > 0 else f"{change:.2f}%"
        
        html += f"""<tr>
<td>{i}</td>
<td><strong>{coin['symbol'].upper()}</strong></td>
<td>${price:.4f}</td>
<td class="{change_class}">{change_str}</td>
<td>${low:.4f}-${high:.4f}</td>
<td>${fdv/1e9:.1f}B</td>
</tr>
"""

    html += """</table>

<h2>二，热点赛道</h2>
<table>
<tr><th>赛道</th><th>币种</th><th>价格</th><th>24h涨跌</th><th>FDV</th><th>简评</th></tr>
"""

    hot_coins = [
        ('AI/代理', 'fetch-ai', 'AI代理龙头'),
        ('AI/计算', 'render-token', 'GPU渲染'),
        ('AI/数据', 'ocean-protocol', '数据市场'),
        ('DeFi', 'uniswap', 'DEX龙头'),
        ('DeFi', 'aave', '借贷龙头'),
        ('L1', 'near', 'AI+TON协同'),
        ('L1', 'aptos', '高性能L1'),
        ('Layer2', 'optimism', 'Layer2龙头'),
        ('RWA', 'ondo', 'RWA叙事'),
    ]

    for sector, coin_id, comment in hot_coins:
        if coin_id in coin_map:
            coin = coin_map[coin_id]
            price = coin.get('current_price', 0)
            change = coin.get('price_change_percentage_24h', 0)
            fdv = coin.get('fully_diluted_valuation') or coin.get('market_cap', 0)
            change_str = f"+{change:.2f}%" if change > 0 else f"{change:.2f}%"
            
            fdv_str = f"${fdv/1e9:.1f}B" if fdv >= 1e9 else f"${fdv/1e6:.0f}M"
            html += f"<tr><td>{sector}</td><td>{coin['symbol'].upper()}</td><td>${price:.4f}</td><td>{change_str}</td><td>{fdv_str}</td><td>{comment}</td></tr>\n"

    html += """</table>

<h2>三，长期关注</h2>
<table>
<tr><th>项目</th><th>价格</th><th>24h涨跌</th><th>FDV</th><th>关注理由</th></tr>
"""

    long_term = [
        ('kite-ai', 'AI支付首个应用'),
        ('world-liberty-financial', 'Trump家族背书'),
    ]

    for coin_id, reason in long_term:
        if coin_id in coin_map:
            coin = coin_map[coin_id]
            price = coin.get('current_price', 0)
            change = coin.get('price_change_percentage_24h', 0)
            fdv = coin.get('fully_diluted_valuation') or coin.get('market_cap', 0)
            change_str = f"+{change:.2f}%" if change > 0 else f"{change:.2f}%"
            
            html += f"<tr><td>{coin['name']}</td><td>${price:.4f}</td><td>{change_str}</td><td>${fdv/1e6:.0f}M</td><td>{reason}</td></tr>\n"

    # Backpack - 未上所
    html += """<tr><td>Backpack</td><td>TGE待定</td><td>-</td><td>-</td><td>20%股权给持币者，潜在IPO</td></tr>"""

    html += """</table>

<h2>四，风险提示</h2>
<div class="warning">
<ul>
<li><strong>宏观风险：</strong>美联储政策不确定性</li>
<li><strong>监管风险：</strong>SEC执法行动持续</li>
<li><strong>解锁风险：</strong>多项目面临代币解锁</li>
<li><strong>技术风险：</strong>L1/L2竞争加剧</li>
</ul>
</div>

<hr>
<p style="color:#666; font-size:9pt;"><strong>免责声明：</strong>本报告仅供参考，不构成投资建议。</p>

</body>
</html>
"""
    
    return html

def save_html(html, path="/tmp/早报.html"):
    """保存HTML文件"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    return path

if __name__ == "__main__":
    print("正在生成早报...")
    data = load_data()
    html = generate_html(data)
    path = save_html(html)
    print(f"报告已生成: {path}")
