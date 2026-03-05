from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Portion:
    grams: float
    note: str

DEFAULT_PORTIONS = {
    "米饭": {
        "碗": Portion(200, "默认：熟米饭 1碗≈200g"),
        "小碗": Portion(150, "默认：熟米饭 小碗≈150g"),
        "大碗": Portion(260, "默认：熟米饭 大碗≈260g"),
    },
    "面条": {
        "碗": Portion(220, "默认：熟面条 1碗≈220g"),
    },
    "燕麦": {
        "勺": Portion(10, "默认：燕麦 1汤勺≈10g"),
    },
    "鸡蛋": {
        "个": Portion(50, "默认：鸡蛋 1个可食部分≈50g"),
    },
    "鸡胸肉": {
        "掌": Portion(120, "默认：鸡胸肉 1掌≈120g"),
    },
    "牛奶": {
        "杯": Portion(250, "默认：牛奶 1杯≈250ml≈250g"),
    },
    "香蕉": {
        "根": Portion(120, "默认：香蕉 1根可食部分≈120g"),
    },
}

UNIT_ALIASES = {
    "克": "g", "g": "g",
    "千克": "kg", "kg": "kg",
    "毫升": "ml", "ml": "ml",
    "升": "l", "l": "l",
    "碗": "碗", "小碗": "小碗", "大碗": "大碗",
    "杯": "杯",
    "勺": "勺", "汤勺": "勺",
    "个": "个", "颗": "个",
    "根": "根",
    "掌": "掌",
}

def normalize_unit(u: str) -> str:
    u = u.strip().lower()
    return UNIT_ALIASES.get(u, u)

def to_grams(name: str, qty: float, unit: str):
    unit = normalize_unit(unit)

    if unit == "g":
        return qty, "单位已是g"
    if unit == "kg":
        return qty * 1000.0, "kg→g"
    if unit == "ml":
        return qty * 1.0, "ml≈g（近似）"
    if unit == "l":
        return qty * 1000.0, "l→ml≈g（近似）"

    for key, portion_map in DEFAULT_PORTIONS.items():
        if key in name:
            p = portion_map.get(unit)
            if p:
                return qty * p.grams, p.note

    return None, f"无法将单位'{unit}'自动换算为g"

AMOUNT_RE = re.compile(r"(?P<qty>\d+(\.\d+)?)\s*(?P<unit>[a-zA-Z\u4e00-\u9fff]+)")
