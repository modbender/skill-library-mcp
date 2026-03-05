#!/usr/bin/env python3
"""
Token Query Script v7 - Ave.ai 集成优化版
通过 gmgn.ai API / Ave.ai API 查询代币数据，支持 sol, bsc, base
数据源优先级: gmgn.ai API -> Ave.ai API -> gmgn.ai 页面抓取 (文本匹配)
"""

import json, asyncio, sys, re, websockets, urllib.parse, urllib.request, traceback
import aiohttp # 用于异步HTTP请求
import time # for age calculation

CHROME_WS_BASE = "ws://localhost:9222"
AVE_API_KEY = "uHxe2IxOYEx3vHNpUpPtVDJVd2UTPycHLimZkAIpyMxkGS9GE84tf05VU96Uwgdm"
AVE_API_BASE = "https://prod.ave-api.com" # Ave.ai 的 API 根域名

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
    if p >= 0.001: return f"${p:.8f}".rstrip('0') # Increased precision for small numbers
    return f"${p:.10f}".rstrip('0')

def fmt_holders(h):
    if h is None: return "N/A"
    h = int(h)
    if h >= 1e6: return f"{h/1e6:.1f}M"
    if h >= 1e3: return f"{h:,}"
    return str(h)

# --- 解析辅助函数 ---
def parse_sub(s):
    """解析下标数字价格如 0.0₄597"""
    smap = {'₀':'0','₁':'1','₂':'2','₃':'3','₄':'4','₅':'5','₆':'6','₇':'7','₈':'8','₉':'9'}
    for sub, d in smap.items():
        if sub in s:
            parts = s.split(sub)
            return float(parts[0] + '0'*int(d) + parts[1])
    try:
        return float(s.replace(',',''))
    except ValueError:
        return None

def parse_val(s):
    s = s.replace(',','')
    m = {'K':1e3,'M':1e6,'B':1e9}
    for k,v in m.items():
        if s.endswith(k): return float(s[:-1])*v
    try:
        return float(s)
    except ValueError:
        return None

def parse_page(text):
    # print("DEBUG: Entering parse_page function (gmgn.ai fallback)", file=sys.stderr)
    r = {}
    # MCap from title (e.g. "↑ $83.53K" or "↓ $61.08K")
    m = re.search(r'[↑↓]\s*\$([\d,.]+[KMB]?)', text)
    if m: r['market_cap'] = parse_val(m.group(1))
    # 也尝试从第一个独立的 $xxxK 行匹配
    if 'market_cap' not in r or r['market_cap'] is None:
        m = re.search(r'MCap\n\$([\d,.]+[KMB])', text) # 匹配 "MCap\n$123K" 这种
        if m: r['market_cap'] = parse_val(m.group(1))

    # Price
    m = re.search(r'Price\n\$([\d.,₀₁₂₃₄₅₆₇₈₉]+)', text)
    if m:
        try: r['price'] = parse_sub(m.group(1))
        except: pass
    # 涨跌幅
    for p in ['5m','1h','6h','24h']:
        m = re.search(rf'{p}\n([+-]?[\d,.]+%)', text)
        if m:
            try: r[f'change_{p}'] = float(m.group(1).replace('%','').replace(',','').replace('+',''))
            except: pass
    # Holders
    m = re.search(r'Holders\s+(\d[\d,]*)', text)
    if m: r['holder_count'] = int(m.group(1).replace(',',''))
    # Tax
    m = re.search(r'Total Tax\n([\d.]+%)\s*/\s*([\d.]+%)', text)
    if m: r['buy_tax'], r['sell_tax'] = m.group(1), m.group(2)
    return r

# --- Chrome DevTools Protocol 辅助函数 ---
async def get_page_id():
    try:
        resp = urllib.request.urlopen(f"http://localhost:9222/json/list")
        tabs = json.loads(resp.read())
        for t in tabs:
            if t.get('type')=='page' and 'gmgn' in t.get('url',''): return t['id']
        # If no gmgn.ai page, use the first available page
        if tabs: return tabs[0]['id']
    except Exception as e:
        print(f"Error getting page ID: {e}", file=sys.stderr)
        pass
    return None

async def chrome_fetch(ws, url):
    js = f"fetch('{url}').then(r=>r.text())"
    await ws.send(json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':js,'awaitPromise':True}}))
    resp = await ws.recv()
    return json.loads(resp).get('result',{}).get('result',{}).get('value','')

async def chrome_eval(ws, js, get_value=False):
    await ws.send(json.dumps({'id':1,'method':'Runtime.evaluate','params':{'expression':js,'awaitPromise':True}}))
    resp = await ws.recv()
    result_obj = json.loads(resp).get('result',{}).get('result',{})
    if get_value:
        return result_obj.get('value','')
    return result_obj

# --- 链自动检测 ---
async def auto_detect_chain(ws, address):
    if not address.startswith('0x'): return 'sol' # 非0x开头的默认为solana
    for chain in ['bsc','base']:
        raw = await chrome_fetch(ws, f"https://gmgn.ai/api/v1/token_info/{chain}/{address}")
        try:
            d = json.loads(raw)
            if d.get('code')==0 and d.get('data'): return chain
        except: pass
    return 'bsc' # 默认返回 bsc

# --- Ave.ai 数据获取 ---
def chain_to_ave_name(chain):
    mapping = {
        'sol': 'solana',
        'bsc': 'bsc',
        'base': 'base'
    }
    return mapping.get(chain, chain)

async def fetch_ave_data(chain, address):
    ave_chain_name = chain_to_ave_name(chain)
    if not ave_chain_name: return {}, {}

    token_id = f"{address}-{ave_chain_name}"
    url = f"{AVE_API_BASE}/v2/tokens/{token_id}"
    headers = {
        "X-API-KEY": AVE_API_KEY
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                response.raise_for_status() # Raise an exception for HTTP errors (e.g. 404, 500)
                data = await response.json()
                
                if data and data.get('status') == 1 and data.get('data'): # Ave.ai uses 'status' not 'code' for success
                    token_info_from_ave = {}
                    price_data_from_ave = {}

                    token_detail = data['data'].get('token', {})
                    token_info_from_ave['name'] = token_detail.get('name', 'N/A')
                    token_info_from_ave['symbol'] = token_detail.get('symbol', 'N/A')
                    token_info_from_ave['address'] = address # 从请求地址填充

                    price_data_from_ave['price'] = float(token_detail.get('current_price_usd')) if token_detail.get('current_price_usd') else None
                    price_data_from_ave['market_cap'] = float(token_detail.get('market_cap')) if token_detail.get('market_cap') else None
                    price_data_from_ave['liquidity'] = float(token_detail.get('tvl')) if token_detail.get('tvl') else None # TVL 作为流动性
                    price_data_from_ave['holders'] = int(token_detail.get('holders')) if token_detail.get('holders') else None
                    
                    pairs = data['data'].get('pairs', [])
                    if pairs:
                        # 优先使用第一个 pair 的数据，它通常是最主要的
                        first_pair = pairs[0]
                        price_data_from_ave['volume_24h'] = float(first_pair.get('volume_u')) if first_pair.get('volume_u') else None
                        
                        # Ave.ai 文档中的价格变化字段有多个，优先使用 token_detail 里的
                        price_data_from_ave['change_24h'] = float(token_detail.get('price_change_24h')) if token_detail.get('price_change_24h') else None
                        price_data_from_ave['change_1h'] = float(token_detail.get('price_change_1h')) if token_detail.get('price_change_1h') else None
                        # Ave API docs for token detail only list 1h, 24h, we will take 4h from token_detail and map to 6h if available
                        price_data_from_ave['change_6h'] = float(token_detail.get('price_change_4h')) if token_detail.get('price_change_4h') else None

                    # Tax info from Ave.ai is available in /v2/contracts/{token-id}
                    # For now, we will not integrate this endpoint to keep the script simpler and faster.
                    # Tax info might be extracted from gmgn.ai if available.

                    # print(f"DEBUG: Fetched from Ave.ai: {price_data_from_ave}", file=sys.stderr)
                    return token_info_from_ave, price_data_from_ave
                return {}, {} # If status != 1 or no data
    except aiohttp.ClientError as e:
        print(f"Error fetching from Ave.ai (ClientError): {e}", file=sys.stderr)
    except Exception as e:
        print(f"Error fetching from Ave.ai: {e}", file=sys.stderr)
    return {}, {}

# --- AI 分析逻辑 ---
def score_token(t):
    """给代币打分 1-10 (同步 meme_scanner.py 的最新逻辑)"""
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

def generate_why_alpha(t, score, risk_level, risks, conviction, narrative_vibe):
    """根据代币数据生成Why Alpha分析 (同步 meme_scanner.py 的最新逻辑)"""
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
    """根据代币信息生成 Narrative Vibe (同步 meme_scanner.py 的最新逻辑)"""
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

# --- 输出构建逻辑 ---
def build_output(t, score, risk_level, risks, conviction):
    """构建推送消息，完全符合用户模板，由脚本直接输出"""
    chain = t['chain'].upper()
    mc = t.get('market_cap')
    liq = t.get('liquidity')
    vol = t.get('volume_24h')
    change_24h = t.get('change_24h')
    change_1h = t.get('change_1h')
    holders = t.get('holder_count')
    
    # 来源标签 (token_query 没有这个概念，保持为空)
    source_tag = ""
    
    vol_mc = ""
    if vol and mc and mc > 0:
        ratio = vol / mc * 100
        vol_mc = f" ({ratio:.0f}% of MC)"
    
    # 创建时间
    age = ""
    if t.get('open_timestamp') and t['open_timestamp'] > 0:
        if len(str(t['open_timestamp'])) == 13: # if ms
            open_ts_s = t['open_timestamp'] / 1000
        else: # if s
            open_ts_s = t['open_timestamp']

        age_sec = time.time() - open_ts_s
        if age_sec < 3600:
            age = f" (创建 {int(age_sec/60)} 分钟前)"
        elif age_sec < 86400:
            age = f" (创建 {int(age_sec/3600)} 小时前)"
        else:
            age = f" (创建 {int(age_sec/86400)} 天前)"
    
    # 推荐动作 (严格按用户指定)
    action = ""
    if score >= 7:
        action = "☢️ 重点关注"
    elif score >= 5:
        action = "👀 可以关注"
    else:
        action = "⚠️ 谨慎观望"

    risk_text = "。".join(risks) if risks else "暂无明显风险"
    
    # Generate Narrative Vibe content early
    narrative_vibe_content = generate_narrative_vibe(t)
    
    # --- 构建 Why Alpha ---
    why_alpha_content = generate_why_alpha(t, score, risk_level, risks, conviction, narrative_vibe_content)

    # --- 构建最终消息 ---
    message_parts = []
    # New header format
    message_parts.append(f"🔔 代币分析 | {chain.upper()} {t['name']} (${t['symbol']}) | {chain.upper()}{age}")
    message_parts.append(f"CA: {t['address']}")

    message_parts.append("") # 空行作为分隔

    # 表格部分
    message_parts.append("| 指标 | 数值 |")
    message_parts.append("| ---------- | -------------------- |") # Change to -------------------- for wider column
    message_parts.append(f"| 💰 价格 | {fmt_price(t.get('price'))} |")
    message_parts.append(f"| 📊 市值 | {fmt_num(mc)} |")
    message_parts.append(f"| 💧 流动性 | {fmt_num(liq)} |")
    message_parts.append(f"| 📈 24h | {fmt_pct(change_24h)} |")
    message_parts.append(f"| 👥 Holders | {fmt_holders(holders)} |")
    message_parts.append(f"| 📦 24h Vol | {fmt_num(vol)}{vol_mc} |") # Re-add vol_mc
    message_parts.append(f"| ⏱️ 1h | {fmt_pct(change_1h)} |")
    
    # 非表格部分
    message_parts.append(f"\n• Early Score: {score}/10")
    message_parts.append(f"• Risk: {risk_level}")
    message_parts.append(f"• Action: {action}")
    
    # 如果有具体的风险，才显示第一个风险点
    if risks:
        message_parts.append(f"• ⚠️ 风险: {risks[0]}")
    
    if t.get('twitter'):
        tw = t['twitter']
        if not tw.startswith('http'): tw = f"https://x.com/{tw}"
        message_parts.append(f"🐦 Twitter: [{tw}]({tw})") # Markdown 链接
    
    if t.get('website'): # 添加 Website 信息
        ws = t['website']
        if not ws.startswith('http'): ws = f"https://{ws}"
        message_parts.append(f"🌐 Website: [{ws}]({ws})") # Changed to use ws for both text and url
    
    if t.get('launchpad'):
        message_parts.append(f"🚀 平台: {t['launchpad']}")
    
    message_parts.append(f"💡 Why Alpha: {why_alpha_content}")
    message_parts.append(f"• Narrative Vibe: {narrative_vibe_content}")
    message_parts.append(f"• ⚠️ 风险提示: {risk_text}") # 风险提示需要从 risks 列表中提取

    return "\n".join(message_parts)

# --- 主入口 ---
async def query_token(chain, address):
    token_info = {}
    price_data = {}
    stat_data = {}
    error = None

    page_id = await get_page_id()
    if not page_id:
        return {'error': "❌ Chrome 未连接"}
    uri = f"{CHROME_WS_BASE}/devtools/page/{page_id}"

    async with websockets.connect(uri) as ws:
        # --- 优先级 1: gmgn.ai API ---
        try:
            # 获取 token_info 和 stat_data
            raw_info = await chrome_fetch(ws, f"https://gmgn.ai/api/v1/token_info/{chain}/{address}")
            info_json = json.loads(raw_info)
            if info_json.get('code') == 0 and info_json.get('data'):
                token_info = info_json['data']
                stat_data = token_info.get('stat_data', {})
            else:
                print(f"DEBUG: gmgn.ai token_info API returned: {info_json}", file=sys.stderr)
                # If gmgn.ai API returns no data, clear token_info
                token_info = {}

            # 获取价格数据 (通常在同一个 token_info 接口中)
            if token_info:
                price_data['price'] = token_info.get('price')
                price_data['market_cap'] = token_info.get('market_cap')
                price_data['liquidity'] = token_info.get('liquidity')
                price_data['holders'] = token_info.get('holder_count')
                price_data['volume_24h'] = token_info.get('volume_24h')
                price_data['change_24h'] = token_info.get('change_24h')
                price_data['change_1h'] = token_info.get('change_1h')
                price_data['change_6h'] = token_info.get('change_6h') # gmgn may have 6h
                price_data['buy_tax'] = token_info.get('buy_tax_rate') # Assuming gmgn provides these
                price_data['sell_tax'] = token_info.get('sell_tax_rate') # Assuming gmgn provides these

            # 检查是否有足够的数据
            if price_data.get('price') and price_data.get('market_cap'):
                return {
                    'token_info': token_info,
                    'price_data': price_data,
                    'stat_data': stat_data
                }
            else:
                print("DEBUG: gmgn.ai API did not provide complete price_data. Trying Ave.ai...", file=sys.stderr)

        except Exception as e:
            print(f"Error fetching from gmgn.ai API: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            error = f"gmgn.ai API查询失败: {e}"

        # --- 优先级 2: Ave.ai API ---
        try:
            ave_token_info, ave_price_data = await fetch_ave_data(chain, address)
            if ave_token_info and ave_price_data.get('price') and ave_price_data.get('market_cap'):
                # Merge Ave.ai data, prioritizing gmgn for missing fields
                token_info.update(ave_token_info)
                price_data.update(ave_price_data)
                # Ave.ai does not provide stat_data directly in this endpoint
                return {
                    'token_info': token_info,
                    'price_data': price_data,
                    'stat_data': stat_data # Keep gmgn's stat_data if available
                }
            else:
                print("DEBUG: Ave.ai API did not provide complete price_data. Trying gmgn.ai page scraping...", file=sys.stderr)
        except Exception as e:
            print(f"Error fetching from Ave.ai API: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            error = f"Ave.ai API查询失败: {e}"
            
        # --- 优先级 3: gmgn.ai 页面抓取 (文本匹配) ---
        try:
            url = f"https://gmgn.ai/sol/{address}" if chain == 'sol' else f"https://gmgn.ai/bsc/{address}" # default to bsc for evm
            await ws.send(json.dumps({'id':1,'method':'Page.navigate','params':{'url':url}}))
            # 等待导航完成，或者超时
            await asyncio.sleep(5) # 简单等待，可以根据实际情况优化
            
            # 获取页面文本
            page_text = await chrome_eval(ws, 'document.body.innerText', get_value=True)
            scraped_data = parse_page(page_text)
            
            if scraped_data and scraped_data.get('price'):
                token_info.update({'address': address, 'chain': chain}) # Add basic info
                price_data.update(scraped_data)
                print(f"DEBUG: Scraped data from gmgn.ai page: {scraped_data}", file=sys.stderr)
                return {
                    'token_info': token_info,
                    'price_data': price_data,
                    'stat_data': stat_data # stat_data is unlikely from page scrape
                }
            else:
                error = "gmgn.ai 页面抓取未能获取到完整数据"

        except Exception as e:
            print(f"Error scraping gmgn.ai page: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            error = f"gmgn.ai页面抓取失败: {e}"

    return {'error': error if error else "未能获取到代币数据"}

async def main():
    if len(sys.argv) < 2:
        print("用法: python3 token_query.py [chain] <address>")
        sys.exit(1)

    page_id = await get_page_id()
    if not page_id:
        print("❌ Chrome 未连接", file=sys.stderr); sys.exit(1)

    uri = f"{CHROME_WS_BASE}/devtools/page/{page_id}"

    if len(sys.argv) >= 3:
        chain, address = sys.argv[1].lower(), sys.argv[2]
    else:
        address = sys.argv[1]
        async with websockets.connect(uri) as ws:
            chain = await auto_detect_chain(ws, address)

    result = await query_token(chain, address)
    if 'error' in result:
        print(f"❌ {result['error']}", file=sys.stderr); sys.exit(1)

    info = result.get('token_info', {})
    price_data = result.get('price_data', {})
    stat = result.get('stat_data', {})
    
    # 构建统一的代币数据字典 t
    t = {
        'chain': chain,
        'address': address,
        'name': info.get('name', 'N/A'),
        'symbol': info.get('symbol', 'N/A'),
        'price': float(price_data.get('price') or info.get('price') or 0),
        'market_cap': float(price_data.get('market_cap') or info.get('market_cap') or 0),
        'liquidity': float(price_data.get('liquidity') or info.get('liquidity') or 0),
        'volume_24h': float(price_data.get('volume_24h') or info.get('volume_24h') or 0),
        'change_24h': float(price_data.get('change_24h') or info.get('change_24h') or 0),
        'change_1h': float(price_data.get('change_1h') or info.get('change_1h') or 0),
        'holder_count': price_data.get('holders') or price_data.get('holder_count') or stat.get('holder_count') or info.get('holder_count'),
        'bundler_rate': stat.get('top_bundler_trader_percentage', 0), # 从 stat_data 获取
        'top_10_holder_rate': stat.get('top_10_holder_rate', 0), # 从 stat_data 获取
        'is_honeypot': info.get('is_honeypot', False),
        'twitter': info.get('twitter_username', ''), # 从 info 获取
        'website': info.get('website', ''), # 从 info 获取
        'launchpad': info.get('launchpad_platform', ''), # 从 info 获取
        'open_timestamp': info.get('open_timestamp', 0), # 从 info 获取
        'buy_tax': price_data.get('buy_tax') or info.get('buy_tax_rate'), # 统一税率
        'sell_tax': price_data.get('sell_tax') or info.get('sell_tax_rate'), # 统一税率
    }
    
    # 传递统一的 t 字典给 score_token
    score, risk_level, risks, conviction = score_token(t)
    
    # 传递统一的 t 字典和评分结果给 build_output
    final_message = build_output(t, score, risk_level, risks, conviction)
    
    print(final_message)
    sys.exit(0) # 确保脚本在发送消息后退出，不产生额外输出
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"脚本执行出错: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr) # 打印详细栈追踪
        sys.exit(1)
