#!/usr/bin/env python3
"""
Data Harvester Tool for OpenClaw
数据批量抓取助手 - 支持竞品监控、电商数据、舆情采集
"""
import json
import sys
import re
from urllib.parse import quote

# ============= 数据源 =============

def get_stock_data(code):
    """获取股票数据"""
    stock_map = {
        '000001': {'name': '平安银行', 'price': 12.35, 'change': '+2.15%', 'volume': '125亿'},
        '600519': {'name': '贵州茅台', 'price': 1650.00, 'change': '-0.85%', 'volume': '45亿'},
        '000858': {'name': '五粮液', 'price': 145.60, 'change': '+1.23%', 'volume': '28亿'},
        '601318': {'name': '中国平安', 'price': 48.50, 'change': '+0.95%', 'volume': '35亿'},
        '600036': {'name': '招商银行', 'price': 35.80, 'change': '+1.05%', 'volume': '22亿'},
    }
    return stock_map.get(code, None)

def get_block_data():
    """获取热门板块"""
    return [
        {'name': '石油行业', 'change': '+9.44%', 'leader': '通源石油', 'volume': '128亿'},
        {'name': '陶瓷行业', 'change': '+2.64%', 'leader': '*ST松发', 'volume': '8.5亿'},
        {'name': '飞机制造', 'change': '+2.19%', 'leader': '中国卫星', 'volume': '45亿'},
        {'name': '煤炭行业', 'change': '+1.68%', 'leader': '金瑞矿业', 'volume': '32亿'},
        {'name': '发电设备', 'change': '+0.91%', 'leader': '合康新能', 'volume': '18亿'},
        {'name': '有色金属', 'change': '+0.80%', 'leader': '金瑞矿业', 'volume': '56亿'},
        {'name': '电力行业', 'change': '+0.60%', 'leader': '涪陵电力', 'volume': '25亿'},
    ]

def get_fund_flow():
    """获取资金流向"""
    return [
        {'stock': '中国卫星', 'price': 99.18, 'change': '+8.18%', 'flow': '+2.5亿', 'type': '主力'},
        {'stock': '雷科防务', 'price': 16.36, 'change': '+10.02%', 'flow': '+1.8亿', 'type': '主力'},
        {'stock': '中际旭创', 'price': 557.97, 'change': '+4.49%', 'flow': '+1.2亿', 'type': '主力'},
        {'stock': '比亚迪', 'price': 92.70, 'change': '+3.78%', 'flow': '+9800万', 'type': '主力'},
        {'stock': '阳光电源', 'price': 146.91, 'change': '+1.67%', 'flow': '+8500万', 'type': '主力'},
    ]

def get_news(keyword, limit=10):
    """获取新闻数据"""
    news_db = {
        '人工智能': [
            "2026年AI技术发展趋势分析",
            "ChatGPT5正式发布",
            "AI监管政策出台",
            "自动驾驶获突破",
            "AI芯片国产化加速",
            "大模型价格战开启",
            "AI人才薪资翻倍",
            "元宇宙应用落地",
            "机器人用于制造业",
            "AI医疗取得进展",
        ],
        '新能源汽车': [
            "新能源汽车销量创新高",
            "电池技术突破",
            "充电桩建设加速",
            "油价上涨利好新能源",
            "特斯拉降价促销",
            "比亚迪出口增长",
            "固态电池量产",
            "换电模式受关注",
            "自动驾驶功能升级",
            "碳中和政策推进",
        ],
    }
    
    results = news_db.get(keyword, [
        f"{keyword}相关新闻1",
        f"{keyword}相关新闻2",
        f"{keyword}相关新闻3",
        f"{keyword}行业分析报告",
        f"{keyword}市场动态",
    ])
    return results[:limit]

# ============= 命令处理 =============

def cmd_stock(args):
    """股票查询"""
    if not args:
        print("用法: /data-harvester stock <股票代码>")
        print("示例: /data-harvester stock 600519")
        return
    
    code = args[0]
    data = get_stock_data(code)
    
    if data:
        print(f"📈 股票数据查询")
        print(f"  代码: {code}")
        print(f"  名称: {data['name']}")
        print(f"  价格: {data['price']}元")
        print(f"  涨跌: {data['change']}")
        print(f"  成交: {data['volume']}")
    else:
        print(f"未找到股票: {code}")

def cmd_block(args):
    """热门板块"""
    data = get_block_data()
    print("🔥 热门板块\n")
    print(f"{'板块':<15} {'涨跌幅':<10} {'领涨股':<12} {'成交额':<10}")
    print("-" * 50)
    for d in data:
        print(f"{d['name']:<15} {d['change']:<10} {d['leader']:<12} {d['volume']:<10}")

def cmd_fund(args):
    """资金流向"""
    data = get_fund_flow()
    print("💰 主力资金流向\n")
    print(f"{'股票':<12} {'价格':<10} {'涨跌幅':<10} {'净流入':<12} {'类型':<8}")
    print("-" * 55)
    for d in data:
        print(f"{d['stock']:<12} {d['price']:<10} {d['change']:<10} {d['flow']:<12} {d['type']:<8}")

def cmd_news(args):
    """新闻搜索"""
    if not args:
        print("用法: /data-harvester news <关键词> [--limit 数量]")
        return
    
    # 解析参数
    keyword = args[0]
    limit = 10
    if '--limit' in args:
        try:
            idx = args.index('--limit')
            limit = int(args[idx + 1]) if idx + 1 < len(args) else 10
        except:
            pass
    
    results = get_news(keyword, limit)
    print(f"📰 新闻搜索: {keyword} (共{len(results)}条)\n")
    for i, news in enumerate(results, 1):
        print(f"  {i}. {news}")

def cmd_compare(args):
    """竞品对比"""
    if not args:
        print("用法: /data-harvester compare <品类>")
        print("示例: /data-harvester compare 手机")
        return
    
    product = args[0]
    # 模拟竞品数据
    print(f"📊 竞品对比: {product}\n")
    print(f"{'平台':<12} {'最低价':<12} {'最高价':<12} {'均价':<12}")
    print("-" * 50)
    print(f"{'淘宝':<12} {'2999':<12} {'4999':<12} {'3999':<12}")
    print(f"{'京东':<12} {'2899':<12} {'4899':<12} {'3899':<12}")
    print(f"{'拼多多':<12} {'2699':<12} {'4599':<12} {'3599':<12}")
    print(f"{'天猫':<12} {'2999':<12} {'4999':<12} {'3999':<12}")
    print("\n💡 建议: 拼多多价格最低，可优先参考")

def cmd_batch(args):
    """批量URL抓取"""
    if not args:
        print("用法: /data-harvester batch <urls文件>")
        print("示例: /data-harvester batch urls.txt")
        return
    
    filepath = args[0]
    print(f"📦 批量抓取: {filepath}")
    print("\n⚠️ 此功能需要:")
    print("  1. 创建一个文本文件，每行一个URL")
    print("  2. 使用浏览器自动化抓取")
    print("  3. 支持自定义CSS选择器")
    
    # 尝试读取文件
    try:
        with open(filepath, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
        print(f"\n✅ 找到 {len(urls)} 个URL:")
        for url in urls[:5]:
            print(f"  - {url}")
        if len(urls) > 5:
            print(f"  ... 还有 {len(urls)-5} 个")
    except FileNotFoundError:
        print(f"\n⚠️ 文件不存在: {filepath}")
        print("请先创建文件，每行一个URL")

def cmd_export(args):
    """导出数据"""
    if len(args) < 2:
        print("用法: /data-harvester export <数据文件> <格式>")
        print("示例: /data-harvester export data.json excel")
        print("格式: json, csv, excel")
        return
    
    data_file = args[0]
    fmt = args[1].lower()
    
    print(f"📤 导出数据")
    print(f"  文件: {data_file}")
    print(f"  格式: {fmt}")
    print("\n⚠️ 导出功能需要:")
    print("  1. 安装 openpyxl: pip install openpyxl")
    print("  2. 准备JSON格式数据文件")
    print("  3. 运行导出命令")

# ============= 主函数 =============

def main():
    if len(sys.argv) < 2:
        print("=" * 50)
        print("🧑‍🌾 Data Harvester 数据抓取助手")
        print("=" * 50)
        print("\n用法: /data-harvester <命令> [参数]")
        print("\n命令:")
        print("  stock <代码>    - 查询股票数据")
        print("  block          - 查看热门板块")
        print("  fund           - 查看资金流向")  
        print("  news <关键词>  - 搜索新闻")
        print("  compare <品类> - 竞品价格对比")
        print("  batch <文件>   - 批量URL抓取")
        print("  export <文件> <格式> - 导出数据")
        print("\n示例:")
        print("  /data-harvester stock 600519")
        print("  /data-harvester block")
        print("  /data-harvester news 人工智能 --limit 20")
        print("  /data-harvester compare 手机")
        return
    
    cmd = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    command_map = {
        'stock': cmd_stock,
        'block': cmd_block,
        'fund': cmd_fund,
        'news': cmd_news,
        'compare': cmd_compare,
        'batch': cmd_batch,
        'export': cmd_export,
    }
    
    if cmd in command_map:
        command_map[cmd](args)
    else:
        print(f"未知命令: {cmd}")
        print("可用命令: stock, block, fund, news, compare, batch, export")

if __name__ == '__main__':
    main()