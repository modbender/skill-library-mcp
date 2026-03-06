"""
港股新股中签率预测算法

基于公开资料推导的中签率估算模型。

核心原理：
1. 基于分配机制（A/B）和超购倍数计算基础一手中签率
2. 应用价格调整因子（低价股中签率略高）
3. 考虑手数需求乘数（甲组一手优先，乙组大额按比例）
4. 使用几何分布计算多手中签概率

机制说明：
- 机制A（有回拨）：公开发售占比可从3.5%最高回拨至50%
- 机制B（无回拨）：公开发售固定比例，通常5-10%

参考：
- 港交所上市规则第18章
"""

import argparse
import json
import math
from typing import Any, Optional, TypedDict

# ============================================================
# 核心常量（基于历史数据拟合）
# ============================================================

# 机制系数 K
# 机制A（有回拨）：公开发售比例会随超购动态调整，所以 K 较小
# 机制B（无回拨）：公开发售固定，需要更大的 K 来补偿
K_MECHANISM_A = 0.02
K_MECHANISM_B = 1.65

# 价格调整区间
PRICE_ADJ_MIN = 0.85
PRICE_ADJ_MAX = 1.15
PRICE_ADJ_BASE = 15.0  # 基准价格（港元）

# 概率边界
MIN_PROBABILITY = 1e-6
MAX_BASE_PROBABILITY = 0.99  # 最高基础概率

# 甲乙组分界线
GROUP_A_MAX_AMOUNT = 5_000_000  # 500万港元


# ============================================================
# 类型定义
# ============================================================

class AllotmentResult(TypedDict):
    """中签预测结果"""
    probability: float        # 至少中一手的概率 (0-1)
    probability_pct: str      # 概率百分比字符串
    expected_lots: str        # 预期中签手数描述
    group: str                # 甲组/乙组
    base_p1: float           # 基础一手中签率
    lots: int                # 申购手数
    mechanism: str           # 分配机制 A/B


class IPOData(TypedDict, total=False):
    """IPO 数据结构"""
    code: str
    name: str
    offer_price: float       # 发售价（港元）
    lot_size: int           # 每手股数
    entry_fee: float        # 入场费（港元）
    mechanism: str          # "A" 或 "B"
    public_ratio: float     # 公开发售比例 (0-1)


# ============================================================
# 核心算法函数
# ============================================================

def get_mechanism_k(mechanism: str) -> float:
    """
    获取分配机制系数 K
    
    Args:
        mechanism: "A"（有回拨）或 "B"（无回拨）
        
    Returns:
        机制系数 K
        
    算法说明：
    - 机制A：公开发售从3.5%起，超购后最高可回拨至50%
    - 机制B：公开发售固定（通常5-10%），无回拨机制
    - K 值决定了基础中签率的计算权重
    """
    return K_MECHANISM_B if mechanism.upper() == "B" else K_MECHANISM_A


def calculate_price_adjustment(offer_price: float) -> float:
    """
    计算价格调整因子
    
    Args:
        offer_price: 发售价（港元）
        
    Returns:
        价格调整因子 (0.85 ~ 1.15)
        
    算法说明：
    - 基准价格 15 港元
    - 低价股（<15）调整因子 > 1，略微提高中签率
    - 高价股（>15）调整因子 < 1，略微降低中签率
    - 调整幅度：每偏离1港元，调整1%
    - 上下限：0.85 ~ 1.15（最大±15%调整）
    """
    raw_adj = 1 + (PRICE_ADJ_BASE - offer_price) / 100
    return max(PRICE_ADJ_MIN, min(PRICE_ADJ_MAX, raw_adj))


def base_p1(mechanism: str, offer_price: float, oversub_multiple: float) -> float:
    """
    计算基础一手中签率
    
    Args:
        mechanism: 分配机制 "A" 或 "B"
        offer_price: 发售价（港元）
        oversub_multiple: 超额认购倍数
        
    Returns:
        基础一手中签率 (0 ~ 1)
        
    算法说明：
    公式：P1 = K × price_adj / oversub
    - K：机制系数（A=0.02, B=1.65）
    - price_adj：价格调整因子
    - oversub：超购倍数（至少为1）
    
    示例（机制A，价格15元）：
    - 10x 超购：0.02 × 1.0 / 10 = 0.002 = 0.2%
    - 100x 超购：0.02 × 1.0 / 100 = 0.0002 = 0.02%
    - 500x 超购：0.02 × 1.0 / 500 = 0.00004 = 0.004%
    """
    k = get_mechanism_k(mechanism)
    price_adj = calculate_price_adjustment(offer_price)
    
    # 确保超购倍数至少为1
    oversub = max(1.0, oversub_multiple)
    
    # 基础概率计算
    prob = k * price_adj / oversub
    
    # 限制概率范围
    return max(MIN_PROBABILITY, min(MAX_BASE_PROBABILITY, prob))


def lot_demand_multiplier(lots: int, is_group_a: bool) -> float:
    """
    计算手数需求乘数
    
    Args:
        lots: 申购手数
        is_group_a: 是否甲组
        
    Returns:
        需求乘数
        
    算法说明：
    甲组（红鞋机制）：
    - 1手：乘数 3.0（一人一手优先）
    - 2-100手：乘数 2.5
    - 101-400手：乘数 2.0
    - 401-1000手：乘数 1.5
    - 1000+手：乘数 1.0
    
    乙组（按比例分配）：
    - ≤2000手：乘数 1.2（小额乙组略有优势）
    - 2001-5000手：乘数 1.0
    - >5000手：乘数 0.8（大额稀释）
    
    原理：甲组一手优先分配（红鞋），多手边际效用递减
          乙组按比例分配，但极大额可能被稀释
    """
    if is_group_a:
        if lots <= 1:
            return 3.0
        if lots <= 100:
            return 2.5
        if lots <= 400:
            return 2.0
        if lots <= 1000:
            return 1.5
        return 1.0
    else:
        if lots <= 2000:
            return 1.2
        if lots <= 5000:
            return 1.0
        return 0.8


def calculate_win_probability(lots: int, supply_ratio: float) -> float:
    """
    计算至少中一手的概率（几何分布）
    
    Args:
        lots: 申购手数
        supply_ratio: 单手供给率（≈基础中签率）
        
    Returns:
        至少中一手的概率 (0 ~ 1)
        
    算法说明：
    假设每手独立抽签，中签概率为 p（supply_ratio）
    至少中一手 = 1 - 一手都不中
    P(至少中1手) = 1 - (1 - p)^n
    
    这是几何分布的累积分布函数
    """
    if lots <= 0:
        return 0.0
    if supply_ratio <= 0:
        return 0.0
    if supply_ratio >= 1:
        return 1.0
    
    # 几何分布：至少成功一次的概率
    return 1 - (1 - supply_ratio) ** lots


def calculate_expected_lots(lots: int, supply_ratio: float, multiplier: float) -> float:
    """
    计算预期中签手数
    
    Args:
        lots: 申购手数
        supply_ratio: 单手供给率
        multiplier: 需求乘数
        
    Returns:
        预期中签手数
    """
    # 期望值 = n × p × multiplier
    expected = lots * supply_ratio * multiplier
    return max(0.0, expected)


def format_expected_lots(expected: float) -> str:
    """
    格式化预期中签手数为可读字符串
    
    Args:
        expected: 预期中签手数
        
    Returns:
        描述字符串
    """
    if expected < 0.01:
        return "极难中签"
    if expected < 0.1:
        return f"约 {expected:.3f} 手（较难）"
    if expected < 0.5:
        return f"约 {expected:.2f} 手"
    if expected < 1.0:
        return f"约 {expected:.2f} 手（有望）"
    if expected < 2.0:
        return f"约 {expected:.1f} 手（大概率）"
    return f"约 {expected:.1f} 手（高概率多签）"


def determine_group(lots: int, entry_fee: float) -> tuple[bool, str]:
    """
    判断甲组还是乙组
    
    Args:
        lots: 申购手数
        entry_fee: 每手入场费（港元）
        
    Returns:
        (is_group_a, group_name)
    """
    total_amount = lots * entry_fee
    is_group_a = total_amount < GROUP_A_MAX_AMOUNT
    group_name = "甲组" if is_group_a else "乙组"
    return is_group_a, group_name


# ============================================================
# 主预测函数
# ============================================================

def predict_allotment(
    ipo_data: IPOData,
    oversub_multiple: float,
    lots: int,
    is_group_a: Optional[bool] = None
) -> AllotmentResult:
    """
    预测中签率
    
    Args:
        ipo_data: IPO 数据，包含 offer_price, mechanism, entry_fee 等
        oversub_multiple: 超额认购倍数
        lots: 申购手数
        is_group_a: 是否甲组（None 时自动判断）
        
    Returns:
        AllotmentResult 字典，包含：
        - probability: 中签概率 (0-1)
        - probability_pct: 概率百分比字符串
        - expected_lots: 预期中签手数描述
        - group: 甲组/乙组
        - base_p1: 基础一手中签率
        - lots: 申购手数
        - mechanism: 分配机制
        
    使用示例：
        >>> ipo = {"offer_price": 10.0, "mechanism": "A", "entry_fee": 5050}
        >>> result = predict_allotment(ipo, oversub_multiple=100, lots=1)
        >>> print(f"中签率: {result['probability_pct']}")
    """
    # 提取参数
    offer_price = ipo_data.get("offer_price", 10.0)
    mechanism = ipo_data.get("mechanism", "A")
    entry_fee = ipo_data.get("entry_fee", 5000.0)
    
    # 判断甲乙组
    if is_group_a is None:
        is_group_a, group = determine_group(lots, entry_fee)
    else:
        group = "甲组" if is_group_a else "乙组"
    
    # 计算基础一手中签率
    p1 = base_p1(mechanism, offer_price, oversub_multiple)
    
    # 获取手数需求乘数
    multiplier = lot_demand_multiplier(lots, is_group_a)
    
    # 调整后的单手供给率
    adjusted_supply_ratio = p1 * multiplier
    adjusted_supply_ratio = min(adjusted_supply_ratio, 0.99)  # 上限
    
    # 计算至少中一手的概率
    win_prob = calculate_win_probability(lots, adjusted_supply_ratio)
    
    # 计算预期中签手数
    expected = calculate_expected_lots(lots, p1, multiplier)
    expected_str = format_expected_lots(expected)
    
    # 格式化概率
    if win_prob < 0.0001:
        prob_pct = f"{win_prob * 100:.4f}%"
    elif win_prob < 0.01:
        prob_pct = f"{win_prob * 100:.3f}%"
    elif win_prob < 0.1:
        prob_pct = f"{win_prob * 100:.2f}%"
    else:
        prob_pct = f"{win_prob * 100:.1f}%"
    
    return {
        "probability": round(win_prob, 6),
        "probability_pct": prob_pct,
        "expected_lots": expected_str,
        "group": group,
        "base_p1": round(p1, 8),
        "lots": lots,
        "mechanism": mechanism
    }


def predict_allotment_table(
    ipo_data: IPOData,
    oversub_multiple: float,
    lot_levels: Optional[list[int]] = None
) -> list[AllotmentResult]:
    """
    生成多档位中签率表
    
    Args:
        ipo_data: IPO 数据
        oversub_multiple: 超额认购倍数
        lot_levels: 手数档位列表（默认常用档位）
        
    Returns:
        各档位的 AllotmentResult 列表
    """
    if lot_levels is None:
        # 默认档位：甲组常用 + 乙组入门
        entry_fee = ipo_data.get("entry_fee", 5000.0)
        
        # 甲组档位
        lot_levels = [1, 2, 5, 10, 20, 50, 100]
        
        # 甲尾（接近500万）
        max_a_lots = int(4_990_000 / entry_fee)
        if max_a_lots > 100:
            lot_levels.append(max_a_lots)
        
        # 乙组入门档
        b_entry_lots = int(5_000_000 / entry_fee) + 1
        lot_levels.append(b_entry_lots)
    
    results = []
    for lots in lot_levels:
        result = predict_allotment(ipo_data, oversub_multiple, lots)
        results.append(result)
    
    return results


def format_allotment_result(result: AllotmentResult, entry_fee: float = 5000) -> str:
    """
    格式化单个预测结果
    
    Args:
        result: 预测结果
        entry_fee: 每手入场费
        
    Returns:
        格式化字符串
    """
    amount = result["lots"] * entry_fee
    if amount >= 1_000_000:
        amount_str = f"{amount / 1_000_000:.1f}M"
    else:
        amount_str = f"{amount / 1000:.0f}K"
    
    return (
        f"{result['lots']:>5}手 │ {amount_str:>6} │ "
        f"{result['probability_pct']:>8} │ {result['group']} │ {result['expected_lots']}"
    )


def format_allotment_table(
    results: list[AllotmentResult],
    ipo_data: IPOData,
    oversub_multiple: float
) -> str:
    """
    格式化完整中签率表
    
    Args:
        results: 预测结果列表
        ipo_data: IPO 数据
        oversub_multiple: 超购倍数
        
    Returns:
        格式化的表格字符串
    """
    entry_fee = ipo_data.get("entry_fee", 5000.0)
    name = ipo_data.get("name", "未知")
    code = ipo_data.get("code", "")
    mechanism = ipo_data.get("mechanism", "A")
    
    lines = [
        f"📊 中签率预测表 - {name} ({code})",
        f"   超购: {oversub_multiple}x | 机制: {mechanism} | 入场费: {entry_fee:,.0f} HKD",
        "",
        "  手数  │  金额  │   中签率   │ 分组 │ 预期",
        "────────┼────────┼────────────┼──────┼─────────────"
    ]
    
    for result in results:
        lines.append(format_allotment_result(result, entry_fee))
    
    lines.extend([
        "",
        "⚠️ 基于 TradeSmart 算法估算，实际以官方公告为准",
        f"   算法参数: K_A={K_MECHANISM_A}, K_B={K_MECHANISM_B}"
    ])
    
    return "\n".join(lines)


# ============================================================
# CLI 入口
# ============================================================

def main(argv=None):
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="港股新股中签率预测（TradeSmart 算法）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 单次预测
  python allotment.py --price 10 --oversub 100 --lots 1
  
  # 生成多档位表
  python allotment.py --price 10 --oversub 500 --table
  
  # 指定机制B（无回拨）
  python allotment.py --price 20 --oversub 50 --lots 10 --mechanism B
  
  # JSON 输出
  python allotment.py --price 15 --oversub 200 --lots 5 --json
"""
    )
    
    parser.add_argument("--price", type=float, default=10.0,
                        help="发售价（港元），默认 10")
    parser.add_argument("--lot-size", type=int, default=500,
                        help="每手股数，默认 500")
    parser.add_argument("--oversub", type=float, required=True,
                        help="超额认购倍数")
    parser.add_argument("--lots", type=int, default=1,
                        help="申购手数，默认 1")
    parser.add_argument("--mechanism", choices=["A", "B"], default="A",
                        help="分配机制：A（有回拨）或 B（无回拨），默认 A")
    parser.add_argument("--group-a", action="store_true",
                        help="强制甲组计算")
    parser.add_argument("--group-b", action="store_true",
                        help="强制乙组计算")
    parser.add_argument("--table", action="store_true",
                        help="生成多档位中签率表")
    parser.add_argument("--json", action="store_true",
                        help="JSON 格式输出")
    parser.add_argument("--name", type=str, default="测试IPO",
                        help="IPO 名称（用于显示）")
    parser.add_argument("--code", type=str, default="",
                        help="股票代码")
    
    args = parser.parse_args(argv)
    
    # 构建 IPO 数据
    entry_fee = args.price * args.lot_size * 1.01  # 加1%手续费估算
    ipo_data: IPOData = {
        "code": args.code,
        "name": args.name,
        "offer_price": args.price,
        "lot_size": args.lot_size,
        "entry_fee": entry_fee,
        "mechanism": args.mechanism
    }
    
    # 判断强制分组
    is_group_a = None
    if args.group_a:
        is_group_a = True
    elif args.group_b:
        is_group_a = False
    
    if args.table:
        # 生成多档位表
        results = predict_allotment_table(ipo_data, args.oversub)
        
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(format_allotment_table(results, ipo_data, args.oversub))
    else:
        # 单次预测
        result = predict_allotment(ipo_data, args.oversub, args.lots, is_group_a)
        
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"📊 中签率预测")
            print(f"   IPO: {args.name}")
            print(f"   发售价: {args.price} HKD | 机制: {args.mechanism}")
            print(f"   超购: {args.oversub}x | 申购: {args.lots}手")
            print()
            print(f"   🎯 中签率: {result['probability_pct']}")
            print(f"   📦 预期: {result['expected_lots']}")
            print(f"   👥 分组: {result['group']}")
            print(f"   📐 基础P1: {result['base_p1']:.8f}")


if __name__ == "__main__":
    main()
