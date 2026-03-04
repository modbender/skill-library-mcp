"""Chinese → English food name translation acceleration cache.

This module provides a built-in dictionary (~200 entries) as an
**acceleration layer** for the translation workflow. It is NOT the
primary translation mechanism.

Primary translation path:
  Non-English input → Decomposer Sub-agent (LLM) → English food names

This dictionary serves as:
  - Fast path for `lookup_food` when called directly with known Chinese names
  - Fallback inside Python code when the LLM sub-agent path is not available
  - Acceleration cache to skip LLM calls for common foods

If no dictionary match is found, `translate_food_name` returns the original
name unchanged. The caller (main agent) should route through the Decomposer
sub-agent for proper LLM-based translation.
"""

import re
from typing import Optional, Tuple

# --- Detection -----------------------------------------------------------

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def is_chinese(name: str) -> bool:
    """Return True if name contains any CJK characters."""
    return bool(_CJK_RE.search(name))


# --- Dictionary ----------------------------------------------------------
# Keys: Chinese food name (or substring).
# Values: English name that USDA FDC can match.
# Ordered roughly by category for maintainability.

FOOD_DICT: dict[str, str] = {
    # ── 肉类 Meat ──
    "鸡胸肉": "chicken breast",
    "鸡腿": "chicken thigh",
    "鸡翅": "chicken wing",
    "鸡肉": "chicken meat",
    "鸡": "chicken",
    "鸭肉": "duck meat",
    "鸭": "duck",
    "猪肉": "pork",
    "猪排": "pork chop",
    "猪里脊": "pork tenderloin",
    "五花肉": "pork belly",
    "猪蹄": "pork feet",
    "牛肉": "beef",
    "牛排": "beef steak",
    "牛腩": "beef brisket",
    "牛腱": "beef shank",
    "羊肉": "lamb",
    "羊排": "lamb chop",
    "培根": "bacon",
    "火腿": "ham",
    "香肠": "sausage",
    "腊肉": "cured pork belly",
    # ── 海鲜 Seafood ──
    "三文鱼": "salmon",
    "鲑鱼": "salmon",
    "金枪鱼": "tuna",
    "鳕鱼": "cod",
    "鲈鱼": "sea bass",
    "带鱼": "hairtail fish",
    "鱼": "fish",
    "虾": "shrimp",
    "虾仁": "shrimp",
    "大虾": "shrimp",
    "龙虾": "lobster",
    "螃蟹": "crab",
    "蟹": "crab",
    "鱿鱼": "squid",
    "墨鱼": "cuttlefish",
    "扇贝": "scallop",
    "蛤蜊": "clam",
    "牡蛎": "oyster",
    "生蚝": "oyster",
    # ── 蛋奶 Eggs & Dairy ──
    "鸡蛋": "egg",
    "蛋": "egg",
    "鸭蛋": "duck egg",
    "鹌鹑蛋": "quail egg",
    "牛奶": "whole milk",
    "脱脂牛奶": "skim milk",
    "全脂牛奶": "whole milk",
    "酸奶": "yogurt",
    "奶酪": "cheese",
    "芝士": "cheese",
    "黄油": "butter",
    "奶油": "cream",
    # ── 主食 Staples ──
    "米饭": "cooked white rice",
    "白米饭": "cooked white rice",
    "糙米饭": "cooked brown rice",
    "糙米": "brown rice",
    "粥": "rice porridge",
    "白粥": "rice porridge",
    "面条": "noodles cooked",
    "面": "noodles cooked",
    "意面": "spaghetti cooked",
    "意大利面": "spaghetti cooked",
    "挂面": "noodles cooked",
    "馒头": "steamed bun",
    "花卷": "steamed roll",
    "包子": "steamed stuffed bun",
    "饺子": "dumpling",
    "馄饨": "wonton",
    "面包": "bread",
    "吐司": "toast bread",
    "全麦面包": "whole wheat bread",
    "燕麦": "oatmeal",
    "燕麦片": "oatmeal",
    "麦片": "cereal",
    "玉米": "corn",
    "红薯": "sweet potato",
    "地瓜": "sweet potato",
    "紫薯": "purple sweet potato",
    "土豆": "potato",
    "马铃薯": "potato",
    "芋头": "taro",
    "山药": "yam",
    "年糕": "rice cake",
    "粽子": "rice dumpling",
    "烧饼": "sesame flatbread",
    "油条": "fried dough stick",
    # ── 蔬菜 Vegetables ──
    "西兰花": "broccoli",
    "花菜": "cauliflower",
    "菜花": "cauliflower",
    "白菜": "chinese cabbage",
    "大白菜": "chinese cabbage",
    "小白菜": "bok choy",
    "青菜": "chinese greens",
    "菠菜": "spinach",
    "生菜": "lettuce",
    "芹菜": "celery",
    "韭菜": "chinese chives",
    "葱": "green onion",
    "洋葱": "onion",
    "蒜": "garlic",
    "大蒜": "garlic",
    "姜": "ginger",
    "辣椒": "chili pepper",
    "青椒": "green bell pepper",
    "红椒": "red bell pepper",
    "甜椒": "bell pepper",
    "茄子": "eggplant",
    "西红柿": "tomato",
    "番茄": "tomato",
    "黄瓜": "cucumber",
    "胡萝卜": "carrot",
    "白萝卜": "daikon radish",
    "萝卜": "radish",
    "南瓜": "pumpkin",
    "冬瓜": "winter melon",
    "苦瓜": "bitter melon",
    "丝瓜": "loofah",
    "西葫芦": "zucchini",
    "豆芽": "bean sprouts",
    "豆角": "green beans",
    "四季豆": "green beans",
    "毛豆": "edamame",
    "豌豆": "green peas",
    "荷兰豆": "snow peas",
    "秋葵": "okra",
    "芦笋": "asparagus",
    "蘑菇": "mushroom",
    "香菇": "shiitake mushroom",
    "金针菇": "enoki mushroom",
    "木耳": "wood ear mushroom",
    "海带": "kelp",
    "紫菜": "seaweed",
    "莲藕": "lotus root",
    "竹笋": "bamboo shoot",
    # ── 水果 Fruits ──
    "苹果": "apple",
    "香蕉": "banana",
    "橙子": "orange",
    "橘子": "tangerine",
    "柚子": "pomelo",
    "柠檬": "lemon",
    "葡萄": "grape",
    "草莓": "strawberry",
    "蓝莓": "blueberry",
    "西瓜": "watermelon",
    "哈密瓜": "cantaloupe",
    "芒果": "mango",
    "菠萝": "pineapple",
    "凤梨": "pineapple",
    "猕猴桃": "kiwi",
    "奇异果": "kiwi",
    "桃子": "peach",
    "梨": "pear",
    "樱桃": "cherry",
    "荔枝": "lychee",
    "龙眼": "longan",
    "石榴": "pomegranate",
    "火龙果": "dragon fruit",
    "百香果": "passion fruit",
    "椰子": "coconut",
    "榴莲": "durian",
    "木瓜": "papaya",
    "杏": "apricot",
    "枣": "jujube",
    "红枣": "jujube",
    "柿子": "persimmon",
    "李子": "plum",
    "无花果": "fig",
    "牛油果": "avocado",
    # ── 豆制品 Soy & Legumes ──
    "豆腐": "tofu",
    "嫩豆腐": "silken tofu",
    "老豆腐": "firm tofu",
    "豆浆": "soy milk",
    "豆干": "dried tofu",
    "腐竹": "tofu skin",
    "黄豆": "soybean",
    "黑豆": "black bean",
    "红豆": "adzuki bean",
    "绿豆": "mung bean",
    "花生": "peanut",
    # ── 坚果 Nuts & Seeds ──
    "核桃": "walnut",
    "杏仁": "almond",
    "腰果": "cashew",
    "开心果": "pistachio",
    "瓜子": "sunflower seeds",
    "芝麻": "sesame seeds",
    "松子": "pine nut",
    "栗子": "chestnut",
    "板栗": "chestnut",
    # ── 饮品 Beverages ──
    "咖啡": "coffee",
    "绿茶": "green tea",
    "红茶": "black tea",
    "茶": "tea",
    "豆奶": "soy milk",
    "椰奶": "coconut milk",
    "果汁": "fruit juice",
    "橙汁": "orange juice",
    "苹果汁": "apple juice",
    "可乐": "cola",
    "啤酒": "beer",
    "红酒": "red wine",
    "白酒": "baijiu",
    # ── 调味/油脂 Oils & Condiments ──
    "橄榄油": "olive oil",
    "花生油": "peanut oil",
    "菜籽油": "canola oil",
    "植物油": "vegetable oil",
    "酱油": "soy sauce",
    "醋": "vinegar",
    "蜂蜜": "honey",
    "白糖": "white sugar",
    "红糖": "brown sugar",
    "冰糖": "rock sugar",
    # ── 零食/加工 Snacks & Processed ──
    "薯片": "potato chips",
    "饼干": "crackers",
    "巧克力": "chocolate",
    "冰淇淋": "ice cream",
    "蛋糕": "cake",
    "月饼": "mooncake",
    "方便面": "instant noodles",
    "泡面": "instant noodles",
    "午餐肉": "luncheon meat",
    "豆腐乳": "fermented tofu",
    "皮蛋": "preserved egg",
    "咸鸭蛋": "salted duck egg",
}

# Sorted by key length descending so longer (more specific) matches win.
_SORTED_KEYS = sorted(FOOD_DICT.keys(), key=len, reverse=True)


# --- Translation ---------------------------------------------------------


def translate_food_name(name: str) -> Tuple[str, Optional[str]]:
    """Translate a Chinese food name to English for USDA queries.

    Returns (english_name, note) where:
    - If a dictionary match is found: (english_name, "翻译：X → Y")
    - If no match and name is Chinese: (original_name, None)
      Caller should fall back to LLM sub-agent or ask user.
    - If name is already English: (original_name, None)
    """
    if not is_chinese(name):
        return name, None

    stripped = name.strip()

    # Exact match first
    if stripped in FOOD_DICT:
        en = FOOD_DICT[stripped]
        return en, f"翻译：{stripped} → {en}"

    # Substring match (longest match wins)
    for zh_key in _SORTED_KEYS:
        if zh_key in stripped:
            en = FOOD_DICT[zh_key]
            return en, f"翻译：{stripped}（匹配 {zh_key}）→ {en}"

    # No match — return original; caller decides fallback
    return stripped, None
