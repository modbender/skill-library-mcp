#!/usr/bin/env python3
"""
MBTI 计分算法
用于计算 AI 智能体的 MBTI 人格类型
"""

import json
from datetime import datetime
from pathlib import Path

# 维度映射：每个问题选 A 对应的维度倾向
SCORING_MAP = {
    "EI": {  # E = 选A, I = 选B
        "E": {"option": "A", "questions": [1, 8, 15, 22, 29, 36, 43, 50, 57, 64]},
        "I": {"option": "B", "questions": [1, 8, 15, 22, 29, 36, 43, 50, 57, 64]},
    },
    "SN": {  # S = 选A, N = 选B
        "S": {"option": "A", "questions": [2, 3, 9, 10, 16, 17, 23, 24, 30, 31, 37, 38, 44, 45, 51, 52, 58, 59, 65, 66]},
        "N": {"option": "B", "questions": [2, 3, 9, 10, 16, 17, 23, 24, 30, 31, 37, 38, 44, 45, 51, 52, 58, 59, 65, 66]},
    },
    "TF": {  # T = 选A, F = 选B
        "T": {"option": "A", "questions": [4, 5, 11, 12, 18, 19, 25, 26, 32, 33, 39, 40, 46, 47, 53, 54, 61, 62, 67, 68]},
        "F": {"option": "B", "questions": [4, 5, 11, 12, 18, 19, 25, 26, 32, 33, 39, 40, 46, 47, 53, 54, 61, 62, 67, 68]},
    },
    "JP": {  # J = 选A, P = 选B
        "J": {"option": "A", "questions": [6, 7, 13, 14, 20, 21, 27, 28, 34, 35, 41, 42, 48, 49, 55, 56, 60, 63, 69, 70]},
        "P": {"option": "B", "questions": [6, 7, 13, 14, 20, 21, 27, 28, 34, 35, 41, 42, 48, 49, 55, 56, 60, 63, 69, 70]},
    },
}

TYPE_DESCRIPTIONS = {
    "INTJ": {"name": "建筑师", "description": "战略规划者，独立思考，追求效率与完美", "emoji": "🏰"},
    "INTP": {"name": "逻辑学家", "description": "理论构建者，好奇心驱动，善于分析复杂问题", "emoji": "🔬"},
    "ENTJ": {"name": "指挥官", "description": "高效执行者，目标导向，天生的领导者", "emoji": "⚡"},
    "ENTP": {"name": "辩论家", "description": "创新探索者，挑战常规，善于发现新可能", "emoji": "🎭"},
    "INFJ": {"name": "提倡者", "description": "理想主义者，深度洞察，追求意义与连接", "emoji": "🔮"},
    "INFP": {"name": "调停者", "description": "价值守护者，真诚创造，追求真实与意义", "emoji": "🦋"},
    "ENFJ": {"name": "主人公", "description": "魅力领袖，激励他人，善于建立连接", "emoji": "🌟"},
    "ENFP": {"name": "竞选者", "description": "热情探索者，启发灵感，充满可能性", "emoji": "✨"},
    "ISTJ": {"name": "物流师", "description": "可靠执行者，事实导向，尽职尽责", "emoji": "📋"},
    "ISFJ": {"name": "守卫者", "description": "忠诚守护者，细节关怀，温暖支持", "emoji": "🛡️"},
    "ESTJ": {"name": "总经理", "description": "高效管理者，秩序维护，务实执行", "emoji": "📊"},
    "ESFJ": {"name": "执政官", "description": "社交协调者，和谐追求，关心他人", "emoji": "💝"},
    "ISTP": {"name": "鉴赏家", "description": "实用技师，灵活应对，善于解决问题", "emoji": "🔧"},
    "ISFP": {"name": "探险家", "description": "艺术表达者，自由灵魂，追求美感", "emoji": "🎨"},
    "ESTP": {"name": "企业家", "description": "行动派，风险承担，活在当下", "emoji": "🚀"},
    "ESFP": {"name": "表演者", "description": "活力四射，享受当下，感染他人", "emoji": "🎪"},
}


def calculate_mbti(responses: dict) -> dict:
    """
    计算 MBTI 类型
    
    Args:
        responses: {1: "A", 2: "B", ...} 格式的答案
    
    Returns:
        包含 MBTI 类型、各维度得分、描述的字典
    """
    # 初始化计分
    scores = {
        "E": 0, "I": 0,
        "S": 0, "N": 0,
        "T": 0, "F": 0,
        "J": 0, "P": 0,
    }
    
    # 计算各维度得分
    for q_id, choice in responses.items():
        q_id = int(q_id)
        choice = choice.upper()
        
        # 检查每个维度
        for dim, traits in SCORING_MAP.items():
            for trait, mapping in traits.items():
                if q_id in mapping["questions"]:
                    if mapping["option"] == choice:
                        scores[trait] += 1
    
    # 确定各维度倾向
    result_type = ""
    dimension_scores = {}
    
    # E/I
    e_total = scores["E"] + scores["I"]
    if e_total > 0:
        e_pct = round(scores["E"] / e_total * 100)
        i_pct = 100 - e_pct
        result_type += "E" if scores["E"] >= scores["I"] else "I"
        dimension_scores["EI"] = {"E": e_pct, "I": i_pct}
    else:
        result_type += "I"  # 默认内向
        dimension_scores["EI"] = {"E": 50, "I": 50}
    
    # S/N
    s_total = scores["S"] + scores["N"]
    if s_total > 0:
        s_pct = round(scores["S"] / s_total * 100)
        n_pct = 100 - s_pct
        result_type += "S" if scores["S"] >= scores["N"] else "N"
        dimension_scores["SN"] = {"S": s_pct, "N": n_pct}
    else:
        result_type += "N"  # 默认直觉
        dimension_scores["SN"] = {"S": 50, "N": 50}
    
    # T/F
    t_total = scores["T"] + scores["F"]
    if t_total > 0:
        t_pct = round(scores["T"] / t_total * 100)
        f_pct = 100 - t_pct
        result_type += "T" if scores["T"] >= scores["F"] else "F"
        dimension_scores["TF"] = {"T": t_pct, "F": f_pct}
    else:
        result_type += "F"  # 默认情感
        dimension_scores["TF"] = {"T": 50, "F": 50}
    
    # J/P
    j_total = scores["J"] + scores["P"]
    if j_total > 0:
        j_pct = round(scores["J"] / j_total * 100)
        p_pct = 100 - j_pct
        result_type += "J" if scores["J"] >= scores["P"] else "P"
        dimension_scores["JP"] = {"J": j_pct, "P": p_pct}
    else:
        result_type += "P"  # 默认知觉
        dimension_scores["JP"] = {"J": 50, "P": 50}
    
    # 获取类型描述
    type_info = TYPE_DESCRIPTIONS.get(result_type, {
        "name": "未知",
        "description": "无法确定",
        "emoji": "❓"
    })
    
    return {
        "type": result_type,
        "type_name": type_info["name"],
        "type_emoji": type_info["emoji"],
        "description": type_info["description"],
        "dimensions": dimension_scores,
        "raw_scores": scores,
    }


def format_report(result: dict, agent_name: str = "Agent") -> str:
    """格式化测评报告"""
    lines = [
        f"# MBTI 测评报告",
        f"",
        f"**被测智能体**: {agent_name}",
        f"**测评时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"",
        f"---",
        f"",
        f"## 测评结果",
        f"",
        f"### {result['type_emoji']} {result['type']} — {result['type_name']}",
        f"",
        f"> {result['description']}",
        f"",
        f"### 维度分析",
        f"",
        f"| 维度 | 倾向 | 得分 |",
        f"|------|------|------|",
    ]
    
    dim_map = {
        "EI": ("外向", "内向"),
        "SN": ("实感", "直觉"),
        "TF": ("思考", "情感"),
        "JP": ("判断", "知觉"),
    }
    
    for dim, (left, right) in dim_map.items():
        scores = result["dimensions"][dim]
        left_key, right_key = dim[0], dim[1]
        tendency = left if scores[left_key] >= scores[right_key] else right
        lines.append(f"| {left}/{right} | {tendency} | {scores[left_key]}% / {scores[right_key]}% |")
    
    lines.extend([
        f"",
        f"### 原始得分",
        f"",
        f"```json",
        json.dumps(result["raw_scores"], indent=2),
        f"```",
    ])
    
    return "\n".join(lines)


def main():
    """示例：使用预设答案测试计分"""
    # 示例答案（INFP 倾向）
    sample_responses = {
        1: "B",   # I - 与少数熟识的人交流
        2: "B",   # N - 投机的
        3: "A",   # N - 想入非非
        4: "B",   # F - 情感
        5: "B",   # F - 触动心灵的感悟
        6: "B",   # P - 随性工作
        7: "B",   # P - 冲动行事
        8: "B",   # I - 早早离开
        9: "B",   # N - 富有想象力的人
        10: "B",  # N - 可能的事物
        # ... 可以继续添加更多答案
    }
    
    result = calculate_mbti(sample_responses)
    print(format_report(result, "测试智能体"))


if __name__ == "__main__":
    main()
