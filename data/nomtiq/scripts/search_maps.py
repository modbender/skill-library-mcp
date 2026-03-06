#!/usr/bin/env python3
"""
Nomtiq 小饭票 - 地图 API 搜索
中国：高德地图 POI 搜索（结构化数据，免费 5000次/天）
海外：Serper Google Maps（结构化数据，有评分/营业时间/价格档次）

用法:
  python3 search_maps.py "约会餐厅 环境好" --city 长沙 --district 岳麓区
  python3 search_maps.py "romantic restaurant" --city "Changsha" --mode overseas
  python3 search_maps.py "dim sum" --city "New York" --mode overseas
"""

import sys, json, argparse, os, re, subprocess
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import URLError
from datetime import date

WORKSPACE = Path(__file__).parent.parent.parent.parent
DATA_DIR = Path(__file__).parent.parent / 'data'
RATE_LIMIT_FILE = DATA_DIR / 'rate_limit.json'
DAILY_LIMIT = 10

# ── 内置高德 Key（新用户零配置，每天限 10 次）─────────────────
# 用户可申请自己的 key 配置到环境变量 AMAP_KEY，无限使用
BUILTIN_AMAP_KEY = '15446a418e6fedc8b4e5e0de4942598e'
AMAP_KEY = os.environ.get('AMAP_KEY', BUILTIN_AMAP_KEY)

def check_rate_limit() -> bool:
    """检查是否超过每日限流"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    today = str(date.today())
    if RATE_LIMIT_FILE.exists():
        data = json.loads(RATE_LIMIT_FILE.read_text())
        if data.get('date') == today:
            return data.get('count', 0) < DAILY_LIMIT
    return True

def increment_rate_limit():
    today = str(date.today())
    data = {'date': today, 'count': 1}
    if RATE_LIMIT_FILE.exists():
        old = json.loads(RATE_LIMIT_FILE.read_text())
        if old.get('date') == today:
            data['count'] = old.get('count', 0) + 1
    RATE_LIMIT_FILE.write_text(json.dumps(data))


# ── 高德地图 POI 搜索 ─────────────────────────────────────────

AMAP_KEY = os.environ.get('AMAP_KEY', '')

# 高德城市代码映射（常用城市）
AMAP_CITY_CODES = {
    '北京': '010', '上海': '021', '广州': '020', '深圳': '0755',
    '成都': '028', '杭州': '0571', '武汉': '027', '西安': '029',
    '南京': '025', '重庆': '023', '长沙': '0731', '天津': '022',
    '苏州': '0512', '郑州': '0371', '青岛': '0532', '厦门': '0592',
}

# 高德餐饮 POI 类型代码
AMAP_FOOD_TYPES = '050000'  # 餐饮服务大类


def search_amap(query: str, city: str = '', district: str = '',
                max_results: int = 20) -> list:
    """高德地图 POI 搜索"""
    # 限流检查（仅当使用内置 key 时）
    if AMAP_KEY == BUILTIN_AMAP_KEY:
        if not check_rate_limit():
            print("❌ 今天的免费次数用完了（10次/天）", file=sys.stderr)
            print("申请自己的高德 key 可以无限用：", file=sys.stderr)
            print("  https://lbs.amap.com → 创建应用 → Web服务", file=sys.stderr)
            return []
        increment_rate_limit()

    if not AMAP_KEY:
        print("⚠️  未配置 AMAP_KEY，跳过高德搜索", file=sys.stderr)
        return []

    city_code = AMAP_CITY_CODES.get(city, city)
    keywords = f"{district} {query}".strip() if district else query

    params = {
        'key': AMAP_KEY,
        'keywords': keywords,
        'types': AMAP_FOOD_TYPES,
        'city': city_code,
        'citylimit': 'true',
        'offset': min(max_results, 25),
        'page': 1,
        'extensions': 'all',  # 返回详细信息（评分、营业时间等）
        'output': 'json',
    }

    url = f"https://restapi.amap.com/v3/place/text?{urlencode(params)}"
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())

        if data.get('status') != '1':
            print(f"高德 API 错误: {data.get('info')}", file=sys.stderr)
            return []

        pois = data.get('pois', [])
        results = []
        for poi in pois:
            r = _parse_amap_poi(poi)
            if r:
                results.append(r)
        return results

    except Exception as e:
        print(f"高德搜索出错: {e}", file=sys.stderr)
        return []


def _parse_amap_poi(poi: dict) -> dict | None:
    """解析高德 POI 数据"""
    name = poi.get('name', '')
    if not name:
        return None

    # 过滤非餐厅（快餐/便利店/超市）
    type_name = poi.get('type', '')
    # 高德 type 格式："餐饮服务;中餐厅;湘菜" → 取最后一段
    type_display = type_name.split(';')[-1] if ';' in type_name else type_name
    poi['_type_display'] = type_display
    skip_types = ['快餐', '便利店', '超市', '食堂', '小吃', '早餐']
    if any(t in type_name for t in skip_types):
        return None

    # 评分（高德评分 1-5 星，biz_ext 里）
    biz_ext = poi.get('biz_ext', {})
    rating = None
    rating_raw = biz_ext.get('rating', '')
    if rating_raw and rating_raw != 'none':
        try:
            rating = float(rating_raw)
        except:
            pass

    # 人均消费
    avg_cost = None
    cost_raw = biz_ext.get('cost', '')
    if cost_raw and cost_raw != 'none':
        try:
            avg_cost = int(float(cost_raw))
        except:
            pass

    # 营业时间
    open_time = biz_ext.get('open_time', '') or poi.get('business_area', '')

    # 地址
    address = poi.get('address', '')
    if isinstance(address, list):
        address = ''.join(address)

    # 区域
    pname = poi.get('pname', '')   # 省
    cityname = poi.get('cityname', '')  # 市
    adname = poi.get('adname', '')  # 区

    # 菜系（从 type 字段提取）
    cuisines = _extract_cuisines_cn(type_name + ' ' + name)
    type_display = poi.get('_type_display', type_name)

    return {
        'name': name,
        'score': rating,
        'avg_price': avg_cost,
        'cuisines': cuisines,
        'type': type_display,
        'address': address,
        'district': adname,
        'city': cityname,
        'open_time': open_time,
        'tel': poi.get('tel', ''),
        'source': 'amap',
        'sources': ['amap'],
        'cross_verified': False,
        'amap_id': poi.get('id', ''),
        'location': poi.get('location', ''),  # 经纬度
    }


# ── 百度地图 POI 搜索 ─────────────────────────────────────────

BMAP_KEY = os.environ.get('BMAP_KEY', '')


def search_bmap(query: str, city: str = '', district: str = '',
                max_results: int = 20) -> list:
    """百度地图地点检索"""
    if not BMAP_KEY:
        print("⚠️  未配置 BMAP_KEY，跳过百度搜索", file=sys.stderr)
        return []

    region = district or city

    params = {
        'ak': BMAP_KEY,
        'query': query,
        'region': region,
        'output': 'json',
        'page_size': min(max_results, 20),
        'page_num': 0,
        'scope': 2,  # 返回详细信息
        'filter': 'industry_type:cater',  # 只返回餐饮
    }

    url = f"https://api.map.baidu.com/place/v2/search?{urlencode(params)}"
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())

        if data.get('status') != 0:
            print(f"百度地图 API 错误: {data.get('message')}", file=sys.stderr)
            return []

        results = []
        for place in data.get('results', []):
            r = _parse_bmap_place(place)
            if r:
                results.append(r)
        return results

    except Exception as e:
        print(f"百度搜索出错: {e}", file=sys.stderr)
        return []


def _parse_bmap_place(place: dict) -> dict | None:
    name = place.get('name', '')
    if not name:
        return None

    detail = place.get('detail_info', {})

    rating = None
    rating_raw = detail.get('overall_rating', '')
    if rating_raw:
        try:
            rating = float(rating_raw)
        except:
            pass

    avg_cost = None
    cost_raw = detail.get('price', '')
    if cost_raw:
        try:
            avg_cost = int(float(cost_raw))
        except:
            pass

    tag = detail.get('tag', '')
    cuisines = _extract_cuisines_cn(tag + ' ' + name)

    return {
        'name': name,
        'score': rating,
        'avg_price': avg_cost,
        'cuisines': cuisines,
        'type': tag,
        'address': place.get('address', ''),
        'district': place.get('area', ''),
        'city': '',
        'tel': place.get('telephone', ''),
        'source': 'bmap',
        'sources': ['bmap'],
        'cross_verified': False,
        'bmap_uid': place.get('uid', ''),
    }


# ── Serper Google Maps（海外）────────────────────────────────

def search_serper_maps(query: str, city: str = '', max_results: int = 20) -> list:
    """Serper Google Maps 搜索（海外场景）"""
    full_query = f"{query} {city}".strip()

    try:
        result = subprocess.run(
            ['serperV', 'search', '-q', full_query, '-t', 'maps',
             '-l', str(max_results)],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode != 0:
            print(f"Serper maps 出错: {result.stderr[:100]}", file=sys.stderr)
            return []

        data = json.loads(result.stdout)
        places = data.get('places', [])

        results = []
        for p in places:
            r = _parse_serper_place(p)
            if r:
                results.append(r)
        return results

    except Exception as e:
        print(f"Serper maps 出错: {e}", file=sys.stderr)
        return []


def _parse_serper_place(p: dict) -> dict | None:
    name = p.get('title', '')
    if not name:
        return None

    # 过滤评分太低或评论太少的
    rating = p.get('rating')
    rating_count = p.get('ratingCount', 0) or 0

    # 价格档次 $ $$ $$$ $$$$
    price_level = len(p.get('priceLevel', '')) if p.get('priceLevel') else None

    type_str = p.get('type', '') or ''
    if isinstance(p.get('types'), list):
        type_str = ', '.join(p['types'])

    cuisines = _extract_cuisines_en(type_str + ' ' + name)

    return {
        'name': name,
        'score': rating,
        'rating_count': rating_count,
        'price_level': price_level,
        'cuisines': cuisines,
        'type': type_str,
        'address': p.get('address', ''),
        'open_now': p.get('openingHours') is not None,
        'opening_hours': p.get('openingHours', {}),
        'thumbnail': p.get('thumbnailUrl', ''),
        'source': 'google_maps',
        'sources': ['google_maps'],
        'cross_verified': False,
        'place_id': p.get('placeId', ''),
        'cid': p.get('cid', ''),
    }


# ── 双源合并（高德 + 百度）────────────────────────────────────

def merge_cn_sources(amap_results: list, bmap_results: list) -> list:
    """合并高德和百度结果，同名店铺交叉验证"""
    merged = {}

    for r in amap_results:
        key = _normalize_name(r['name'])
        merged[key] = r

    for r in bmap_results:
        key = _normalize_name(r['name'])
        if key in merged:
            merged[key]['cross_verified'] = True
            merged[key]['sources'].append('bmap')
            # 补充缺失的评分
            if not merged[key].get('score') and r.get('score'):
                merged[key]['score'] = r['score']
            if not merged[key].get('avg_price') and r.get('avg_price'):
                merged[key]['avg_price'] = r['avg_price']
        else:
            merged[key] = r

    return list(merged.values())


def _normalize_name(name: str) -> str:
    """标准化店名用于匹配（去掉括号内容、空格）"""
    name = re.sub(r'[（(][^）)]*[）)]', '', name)
    name = re.sub(r'\s+', '', name)
    return name.lower()


# ── 菜系提取 ─────────────────────────────────────────────────

def _extract_cuisines_cn(text: str) -> list:
    mapping = {
        '湘菜': ['湘菜', '湖南菜', '湘式'],
        '粤菜': ['粤菜', '广东菜', '顺德', '港式', '烧味', '早茶'],
        '川菜': ['川菜', '四川', '麻辣', '火锅'],
        '日料': ['日料', '日本料理', '寿司', '刺身', '居酒屋', 'omakase'],
        '西餐': ['西餐', '法餐', '意大利', '牛排', 'bistro', 'Bistro'],
        '云南菜': ['云南', '滇菜', '米线'],
        '海鲜': ['海鲜', '水产', '鱼'],
        '烧烤': ['烧烤', '烤肉', '串串'],
        '私房菜': ['私房', '私厨', '家宴'],
    }
    result = []
    for cuisine, kws in mapping.items():
        if any(kw in text for kw in kws):
            result.append(cuisine)
    return result


def _extract_cuisines_en(text: str) -> list:
    mapping = {
        'Chinese': ['chinese', 'hunan', 'cantonese', 'sichuan', 'dim sum'],
        'Japanese': ['japanese', 'sushi', 'ramen', 'izakaya'],
        'Korean': ['korean', 'bbq'],
        'Italian': ['italian', 'pizza', 'pasta'],
        'French': ['french', 'bistro', 'brasserie'],
        'Thai': ['thai'],
        'Indian': ['indian', 'curry'],
        'American': ['american', 'burger', 'steakhouse'],
        'Western': ['western', 'european'],
    }
    text_lower = text.lower()
    result = []
    for cuisine, kws in mapping.items():
        if any(kw in text_lower for kw in kws):
            result.append(cuisine)
    return result


# ── 主入口 ────────────────────────────────────────────────────

def search_maps(query: str, city: str = '', district: str = '',
                mode: str = 'china', max_results: int = 20) -> list:
    """统一地图搜索入口"""
    if mode == 'china':
        print(f"🗺️  高德地图搜索...", file=sys.stderr)
        amap = search_amap(query, city, district, max_results)
        print(f"   高德: {len(amap)} 家", file=sys.stderr)

        print(f"🗺️  百度地图搜索...", file=sys.stderr)
        bmap = search_bmap(query, city or district, district, max_results)
        print(f"   百度: {len(bmap)} 家", file=sys.stderr)

        merged = merge_cn_sources(amap, bmap)
        print(f"   合并后: {len(merged)} 家（{sum(1 for r in merged if r.get('cross_verified'))} 家双源验证）", file=sys.stderr)
        return merged

    else:  # overseas
        print(f"🗺️  Google Maps 搜索...", file=sys.stderr)
        results = search_serper_maps(f"{query} restaurant", city, max_results)
        print(f"   找到: {len(results)} 家", file=sys.stderr)
        return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Nomtiq - 地图 API 搜索')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('--city', default='', help='城市')
    parser.add_argument('--district', default='', help='区域（如：岳麓区）')
    parser.add_argument('--mode', choices=['china', 'overseas'], default='china')
    parser.add_argument('--max', type=int, default=20)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()

    results = search_maps(args.query, args.city, args.district, args.mode, args.max)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        sys.exit(0)

    print(f"\n找到 {len(results)} 家餐厅\n")
    for i, r in enumerate(results[:15], 1):
        score = f"⭐{r['score']}" if r.get('score') else ''
        price_cn = f"¥{r['avg_price']}" if r.get('avg_price') else ''
        price_en = '$' * r['price_level'] if r.get('price_level') else ''
        price = price_cn or price_en
        cuisines = '/'.join(r.get('cuisines', [])[:2])
        verified = '✅双源' if r.get('cross_verified') else ''
        district = r.get('district', '')
        info = ' | '.join(p for p in [price, score, cuisines, district, verified] if p)
        print(f"{i}. {r['name']}")
        if info:
            print(f"   {info}")
        if r.get('address'):
            print(f"   📍 {r['address'][:60]}")
        print()


# ── 社交媒体交叉验证（公开数据，无需登录）────────────────────

WORKSPACE = Path(__file__).parent.parent.parent.parent
HUB_SCRIPT = str(WORKSPACE / 'skills/search-hub/scripts/hub.py')


def cross_verify_social(restaurants: list, max_verify: int = 5) -> list:
    """
    用 Serper 搜索公开社交媒体数据做交叉验证。
    不需要用户登录任何账号。
    国内：搜小红书 + 大众点评公开页面
    """
    import subprocess

    print(f"🔍 社交媒体交叉验证（top {max_verify}）...", file=sys.stderr)

    for r in restaurants[:max_verify]:
        name = r['name']
        clean_name = re.sub(r'[（(][^）)]*[）)]', '', name).strip()

        # 搜小红书公开页面
        xhs_query = f'site:xiaohongshu.com {clean_name} 探店'
        try:
            result = subprocess.run(
                ['python3.13', HUB_SCRIPT, 'search', xhs_query, '-t', 'text', '-l', '3'],
                capture_output=True, text=True, timeout=20
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                hits = data.get('results', [])
                if hits:
                    r['xhs_verified'] = True
                    snippets = ' '.join(
                        h.get('snippet', '') + h.get('title', '') for h in hits
                    )
                    neg_words = ['难吃', '踩雷', '失望', '不推荐', '差评', '坑', '后悔', '一般']
                    pos_words = ['好吃', '推荐', '必去', '超棒', '喜欢', '值得', '宝藏', '惊喜']
                    neg = sum(1 for w in neg_words if w in snippets)
                    pos = sum(1 for w in pos_words if w in snippets)
                    r['xhs_sentiment'] = 'negative' if neg > pos else ('positive' if pos > 0 else 'neutral')
                    print(f"   ✅ {clean_name}: 小红书 {len(hits)} 条，情感={r['xhs_sentiment']}", file=sys.stderr)
                else:
                    print(f"   — {clean_name}: 小红书无记录", file=sys.stderr)
        except Exception as e:
            print(f"   ⚠️  {clean_name} 验证出错: {e}", file=sys.stderr)

    return restaurants




# 连锁品牌黑名单（饭卡模式过滤）
CHAIN_BRANDS = [
    '麦当劳', '肯德基', '必胜客', '星巴克', '海底捞', '西贝', '外婆家',
    '绿茶', '太二', '九毛九', '呷哺', '小龙坎', '大龙燚', '巴奴',
    '眉州东坡', '全聚德', '便宜坊', '东来顺', '旺顺阁',
    '萨莉亚', '必胜客', '棒约翰', '汉堡王', '德克士',
]

def fancard_filter(results: list, budget_low: int = 60, budget_high: int = 250) -> list:
    """
    饭卡模式过滤：
    - 评分 >= 4.3（陈晓卿定律：街边小店 3.5-4 才真实，这里用高德评分体系）
    - 人均在预算范围内
    - 非连锁品牌
    - 非快餐/食堂类型
    """
    filtered = []
    for r in results:
        # 评分过滤
        score = r.get('score')
        if score and score < 4.3:
            continue

        # 人均过滤
        price = r.get('avg_price')
        if price:
            if price < budget_low or price > budget_high:
                continue

        # 连锁过滤
        name = r.get('name', '')
        if any(brand in name for brand in CHAIN_BRANDS):
            continue

        # 类型过滤（快餐/食堂）
        type_name = r.get('type', '')
        skip = ['快餐', '食堂', '便利', '超市', '早餐', '面包', '甜品', '奶茶', '咖啡']
        if any(s in type_name for s in skip):
            continue

        filtered.append(r)

    # 按评分排序
    filtered.sort(key=lambda x: (x.get('score') or 0), reverse=True)
    return filtered


def generate_fancard_blurb(r: dict, is_explorer: bool = False) -> str:
    """饭卡模式推荐语（规则版，供 OpenClaw 润色）"""
    address = r.get('address', '') or ''
    cuisines = r.get('cuisines', [])
    price = r.get('avg_price', 0) or 0
    name = r.get('name', '')
    score = r.get('score', 0) or 0

    parts = []

    # 菜系稀缺性优先（比位置更有个性）
    rare = {
        '江苏菜': '苏帮菜在北京不多见',
        '闽菜': '闽菜在北京少见，值得试',
        '云南菜': '云南菜的香料用得讲究',
        '私房菜': '私房菜，不是连锁，有自己的风格',
        '粤菜': '粤菜讲究食材本味，不靠调料',
    }
    # cuisines 字段 + type 字段都检查
    cuisine_text = cuisines + [r.get('type', '')]
    for c in cuisine_text:
        if c in rare:
            parts.append(rare[c])
            break

    # 位置感知（菜系没命中时用）
    if not parts:
        loc_hints = {
            '798': '798 艺术区里，环境有调性，两个人坐下来不会觉得吵',
            '丽都': '藏在丽都花园里，安静，不是随便就能找到的地方',
            '将台': '将台的老街区，不靠流量，靠口碑',
            '蓝色港湾': '蓝色港湾里，环境好，适合慢慢聊',
            '酒仙桥': '酒仙桥的本地馆子，开了好几年了',
            '三里屯': '三里屯里的馆子，热闹但不嘈杂',
            '望京': '望京的街边小馆，本地人常去的那种',
        }
        for loc, hint in loc_hints.items():
            if loc in address or loc in name:
                parts.append(hint)
                break

    # 探索推荐专属
    if is_explorer and not parts:
        parts.append('你可能没去过，但值得试一次')

    # 社交媒体口碑（不暴露技术细节，只说结论）
    if r.get('xhs_verified'):
        if r.get('xhs_sentiment') == 'negative':
            parts.append('留个心眼，有差评')
        else:
            # positive 或 neutral 都算有口碑
            parts.append('小红书有探店，本地人去过')

    # 价格感知（中国逻辑：价格越高，人越少，越安静）
    if price:
        if price >= 150 and not any('安静' in p for p in parts):
            parts.append('人均过百五，人不多，安静，适合聊天')
        elif price >= 80 and price < 150:
            parts.append('人均一百左右，不会有压力')
        elif price < 80:
            parts.append('价格实惠，但可能热闹')

    if not parts and score >= 4.7:
        parts.append('4.7 分，口碑在那里，不用多说')

    return '。'.join(parts[:2]) + '。' if parts else ''


def search_fancard(location: str, city: str = '北京',
                   budget_low: int = 80, budget_high: int = 300) -> list:
    """
    饭卡模式主入口：找适合两人聊天的本地小馆
    location: 地点（如"酒仙桥"）
    """
    # 多关键词搜索，覆盖不同风格
    queries = [
        f"特色餐厅",
        f"小馆",
        f"私房菜",
    ]

    all_results = {}
    for q in queries:
        results = search_amap(q, city, location, max_results=25)
        for r in results:
            key = _normalize_name(r['name'])
            if key not in all_results:
                all_results[key] = r

    merged = list(all_results.values())
    filtered = fancard_filter(merged, budget_low, budget_high)

    # 社交媒体交叉验证（top 5，公开数据，无需登录）
    filtered = cross_verify_social(filtered, max_verify=5)

    # 加推荐语
    for i, r in enumerate(filtered):
        r['blurb'] = generate_fancard_blurb(r, is_explorer=(i >= 2))

    return filtered
