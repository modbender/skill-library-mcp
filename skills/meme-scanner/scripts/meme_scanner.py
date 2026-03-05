#!/usr/bin/env python3
"""
Meme Scanner v1 - 扫链发现有机会的 Meme 代币 (精简版，Why Alpha由 Agent 生成)
数据源: gmgn.ai rank API + Ave.ai trending API
扫描链: SOL, BSC
筛选条件: 市值 $10K~$5M, 流动性>$5K, 持有者>50, 24h涨幅>50%, 交易量/市值>30%, Bundler<70%, 非蜜罐
"""

import json, asyncio, sys, os, time, traceback, websockets, urllib.request, urllib.parse
import aiohttp
from datetime import datetime

CHROME_WS_BASE = "ws://localhost:9222"
AVE_API_KEY = "uHxe2IxOYEx3vHNpUpPtVDJVd2UTPycHLimZkAIpyMxkGS9GE84tf05VU96Uwgdm"
AVE_API_BASE = "https://prod.ave-api.com"
SCANNED_FILE = "/root/.openclaw/workspace/scanned_tokens.json"

# 筛选条件
MIN_MCAP = 10000        # $10K
MAX_MCAP = 5000000      # $5M
MIN_LIQUIDITY = 4000    # $5K
MIN_HOLDERS = 50
MIN_CHANGE_24H = 100     # 50%
MIN_VOL_MCAP_RATIO = 0.3  # 30%
MAX_BUNDLER_RATE = 0.5  # 50%

# --- 格式化辅助函数 ---
def fmt_num(n):
    if n is None: return "N/A"
    n = float(n)
    if n >= 1e9: return f"${n/1e9:.2f}B"
    if n >= 1e6: return f"${n/1e6:.2f}M"
    if n >= 1e3: return f"${n/1e3:.1f}K"
    if n >= 1: return f"${n:.2f}"
    if n >= 0.01: return f"${n:.4f}"
    return f"${n:.10f}".rstrip('0')

def fmt_pct(p):
    if p is None: return "N/A"
    return f"{'+' if float(p)>=0 else ''}{float(p):.2f}%"

def fmt_price(p):
    if p is None: return "N/A"
    p = float(p)
    if p >= 1: return f"${p:.4f}"
    if p >= 0.001: return f"${p:.8f}".rstrip('0')
    return f"${p:.10f}".rstrip('0')

def fmt_holders(h):
    if h is None: return "N/A"
    h = int(h)
    if h >= 1e6: return f"{h/1e6:.1f}M"
    if h >= 1e3: return f"{h:,}"
    return str(h)

def load_scanned():
    if os.path.exists(SCANNED_FILE):
        try:
            with open(SCANNED_FILE, 'r') as f:
                data = json.load(f)
                # 清理超过24小时的记录
                now = time.time()
                cleaned = {k: v for k, v in data.items() if now - v < 86400}
                return cleaned
        except:
            return {}
    return {}

def save_scanned(scanned):
    with open(SCANNED_FILE, 'w') as f:
        json.dump(scanned, f)

async def get_page_id():
    try:
        resp = urllib.request.urlopen("http://localhost:9222/json/list")
        tabs = json.loads(resp.read())
        for t in tabs:
            if t.get('type') == 'page' and 'gmgn' in t.get('url', ''):
                return t['id']
        if tabs:
            return tabs[0]['id']
    except Exception as e:
        print(f"Error getting page ID: {e}", file=sys.stderr)
    return None

async def chrome_fetch(ws, url):
    js = f"fetch('{url}').then(r=>r.text())"
    await ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {'expression': js, 'awaitPromise': True}}))
    resp = await ws.recv()
    return json.loads(resp).get('result', {}).get('result', {}).get('value', '')

async def scan_gmgn(ws, chain):
    """从 gmgn.ai rank 接口扫描热门代币"""
    tokens = []
    # 1h 交易最活跃
    url = f"https://gmgn.ai/defi/quotation/v1/rank/{chain}/swaps/1h?limit=50"
    raw = await chrome_fetch(ws, url)
    try:
        data = json.loads(raw)
        if data.get('code') == 0 and data.get('data', {}).get('rank'):
            for t in data['data']['rank']:
                tokens.append({
                    'source': 'gmgn_rank',
                    'chain': chain,
                    'address': t.get('address', ''),
                    'name': t.get('name', 'N/A'),
                    'symbol': t.get('symbol', 'N/A'),
                    'price': float(t['price']) if t.get('price') else None,
                    'market_cap': float(t['market_cap']) if t.get('market_cap') else None,
                    'liquidity': float(t['liquidity']) if t.get('liquidity') else None,
                    'volume_24h': float(t['volume']) if t.get('volume') else None,
                    'change_24h': float(t['price_change_percent']) if t.get('price_change_percent') else None,
                    'change_1h': float(t['price_change_percent1h']) if t.get('price_change_percent1h') else None,
                    'holder_count': int(t['holder_count']) if t.get('holder_count') else None,
                    'bundler_rate': float(t['bundler_rate']) if t.get('bundler_rate') else 0,
                    'is_honeypot': t.get('is_honeypot', False),
                    'top_10_holder_rate': float(t['top_10_holder_rate']) if t.get('top_10_holder_rate') else 0,
                    'swaps': int(t['swaps']) if t.get('swaps') else 0,
                    'buys': int(t['buys']) if t.get('buys') else 0,
                    'sells': int(t['sells']) if t.get('sells') else 0,
                    'twitter': t.get('twitter_username', ''),
                    'website': t.get('website', ''),
                    'launchpad': t.get('launchpad_platform', ''),
                    'open_timestamp': t.get('open_timestamp', 0),
                    'buy_tax': 0,
                    'sell_tax': 0,
                })
    except Exception as e:
        print(f"Error scanning gmgn rank {chain}: {e}", file=sys.stderr)
    
    # 新交易对
    url2 = f"https://gmgn.ai/defi/quotation/v1/pairs/{chain}/new_pairs?limit=30"
    raw2 = await chrome_fetch(ws, url2)
    try:
        data2 = json.loads(raw2)
        if data2.get('code') == 0 and data2.get('data', {}).get('pairs'):
            for p in data2['data']['pairs']:
                base = p.get('base_token_info', {})
                if not base:
                    continue
                tokens.append({
                    'source': 'gmgn_new',
                    'chain': chain,
                    'address': base.get('address', ''),
                    'name': base.get('name', 'N/A'),
                    'symbol': base.get('symbol', 'N/A'),
                    'price': None,  # new_pairs 通常没有价格
                    'market_cap': None,
                    'liquidity': float(p['initial_liquidity']) if p.get('initial_liquidity') else None,
                    'volume_24h': None,
                    'change_24h': None,
                    'change_1h': None,
                    'holder_count': int(base['holder_count']) if base.get('holder_count') else None,
                    'bundler_rate': 0,
                    'is_honeypot': base.get('is_honeypot', False),
                    'top_10_holder_rate': float(base['top_10_holder_rate']) if base.get('top_10_holder_rate') else 0,
                    'swaps': 0,
                    'buys': 0,
                    'sells': 0,
                    'twitter': base.get('social_links', {}).get('twitter_username', '') if isinstance(base.get('social_links'), dict) else '',
                    'website': base.get('social_links', {}).get('website', '') if isinstance(base.get('social_links'), dict) else '',
                    'launchpad': p.get('launchpad_platform', ''),
                    'open_timestamp': p.get('open_timestamp', 0),
                    'buy_tax': 0,
                    'sell_tax': 0,
                })
    except Exception as e:
        print(f"Error scanning gmgn new_pairs {chain}: {e}", file=sys.stderr)
    
    return tokens

async def scan_ave(chain):
    """从 Ave.ai trending 接口扫描热门代币"""
    tokens = []
    ave_chain = 'solana' if chain == 'sol' else chain
    url = f"{AVE_API_BASE}/v2/tokens/trending?chain={ave_chain}&page_size=50"
    headers = {"X-API-KEY": AVE_API_KEY}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                if data and data.get('status') == 1 and data.get('data', {}).get('tokens'):
                    for t in data['data']['tokens']:
                        tokens.append({
                            'source': 'ave_trending',
                            'chain': chain,
                            'address': t.get('token', ''),
                            'name': t.get('name', 'N/A'),
                            'symbol': t.get('symbol', 'N/A'),
                            'price': float(t['current_price_usd']) if t.get('current_price_usd') else None,
                            'market_cap': float(t['market_cap']) if t.get('market_cap') else None,
                            'liquidity': float(t['tvl']) if t.get('tvl') else None,
                            'volume_24h': float(t['token_tx_volume_usd_24h']) if t.get('token_tx_volume_usd_24h') else None,
                            'change_24h': float(t['token_price_change_24h']) if t.get('token_price_change_24h') else None,
                            'change_1h': float(t['token_price_change_1h']) if t.get('token_price_change_1h') else None,
                            'holder_count': int(t['holders']) if t.get('holders') else None,
                            'bundler_rate': 0,  # Ave 不提供 bundler_rate
                            'is_honeypot': t.get('is_honeypot', False),
                            'top_10_holder_rate': 0,
                            'swaps': int(t.get('token_buy_tx_count_5m', 0) or 0),
                            'buys': int(t.get('token_buy_tx_count_5m', 0) or 0),
                            'sells': int(t.get('token_sell_tx_count_5m', 0) or 0),
                            'twitter': '',
                            'website': '',
                            'launchpad': t.get('issue_platform', ''),
                            'open_timestamp': t.get('created_at', 0),
                            'buy_tax': 0,
                            'sell_tax': 0,
                        })
    except Exception as e:
        print(f"Error scanning Ave trending {chain}: {e}", file=sys.stderr)
    return tokens

def filter_token(t):
    """筛选符合条件的代币"""
    # 蜜罐排除
    if t.get('is_honeypot'):
        return False, "蜜罐"
    
    mc = t.get('market_cap')
    liq = t.get('liquidity')
    holders = t.get('holder_count')
    change_24h = t.get('change_24h')
    vol = t.get('volume_24h')
    bundler = t.get('bundler_rate', 0)
    
    # 市值范围
    if mc is None or mc < MIN_MCAP or mc > MAX_MCAP:
        return False, f"市值不符: {mc}"
    
    # 流动性
    if liq is None or liq < MIN_LIQUIDITY:
        return False, f"流动性不足: {liq}"
    
    # 持有者
    if holders is None or holders < MIN_HOLDERS:
        return False, f"持有者不足: {holders}"
    
    # 24h 涨幅
    if change_24h is None or change_24h < MIN_CHANGE_24H:
        return False, f"涨幅不足: {change_24h}"
    
    # 交易量/市值比
    if vol and mc and mc > 0:
        ratio = vol / mc
        if ratio < MIN_VOL_MCAP_RATIO:
            return False, f"交易量/市值比不足: {ratio:.2f}"
    
    # Bundler 比例
    if bundler > MAX_BUNDLER_RATE:
        return False, f"Bundler过高: {bundler}"
    
    return True, "通过"

def score_token(t):
    """给代币打分 1-10"""
    score = 5
    risks = []
    
    mc = t.get('market_cap', 0) or 0
    liq = t.get('liquidity', 0) or 0
    holders = t.get('holder_count', 0) or 0
    change_24h = t.get('change_24h', 0) or 0
    vol = t.get('volume_24h', 0) or 0
    bundler = t.get('bundler_rate', 0) or 0
    top10 = t.get('top_10_holder_rate', 0) or 0
    buy_tax = float(t.get('buy_tax', 0) or 0)
    sell_tax = float(t.get('sell_tax', 0) or 0)
    
    # 流动性评分
    if liq > 500000: score += 1
    elif liq < 20000:
        score -= 1
        risks.append("流动性偏低")
    
    # 市值评分
    if 100000 < mc < 2000000: score += 1
    elif mc > 5000000: score -= 1
    
    # 持有者评分
    if holders > 5000: score += 1
    elif holders < 200:
        score -= 1
        risks.append("持有者较少")
    
    # 涨幅评分
    if change_24h > 500: risks.append(f"24h涨{change_24h:.0f}%，注意回调")
    elif change_24h > 100: score += 1
    
    # Top10 集中度
    if top10 > 0.5:
        score -= 1
        risks.append(f"Top10集中度{top10*100:.1f}%")
    
    # Bundler
    if bundler > 0.3:
        score -= 1
        risks.append(f"Bundler比例{bundler*100:.1f}%")
    
    # Tax
    if buy_tax > 5 or sell_tax > 5:
        score -= 1
        risks.append(f"税率偏高(买{buy_tax}%/卖{sell_tax}%)")
    
    # 有社交媒体加分
    if t.get('twitter'): score += 1
    if t.get('website'): score += 1
    
    score = max(1, min(10, score))
    if len(risks) >= 3 or score <= 3:
        risk_level = "🔴 High"
    elif len(risks) >= 1 or score <= 5:
        risk_level = "🟡 Medium"
    else:
        risk_level = "🟢 Low"
    
    conviction = score # 暂时将 conviction 设置为和 score 一样，后续可以细化

    return score, risk_level, risks, conviction

def generate_why_alpha_v2(t, score, risk_level, risks, conviction, narrative_vibe):
    """根据代币数据生成Why Alpha分析 (精简版，融入叙事)"""
    name = t.get('name', '该代币')
    symbol = t.get('symbol', 'TOKEN')
    mc = t.get('market_cap', 0) or 0
    liq = t.get('liquidity', 0) or 0
    change_24h = t.get('change_24h', 0) or 0
    vol_24h = t.get('volume_24h', 0) or 0
    holders = t.get('holder_count', 0) or 0
    
    alpha_analysis = []

    # 1. 总体评价基于得分和风险
    alpha_analysis.append(f"{name}(${symbol})")
    if score >= 7:
        alpha_analysis.append(f"得分{score}/10，潜力强劲。")
    elif score >= 5:
        alpha_analysis.append(f"得分{score}/10，值得关注。")
    else:
        alpha_analysis.append(f"得分{score}/10，波动大，需谨慎。")

    # 2. 市场表现和流动性分析
    if change_24h > 100:
        alpha_analysis.append(f"24h暴涨{int(change_24h)}%，短期爆发力强。")
        if mc > 0 and vol_24h > mc * 5:
            alpha_analysis.append(f"交易量是市值{int(vol_24h/mc)}倍，市场关注度极高。")
    
    if liq < 10000:
        alpha_analysis.append(f"流动性{fmt_num(liq)}极低，存在巨大滑点风险。")
    elif liq < 50000:
        alpha_analysis.append(f"流动性{fmt_num(liq)}偏低，交易时需警惕。")
    
    if holders < 200:
        alpha_analysis.append(f"持有者少（{holders}），存在巨鲸控盘风险。")

    # 3. 融入叙事分析
    if "动物币" in narrative_vibe:
        alpha_analysis.append("作为动物币，其社区共识和FOMO情绪是关键。")
    elif "政治名人币" in narrative_vibe:
        alpha_analysis.append("政治概念币受事件驱动影响大，波动性强。")
    elif "AI概念" in narrative_vibe:
        alpha_analysis.append("AI概念热度高，技术突破或合作可能带来机遇。")
    
    # 4. 关键风险点
    if "蜜罐" in risks:
        alpha_analysis.append("警惕蜜罐陷阱。")
    if any("Bundler" in r for r in risks):
        alpha_analysis.append("Bundler活动频繁，需警惕。")
    if any("税率偏高" in r for r in risks):
        alpha_analysis.append("交易税率较高，影响收益。")

    # 5. 总结性建议
    if score >= 7:
        alpha_analysis.append("综合看潜力强，但仍需密切关注市场。")
    elif score >= 5:
        alpha_analysis.append("作为新兴代币，值得追踪。")
    else:
        alpha_analysis.append("高风险，建议谨慎。")

    final_alpha = " ".join(alpha_analysis)
    if len(final_alpha) > 250: # 限制长度
        final_alpha = final_alpha[:247] + "..."
    return final_alpha.strip()

def generate_narrative_vibe(t):
    """根据代币信息生成 Narrative Vibe"""
    name = t.get('name', '')
    symbol = t.get('symbol', '')
    chain_name = t.get('chain', '').upper()

    vibe = []
    vibe.append(f"{chain_name} 生态")

    if "dog" in name.lower() or "shib" in name.lower() or "floki" in name.lower():
        vibe.append("动物币")
    elif "trump" in name.lower() or "biden" in name.lower() or "elon" in name.lower():
        vibe.append("政治名人币")
    elif "pepe" in name.lower() or "frog" in name.lower():
        vibe.append("青蛙币")
    elif "ai" in name.lower() or "gpt" in name.lower():
        vibe.append("AI概念")
    elif "game" in name.lower() or "play" in name.lower():
        vibe.append("GameFi")
    elif "meta" in name.lower():
        vibe.append("元宇宙")
    else:
        vibe.append("Memecoin")
    
    return ", ".join(vibe)


def format_token_data_for_agent(t, score, risk_level, risks, conviction):
    """构建推送消息，完全符合用户模板，由脚本直接输出"""
    chain = t['chain'].upper()
    mc = t.get('market_cap')
    liq = t.get('liquidity')
    vol = t.get('volume_24h')
    change_24h = t.get('change_24h')
    change_1h = t.get('change_1h')
    holders = t.get('holder_count')

    # 来源标签
    source_tag = ""
    if t.get('source') == 'gmgn_rank':
        source_tag = "📊 gmgn热门"
    elif t.get('source') == 'gmgn_new':
        source_tag = "🆕 gmgn新币"
    elif t.get('source') == 'ave_trending':
        source_tag = "🔥 Ave热门"

    vol_mc = ""
    if vol and mc and mc > 0:
        ratio = vol / mc * 100
        vol_mc = f" ({ratio:.0f}% of MC)"

    # 创建时间
    age = ""
    if t.get('open_timestamp') and t['open_timestamp'] > 0:
        if len(str(t['open_timestamp'])) == 13:  # if ms
            open_ts_s = t['open_timestamp'] / 1000
        else:  # if s
            open_ts_s = t['open_timestamp']

        age_sec = time.time() - open_ts_s
        if age_sec < 60:
            age = f" (创建 {int(age_sec)} 秒前)"
        elif age_sec < 3600:
            age = f" (创建 {int(age_sec / 60)} 分钟前)"
        elif age_sec < 86400:
            age = f" (创建 {int(age_sec / 3600)} 小时前)"
        else:
            age = f" (创建 {int(age_sec / 86400)} 天前)"

    # 推荐动作 (严格按用户指定)
    action = ""
    if score >= 8: # 恢复为8分重点关注
        action = "☢️ 重点关注"
    elif score >= 5: # 调整为5分可以关注
        action = "👀 可以关注"
    else:
        action = "⚠️ 谨慎观望"

    # Generate Narrative Vibe content early
    narrative_vibe_content = generate_narrative_vibe(t)

    # --- 构建 Why Alpha ---
    why_alpha_content = generate_why_alpha_v2(t, score, risk_level, risks, conviction, narrative_vibe_content)
    risk_text = risks[0] if risks else "暂无明显风险"

    # --- 构建最终消息 ---
    message_parts = []
    # New header format
    message_parts.append(f"🔔 发现潜力 Meme 代币！{source_tag} 🔍 {t['name']} (${t['symbol']}) | {chain}{age}")
    message_parts.append(f"CA: {t['address']}")  # CA独立成行

    message_parts.append("")  # 空行作为分隔

    # 表格部分
    message_parts.append("| 指标 | 数值 |")
    message_parts.append("| ---------- | -------------------- |") # 使用模板的更宽分隔
    message_parts.append(f"| 💰 价格 | {fmt_price(t.get('price'))} |")
    message_parts.append(f"| 📊 市值 | {fmt_num(mc)} |")
    message_parts.append(f"| 💧 流动性 | {fmt_num(liq)} |")
    message_parts.append(f"| 📈 24h | {fmt_pct(change_24h)} |")
    message_parts.append(f"| 👥 Holders | {fmt_holders(holders)} |")
    message_parts.append(f"| 📦 24h Vol | {fmt_num(vol)}{vol_mc} |") # 恢复市值百分比
    message_parts.append(f"| ⏱️ 1h | {fmt_pct(change_1h)} |")
    message_parts.append("")  # 显式添加一个空行来终止表格格式

    # 非表格部分
    message_parts.append(f"• Early Score: {score}/10")
    message_parts.append(f"• Risk: {risk_level}")
    message_parts.append(f"• Action: {action}")

    if risks:  # 如果有具体的风险，才显示第一个风险点
        message_parts.append(f"• ⚠️ 风险: {risks[0]}")

    # 确保 Website 格式匹配模板：[链接文字](链接地址)
    if t.get('twitter'):
        tw = t['twitter']
        if not tw.startswith('http'): tw = f"https://x.com/{tw}"
        message_parts.append(f"🐦 Twitter: [{tw}]({tw})")  # Markdown 链接

    if t.get('website'):  # 添加 Website 信息
        ws = t['website']
        if not ws.startswith('http'): ws = f"https://{ws}"
        message_parts.append(f"🌐 Website: [{ws}]({ws})") # 链接文字和地址相同，符合新的理解

    if t.get('launchpad'):
        message_parts.append(f"🚀 平台: {t['launchpad']}")

    message_parts.append(f"💡 Why Alpha: {why_alpha_content}")
    message_parts.append(f"• Narrative Vibe: {narrative_vibe_content}") # 从模板恢复 Narrative Vibe
    message_parts.append(f"• ⚠️ 风险提示: {risk_text}") # 从模板恢复风险提示，并匹配格式

    return "\n".join(message_parts)

    return "\n".join(message_parts)


async def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Meme Scanner 启动...", file=sys.stderr)
    
    scanned = load_scanned()
    
    page_id = await get_page_id()
    if not page_id:
        print("❌ Chrome 未连接", file=sys.stderr)
        sys.exit(1)
    
    uri = f"{CHROME_WS_BASE}/devtools/page/{page_id}"
    
    all_tokens = []
    
    async with websockets.connect(uri) as ws:
        current_url = await ws.send(json.dumps({'id': 0, 'method': 'Runtime.evaluate', 'params': {'expression': 'window.location.href', 'awaitPromise': False}}))
        resp = await ws.recv()
        current_url = json.loads(resp).get('result', {}).get('result', {}).get('value', '')
        if "gmgn.ai" not in current_url:
            await ws.send(json.dumps({'id': 0, 'method': 'Page.navigate', 'params': {'url': 'https://gmgn.ai/'}}))
            await ws.recv()
            await asyncio.sleep(2)
        
        for chain in ['sol', 'bsc']:
            tokens = await scan_gmgn(ws, chain)
            all_tokens.extend(tokens)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] gmgn {chain}: 获取 {len(tokens)} 个代币", file=sys.stderr)
    
    for chain in ['sol', 'bsc']:
        tokens = await scan_ave(chain)
        all_tokens.extend(tokens)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Ave {chain}: 获取 {len(tokens)} 个代币", file=sys.stderr)
    
    seen_addresses = set()
    unique_tokens = []
    for t in all_tokens:
        addr = t['address'].lower()
        if addr not in seen_addresses:
            seen_addresses.add(addr)
            unique_tokens.append(t)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 去重后共 {len(unique_tokens)} 个代币", file=sys.stderr)
    
    qualified = []
    for t in unique_tokens:
        addr = t['address'].lower()
        if addr in scanned:
            continue
        
        passed, reason = filter_token(t)
        if passed:
            # 记录为已扫描，避免下次重复处理，无论最终是否推送消息
            scanned[addr] = time.time() 
            
            # 添加评分和其他临时数据，用于后续排序和消息生成
            score_val, risk_level_val, risks_val, conviction_val = score_token(t)
            t['__score'] = score_val
            t['__risk_level'] = risk_level_val
            t['__risks'] = risks_val
            t['__conviction'] = conviction_val
            qualified.append(t)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 筛选通过 {len(qualified)} 个代币", file=sys.stderr)
    
    qualified.sort(key=lambda t: t['__score'], reverse=True)
    
    # 收集所有符合条件的代币消息
    if messages_to_send:
        # 将所有消息打包成JSON数组输出到stdout，确保不转义Unicode
        print(json.dumps(messages_to_send, ensure_ascii=False))
    else:
        print("[]") # 没有消息时输出空数组

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"扫链脚本出错: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)