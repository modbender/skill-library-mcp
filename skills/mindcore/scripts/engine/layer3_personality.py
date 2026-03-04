"""
layer3_personality.py — Layer 3: 前额叶性格闸门 (Prefrontal Personality Gate)
仿生情感心智引擎 (Biomimetic Mind Engine)

核心机制：
1. 性格权重过滤：每个冲动有对应的性格权重 (0~1)
2. Softmax 概率采样：多个冲动同时激活时，基于概率竞争
3. RL 衰减养成：通过 +1/-1 反馈调整权重，实现性格固化
4. 情绪残留衰减：每 tick 对 mood_valence 执行衰减

输入：Layer 2 的 shape=(50,) 冲动激活向量
输出：胜出的 1~2 个冲动 + 更新后的 mood_valence
"""

import json
import os
import numpy as np
from datetime import datetime
from engine.config import ENGINE_TIMEZONE
from engine.config import (
    TOTAL_LAYER2_NODES, TOTAL_LAYER3_NODES,
    PERSONALITY_INIT_WEIGHT, MOOD_DECAY_RATE,
    SHORT_TERM_MEMORY_PATH, SENSOR_STATE_PATH,
)
from engine.short_term_memory import get_memories_weighted


# ================================================================
# Softmax 温度参数
# ================================================================
SOFTMAX_TEMPERATURE = 0.5       # 越低 → 越倾向于选择最强冲动 (确定性)
                                 # 越高 → 越随机 (纠结/犹豫)
MAX_OUTPUT_IMPULSES = 2          # 最多同时输出的冲动数
MIN_IMPULSE_INTENSITY = 0.1     # 冲动强度低于此值不参与竞争

# RL 养成参数（性格成熟度衰减）
RL_LEARNING_RATE_INITIAL = 0.01  # 早期学习率
RL_LEARNING_RATE_MID = 0.005     # 中期学习率 (100~500 次反馈)
RL_LEARNING_RATE_LATE = 0.001    # 后期学习率 (500+ 次反馈)
RL_MATURITY_MID = 100            # 中期阈值
RL_MATURITY_LATE = 500           # 后期阈值
RL_WEIGHT_MIN = 0.05             # 权重下限 (永远不会完全压死)
RL_WEIGHT_MAX = 0.95             # 权重上限 (永远不会完全放行)

# ================================================================
# 冲动类别索引范围 (对应 layer2_impulses.py 的定义顺序)
# ================================================================
CAT_FOOD      = range(0, 18)     # 饮食
CAT_PHYSICAL  = range(18, 33)    # 身体/生理
CAT_ENTERTAIN = range(33, 58)    # 娱乐/消遣
CAT_STUDY     = range(58, 73)    # 学习/工作
CAT_EXERCISE  = range(73, 88)    # 运动/健康
CAT_SOCIAL    = range(88, 108)   # 社交
CAT_CHORES    = range(108, 125)  # 生活琐事
CAT_EMOTIONAL = range(125, 140)  # 情绪/心理
CAT_CREATIVE  = range(140, 150)  # 创造/表达

# ================================================================
# 话题 → 冲动类别映射表（短期记忆注入用）
# 关键词命中时，对应类别的冲动获得临时加权
# 可自由拓展，不需要改引擎代码
# ================================================================
TOPIC_CATEGORY_MAP = {
    # 运动/健身
    "运动": ["exercise"],
    "健身": ["exercise"],
    "攀岩": ["exercise"],
    "跑步": ["exercise"],
    "游泳": ["exercise"],
    "球": ["exercise"],
    "gym": ["exercise"],
    "瑜伽": ["exercise"],
    "徒步": ["exercise"],
    "拉伸": ["exercise", "physical"],
    # 饮食
    "吃": ["food"],
    "喝": ["food"],
    "饿": ["food"],
    "渴": ["food"],
    "奶茶": ["food"],
    "咖啡": ["food"],
    "火锅": ["food", "social"],
    "零食": ["food"],
    "做饭": ["food"],
    "外卖": ["food"],
    "餐厅": ["food", "social"],
    # 社交
    "聊天": ["social"],
    "朋友": ["social"],
    "约": ["social"],
    "群聊": ["social"],
    "见面": ["social"],
    "聚会": ["social", "food"],
    # 情绪
    "累": ["emotional", "physical"],
    "难过": ["emotional"],
    "开心": ["emotional", "social"],
    "焦虑": ["emotional"],
    "孤独": ["emotional", "social"],
    "无聊": ["emotional", "entertainment"],
    "压力": ["emotional"],
    # 工作/学习
    "工作": ["study"],
    "学习": ["study"],
    "代码": ["study", "creative"],
    "项目": ["study"],
    "考试": ["study"],
    "作业": ["study"],
    # 娱乐
    "电影": ["entertainment"],
    "动漫": ["entertainment"],
    "游戏": ["entertainment"],
    "音乐": ["entertainment"],
    "刷手机": ["entertainment"],
    "视频": ["entertainment"],
    "小说": ["entertainment"],
    # 生活
    "打扫": ["chores"],
    "洗衣": ["chores"],
    "收拾": ["chores"],
    "天气": ["chores"],
    "快递": ["chores"],
    # 创造
    "画画": ["creative"],
    "写作": ["creative"],
    "拍照": ["creative"],
    "设计": ["creative"],
    "唱歌": ["creative"],
}

# 类别名 → 索引范围
CATEGORY_RANGES = {
    "food": CAT_FOOD,
    "physical": CAT_PHYSICAL,
    "entertainment": CAT_ENTERTAIN,
    "study": CAT_STUDY,
    "exercise": CAT_EXERCISE,
    "social": CAT_SOCIAL,
    "chores": CAT_CHORES,
    "emotional": CAT_EMOTIONAL,
    "creative": CAT_CREATIVE,
}

# 话题注入参数
TOPIC_BOOST_BASE = 1.5    # 基础加权倍数（1.0 = 无影响）
TOPIC_BOOST_MAX = 2.0     # 单节点最大加权倍数


# ================================================================
# Layer 3 性格闸门
# ================================================================
class Layer3Personality:
    """
    前额叶性格闸门 — 冲动的最终裁决者。

    工作流程：
    1. 接收 Layer 2 的冲动激活向量
    2. 乘以性格权重向量 → 加权冲动
    3. 过滤掉低于最小强度的冲动
    4. 对候选冲动执行 Softmax 概率采样
    5. 输出胜出的 1~2 个冲动
    6. 每 tick 执行 mood_valence 衰减
    """

    def __init__(self, memory_path: str = SHORT_TERM_MEMORY_PATH):
        self.num_nodes = TOTAL_LAYER3_NODES
        self.memory_path = memory_path

        # 性格权重：初始全部为 0.5 (白纸状态)
        self.weights = np.full(self.num_nodes, PERSONALITY_INIT_WEIGHT, dtype=np.float64)

        # RL 反馈计数器（用于性格成熟度衰减）
        self.total_rewards = 0

        # 尝试加载持久化的权重
        self._weights_path = os.path.join(os.path.dirname(memory_path), "personality_weights.npy")
        self._rewards_path = os.path.join(os.path.dirname(memory_path), "personality_rewards_count.json")
        self._load_persistent()

        # 输出
        self.last_winners = []
        self.last_all_candidates = []

    def _load_persistent(self):
        """启动时加载持久化的性格权重和反馈计数。"""
        try:
            if os.path.exists(self._weights_path):
                self.weights = np.load(self._weights_path)
                print(f"[Layer3] 🧠 加载性格权重: {self._weights_path}")
        except Exception as e:
            print(f"[Layer3] ⚠️ 加载权重失败: {e}")

        try:
            if os.path.exists(self._rewards_path):
                with open(self._rewards_path, "r") as f:
                    data = json.load(f)
                self.total_rewards = data.get("total_rewards", 0)
                print(f"[Layer3] 🧠 加载反馈计数: {self.total_rewards}")
        except Exception as e:
            print(f"[Layer3] ⚠️ 加载反馈计数失败: {e}")

    def _save_persistent(self):
        """保存性格权重和反馈计数到文件。"""
        try:
            np.save(self._weights_path, self.weights)
            with open(self._rewards_path, "w") as f:
                json.dump({"total_rewards": self.total_rewards}, f)
        except Exception as e:
            print(f"[Layer3] ⚠️ 保存失败: {e}")

    def _get_learning_rate(self) -> float:
        """根据总反馈次数返回当前学习率（性格成熟度衰减）。"""
        if self.total_rewards < RL_MATURITY_MID:
            return RL_LEARNING_RATE_INITIAL
        elif self.total_rewards < RL_MATURITY_LATE:
            return RL_LEARNING_RATE_MID
        else:
            return RL_LEARNING_RATE_LATE

    def _read_sensors(self) -> dict:
        """读取当前感知状态，失败时返回空 dict。"""
        try:
            with open(SENSOR_STATE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _apply_context_mask(self, weighted: np.ndarray) -> np.ndarray:
        """
        情境抑制 mask：根据时间和感知状态压低不合理的冲动。
        直接修改 weighted 向量并返回。
        """
        mask = np.ones(len(weighted), dtype=np.float64)
        hour = datetime.now(ENGINE_TIMEZONE).hour
        sensors = self._read_sensors()
        body = sensors.get("body", {})
        env = sensors.get("environment", {})

        # 深夜 (00:00-06:00)：压低运动、社交、外出
        if 0 <= hour < 6:
            for i in CAT_EXERCISE:
                mask[i] *= 0.05
            for i in CAT_SOCIAL:
                mask[i] *= 0.1
            # 提升休息/情绪类
            for i in CAT_EMOTIONAL:
                mask[i] *= 1.3

        # 凌晨到早上 (06:00-09:00)：运动和社交轻微压低
        elif 6 <= hour < 9:
            for i in CAT_EXERCISE:
                mask[i] *= 0.3
            for i in CAT_SOCIAL:
                mask[i] *= 0.5

        # 吃饱了：压低饮食类
        if body.get("full_stomach", 0) > 0:
            for i in CAT_FOOD:
                mask[i] *= 0.1

        # 饿了：提升饮食类
        if body.get("empty_stomach", 0) > 0:
            for i in CAT_FOOD:
                mask[i] *= 1.5

        # 眼睛疲劳：压低屏幕娱乐，提升身体活动
        if body.get("eye_fatigue", 0) > 0:
            for i in CAT_ENTERTAIN:
                mask[i] *= 0.3
            for i in CAT_PHYSICAL:
                mask[i] *= 1.3

        # 缺觉：压低运动和学习，提升休息
        if body.get("sleep_deprived", 0) > 0:
            for i in CAT_EXERCISE:
                mask[i] *= 0.2
            for i in CAT_STUDY:
                mask[i] *= 0.3
            for i in CAT_EMOTIONAL:
                mask[i] *= 1.3

        # 运动后兴奋：压低再次运动，提升饮食和休息
        if body.get("post_workout_high", 0) > 0:
            for i in CAT_EXERCISE:
                mask[i] *= 0.2
            for i in CAT_FOOD:
                mask[i] *= 1.5

        # 下雨：压低户外运动
        if env.get("is_raining", 0) > 0:
            for i in CAT_EXERCISE:
                mask[i] *= 0.4

        # === 场景上下文过滤 ===

        # 在家：外出/社交类压低，宅家娱乐提升
        if env.get("alone_at_home", 0) > 0:
            for i in CAT_SOCIAL:
                mask[i] *= 0.4
            for i in CAT_ENTERTAIN:
                mask[i] *= 1.3

        # 人多的地方：独处/情绪类压低，社交提升
        if env.get("crowded_place", 0) > 0:
            for i in CAT_EMOTIONAL:
                mask[i] *= 0.4
            for i in CAT_SOCIAL:
                mask[i] *= 1.3

        # 安静环境：阅读/冥想提升，嘈杂娱乐压低
        if env.get("quiet_environment", 0) > 0:
            for i in CAT_STUDY:
                mask[i] *= 1.3
            for i in CAT_EMOTIONAL:
                mask[i] *= 1.2

        # 嘈杂环境：阅读/冥想压低
        if env.get("noisy_environment", 0) > 0:
            for i in CAT_STUDY:
                mask[i] *= 0.4
            for i in CAT_EMOTIONAL:
                mask[i] *= 0.5

        # 深度对话中：无关娱乐压低，学习/思考提升
        social = sensors.get("social", {})
        if social.get("deep_conversation", 0) > 0:
            for i in CAT_ENTERTAIN:
                mask[i] *= 0.3
            for i in CAT_STUDY:
                mask[i] *= 1.4

        # 周末：工作轻微压低，娱乐/运动提升
        if env.get("weekend", 0) > 0:
            for i in CAT_STUDY:
                mask[i] *= 0.7
            for i in CAT_ENTERTAIN:
                mask[i] *= 1.2
            for i in CAT_EXERCISE:
                mask[i] *= 1.2

        # 咖啡因高：不再想喝咖啡/茶，工作提升
        if body.get("caffeine_high", 0) > 0:
            for i in CAT_FOOD:
                mask[i] *= 0.7
            for i in CAT_STUDY:
                mask[i] *= 1.3

        # 天气好/空气好：户外活动提升
        if env.get("sunny_outside", 0) > 0 or env.get("fresh_air", 0) > 0:
            for i in CAT_EXERCISE:
                mask[i] *= 1.3
            for i in CAT_CREATIVE:
                mask[i] *= 1.2

        return weighted * mask

    def _apply_topic_boost(self, weighted: np.ndarray) -> np.ndarray:
        """
        短期记忆话题加权：根据最近对话话题，临时提升相关类别冲动的权重。
        不修改性格权重本身，只是临时调制。
        失败时返回原始 weighted，不影响引擎。
        """
        try:
            memories = get_memories_weighted()
        except Exception:
            return weighted

        if not memories:
            return weighted

        boost = np.ones(len(weighted), dtype=np.float64)

        for mem in memories:
            w = mem.get("weight", 0.0)
            if w < 0.01:
                continue

            keywords = mem.get("keywords", [])
            for kw in keywords:
                categories = TOPIC_CATEGORY_MAP.get(kw, [])
                for cat_name in categories:
                    idx_range = CATEGORY_RANGES.get(cat_name)
                    if idx_range is None:
                        continue
                    # 加权 = 1.0 + (boost_base - 1.0) * 衰减权重
                    # 例：w=1.0 → boost=1.5, w=0.5 → boost=1.25
                    for i in idx_range:
                        boost[i] += (TOPIC_BOOST_BASE - 1.0) * w

        # 限制最大加权
        boost = np.clip(boost, 1.0, TOPIC_BOOST_MAX)

        return weighted * boost

    def _softmax(self, values: np.ndarray, temperature: float = SOFTMAX_TEMPERATURE) -> np.ndarray:
        """带温度参数的 Softmax 概率分布。"""
        if len(values) == 0:
            return np.array([])

        # 数值稳定性：减去最大值
        scaled = values / max(temperature, 1e-8)
        shifted = scaled - np.max(scaled)
        exp_vals = np.exp(shifted)
        probs = exp_vals / (np.sum(exp_vals) + 1e-10)
        return probs

    def tick(self, impulse_vector: np.ndarray, mood_valence: float = 0.0) -> list:
        """
        执行性格闸门裁决。

        Args:
            impulse_vector: shape=(50,) 来自 Layer 2 的冲动激活
            mood_valence: 当前心境 (-1 to 1)

        Returns:
            winners: list of dicts [{index, name, intensity, probability}, ...]
        """
        from engine.layer2_impulses import IMPULSE_NAMES

        # 1. 性格权重过滤
        weighted = impulse_vector * self.weights

        # 1.5 情境抑制 mask
        weighted = self._apply_context_mask(weighted)

        # 1.6 短期记忆话题加权（对话影响冲动倾向）
        weighted = self._apply_topic_boost(weighted)

        # 2. 筛选有效候选 (强度 > 最小阈值)
        candidate_indices = np.where(weighted > MIN_IMPULSE_INTENSITY)[0]
        self.last_all_candidates = []

        if len(candidate_indices) == 0:
            self.last_winners = []
            self._decay_mood()
            return []

        candidate_values = weighted[candidate_indices]

        # 记录所有候选
        for idx, val in zip(candidate_indices, candidate_values):
            self.last_all_candidates.append({
                "index": int(idx),
                "name": IMPULSE_NAMES[idx],
                "weighted_intensity": round(float(val), 4),
            })

        # 3. Softmax 概率采样
        probs = self._softmax(candidate_values)

        # 4. 根据概率选择 1~2 个胜出冲动
        num_winners = min(MAX_OUTPUT_IMPULSES, len(candidate_indices))

        # 不重复采样
        chosen_local = np.random.choice(
            len(candidate_indices), size=num_winners,
            replace=False, p=probs
        )

        winners = []
        for local_idx in chosen_local:
            global_idx = int(candidate_indices[local_idx])
            winners.append({
                "index": global_idx,
                "name": IMPULSE_NAMES[global_idx],
                "intensity": round(float(candidate_values[local_idx]), 4),
                "probability": round(float(probs[local_idx]), 4),
            })

        # 按强度降序排列
        winners.sort(key=lambda x: x["intensity"], reverse=True)

        self.last_winners = winners

        # 5. mood 衰减
        self._decay_mood()

        return winners

    def _decay_mood(self):
        """每 tick 执行 mood_valence 的指数衰减。"""
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            mood = data.get("mood_valence", 0.0)
            # 指数衰减：乘以 decay_rate
            mood *= MOOD_DECAY_RATE
            # 接近零时直接归零
            if abs(mood) < 0.001:
                mood = 0.0
            data["mood_valence"] = round(mood, 6)

            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # 文件不存在或损坏时跳过

    def reward(self, impulse_index: int, signal: float):
        """
        RL 反馈信号：调整性格权重。

        Args:
            impulse_index: 冲动节点索引
            signal: +1 (正面反馈，鼓励) 或 -1 (负面反馈，抑制)
        """
        if 0 <= impulse_index < self.num_nodes:
            lr = self._get_learning_rate()
            delta = lr * signal
            self.weights[impulse_index] = np.clip(
                self.weights[impulse_index] + delta,
                RL_WEIGHT_MIN, RL_WEIGHT_MAX
            )
            self.total_rewards += 1
            self._save_persistent()

    def get_personality_profile(self) -> dict:
        """返回当前性格轮廓（调试用）。"""
        from engine.layer2_impulses import IMPULSE_NAMES
        profile = {}
        for i, name in enumerate(IMPULSE_NAMES):
            w = self.weights[i]
            if abs(w - PERSONALITY_INIT_WEIGHT) > 0.01:
                profile[name] = round(float(w), 3)
        return profile if profile else {"status": "blank_slate (all weights = 0.5)"}

    def save_weights(self, path: str):
        """持久化性格权重。"""
        np.save(path, self.weights)

    def load_weights(self, path: str):
        """加载性格权重。"""
        self.weights = np.load(path)

    def reset(self):
        self.weights = np.full(self.num_nodes, PERSONALITY_INIT_WEIGHT, dtype=np.float64)
        self.last_winners = []
        self.last_all_candidates = []
