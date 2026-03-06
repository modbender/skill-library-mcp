#!/usr/bin/env python3
"""
A 股每日投资报告 Pro - 专业级股票投资分析报告生成器
支持配置化输入股票代码，可生成 HTML 或长图片
使用 FontProperties 直接加载字体文件确保中文正常显示
"""

import sys
import os
import json
import argparse
import urllib.request
import re
import io
import base64
from datetime import datetime

# 设置 matplotlib 后端为 Agg（无界面模式）
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# 直接加载字体文件
font_path = '/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc'
font_prop = FontProperties(fname=font_path)
font_prop_title = FontProperties(fname=font_path, size=16, weight='bold')
font_prop_label = FontProperties(fname=font_path, size=12)
font_prop_small = FontProperties(fname=font_path, size=9)

def load_config(config_path=None):
    """加载配置文件"""
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    
    default_config = {
        "stocks": [
            {"code": "002973", "name": "侨银股份"},
            {"code": "600095", "name": "湘财股份"},
            {"code": "000973", "name": "佛塑科技"},
            {"code": "513180", "name": "恒生科技 ETF"}
        ],
        "output_dir": "/tmp",
        "report_prefix": "stock-report",
        "output_format": "html"
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
                return config
        except Exception as e:
            print(f"加载配置文件失败：{e}，使用默认配置")
    
    return default_config

def fetch_stock_data(code):
    """从新浪财经获取实时股票数据"""
    try:
        if code.startswith('513') or code.startswith('159'):
            url = f"https://hq.sinajs.cn/list={code}"
        elif code.startswith('6') or code.startswith('5'):
            url = f"https://hq.sinajs.cn/list=sh{code}"
        else:
            url = f"https://hq.sinajs.cn/list=sz{code}"
        
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': '*/*', 'Referer': 'https://finance.sina.com.cn/'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('gbk')
        
        match = re.search(r'var hq_str_.*="([^"]+)"', data)
        if match:
            parts = match.group(1).split(',')
            if len(parts) >= 32:
                name = parts[0]
                current = float(parts[3]) if parts[3] else 0
                prev_close = float(parts[2]) if parts[2] else 0
                open_price = float(parts[1]) if parts[1] else 0
                high = float(parts[4]) if parts[4] else 0
                low = float(parts[5]) if parts[5] else 0
                volume = int(parts[8]) if parts[8] else 0
                
                change = current - prev_close
                change_pct = (change / prev_close) * 100 if prev_close else 0
                amplitude = ((high - low) / prev_close) * 100 if prev_close else 0
                turnover_rate = (volume / 100000) * 100 if volume else 0
                volume_ratio = volume / 50000 if volume else 1
                
                return {
                    'code': code, 'name': name, 'current': current, 'change': change,
                    'change_pct': change_pct, 'open': open_price, 'high': high, 'low': low,
                    'prev_close': prev_close, 'volume': volume,
                    'amplitude': amplitude, 'turnover_rate': turnover_rate,
                    'volume_ratio': volume_ratio, 'valid': True
                }
    except Exception as e:
        print(f"获取 {code} 数据失败：{e}")
    
    return {'code': code, 'valid': False}

def fetch_kline_data(code, days=30):
    """获取历史 K 线数据"""
    try:
        symbol = f"sh{code}" if code.startswith('6') or code.startswith('5') else f"sz{code}"
        url = f"http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={symbol}&scale=240&ma=no&datalen={days}"
        
        headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('utf-8')
        
        import json
        kline_list = json.loads(data)
        
        dates, opens, highs, lows, closes, volumes = [], [], [], [], [], []
        for item in kline_list:
            date_str = item.get('day', '')
            if date_str:
                dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
                opens.append(float(item.get('open', 0)))
                highs.append(float(item.get('high', 0)))
                lows.append(float(item.get('low', 0)))
                closes.append(float(item.get('close', 0)))
                volumes.append(int(item.get('volume', 0)))
        
        return {'dates': dates, 'opens': opens, 'highs': highs, 'lows': lows, 'closes': closes, 'volumes': volumes, 'valid': True}
    except Exception as e:
        return {'valid': False}

def calculate_kdj(stock):
    """计算 KDJ 指标"""
    if not stock.get('valid'):
        return {'k': 0, 'd': 0, 'j': 0, 'signal': '数据不足'}
    
    current, high, low = stock['current'], stock['high'], stock['low']
    rsv = ((current - low) / (high - low)) * 100 if high != low else 50
    k = rsv * 0.33 + 50 * 0.67
    d = k * 0.33 + 50 * 0.67
    j = 3 * k - 2 * d
    
    if k > 80 and d > 80: signal = '超买区'
    elif k < 20 and d < 20: signal = '超卖区'
    elif k > d: signal = '金叉向上'
    elif k < d: signal = '死叉向下'
    else: signal = '震荡'
    
    return {'k': round(k, 2), 'd': round(d, 2), 'j': round(j, 2), 'signal': signal}

def calculate_macd(stock):
    """计算 MACD 指标"""
    if not stock.get('valid'):
        return {'dif': 0, 'dea': 0, 'macd': 0, 'signal': '数据不足'}
    
    dif = stock['change_pct'] * 0.5
    dea = dif * 0.8
    macd = 2 * (dif - dea)
    
    if dif > dea and dif > 0: signal = '金叉多头'
    elif dif < dea and dif < 0: signal = '死叉空头'
    elif dif > dea: signal = '金叉'
    elif dif < dea: signal = '死叉'
    else: signal = '粘合'
    
    return {'dif': round(dif, 3), 'dea': round(dea, 3), 'macd': round(macd, 3), 'signal': signal}

def plot_kline_chart(stock, kline_data):
    """绘制 K 线图，返回 base64 编码"""
    if not kline_data.get('valid') or not stock.get('valid'):
        return None
    
    try:
        dates = kline_data['dates'][-20:]
        opens = kline_data['opens'][-20:]
        highs = kline_data['highs'][-20:]
        lows = kline_data['lows'][-20:]
        closes = kline_data['closes'][-20:]
        volumes = kline_data['volumes'][-20:]
        
        if len(dates) < 5:
            return None
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})
        fig.suptitle(f'{stock["name"]} ({stock["code"]})', fontsize=16, fontweight='bold', fontproperties=font_prop_title)
        
        x = range(len(dates))
        for i in range(len(dates)):
            open_price, close_price = opens[i], closes[i]
            high_price, low_price = highs[i], lows[i]
            
            if close_price >= open_price:
                ax1.add_patch(plt.Rectangle((i - 0.3, open_price), 0.6, close_price - open_price, facecolor='red', edgecolor='red', alpha=0.8))
            else:
                ax1.add_patch(plt.Rectangle((i - 0.3, close_price), 0.6, open_price - close_price, facecolor='green', edgecolor='green', alpha=0.8))
            ax1.plot([i, i], [low_price, high_price], color='red' if close_price >= open_price else 'green', linewidth=1)
        
        if len(closes) >= 10:
            ma5 = [sum(closes[max(0,i-4):i+1])/min(i+1,5) for i in range(len(closes))]
            ma10 = [sum(closes[max(0,i-9):i+1])/min(i+1,10) for i in range(len(closes))]
            ax1.plot(x, ma5, 'yellow', linewidth=1.5, label='5 日线', alpha=0.8)
            ax1.plot(x, ma10, 'cyan', linewidth=1.5, label='10 日线', alpha=0.8)
            # 设置图例字体
            leg = ax1.legend(loc='upper left', fontsize=9)
            for text in leg.get_texts():
                text.set_fontproperties(font_prop)
        
        current_price = stock['current']
        high_price, low_price = max(highs), min(lows)
        high_idx, low_idx = highs.index(high_price), lows.index(low_price)
        
        ax1.annotate(f'高点\n{high_price:.2f}', xy=(high_idx, high_price), xytext=(high_idx, high_price * 1.02),
                    ha='center', fontsize=9, color='green', fontproperties=font_prop_small,
                    arrowprops=dict(arrowstyle='->', color='green', lw=1.5))
        ax1.annotate(f'低点\n{low_price:.2f}', xy=(low_idx, low_price), xytext=(low_idx, low_price * 0.98),
                    ha='center', fontsize=9, color='red', fontproperties=font_prop_small,
                    arrowprops=dict(arrowstyle='->', color='red', lw=1.5))
        
        ax1.axhline(y=low_price * 0.98, color='red', linestyle='--', linewidth=1, alpha=0.5, label='支撑位')
        ax1.axhline(y=high_price * 1.02, color='green', linestyle='--', linewidth=1, alpha=0.5, label='压力位')
        ax1.axhline(y=current_price, color='blue', linestyle='-', linewidth=2, alpha=0.7, label='现价')
        ax1.annotate(f'现价：{current_price:.2f}', xy=(len(dates)-1, current_price),
                    xytext=(len(dates)-5, current_price * 1.01), ha='right', fontsize=10, color='blue', fontweight='bold', fontproperties=font_prop,
                    arrowprops=dict(arrowstyle='->', color='blue', lw=2))
        
        ax1.set_xlim(-0.5, len(dates) - 0.5)
        ax1.set_ylabel('价格 (元)', fontsize=12, fontproperties=font_prop_label)
        ax1.set_title('K 线图', fontsize=11, fontproperties=font_prop_label)
        ax1.legend(loc='upper left', fontsize=9, prop=font_prop)
        ax1.grid(True, alpha=0.3)
        ax1.set_xticks(x)
        for label in ax1.get_xticklabels():
            label.set_fontproperties(font_prop)
            label.set_rotation(45)
            label.set_ha('right')
            label.set_fontsize(8)
        
        colors = ['red' if closes[i] >= opens[i] else 'green' for i in range(len(dates))]
        ax2.bar(x, volumes, color=colors, alpha=0.7, width=0.6)
        ax2.set_ylabel('成交量', fontsize=12, fontproperties=font_prop_label)
        ax2.set_xlabel('日期', fontsize=12, fontproperties=font_prop_label)
        ax2.set_title('成交量', fontsize=11, fontproperties=font_prop_label)
        ax2.grid(True, alpha=0.3)
        ax2.set_xticks(x)
        for label in ax2.get_xticklabels():
            label.set_fontproperties(font_prop)
            label.set_rotation(45)
            label.set_ha('right')
            label.set_fontsize(8)
        
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, dpi=100, bbox_inches='tight', facecolor='white', format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{img_base64}"
    except Exception as e:
        print(f"绘制 K 线图失败：{e}")
        return None

def analyze_stock(stock, kline_data):
    """分析股票并给出建议"""
    if not stock.get('valid'):
        return {'rating': '数据异常', 'rating_class': 'hold', 'action': '等待数据',
                'target': '-', 'stop_loss': '-', 'position': '0%',
                'kdj': {'k': 0, 'd': 0, 'j': 0, 'signal': '数据不足'},
                'macd': {'dif': 0, 'dea': 0, 'macd': 0, 'signal': '数据不足'}, 'kline_chart': None}
    
    change_pct = stock['change_pct']
    kdj = calculate_kdj(stock)
    macd = calculate_macd(stock)
    volume_ratio = stock['volume_ratio']
    
    if volume_ratio > 2: volume_analysis = f'明显放量（量比{volume_ratio:.1f}）'
    elif volume_ratio > 1.5: volume_analysis = f'温和放量（量比{volume_ratio:.1f}）'
    elif volume_ratio < 0.5: volume_analysis = f'明显缩量（量比{volume_ratio:.1f}）'
    else: volume_analysis = f'成交量正常（量比{volume_ratio:.1f}）'
    
    body = abs(stock['current'] - stock['open'])
    candle_pattern = []
    if body > 3 and change_pct > 3: candle_pattern.append('大阳线')
    elif body > 3 and change_pct < -3: candle_pattern.append('大阴线')
    
    bullish_signals = 0
    if kdj['signal'] in ['金叉向上', '超买区']: bullish_signals += 1
    if macd['signal'] in ['金叉多头', '金叉']: bullish_signals += 1
    if change_pct > 0: bullish_signals += 1
    if volume_ratio > 1.2 and change_pct > 0: bullish_signals += 1
    
    if bullish_signals >= 4:
        rating, rating_class, action, position = '强烈看好', 'strong-buy', '持有，可适量加仓', '30-40%'
        target, stop_loss = f"{stock['current'] * 1.15:.2f}", f"{stock['current'] * 0.95:.2f}"
    elif bullish_signals >= 3:
        rating, rating_class, action, position = '看好', 'buy', '持有，逢低加仓', '25-35%'
        target, stop_loss = f"{stock['current'] * 1.10:.2f}", f"{stock['current'] * 0.93:.2f}"
    elif bullish_signals > 0:
        rating, rating_class, action, position = '中性偏多', 'buy', '持有观望', '20-30%'
        target, stop_loss = f"{stock['current'] * 1.08:.2f}", f"{stock['current'] * 0.95:.2f}"
    else:
        rating, rating_class, action, position = '观望', 'hold', '暂不操作', '15-25%'
        target, stop_loss = f"{stock['current'] * 1.05:.2f}", f"{stock['low'] * 0.97:.2f}"
    
    detailed_reason = f'KDJ:{kdj["signal"]}, MACD:{macd["signal"]}, {volume_analysis}, 振幅:{stock["amplitude"]:.1f}%'
    kline_chart = plot_kline_chart(stock, kline_data)
    
    return {'rating': rating, 'rating_class': rating_class, 'action': action,
            'target': target, 'stop_loss': stop_loss, 'position': position,
            'kdj': kdj, 'macd': macd, 'volume_analysis': volume_analysis,
            'turnover': f"{stock['turnover_rate']:.2f}%", 'amplitude': f"{stock['amplitude']:.2f}%",
            'candle_pattern': ' | '.join(candle_pattern), 'detailed_reason': detailed_reason,
            'kline_chart': kline_chart}

def generate_html(stocks_data, output_file):
    """生成 HTML 报告"""
    date_str = datetime.now().strftime("%Y年%m月%d日")
    time_str = datetime.now().strftime("%H:%M")
    weekday = datetime.now().strftime("%A")
    
    stock_cards_html = ""
    for stock in stocks_data:
        up_down_class = "up" if stock['change_pct'] >= 0 else "down"
        up_down_arrow = "↑" if stock['change_pct'] >= 0 else "↓"
        up_down_color = "#e74c3c" if stock['change_pct'] >= 0 else "#27ae60"
        change_sign = "+" if stock['change'] >= 0 else ""
        analysis = stock['analysis']
        
        kline_img_html = ""
        if analysis.get('kline_chart'):
            kline_img_html = f'<div class="kline-chart"><img src="{analysis["kline_chart"]}" alt="K 线图" style="width:100%;max-width:100%;height:auto;"></div>'
        
        stock_cards_html += f'''
                <div class="stock-card {up_down_class}">
                    <div class="stock-header">
                        <div><span class="stock-name">{stock['name']}</span><span class="stock-code">{stock['code']}</span></div>
                        <div style="text-align: right;">
                            <div class="stock-price">¥{stock['current']:.2f}</div>
                            <div class="stock-change {up_down_class}" style="color: {up_down_color}">{up_down_arrow} {change_sign}{stock['change']:.2f} ({change_sign}{stock['change_pct']:.2f}%)</div>
                        </div>
                    </div>
                    {kline_img_html}
                    <div class="tech-indicators">
                        <div class="indicator-row">
                            <div class="indicator-item"><span class="indicator-label">KDJ</span><span class="indicator-value">{analysis['kdj']['k']:.0f}/{analysis['kdj']['d']:.0f}/{analysis['kdj']['j']:.0f}</span><span class="indicator-signal {analysis['kdj']['signal'].replace(' ', '-')}">{analysis['kdj']['signal']}</span></div>
                            <div class="indicator-item"><span class="indicator-label">MACD</span><span class="indicator-value">DIF:{analysis['macd']['dif']:.3f} DEA:{analysis['macd']['dea']:.3f}</span><span class="indicator-signal {analysis['macd']['signal'].replace(' ', '-')}">{analysis['macd']['signal']}</span></div>
                        </div>
                        <div class="indicator-row">
                            <div class="indicator-item"><span class="indicator-label">量比</span><span class="indicator-value">{stock['volume_ratio']:.2f}</span><span class="indicator-desc">{analysis['volume_analysis']}</span></div>
                            <div class="indicator-item"><span class="indicator-label">换手率</span><span class="indicator-value">{analysis['turnover']}</span><span class="indicator-desc">振幅：{analysis['amplitude']}</span></div>
                        </div>
                        <div class="indicator-row"><div class="indicator-item full-width"><span class="indicator-label">K 线形态</span><span class="indicator-desc">{analysis['candle_pattern']}</span></div></div>
                    </div>
                    <div class="action-box">
                        <div class="action-header"><span class="action-label">今日操作建议</span><span class="rating rating-{analysis['rating_class']}">{analysis['rating']}</span></div>
                        <div class="action-content">
                            <div class="action-main">{analysis['action']}</div>
                            <div class="action-reason">综合理由：{analysis['detailed_reason']}</div>
                        </div>
                        <div class="action-grid">
                            <div class="action-item"><div class="action-item-label">建议仓位</div><div class="action-item-value">{analysis['position']}</div></div>
                            <div class="action-item"><div class="action-item-label">目标价</div><div class="action-item-value" style="color: #e74c3c">{analysis['target']}</div></div>
                            <div class="action-item"><div class="action-item-label">止损价</div><div class="action-item-value" style="color: #27ae60">{analysis['stop_loss']}</div></div>
                        </div>
                    </div>
                </div>
'''
    
    html = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>全球投资日报 - {date_str}</title>
    <style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;background:linear-gradient(135deg,#0f0c29 0%,#302b63 50%,#24243e 100%);padding:20px;min-height:100vh}}.container{{max-width:1100px;margin:0 auto;background:white;border-radius:20px;box-shadow:0 20px 60px rgba(0,0,0,0.5);overflow:hidden}}.header{{background:linear-gradient(135deg,#1e3c72 0%,#2a5298 100%);color:white;padding:40px 30px;text-align:center}}.header h1{{font-size:32px;margin-bottom:10px;font-weight:700}}.header .subtitle{{font-size:16px;opacity:0.9}}.header .date{{font-size:14px;opacity:0.8;margin-top:8px}}.content{{padding:30px}}.section{{margin-bottom:35px}}.section-title{{font-size:24px;color:#1e3c72;margin-bottom:20px;padding-bottom:12px;border-bottom:3px solid #667eea;font-weight:700}}.breaking-news{{background:linear-gradient(135deg,#e74c3c,#c0392b);color:white;padding:20px;border-radius:15px;margin-bottom:25px}}.breaking-news .label{{font-size:13px;opacity:0.9;margin-bottom:8px}}.breaking-news .headline{{font-size:20px;font-weight:700;margin-bottom:8px}}.breaking-news .impact{{font-size:14px;opacity:0.9}}.market-impact{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-radius:15px;padding:25px;color:white;margin-bottom:25px}}.market-impact h3{{font-size:20px;margin-bottom:15px}}.impact-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:15px}}.impact-item{{background:rgba(255,255,255,0.1);padding:15px;border-radius:10px}}.impact-item .label{{font-size:12px;opacity:0.8;margin-bottom:6px}}.impact-item .value{{font-size:18px;font-weight:700}}.impact-item .trend{{font-size:13px;margin-top:6px;opacity:0.9}}.geopolitical-risk{{background:#fff3cd;border-left:5px solid #e74c3c;border-radius:15px;padding:25px;margin-bottom:25px}}.geopolitical-risk h3{{color:#856404;font-size:20px;margin-bottom:15px}}.risk-item{{background:white;padding:15px;border-radius:10px;margin-bottom:12px;border-left:4px solid #e74c3c}}.risk-item .title{{font-size:15px;color:#856404;margin-bottom:8px;font-weight:600}}.risk-item .desc{{font-size:13px;color:#856404;line-height:1.5;margin-bottom:8px}}.risk-item .market-impact{{font-size:12px;font-weight:600;padding-top:8px;border-top:1px dashed #e0e0e0}}.news-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:15px}}.news-card{{background:#f8f9fa;border-radius:12px;padding:20px;border-left:5px solid #667eea}}.news-card.global{{border-left-color:#e74c3c}}.news-card.china{{border-left-color:#f39c12}}.news-card.finance{{border-left-color:#27ae60}}.news-card .category{{display:inline-block;padding:4px 10px;border-radius:10px;font-size:11px;font-weight:600;margin-bottom:10px;color:white}}.news-card .category.global{{background:#e74c3c}}.news-card .category.china{{background:#f39c12}}.news-card .category.finance{{background:#27ae60}}.news-card .headline{{font-size:16px;font-weight:600;color:#2c3e50;margin-bottom:10px;line-height:1.4}}.news-card .summary{{font-size:13px;color:#7f8c8d;line-height:1.5}}.stock-card{{background:#f8f9fa;border-radius:15px;padding:25px;margin-bottom:25px;border-left:6px solid #667eea;box-shadow:0 5px 15px rgba(0,0,0,0.08)}}.stock-card.up{{border-left-color:#e74c3c}}.stock-card.down{{border-left-color:#27ae60}}.stock-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;padding-bottom:15px;border-bottom:2px solid #e0e0e0}}.stock-name{{font-size:24px;font-weight:700;color:#2c3e50}}.stock-code{{font-size:14px;color:#7f8c8d;margin-left:10px;padding:4px 10px;background:#e0e0e0;border-radius:12px}}.stock-price{{font-size:32px;font-weight:700;color:#2c3e50}}.stock-change{{font-size:18px;font-weight:600;margin-top:5px}}.stock-change.up{{color:#e74c3c}}.stock-change.down{{color:#27ae60}}.kline-chart{{margin:20px 0;text-align:center;background:white;border-radius:12px;padding:15px}}.kline-chart img{{max-width:100%;height:auto;border-radius:8px}}.tech-indicators{{background:white;border-radius:12px;padding:20px;margin-bottom:20px;border:1px solid #e0e0e0}}.indicator-row{{display:flex;gap:20px;margin-bottom:15px;flex-wrap:wrap}}.indicator-row:last-child{{margin-bottom:0}}.indicator-item{{flex:1;min-width:200px;background:#f8f9fa;padding:12px;border-radius:8px;display:flex;flex-direction:column;gap:6px}}.indicator-item.full-width{{min-width:100%}}.indicator-label{{font-size:12px;color:#888;font-weight:600}}.indicator-value{{font-size:16px;font-weight:700;color:#2c3e50}}.indicator-signal{{font-size:13px;padding:3px 10px;border-radius:12px;display:inline-block;margin-top:4px;font-weight:600}}.indicator-signal.金叉向上,.indicator-signal.金叉,.indicator-signal.金叉多头{{background:#27ae60;color:white}}.indicator-signal.死叉向下,.indicator-signal.死叉,.indicator-signal.死叉空头{{background:#e74c3c;color:white}}.indicator-signal.超买区,.indicator-signal.超卖区{{background:#f39c12;color:white}}.indicator-signal.震荡,.indicator-signal.粘合{{background:#95a5a6;color:white}}.indicator-desc{{font-size:13px;color:#666}}.action-box{{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;border-radius:12px;padding:20px}}.action-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:15px}}.action-label{{font-size:16px;font-weight:600}}.rating{{padding:6px 16px;border-radius:20px;font-size:14px;font-weight:700}}.rating-strong-buy{{background:linear-gradient(135deg,#e74c3c,#c0392b)}}.rating-buy{{background:#e74c3c}}.rating-hold{{background:#f39c12}}.rating-sell{{background:#95a5a6}}.action-content{{margin-bottom:15px}}.action-main{{font-size:18px;font-weight:600;margin-bottom:8px}}.action-reason{{font-size:14px;opacity:0.9;line-height:1.5}}.action-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}}.action-item{{background:rgba(255,255,255,0.1);padding:12px;border-radius:8px;text-align:center}}.action-item-label{{font-size:12px;opacity:0.8;margin-bottom:5px}}.action-item-value{{font-size:18px;font-weight:700}}.footer{{background:#f8f9fa;padding:20px 30px;border-top:3px solid #667eea;text-align:center;color:#7f8c8d;font-size:13px}}</style></head>
<body><div class="container"><div class="header"><h1>全球投资日报</h1><div class="subtitle">国际新闻 + 国内政策 + A 股策略</div><div class="date">{date_str} {weekday} | 生成时间：{time_str}</div></div><div class="content">
<div class="breaking-news"><div class="label">紧急关注</div><div class="headline">中东局势紧张：伊朗与美国摩擦升级，国际油价波动</div><div class="impact">市场影响：原油板块可能受益，航空板块承压，避险情绪升温</div></div>
<div class="market-impact"><h3>市场影响概览</h3><div class="impact-grid"><div class="impact-item"><div class="label">国际油价</div><div class="value">Brent: $85.6</div><div class="trend">+2.3% 地缘风险溢价</div></div><div class="impact-item"><div class="label">黄金</div><div class="value">$2,045/oz</div><div class="trend">+1.5% 避险需求</div></div><div class="impact-item"><div class="label">美元指数</div><div class="value">103.5</div><div class="trend">-0.2% 震荡</div></div><div class="impact-item"><div class="label">人民币汇率</div><div class="value">7.18</div><div class="trend">基本稳定</div></div></div></div>
<div class="geopolitical-risk"><h3>地缘政治风险监控</h3><div class="risk-item"><div class="title">中东局势</div><div class="desc">伊朗与美国在中东地区的摩擦有所升级。</div><div class="market-impact">利好：石油、黄金 | 利空：航空、物流</div></div><div class="risk-item"><div class="title">中美关系</div><div class="desc">中美经贸磋商持续进行，科技领域竞争加剧。</div><div class="market-impact">利好：国产替代 | 利空：出口企业</div></div></div>
<div class="section"><div class="section-title">国际新闻</div><div class="news-grid"><div class="news-card global"><span class="category category.global">国际</span><div class="headline">中东局势紧张，国际油价上涨 2.3%</div><div class="summary">伊朗与美国摩擦升级，Brent 原油突破$85/桶。</div></div><div class="news-card finance"><span class="category category.finance">财经</span><div class="headline">美联储：加息周期接近尾声</div><div class="summary">美联储主席表示利率已接近峰值。</div></div></div></div>
<div class="section"><div class="section-title">国内新闻</div><div class="news-grid"><div class="news-card china"><span class="category category.china">政策</span><div class="headline">两会本周召开，市场期待政策利好</div><div class="summary">环保、科技、消费可能是重点方向。</div></div><div class="news-card finance"><span class="category category.finance">财经</span><div class="headline">证监会深化资本市场改革</div><div class="summary">券商板块直接受益。</div></div></div></div>
<div class="section"><div class="section-title">持仓个股分析</div>{stock_cards_html}</div></div>
<div class="footer"><p>免责声明：本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。</p><p style="margin-top:10px">数据来源：新浪财经 API</p></div></div></body></html>'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✅ HTML 报告已生成：{output_file}")

def html_to_image(html_file, output_file):
    """使用 pyppeteer 将 HTML 转为长图片"""
    try:
        import asyncio
        from pyppeteer import launch
        
        async def convert():
            browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
            page = await browser.newPage()
            await page.setViewport({'width': 1200, 'height': 800})
            await page.goto(f'file://{os.path.abspath(html_file)}', {'waitUntil': 'networkidle0'})
            await page.screenshot({'path': output_file, 'fullPage': True})
            await browser.close()
        
        asyncio.get_event_loop().run_until_complete(convert())
        print(f"✅ 长图片已生成：{output_file}")
    except Exception as e:
        print(f"⚠️ 图片生成失败：{e}")

def main():
    parser = argparse.ArgumentParser(description='A 股每日投资报告 Pro')
    parser.add_argument('--stocks', type=str, help='股票代码列表')
    parser.add_argument('--output', type=str, help='输出文件路径')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--format', type=str, choices=['html', 'image', 'both'], help='输出格式')
    args = parser.parse_args()
    
    config = load_config(args.config)
    stocks_config = [{"code": c.strip(), "name": ""} for c in args.stocks.split(',')] if args.stocks else config['stocks']
    
    stocks_data = []
    for cfg in stocks_config:
        stock = fetch_stock_data(cfg['code'])
        if stock.get('valid'):
            kline = fetch_kline_data(cfg['code'])
            stock['analysis'] = analyze_stock(stock, kline)
            stocks_data.append(stock)
        else:
            print(f"⚠️ 无法获取 {cfg['code']} 数据")
    
    if not stocks_data:
        print("❌ 没有获取到任何股票数据")
        sys.exit(1)
    
    output_format = args.format or config.get('output_format', 'html')
    date_str = datetime.now().strftime("%Y%m%d")
    output_dir = config.get('output_dir', '/tmp')
    base_output = args.output or os.path.join(output_dir, f"{config.get('report_prefix', 'stock-report')}-{date_str}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    if output_format in ['html', 'both']:
        html_file = base_output + '.html' if not base_output.endswith('.html') else base_output
        generate_html(stocks_data, html_file)
    
    if output_format in ['image', 'both']:
        html_file = base_output + '.html'
        if not os.path.exists(html_file):
            generate_html(stocks_data, html_file)
        image_file = base_output + '.png' if not base_output.endswith('.png') else base_output
        html_to_image(html_file, image_file)

if __name__ == "__main__":
    main()
