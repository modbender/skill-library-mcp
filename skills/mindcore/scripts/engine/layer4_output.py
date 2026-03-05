"""
layer4_output.py — Layer 4: 决策输出翻译器 (Decision Output Translator)
仿生情感心智引擎 (Biomimetic Mind Engine)

将 Layer 3 胜出的冲动打包为结构化 JSON，
映射到 10 种情绪烈度等级的 System Prompt 模板。

输出：ready-to-use 的 JSON，可直接注入 OpenClaw 的 System Prompt。
"""

import json
import time
import os
from datetime import datetime
from engine.config import ENGINE_TIMEZONE
from engine.config import OUTPUT_DIR, SHORT_TERM_MEMORY_PATH

# mood 调整幅度
MOOD_IMPULSE_DELTA = 0.05  # 每次冲动触发对 mood 的影响


# ================================================================
# 10 种情绪烈度等级 (Emotional Intensity Levels)
# ================================================================
INTENSITY_LEVELS = [
    # (等级名, 最低强度阈值, Prompt 风格描述)
    ("comatose",    0.0,  "完全沉默，不主动发言，仅在被直接提问时简短回应"),
    ("drowsy",      0.2,  "昏昏欲睡，回应迟缓，用词极简，偶尔打哈欠式省略号"),
    ("calm",        0.4,  "平静温和，语气平稳，正常社交距离的友好对话"),
    ("engaged",     0.6,  "活跃投入，话变多了，主动延伸话题，偶尔加表情"),
    ("excited",     0.8,  "兴奋激动，语速加快，感叹号增多，想分享各种东西"),
    ("passionate",  1.0,  "充满热情，滔滔不绝，可能跑题，强烈表达观点"),
    ("agitated",    1.3,  "烦躁不安，语气变冲，容易杠，缺乏耐心"),
    ("volatile",    1.6,  "情绪volatile，忽冷忽热，可能前后矛盾，需要被关注"),
    ("explosive",   2.0,  "情绪爆发，用词激烈，可能说出平时不会说的话"),
    ("meltdown",    2.5,  "彻底崩溃／狂喜，失去理性过滤，纯粹的情绪宣泄"),
]


# ================================================================
# Layer 4 输出翻译器
# ================================================================
class Layer4Output:
    """
    将内部冲动状态翻译为外部可执行的 JSON 指令。
    """

    def __init__(self):
        self.last_output = None
        self.output_count = 0

        # 确保输出目录存在
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def _classify_intensity(self, intensity: float) -> dict:
        """根据冲动强度匹配情绪烈度等级。"""
        matched = INTENSITY_LEVELS[0]
        for level in INTENSITY_LEVELS:
            if intensity >= level[1]:
                matched = level
        return {
            "level_name": matched[0],
            "threshold": matched[1],
            "style_prompt": matched[2],
        }

    def _determine_valence(self, impulse_name: str) -> str:
        """根据冲动名称判断正负极性。"""
        negative_prefixes = [
            "complain", "snap", "withdraw", "ghosting", "passive",
            "cry", "self_blame", "jealousy", "overthink", "rage",
            "sarcasm", "silent_treatment", "anxiety", "doom", "vent",
            "procrastinate", "argue", "defend", "blame", "revenge",
            "sulk", "panic", "run", "hide", "deny", "obsess",
            "pity", "cynicism", "pessimism", "distrust", "rebel",
            "destructive", "give_up", "lash", "whine", "guilt",
        ]
        positive_prefixes = [
            "share", "joke", "love", "comfort", "forgive",
            "confide", "hug", "celebrate", "encourage", "flirt",
            "reminisce", "philosophize", "adventure", "kindness", "show_off",
            "learn", "create", "organize", "praise", "thank",
            "inspire", "motivate", "cheer", "nurture", "protect",
            "collaborate", "compromise", "trust", "vulnerable",
            "laugh", "smile", "sing", "dance", "optimism",
            "hope", "marvel", "appreciate", "generous",
        ]

        name_lower = impulse_name.lower().replace("impulse_", "")
        for p in negative_prefixes:
            if p in name_lower:
                return "negative"
        for p in positive_prefixes:
            if p in name_lower:
                return "positive"
        return "neutral"

    def tick(self, winners: list, mood_valence: float = 0.0,
             active_sensors: list = None, membrane_state: dict = None) -> dict:
        """
        将胜出冲动打包为完整的 JSON 输出。

        Args:
            winners: Layer 3 输出的胜出冲动列表
            mood_valence: 当前心境底色
            active_sensors: 当前激活的传感器列表（可选，用于上下文）
            membrane_state: Layer 2 膜电位状态（可选，用于调试）

        Returns:
            output_json: 完整的决策输出字典
        """
        self.output_count += 1
        now = datetime.now(ENGINE_TIMEZONE)

        if not winners:
            output = {
                "timestamp": now.isoformat(),
                "tick_id": self.output_count,
                "action": "IDLE",
                "should_speak": False,
                "mood_valence": round(mood_valence, 4),
                "impulses": [],
                "intensity_level": self._classify_intensity(0.0),
                "system_prompt_injection": None,
            }
            self.last_output = output
            return output

        # 主冲动 (最强)
        primary = winners[0]
        primary_intensity = primary["intensity"]

        # 次要冲动 (如果有)
        secondary = winners[1] if len(winners) > 1 else None

        # 情绪烈度
        intensity_info = self._classify_intensity(primary_intensity)

        # 极性判断
        primary_valence = self._determine_valence(primary["name"])

        # 构建 System Prompt 注入
        prompt_injection = self._build_prompt(
            primary, secondary, intensity_info,
            mood_valence, active_sensors
        )

        output = {
            "timestamp": now.isoformat(),
            "tick_id": self.output_count,
            "action": "SPEAK" if primary_intensity > 0.3 else "SUBTLE",
            "should_speak": primary_intensity > 0.3,
            "mood_valence": round(mood_valence, 4),
            "impulses": [
                {
                    "name": primary["name"],
                    "intensity": primary["intensity"],
                    "probability": primary.get("probability", 1.0),
                    "valence": primary_valence,
                    "is_primary": True,
                },
            ],
            "intensity_level": intensity_info,
            "system_prompt_injection": prompt_injection,
        }

        if secondary:
            output["impulses"].append({
                "name": secondary["name"],
                "intensity": secondary["intensity"],
                "probability": secondary.get("probability", 0.0),
                "valence": self._determine_valence(secondary["name"]),
                "is_primary": False,
            })

        # 附加调试信息
        if membrane_state:
            output["_debug_membrane"] = membrane_state
        if active_sensors:
            output["_debug_active_sensors"] = active_sensors[:10]  # 只取前10个

        # 根据冲动 valence 更新 mood_valence
        if output.get("should_speak"):
            self._update_mood_from_impulse(primary_valence, mood_valence)

        self.last_output = output
        return output

    def _build_prompt(self, primary: dict, secondary: dict,
                      intensity_info: dict, mood_valence: float,
                      active_sensors: list = None) -> str:
        """构建发送给 OpenClaw 的 System Prompt 注入片段。"""
        parts = []

        # 核心情绪指令
        parts.append(f"[MIND ENGINE STATE]")
        parts.append(f"当前情绪烈度: {intensity_info['level_name'].upper()}")
        parts.append(f"风格要求: {intensity_info['style_prompt']}")
        parts.append(f"心境底色: {'负面' if mood_valence < -0.2 else '正面' if mood_valence > 0.2 else '中性'} ({mood_valence:+.2f})")
        parts.append(f"")

        # 主冲动
        parts.append(f"主要冲动: {primary['name']} (强度: {primary['intensity']:.2f})")

        # 次要冲动 (内心纠结)
        if secondary:
            parts.append(f"次要冲动 (内心纠结): {secondary['name']} (强度: {secondary['intensity']:.2f})")
            parts.append(f"注意：你的内心正在这两种冲动之间纠结，这应该体现在你的语气中。")

        # 环境上下文
        if active_sensors:
            # 只展示强度 > 0.3 的感知，过滤掉身体底噪
            strong_sensors = [s for s in active_sensors if (isinstance(s, tuple) and s[1] > 0.3) or not isinstance(s, tuple)]
            sensor_names = [s[0] if isinstance(s, tuple) else s for s in strong_sensors[:5]]
            parts.append(f"")
            parts.append(f"当前感知: {', '.join(sensor_names)}")

        parts.append(f"[/MIND ENGINE STATE]")

        return "\n".join(parts)

    def save_output(self, output: dict = None):
        """将输出保存到文件。"""
        if output is None:
            output = self.last_output
        if output is None:
            return

        filename = f"output_{output['tick_id']:06d}.json"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

    def _update_mood_from_impulse(self, valence: str, current_mood: float):
        """根据冲动的正负极性更新 ShortTermMemory 中的 mood_valence。"""
        if valence == "positive":
            delta = MOOD_IMPULSE_DELTA
        elif valence == "negative":
            delta = -MOOD_IMPULSE_DELTA
        else:
            return  # neutral 不影响

        try:
            with open(SHORT_TERM_MEMORY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            mood = data.get("mood_valence", 0.0)
            mood = max(-1.0, min(1.0, mood + delta))
            data["mood_valence"] = round(mood, 6)
            with open(SHORT_TERM_MEMORY_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def reset(self):
        self.last_output = None
        self.output_count = 0
