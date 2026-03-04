#!/usr/bin/env python3
"""
二次元烂梗收集器
每天自动收集网络上的二次元相关梗、流行语和热点
"""

import json
import re
import urllib.request
import urllib.parse
import ssl
from datetime import datetime
from pathlib import Path

def create_ssl_context():
    """创建SSL上下文，忽略证书验证（用于某些环境）"""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context

def fetch_bilibili_trending():
    """获取B站热门视频标题和标签"""
    try:
        url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com'
        }
        req = urllib.request.Request(url, headers=headers)
        context = create_ssl_context()
        
        with urllib.request.urlopen(req, timeout=15, context=context) as response:
            data = json.loads(response.read().decode('utf-8'))
            memes = []
            if data.get('data', {}).get('list'):
                for item in data['data']['list'][:30]:
                    title = item.get('title', '')
                    # 提取引号内的内容
                    quotes = re.findall(r'[""""""]([^""""""]+)[""""""]', title)
                    memes.extend(quotes)
                    # 提取方括号内容
                    brackets = re.findall(r'\[([^\]]+)\]', title)
                    memes.extend(brackets)
                    # 提取书名号内容
                    books = re.findall(r'《([^》]+)》', title)
                    memes.extend(books)
                    # 提取特定模式（如"XXのXX"）
                    japanese_pattern = re.findall(r'[\u3040-\u309F\u30A0-\u30FFの]+', title)
                    memes.extend([p for p in japanese_pattern if len(p) > 2])
                    
            return list(set([m.strip() for m in memes if len(m.strip()) > 1]))[:20]
    except Exception as e:
        print(f"B站获取失败: {e}")
        return []

def fetch_bilibili_hot_search():
    """获取B站热搜"""
    try:
        url = "https://s.search.bilibili.com/main/hotword"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        context = create_ssl_context()
        
        with urllib.request.urlopen(req, timeout=15, context=context) as response:
            data = json.loads(response.read().decode('utf-8'))
            memes = []
            if data.get('list'):
                for item in data['list'][:20]:
                    keyword = item.get('keyword', '')
                    if keyword:
                        memes.append(keyword)
            return memes
    except Exception as e:
        print(f"B站热搜获取失败: {e}")
        return []

def fetch_galgame_keywords():
    """获取Galgame相关关键词"""
    gal_keywords = [
        "Ciallo", "柚子社", "千恋万花", "魔女的夜宴", "RIDDLE JOKER",
        "星光咖啡馆", "PARQUET", "天使嚣嚣", "绫地宁宁", "丛雨",
        "因幡爱瑠", "常陆茉子", "朝武芳乃", "白雪乃爱", "谷风天音",
        "Key社", "Clannad", "Air", "Kanon", "Rewrite", "Summer Pockets",
        "白色相簿2", "冬马和纱", "小木曾雪菜", "北原春希",
        "型月", "Fate", "月姬", "魔法使之夜", "空之境界",
        "枕社", "樱之诗", "樱之刻", "素晴日", "美好的每一天",
        "调色板", "9-nine", "纯白交响曲", "恋花绽放樱飞时",
        "颜艺社", "借恋", "恋爱成双", "富婆妹",
        "水晶社", "红月摇曳的恋之星火", "牵绊闪耀的恋之伊吕波",
        "近月少女的礼仪", "樱小路露娜", "Navel",
        "School Days", "寒蝉鸣泣之时", "海猫鸣泣之时",
        "命运石之门", "Steins;Gate", "助手", "克里斯蒂娜",
        "ATRI", "亚托莉", "GINKA", "SPPL",
        "Muv-Luv", "Alternative", "鉴纯夏",
        "兰斯", "夏娃年代记", "多娜多娜",
        "E社", "天结", "封缄", "神采",
        "A社", "兰斯系列", "夏娃系列",
        "BALDR", "BALDR SKY", "BALDR FORCE",
        "Euphoria", "3days", "11eyes",
        "素晴らしき日々", "终之空", "樱之诗", "樱之刻",
        "冥契的牧神节", "纸上的魔法使", "水葬银货的伊斯特里亚",
        "想要传达给你的爱恋", "恋×シンアイ彼女",
        "初雪樱", "樱花萌放", "五彩斑斓的世界",
        "向日葵教会和漫长的暑假", "永不落幕的前奏诗",
        "奇异恩典", "金辉恋曲四重奏", "金色Loveriche",
        "RIDDLE JOKER", "密命王牌",
        "DRACU-RIOT", "天色幻想岛", "魔卡魅恋",
        "Noble Works", "管乐恋曲", "夏空彼方",
        "缘之空", "悠之空", "春日野穹",
        "灰色的果实", "灰色的迷宫", "灰色的乐园",
        "少女理论", "近月少女的礼仪2",
        "大图书馆的牧羊人", "幸运草的约定",
        "星织梦未来", "永不枯萎的世界与终结之花",
        "Trinoline", "宿星的女朋友",
        "野良与皇女与流浪猫之心", "Hulotte",
        "making lovers", "SMEE", "Hooksoft",
        "PRIMAL×HEARTS", "Marmalade", "甜蜜女友",
        "任性High Spec", "Madosoft", "窗社",
        "寄宿之恋", "ASa Project", "恋爱，我借走了",
        "八卦恋爱", "恋爱成双", "她的圣域",
        "富婆妹", "灵感满溢的甜蜜创想",
        "天使嚣嚣", "天使纷扰", "天使☆騒々 RE-BOOT!",
        "魔女的夜宴", "魔宴", "宁宁", "绫地宁宁",
        "因幡巡", "椎叶紬", "户隐憧子", "仮屋和奏",
        "千恋万花", "丛雨", "朝武芳乃", "常陆茉子", "马庭芦花",
        "蕾娜", "蕾娜·列支敦瑙尔",
        "RIDDLE JOKER", "三司绫濑", "在原七海", "式部茉优", "二条院羽月",
        "星光咖啡馆", "明月栞那", "四季夏目", "墨染希", "火打谷爱衣", "汐山凉音",
        "PARQUET", "城门翼", "茨木梨乃",
        "天使嚣嚣", "白雪乃爱", "谷风天音", "小云雀来海", "星河辉耶", "高楯欧丽叶",
    ]
    return gal_keywords

def fetch_streamer_keywords():
    """获取主播/电竞圈关键词（易拉罐文化）"""
    streamer_keywords = [
        # 核心主播
        "电棍", "otto", "侯国玉", "稳健棍", "吉吉国王",
        "张顺飞", "劳张", "顺飞", "唐氏",
        "山泥若", "腾杨天下", "若子",
        "炫神", "炫狗", "Last炫神", "选购",
        "大司马", "芜湖大司马", "马老师",
        # 经典梗
        "易拉罐", "引流狗", "ylg",
        "说的道理", "欧内的手", "哈姆", "哇袄",
        "冲刺", "独轮车",
        "房管呢", "封一下", "成分查询", "小仲",
        "唐", "劳", "顺",
        "腾杨赛评", "永远的神", "yyds", "乌兹",
        "起飞", "肉蛋葱鸡", "千层饼", "正方形打野",
        "皮克斯", "kiyomi",
        "白字", "彩字", "钻粉", "SC", "醒目留言",
        "舰长", "提督", "总督",
        "礼物呢", "老板大气",
        # 弹幕文化
        "666", "???", "哈哈哈", "泪目", "破防了",
        "急了急了", "不会吧不会吧", "就这", "差不多得了",
        "典中典", "蚌埠住了", "笑死", "逆天", "离谱",
        "好家伙", "绝了", "好活", "烂活", "整活",
        "开团", "节奏", "吃瓜", "站队", "洗地",
        "黑子", "孝子", "反串", "钓鱼", "上钩了",
        "红温", "沉默", "光速下播", "今天不播",
        "请假", "身体不舒服", "家里有事", "网炸了", "电脑坏了", "被gank了",
        # 电竞相关
        "LPL", "LCK", "LOL", "英雄联盟",
        "乌兹", "Uzi", "Faker", "TheShy", "Rookie",
        "杰克爱", "阿水", "Knight", "左手",
        "Doinb", "金咕咕", "猴子",
        "Viper", "Scout", "小学弟",
        "Ming", "小明", "Meiko", "田野",
        "厂长", "Clearlove", "7酱",
        "污渍", "永远滴神",
        "世界第一ADC", "虚空冠军",
        "gsl", "狗斯林",
        "皇杂", "猪杂", "鸡杂", "水鬼",
        "科杂", "T1粉丝",
        "韩杂", "精韩",
        # 游戏梗
        "白银", "癌症晚期", "上不去下不来",
        "卡在这里了", "上不去",
        "队友呢", "队友呢队友呢",
        "这波不亏", "小赚",
        "这波血赚", "这波血亏",
        "可以打", "不能打", "撤", "卖",
        "别追了", "追", "一波", "一波了",
        "GG", "投降", "点了", "15", "/ff",
        "打野差距", "中单差距", "AD差距", "辅助差距", "上单差距",
        "意识", "操作", "细节", "拉扯",
        "这波我在第五层", "他在第一层",
        "博弈", "心理战",
        "预判", "反预判", "我预判了你的预判",
    ]
    return streamer_keywords

def fetch_zhihu_hot():
    """获取知乎热榜"""
    try:
        url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.zhihu.com'
        }
        req = urllib.request.Request(url, headers=headers)
        context = create_ssl_context()
        
        with urllib.request.urlopen(req, timeout=15, context=context) as response:
            data = json.loads(response.read().decode('utf-8'))
            memes = []
            anime_keywords = ['动漫', '二次元', '动画', '漫画', '番剧', 'ACG', '鬼灭', '咒术', 
                           '原神', '崩坏', '明日方舟', '碧蓝', '米哈游', 'B站', '哔哩哔哩',
                           '宫崎骏', '新海诚', '柯南', '海贼王', '火影', '进击的巨人']
            if data.get('data'):
                for item in data['data']:
                    title = item.get('target', {}).get('title', '')
                    # 检查是否包含二次元关键词
                    if any(keyword in title for keyword in anime_keywords):
                        memes.append(title)
            return memes[:10]
    except Exception as e:
        print(f"知乎获取失败: {e}")
        return []

def generate_daily_memes():
    """生成每日梗（包括固定经典梗和随机组合）"""
    daily_memes = [
        "今日份的二次元能量",
        "追番时间到",
        "肝游戏了吗",
        "今日抽卡运势",
        "新番更新日",
    ]
    return daily_memes

def load_existing_memes(filepath):
    """加载已有的梗库"""
    if Path(filepath).exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"memes": [], "last_update": "", "stats": {}}
    return {"memes": [], "last_update": "", "stats": {}}

def save_memes(filepath, memes_data):
    """保存梗库"""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(memes_data, f, ensure_ascii=False, indent=2)

def main():
    """主函数：收集并更新梗库"""
    output_file = Path(__file__).parent.parent / "references" / "anime_memes_db.json"
    
    print("🔍 开始收集二次元烂梗...")
    
    # 加载现有数据
    existing = load_existing_memes(output_file)
    existing_memes = set(existing.get("memes", []))
    
    # 收集新梗
    new_memes = []
    
    print("📺 正在获取B站热门...")
    bili_memes = fetch_bilibili_trending()
    new_memes.extend(bili_memes)
    print(f"   获取到 {len(bili_memes)} 个")
    
    print("🔥 正在获取B站热搜...")
    hot_memes = fetch_bilibili_hot_search()
    new_memes.extend(hot_memes)
    print(f"   获取到 {len(hot_memes)} 个")
    
    print("📱 正在获取知乎热榜...")
    zhihu_memes = fetch_zhihu_hot()
    new_memes.extend(zhihu_memes)
    print(f"   获取到 {len(zhihu_memes)} 个")
    
    print("🎮 正在加载Galgame关键词...")
    gal_memes = fetch_galgame_keywords()
    new_memes.extend(gal_memes)
    print(f"   加载了 {len(gal_memes)} 个")
    
    print("📺 正在加载主播圈关键词...")
    streamer_memes = fetch_streamer_keywords()
    new_memes.extend(streamer_memes)
    print(f"   加载了 {len(streamer_memes)} 个")
    
    # 添加每日固定梗
    daily_memes = generate_daily_memes()
    new_memes.extend(daily_memes)
    
    # 去重并合并
    all_memes = list(existing_memes)
    added_count = 0
    for meme in new_memes:
        meme_clean = meme.strip()
        if meme_clean and meme_clean not in existing_memes and len(meme_clean) > 1:
            all_memes.append(meme_clean)
            added_count += 1
    
    # 更新数据
    updated_data = {
        "memes": all_memes[-300:],  # 只保留最近300个
        "last_update": datetime.now().isoformat(),
        "stats": {
            "total": len(all_memes),
            "added_today": added_count,
            "sources": {
                "bilibili_trending": len(bili_memes),
                "bilibili_hot": len(hot_memes),
                "zhihu": len(zhihu_memes),
                "galgame": len(gal_memes),
                "streamer": len(streamer_memes),
                "daily": len(daily_memes)
            }
        }
    }
    
    # 保存
    save_memes(output_file, updated_data)
    
    print(f"\n✅ 收集完成！")
    print(f"   新增: {added_count} 个梗")
    print(f"   总计: {len(all_memes)} 个梗")
    print(f"📁 数据已保存到: {output_file}")
    
    # 显示部分新梗
    if added_count > 0:
        print(f"\n📝 今日新增梗示例:")
        for meme in all_memes[-added_count:][:5]:
            print(f"   - {meme}")
    
    return updated_data

if __name__ == "__main__":
    result = main()
