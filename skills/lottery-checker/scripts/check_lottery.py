#!/usr/bin/env python3
"""中国体育彩票查奖工具 - 检查用户号码是否中奖，生成精美报表"""

import json
import sys
import urllib.request
import urllib.error
import re
from datetime import datetime

# 体彩查询API配置
API_CONFIG = {
    "dlt": {
        "name": "超级大乐透",
        "game_no": "85",
        "url": "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry",
    },
    "pl3": {
        "name": "排列3",
        "game_no": "35",
        "url": "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry",
    },
    "pl5": {
        "name": "排列5",
        "game_no": "350133",
        "url": "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry",
    },
    "7xc": {
        "name": "七星彩",
        "game_no": "04",
        "url": "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry",
    }
}

# 奖级名称映射
PRIZE_LEVEL_NAMES = {
    "dlt": ["一等奖", "二等奖", "三等奖", "四等奖", "五等奖", "六等奖", "七等奖", "八等奖", "九等奖"],
    "pl3": ["直选", "组选3", "组选6"],
    "pl5": ["一等奖"],
    "7xc": ["一等奖", "二等奖", "三等奖", "四等奖", "五等奖", "六等奖"]
}

def format_money(amount):
    """格式化金额"""
    if amount is None or amount == "":
        return "--"
    try:
        # 如果已经是字符串且包含单位
        if isinstance(amount, str):
            if "元" in amount:
                return amount
            amount = float(amount)
        
        if amount >= 100000000:
            return f"{amount/100000000:.2f}亿"
        elif amount >= 10000:
            return f"{amount/10000:.2f}万"
        else:
            return f"{amount:.0f}元"
    except:
        return str(amount)

def format_number(num):
    """格式化数字，添加千分位"""
    if num is None:
        return "--"
    try:
        return f"{int(num):,}"
    except:
        return str(num)

def fetch_latest_draw(lottery_type):
    """获取最新开奖结果（包含详细奖项数据）"""
    config = API_CONFIG.get(lottery_type)
    if not config:
        return None
    
    try:
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        # 构建查询URL
        params = {
            "gameNo": config["game_no"],
            "provinceId": "0",
            "isVerify": "1",
            "termLimits": "1"
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{config['url']}?{query_string}"
        
        req = urllib.request.Request(
            full_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://www.lottery.gov.cn/",
                "Accept": "application/json"
            }
        )
        
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            data = json.loads(resp.read().decode())
        
        if data.get("success") and data.get("value", {}).get("list"):
            latest = data["value"]["list"][0]
            
            # 解析奖项详情
            prize_details = []
            prize_list = latest.get("prizeLevelList", [])
            
            for i, prize in enumerate(prize_list):
                # API 中 prizeLevel 是奖项名称，如"一等奖"
                prize_level = prize.get("prizeLevel", "")
                prize_details.append({
                    "level": prize_level,
                    "name": prize.get("prizeLevelName", ""),
                    "winners": prize.get("stakeCount", 0),
                    "amount": prize.get("stakeAmount", "")
                })
            
            return {
                "lottery_type": lottery_type,
                "lottery_name": config["name"],
                "draw_num": latest.get("lotteryDrawNum"),
                "draw_date": latest.get("lotteryDrawTime"),
                "draw_result": latest.get("lotteryDrawResult", ""),
                "prize_details": prize_details,
                "pool_amount": latest.get("poolBalanceAfterdraw", ""),
                "sales_amount": latest.get("totalSaleAmount", ""),
            }
        return None
    except Exception as e:
        return {"error": str(e)}

def parse_numbers(numbers_str, lottery_type):
    """解析用户输入的号码"""
    numbers_str = numbers_str.strip().replace("，", ",").replace(" ", "")
    
    if lottery_type == "dlt":
        # 大乐透: 前区5个(1-35) + 后区2个(1-12), 格式如 "03,15,22,28,33+05,12"
        match = re.match(r"([\d,]+)\+([\d,]+)", numbers_str)
        if match:
            front = [n.zfill(2) for n in match.group(1).split(",")]
            back = [n.zfill(2) for n in match.group(2).split(",")]
            return {"front": front, "back": back}
    elif lottery_type in ["pl3", "pl5"]:
        # 排列3/5: 纯数字
        nums = re.findall(r"\d", numbers_str)
        expected_len = 3 if lottery_type == "pl3" else 5
        if len(nums) == expected_len:
            return {"numbers": nums}
    elif lottery_type == "7xc":
        # 七星彩: 7个数字
        nums = re.findall(r"\d", numbers_str)
        if len(nums) == 7:
            return {"numbers": nums}
    
    return None

def check_dlt(user_nums, draw_result):
    """检查大乐透中奖"""
    # 处理两种格式: "09 11 19 30 35 | 01 12" 或 "09 11 19 30 35 01 12"
    if "|" in draw_result:
        parts = draw_result.split("|")
        draw_front = parts[0].strip().split()
        draw_back = parts[1].strip().split()
    else:
        # 没有分隔符，前5个是前区，后2个是后区
        nums = draw_result.strip().split()
        if len(nums) >= 7:
            draw_front = nums[:5]
            draw_back = nums[5:7]
        else:
            return {"name": "未中奖", "front_match": 0, "back_match": 0}
    
    user_front = user_nums.get("front", [])
    user_back = user_nums.get("back", [])
    
    front_match = len(set(user_front) & set(draw_front))
    back_match = len(set(user_back) & set(draw_back))
    
    # 匹配规则
    rules = [
        (5, 2, "一等奖"),
        (5, 1, "二等奖"),
        (5, 0, "三等奖"),
        (4, 2, "四等奖"),
        (4, 1, "五等奖"),
        (3, 2, "六等奖"),
        (4, 0, "七等奖"),
        (3, 1, "八等奖"), (2, 2, "八等奖"),
        (3, 0, "九等奖"), (2, 1, "九等奖"), (1, 2, "九等奖"), (0, 2, "九等奖")
    ]
    
    for f, b, name in rules:
        if front_match == f and back_match == b:
            return {"name": name, "front_match": front_match, "back_match": back_match}
    
    return {"name": "未中奖", "front_match": front_match, "back_match": back_match}

def check_pl3(user_nums, draw_result):
    """检查排列3中奖"""
    draw_nums = re.findall(r"\d", draw_result.replace(" ", ""))
    user_nums_list = user_nums.get("numbers", [])
    
    if user_nums_list == draw_nums:
        return {"name": "直选", "match_type": "直选"}
    
    # 组选判断
    user_set = set(user_nums_list)
    draw_set = set(draw_nums)
    
    if user_set == draw_set:
        if len(user_set) == 2:
            return {"name": "组选3", "match_type": "组选3"}
        elif len(user_set) == 3:
            return {"name": "组选6", "match_type": "组选6"}
    
    return {"name": "未中奖", "match_type": "未中奖"}

def check_pl5(user_nums, draw_result):
    """检查排列5中奖"""
    draw_nums = re.findall(r"\d", draw_result.replace(" ", ""))
    user_nums_list = user_nums.get("numbers", [])
    
    if user_nums_list == draw_nums:
        return {"name": "一等奖", "match_type": "直选"}
    
    return {"name": "未中奖", "match_type": "未中奖"}

def check_7xc(user_nums, draw_result):
    """检查七星彩中奖"""
    draw_nums = list(draw_result.replace(" ", "").replace("|", ""))
    user_nums_list = user_nums.get("numbers", [])
    
    # 计算连续匹配位数(从前往后)
    match_count = 0
    for i in range(min(len(user_nums_list), len(draw_nums))):
        if user_nums_list[i] == draw_nums[i]:
            match_count += 1
        else:
            break
    
    # 七星彩奖级
    level_names = ["一等奖", "二等奖", "三等奖", "四等奖", "五等奖", "六等奖"]
    if match_count >= 2:
        level = min(7 - match_count, 5)
        return {"name": level_names[level], "match_count": match_count}
    
    return {"name": "未中奖", "match_count": match_count}

def check_winner(lottery_type, user_nums, draw_result):
    """统一中奖检查入口"""
    if lottery_type == "dlt":
        return check_dlt(user_nums, draw_result)
    elif lottery_type == "pl3":
        return check_pl3(user_nums, draw_result)
    elif lottery_type == "pl5":
        return check_pl5(user_nums, draw_result)
    elif lottery_type == "7xc":
        return check_7xc(user_nums, draw_result)
    return {"name": "未中奖", "match_info": ""}

def generate_ui_report(data):
    """生成漂亮的 UI 文字报表"""
    lottery_name = data.get("lottery_name", "未知")
    draw_num = data.get("draw_num", "")
    draw_date = data.get("draw_date", "")
    draw_result = data.get("draw_result", "")
    user_numbers = data.get("user_numbers", "")
    result = data.get("result") or {}
    prize_details = data.get("prize_details", [])
    pool_amount = data.get("pool_amount", "")
    sales_amount = data.get("sales_amount", "")
    
    # 确保 result 是字典且有 name 键
    if not isinstance(result, dict):
        result = {}
    result_name = result.get("name", "未中奖")
    
    lines = []
    
    # 顶部装饰
    lines.append("╔" + "═" * 58 + "╗")
    lines.append("║" + " " * 15 + "🎰 中国体育彩票查奖报告" + " " * 16 + "║")
    lines.append("╠" + "═" * 58 + "╣")
    
    # 彩种信息
    lines.append(f"║  📋 彩种：{lottery_name:<43}║")
    lines.append(f"║  📅 期号：第 {draw_num} 期" + " " * (39 - len(draw_num)) + "║")
    lines.append(f"║  🕐 日期：{draw_date:<43}║")
    lines.append("╠" + "═" * 58 + "╣")
    
    # 开奖号码
    lines.append("║" + " " * 58 + "║")
    lines.append("║  🎱 开奖号码：" + " " * 42 + "║")
    
    # 格式化开奖号码
    if "|" in draw_result:
        parts = draw_result.split("|")
        front = parts[0].strip()
        back = parts[1].strip() if len(parts) > 1 else ""
        lines.append(f"║      前区：{front:<40}║")
        if back:
            lines.append(f"║      后区：{back:<40}║")
    else:
        lines.append(f"║      {draw_result:<48}║")
    
    lines.append("║" + " " * 58 + "║")
    lines.append("╠" + "═" * 58 + "╣")
    
    # 用户号码
    lines.append("║  📝 您的号码：" + " " * 42 + "║")
    lines.append(f"║      {user_numbers:<48}║")
    lines.append("║" + " " * 58 + "║")
    lines.append("╠" + "═" * 58 + "╣")
    
    # 中奖结果（突出显示）
    is_winner = result_name != "未中奖"
    lines.append("║" + " " * 58 + "║")
    
    if is_winner:
        lines.append("║        🎉🎉🎉  恭喜您中奖啦！  🎉🎉🎉         ║")
        lines.append("║" + " " * 58 + "║")
        lines.append(f"║     🏆 中奖等级：{result_name:<30}║")
        
        # 找到对应奖金
        for prize in prize_details:
            # 使用 level 字段匹配奖项名称
            if result_name in prize.get("level", ""):
                amount = format_money(prize.get("amount", ""))
                lines.append(f"║     💰 单注奖金：{amount:<30}║")
                break
    else:
        lines.append("║              😔  未中奖，再接再厉！               ║")
    
    lines.append("║" + " " * 58 + "║")
    lines.append("╠" + "═" * 58 + "╣")
    
    # 奖级详情表
    lines.append("║" + " " * 58 + "║")
    lines.append("║  📊 本期各奖项中奖情况：" + " " * 32 + "║")
    lines.append("║" + " " * 58 + "║")
    lines.append("║  ┌────────────┬──────────────┬──────────────────┐  ║")
    lines.append("║  │   奖项     │   中奖注数   │    单注奖金      │  ║")
    lines.append("║  ├────────────┼──────────────┼──────────────────┤  ║")
    
    for prize in prize_details[:6]:  # 只显示前6个奖项
        # 使用 level 作为奖项名称（如"一等奖"）
        prize_name = prize.get("level", "")[:8].center(10)
        winners = format_number(prize.get("winners", 0)).center(12)
        amount = format_money(prize.get("amount", ""))[:16].center(16)
        lines.append(f"║  │{prize_name}│{winners}│{amount}│  ║")
    
    lines.append("║  └────────────┴──────────────┴──────────────────┘  ║")
    lines.append("║" + " " * 58 + "║")
    
    # 奖池和销售信息
    if pool_amount:
        lines.append(f"║  💵 奖池滚存：{format_money(pool_amount):<38}║")
    if sales_amount:
        lines.append(f"║  📈 本期销量：{format_money(sales_amount):<38}║")
    
    lines.append("║" + " " * 58 + "║")
    lines.append("╚" + "═" * 58 + "╝")
    
    # 底部提示
    lines.append("")
    lines.append("💡 提示：数据来自中国体彩中心官方API，仅供参考")
    lines.append("📌 实际奖金以当地体彩中心兑奖为准")
    
    return "\n".join(lines)

def generate_batch_report(latest_draw, results):
    """生成批量查询报表（大乐透专用）"""
    lottery_name = latest_draw.get("lottery_name", "超级大乐透")
    draw_num = latest_draw.get("draw_num", "")
    draw_date = latest_draw.get("draw_date", "")
    draw_result = latest_draw.get("draw_result", "")
    prize_details = latest_draw.get("prize_details", [])
    pool_amount = latest_draw.get("pool_amount", "")
    sales_amount = latest_draw.get("sales_amount", "")
    
    lines = []
    
    # 顶部装饰
    lines.append("╔" + "═" * 70 + "╗")
    lines.append("║" + " " * 20 + "🎰 大乐透批量查奖报告" + " " * 21 + "║")
    lines.append("╠" + "═" * 70 + "╣")
    
    # 期号信息
    lines.append(f"║  📅 第 {draw_num} 期    {draw_date}" + " " * (35 - len(draw_num) - len(draw_date)) + "║")
    lines.append("╠" + "═" * 70 + "╣")
    
    # 开奖号码
    lines.append("║  🎱 开奖号码：" + " " * 54 + "║")
    if "|" in draw_result:
        parts = draw_result.split("|")
        front = parts[0].strip()
        back = parts[1].strip() if len(parts) > 1 else ""
        lines.append(f"║      前区：{front:<52}║")
        lines.append(f"║      后区：{back:<52}║")
    else:
        lines.append(f"║      {draw_result:<60}║")
    lines.append("╠" + "═" * 70 + "╣")
    
    # 用户号码对比表
    lines.append("║  📋 您的号码及中奖情况：" + " " * 44 + "║")
    lines.append("║" + " " * 70 + "║")
    lines.append("║  ┌──────┬────────────────────────────┬────────────┬────────┐  ║")
    lines.append("║  │ 序号 │          号码              │  中奖等级  │  状态  │  ║")
    lines.append("║  ├──────┼────────────────────────────┼────────────┼────────┤  ║")
    
    winner_count = 0
    for i, result in enumerate(results, 1):
        numbers = result.get("numbers", "")
        result_name = result.get("result", {}).get("name", "未中奖")
        is_winner = result_name != "未中奖"
        
        if is_winner:
            winner_count += 1
            status = "🎉"
            prize_name = result_name
        else:
            status = "❌"
            prize_name = "-"
        
        # 格式化显示
        num_display = numbers[:26].center(26)
        prize_display = prize_name[:10].center(10)
        lines.append(f"║  │  {i:>2}  │{num_display}│{prize_display}│   {status}   │  ║")
    
    lines.append("║  └──────┴────────────────────────────┴────────────┴────────┘  ║")
    lines.append("║" + " " * 70 + "║")
    
    # 中奖统计
    if winner_count > 0:
        lines.append(f"║  ✅ 中奖统计：共 {winner_count} 注中奖" + " " * (47 - len(str(winner_count))) + "║")
    else:
        lines.append("║  😔 很遗憾，本期未中奖" + " " * 46 + "║")
    
    lines.append("║" + " " * 70 + "║")
    lines.append("╠" + "═" * 70 + "╣")
    
    # 奖项详情
    lines.append("║  📊 本期各奖项中奖情况：" + " " * 44 + "║")
    lines.append("║" + " " * 70 + "║")
    lines.append("║  ┌────────────┬──────────────┬──────────────────┐  ║")
    lines.append("║  │   奖项     │   中奖注数   │    单注奖金      │  ║")
    lines.append("║  ├────────────┼──────────────┼──────────────────┤  ║")
    
    for prize in prize_details[:8]:
        prize_name = prize.get("level", "")[:10].center(10)
        winners = format_number(prize.get("winners", 0)).center(12)
        amount = format_money(prize.get("amount", ""))[:16].center(16)
        lines.append(f"║  │{prize_name}│{winners}│{amount}│  ║")
    
    lines.append("║  └────────────┴──────────────┴──────────────────┘  ║")
    lines.append("║" + " " * 70 + "║")
    
    # 奖池和销售
    if pool_amount:
        lines.append(f"║  💵 奖池滚存：{format_money(pool_amount):<50}║")
    if sales_amount:
        lines.append(f"║  📈 本期销量：{format_money(sales_amount):<50}║")
    
    lines.append("║" + " " * 70 + "║")
    lines.append("╚" + "═" * 70 + "╝")
    lines.append("")
    lines.append("💡 提示：数据来自中国体彩中心官方API，仅供参考")
    lines.append("📌 实际奖金以当地体彩中心兑奖为准")
    
    return "\n".join(lines)

def main():
    """主函数 - 支持批量查询大乐透"""
    if len(sys.argv) > 1:
        args = json.loads(sys.argv[1])
    else:
        args = {}
    
    # 只查询大乐透
    lottery_type = "dlt"
    
    # 支持单号码或多号码列表
    user_numbers = args.get("numbers", [])
    output_format = args.get("format", "ui")  # ui 或 json
    
    # 如果传入的是单个字符串，转换为列表
    if isinstance(user_numbers, str):
        user_numbers = [user_numbers]
    
    if not user_numbers:
        print("❌ 请提供彩票号码")
        print("\n使用示例：")
        print('  单注: python3 check_lottery.py \'{"numbers":"03,15,22,28,33+05,12"}\'')
        print('  多注: python3 check_lottery.py \'{"numbers":["03,15,22,28,33+05,12","01,02,03,04,05+06,07"]}\'')
        return
    
    # 获取最新开奖（只查一次）
    latest_draw = fetch_latest_draw(lottery_type)
    if not latest_draw:
        print("❌ 无法获取最新开奖结果")
        return
    
    if "error" in latest_draw:
        print(f"❌ API错误: {latest_draw['error']}")
        return
    
    # 批量检查每个号码
    results = []
    for numbers in user_numbers:
        parsed_nums = parse_numbers(numbers, lottery_type)
        if parsed_nums:
            result = check_winner(lottery_type, parsed_nums, latest_draw["draw_result"])
            results.append({
                "numbers": numbers,
                "result": result
            })
        else:
            results.append({
                "numbers": numbers,
                "result": {"name": "格式错误"}
            })
    
    # 输出格式选择
    if output_format == "json":
        data = {
            "lottery_name": latest_draw["lottery_name"],
            "draw_num": latest_draw["draw_num"],
            "draw_date": latest_draw["draw_date"],
            "draw_result": latest_draw["draw_result"],
            "results": results,
            "prize_details": latest_draw.get("prize_details", []),
            "pool_amount": latest_draw.get("pool_amount", ""),
            "sales_amount": latest_draw.get("sales_amount", ""),
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        # 生成批量UI报表
        print(generate_batch_report(latest_draw, results))

if __name__ == "__main__":
    main()
