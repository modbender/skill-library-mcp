"""
layer2_impulses.py — Layer 2: 潜意识冲动层 (Impulse Emergence Layer)
仿生情感心智引擎 (Biomimetic Mind Engine)

核心机制：LIF (Leaky Integrate-and-Fire) 漏电积分触发神经元模型。

数据流：
  Layer 1 (50 感知) × Synapse_Matrix (50×50) → 引申信号
  + Layer 0 (3000 噪声) → 随机点燃能量
  + mood_valence → 阈值调制
  = 膜电位累积 → 突破阈值 → 冲动涌现！

输出：shape=(50,) 的冲动激活向量
"""

import numpy as np
from engine.config import (
    TOTAL_LAYER1_NODES, TOTAL_LAYER2_NODES, TOTAL_LAYER0_NODES,
    BURST_BASE_OFFSET,
)


# ================================================================
# 50 个冲动节点定义
# ================================================================
IMPULSE_NAMES = [
    # 🍜 饮食 Food/Drink (18)
    "impulse_drink_water", "impulse_drink_coffee", "impulse_drink_boba", "impulse_eat_snack", "impulse_eat_fruit",
    "impulse_order_takeout", "impulse_cook_meal", "impulse_eat_sweets", "impulse_eat_spicy", "impulse_drink_alcohol",
    "impulse_make_tea", "impulse_eat_icecream", "impulse_drink_juice", "impulse_eat_chocolate", "impulse_drink_soda",
    "impulse_eat_hotpot", "impulse_try_new_restaurant", "impulse_chew_gum",

    # 🧍 身体/生理 Physical (15)
    "impulse_stretch", "impulse_go_bathroom", "impulse_wash_face", "impulse_change_clothes", "impulse_take_shower",
    "impulse_lie_down", "impulse_stand_up_walk", "impulse_rub_shoulders", "impulse_rub_eyes", "impulse_yawn",
    "impulse_deep_breath", "impulse_crack_knuckles", "impulse_get_some_sun", "impulse_foot_bath", "impulse_look_in_mirror",

    # 📱 娱乐/消遣 Entertainment (25)
    "impulse_scroll_phone", "impulse_watch_shorts", "impulse_watch_movie", "impulse_binge_show", "impulse_watch_anime",
    "impulse_play_pc_game", "impulse_listen_music", "impulse_watch_stream", "impulse_online_shopping", "impulse_read_news",
    "impulse_watch_memes", "impulse_read_manga", "impulse_play_mobile_game", "impulse_watch_variety_show", "impulse_listen_podcast",
    "impulse_read_novel", "impulse_scroll_social_media", "impulse_watch_sports", "impulse_watch_documentary", "impulse_rewatch_old_movie",
    "impulse_find_new_music", "impulse_read_gossip", "impulse_watch_reviews", "impulse_look_at_old_photos", "impulse_browse_forums",

    # 📚 学习/工作 Study/Work (15)
    "impulse_learn_something_new", "impulse_read_book", "impulse_write_something", "impulse_organize_notes", "impulse_make_plan",
    "impulse_review_material", "impulse_memorize_vocab", "impulse_watch_tutorial", "impulse_practice_skill", "impulse_work_on_project",
    "impulse_make_todo_list", "impulse_organize_files", "impulse_research_topic", "impulse_learn_recipe", "impulse_watch_ted_talk",

    # 🏃 运动/健康 Exercise (15)
    "impulse_go_running", "impulse_go_to_gym", "impulse_do_yoga", "impulse_stretch_body", "impulse_go_cycling",
    "impulse_go_swimming", "impulse_play_ball_game", "impulse_go_hiking", "impulse_jump_rope", "impulse_do_pushups",
    "impulse_go_for_walk", "impulse_mobilize_joints", "impulse_check_weight", "impulse_check_health_data", "impulse_invite_workout",

    # 💬 社交 Social (20)
    "impulse_chat_with_someone", "impulse_reply_messages", "impulse_post_moment", "impulse_check_friends_updates", "impulse_invite_dinner",
    "impulse_voice_call", "impulse_video_call", "impulse_share_meme", "impulse_complain_to_friend", "impulse_gossip",
    "impulse_greet_old_friend", "impulse_join_group_chat", "impulse_comment_post", "impulse_like_post", "impulse_send_sticker",
    "impulse_compliment_someone", "impulse_comfort_friend", "impulse_organize_gathering", "impulse_meet_new_people", "impulse_post_tweet",

    # 🏠 生活琐事 Daily Chores (17)
    "impulse_clean_room", "impulse_organize_desk", "impulse_do_laundry", "impulse_go_grocery", "impulse_charge_phone",
    "impulse_change_wallpaper", "impulse_organize_bookshelf", "impulse_take_out_trash", "impulse_open_window", "impulse_set_alarm",
    "impulse_check_weather", "impulse_pack_bag", "impulse_fix_something", "impulse_water_plants", "impulse_check_delivery",
    "impulse_pickup_package", "impulse_track_expenses",

    # 😌 情绪/心理 Emotional (15)
    "impulse_zone_out", "impulse_sigh", "impulse_seek_quiet_alone", "impulse_get_fresh_air", "impulse_vent_emotions",
    "impulse_find_listener", "impulse_write_diary", "impulse_reminisce_past", "impulse_fantasize_future", "impulse_complain_life",
    "impulse_encourage_self", "impulse_treat_myself", "impulse_empty_mind", "impulse_meditate", "impulse_cry_a_bit",

    # 🎨 创造/表达 Creative (10)
    "impulse_take_photo", "impulse_draw_picture", "impulse_write_paragraph", "impulse_record_video", "impulse_do_crafts",
    "impulse_play_instrument", "impulse_sing_song", "impulse_design_something", "impulse_write_code", "impulse_write_poem"
]

assert len(IMPULSE_NAMES) == TOTAL_LAYER2_NODES, \
    f"Impulse count mismatch: {len(IMPULSE_NAMES)} vs {TOTAL_LAYER2_NODES}"


# ================================================================
# 纯随机涌现参数 (Stochastic Burst Parameters)
# ================================================================
BURST_THRESHOLD = 1.5        # 瞬间爆发阈值 (纯靠噪音随机暴击驱动，synapse 只提供微弱偏置)
BURST_REFRACTORY_TICKS = 600  # 触发后冷却 600 秒 (同一冲动 10 分钟内不重复，防止 burst flooding)

# 噪声耦合：Layer 0 的 3000 个节点如何影响 Layer 2 的 150 个节点
# 策略：将 3000 个噪声节点分成 150 组，取均值作为该冲动的随机驱动力
NOISE_GROUP_SIZE = TOTAL_LAYER0_NODES // TOTAL_LAYER2_NODES

# mood 对阈值的调制强度
MOOD_THRESHOLD_SCALE = 0.3   # mood=-1 时，负面冲动更容易爆发

# 思维惯性参数
CATEGORY_BOOST_STRENGTH = 0.15   # 同类别冲动的加成强度
CATEGORY_BOOST_HALFLIFE = 180.0  # 加成半衰期（秒），约 3 分钟

# 冲动类别映射（索引范围）
IMPULSE_CATEGORIES = {
    "food":         range(0, 18),
    "physical":     range(18, 33),
    "entertainment":range(33, 58),
    "study":        range(58, 73),
    "exercise":     range(73, 88),
    "social":       range(88, 108),
    "chores":       range(108, 125),
    "emotional":    range(125, 140),
    "creative":     range(140, 150),
}

# 反向映射：冲动索引 → 类别名
IMPULSE_TO_CATEGORY = {}
for cat, idx_range in IMPULSE_CATEGORIES.items():
    for idx in idx_range:
        IMPULSE_TO_CATEGORY[idx] = cat

# ================================================================
# Layer 2 冲动涌现器 (Stochastic Burst Engine)
# ================================================================
class Layer2Impulses:
    """
    纯随机涌现引擎 (Stochastic Burst Engine)。
    
    抛弃了记忆和漏电累积，每一秒钟 (tick) 只看瞬间状态：
    1. 瞬间基底：突触输入 (synapse_matrix.T @ sensor_vector)
    2. 瞬间扰动：Layer 0 的随机暴击 (noise_coupling)
    3. 心境调整：根据 mood_valence 调整门槛
    4. 爆发判定：如果 (基底 + 噪音暴击) > 阈值 → 瞬间爆发产生冲动！
    """

    def __init__(self, synapse_matrix: np.ndarray = None):
        """
        Args:
            synapse_matrix: shape=(TOTAL_LAYER1_NODES, TOTAL_LAYER2_NODES)
                           Layer 1 → Layer 2 的突触权重矩阵。
                           如果为 None，使用随机初始化（测试用）。
        """
        self.num_impulses = TOTAL_LAYER2_NODES

        # 突触矩阵
        if synapse_matrix is not None:
            assert synapse_matrix.shape == (TOTAL_LAYER1_NODES, TOTAL_LAYER2_NODES), \
                f"Synapse matrix shape mismatch: {synapse_matrix.shape}"
            self.synapse_matrix = synapse_matrix
        else:
            # 随机稀疏矩阵（测试用，正式版由 Embedding 自动生成）
            self.synapse_matrix = self._create_random_synapse()

        # LIF 状态
        self.membrane = np.zeros(self.num_impulses, dtype=np.float64)
        self.refractory = np.zeros(self.num_impulses, dtype=np.int64)  # 不应期倒计时

        # 思维惯性：记录每个类别最近一次触发的时间戳
        self.category_last_fired = {}  # {category_name: timestamp}

        # 输出
        self.last_output = None
        self.last_fired = None

    def _create_random_synapse(self) -> np.ndarray:
        """生成随机稀疏突触矩阵（测试用）。"""
        matrix = np.random.randn(TOTAL_LAYER1_NODES, TOTAL_LAYER2_NODES) * 0.3
        # 稀疏化：只保留约 30% 的连接
        mask = np.random.random((TOTAL_LAYER1_NODES, TOTAL_LAYER2_NODES)) > 0.7
        matrix *= mask
        return matrix.astype(np.float64)

    def _couple_noise(self, noise_vector: np.ndarray) -> np.ndarray:
        """
        将 Layer 0 的 3000 维噪声耦合到 50 个冲动节点。

        策略：将噪声向量分成 50 组，每组 60 个节点，
        取每组的均值作为该冲动节点的噪声驱动。
        """
        n = min(len(noise_vector), TOTAL_LAYER0_NODES)
        groups = TOTAL_LAYER2_NODES
        group_size = n // groups

        coupling = np.zeros(groups, dtype=np.float64)
        for i in range(groups):
            start = i * group_size
            end = start + group_size
            coupling[i] = np.max(noise_vector[start:end])  # 取最大值保留随机尖峰

        return coupling

    def _compute_dynamic_threshold(self, mood_valence: float) -> np.ndarray:
        """
        根据心境动态调整每个冲动的爆发门槛。
        """
        thresholds = np.full(self.num_impulses, BURST_THRESHOLD, dtype=np.float64)

        if mood_valence < 0:
            # 负面心境：负面冲动门槛降低
            thresholds[:35] -= abs(mood_valence) * MOOD_THRESHOLD_SCALE
            # 正面冲动门槛提高
            thresholds[35:70] += abs(mood_valence) * MOOD_THRESHOLD_SCALE * 0.5
        elif mood_valence > 0:
            # 正面心境：正面冲动门槛降低
            thresholds[35:70] -= mood_valence * MOOD_THRESHOLD_SCALE
            # 负面冲动门槛提高
            thresholds[:35] += mood_valence * MOOD_THRESHOLD_SCALE * 0.5

        # 确保门槛下限
        thresholds = np.maximum(thresholds, 5.0)
        return thresholds

    def tick(self, sensor_vector: np.ndarray, noise_vector: np.ndarray,
             mood_valence: float = 0.0) -> np.ndarray:
        """
        执行一次随机暴击判定 (Probabilistic Burst Tick)。
        
        核心机制：
        1. 计算每个冲动的瞬间激活强度 (instant_power)
        2. 通过 sigmoid 将强度映射为触发概率 (0~1)
        3. 掷骰子！概率越高越容易触发，但永远有随机性
        
        这就是你说的"随机数" — 每一帧都在掷骰子，
        有时 5 分钟就中了，有时好几个小时都不中。
        """
        output = np.zeros(self.num_impulses, dtype=np.float64)

        # 1. 瞬间基底力：Layer 1 -> Sensor -> Synapse Matrix -> Layer 2
        safe_sensor = np.clip(sensor_vector, 0.0, 10.0)
        synapse_input = safe_sensor @ self.synapse_matrix  # shape=(150,)
        synapse_input = np.nan_to_num(synapse_input, nan=0.0, posinf=10.0, neginf=-10.0)

        # 2. 瞬间扰动力：来自 Layer 0 (纯随机粉红/OU噪音)
        noise_coupling = self._couple_noise(noise_vector)  # shape=(150,)

        # 3. 合并为"激活强度" (范围大约 [0, ~5])
        # synapse 提供了基础偏置（哪些冲动更容易被激活）
        # noise 提供了随机波动（每一帧都不同的掷骰子干扰）
        instant_power = synapse_input * 0.3 + noise_coupling * 0.3

        # 4. 不应期冷却
        in_refractory = self.refractory > 0
        instant_power[in_refractory] = -999.0  # 冷却中的冲动概率归零
        self.refractory[in_refractory] -= 1

        # 4.5 思维惯性：最近触发过的类别获得加成
        import time as _time
        import math as _math
        now_ts = _time.time()
        for cat, last_ts in self.category_last_fired.items():
            elapsed = now_ts - last_ts
            decay = _math.pow(0.5, elapsed / CATEGORY_BOOST_HALFLIFE)
            boost = CATEGORY_BOOST_STRENGTH * decay
            if boost > 0.001 and cat in IMPULSE_CATEGORIES:
                for idx in IMPULSE_CATEGORIES[cat]:
                    if not in_refractory[idx]:
                        instant_power[idx] += boost

        # 5. 转换为触发概率 (Sigmoid)
        # BURST_BASE_OFFSET 控制整体频率：
        #   -12.5 → 基础概率 ≈ 0.000004/tick → 150节点×3600秒 ≈ 2次/小时
        #   noise 波动会让有些时段密集、有些时段完全空白
        fire_prob = 1.0 / (1.0 + np.exp(-(instant_power - BURST_BASE_OFFSET)))
        
        # 6. 心境调制：负面心境下负面冲动概率翻倍
        if mood_valence < 0:
            fire_prob[:35] *= (1.0 + abs(mood_valence))  # 负面冲动更容易
            fire_prob[35:70] *= max(0.3, 1.0 - abs(mood_valence))  # 正面冲动更难
        elif mood_valence > 0:
            fire_prob[35:70] *= (1.0 + mood_valence)
            fire_prob[:35] *= max(0.3, 1.0 - mood_valence)

        # 6.5 时段权重调制 (Time-Period Presets)
        # 根据当前真实时间，微调特定行为的触发概率，使其更像"真人习惯"
        import time as pytime
        from datetime import datetime
        hour = datetime.fromtimestamp(pytime.time()).hour + datetime.fromtimestamp(pytime.time()).minute / 60.0
        
        # 默认全部权重为 1.0，只微调特殊的
        time_weights = np.ones(self.num_impulses, dtype=np.float64)
        
        if 6 <= hour < 9:  # 早上
            time_weights[IMPULSE_NAMES.index("impulse_drink_coffee")] = 2.0
            time_weights[IMPULSE_NAMES.index("impulse_stretch")] = 2.0
            time_weights[IMPULSE_NAMES.index("impulse_drink_alcohol")] = 0.05
            time_weights[IMPULSE_NAMES.index("impulse_play_pc_game")] = 0.2
            time_weights[IMPULSE_NAMES.index("impulse_binge_show")] = 0.2
        elif 9 <= hour < 17:  # 白天工作学习
            time_weights[IMPULSE_NAMES.index("impulse_learn_something_new")] = 1.5
            time_weights[IMPULSE_NAMES.index("impulse_work_on_project")] = 1.5
            time_weights[IMPULSE_NAMES.index("impulse_drink_coffee")] = 1.5
            time_weights[IMPULSE_NAMES.index("impulse_drink_alcohol")] = 0.1
        elif 17 <= hour < 21:  # 傍晚
            time_weights[IMPULSE_NAMES.index("impulse_go_running")] = 1.5
            time_weights[IMPULSE_NAMES.index("impulse_go_to_gym")] = 1.5
            time_weights[IMPULSE_NAMES.index("impulse_order_takeout")] = 1.5
            time_weights[IMPULSE_NAMES.index("impulse_cook_meal")] = 1.5
        elif 21 <= hour < 24:  # 夜晚
            time_weights[IMPULSE_NAMES.index("impulse_play_pc_game")] = 2.0
            time_weights[IMPULSE_NAMES.index("impulse_play_mobile_game")] = 2.0
            time_weights[IMPULSE_NAMES.index("impulse_binge_show")] = 2.0
            time_weights[IMPULSE_NAMES.index("impulse_drink_coffee")] = 0.1
            time_weights[IMPULSE_NAMES.index("impulse_drink_alcohol")] = 1.5
        elif 0 <= hour < 6:  # 深夜
            time_weights[IMPULSE_NAMES.index("impulse_fantasize_future")] = 2.0
            time_weights[IMPULSE_NAMES.index("impulse_reminisce_past")] = 2.0
            time_weights[IMPULSE_NAMES.index("impulse_complain_life")] = 2.0
            time_weights[IMPULSE_NAMES.index("impulse_eat_snack")] = 1.5
            time_weights[IMPULSE_NAMES.index("impulse_play_pc_game")] = 1.5
            time_weights[IMPULSE_NAMES.index("impulse_go_running")] = 0.01
            time_weights[IMPULSE_NAMES.index("impulse_go_to_gym")] = 0.01

        fire_prob *= time_weights

        # 7. 掷骰子！
        dice = np.random.random(self.num_impulses)
        fired = dice < fire_prob

        # 记录触发冲动 (强度 = instant_power，但最小为 1.0)
        output[fired] = np.maximum(instant_power[fired], 1.0)

        # 触发的节点进入冷却
        self.refractory[fired] = BURST_REFRACTORY_TICKS

        # 更新思维惯性：记录触发冲动的类别时间戳
        for i in np.where(fired)[0]:
            cat = IMPULSE_TO_CATEGORY.get(int(i))
            if cat:
                self.category_last_fired[cat] = now_ts

        self.last_output = output
        self.last_fired = fired
        self.instant_power = instant_power
        self.fire_prob = fire_prob  # 调试用

        return output

    def get_fired_impulses(self) -> list:
        """返回本次 tick 触发爆发的冲动列表。"""
        if self.last_fired is None:
            return []
        result = []
        for i, fired in enumerate(self.last_fired):
            if fired:
                result.append({
                    "index": i,
                    "name": IMPULSE_NAMES[i],
                    "intensity": round(float(self.last_output[i]), 4),
                })
        return result

    def get_membrane_state(self) -> dict:
        """返回瞬间爆发点的状态分析 (改名但为了兼容外部接口)"""
        if not hasattr(self, 'instant_power'):
            return {}
        top_indices = np.argsort(self.fire_prob)[-3:][::-1]
        top_simmering = []
        for idx in top_indices:
            top_simmering.append({
                "name": IMPULSE_NAMES[idx],
                "prob": float(self.fire_prob[idx]),
                "power": float(self.instant_power[idx])
            })
            
        return {
            "max_instant_power": round(float(np.max(self.instant_power)), 4),
            "mean_instant_power": round(float(np.mean(self.instant_power)), 4),
            "num_near_burst_threshold": int(np.sum(self.instant_power > BURST_THRESHOLD * 0.8)),
            "num_in_refractory": int(np.sum(self.refractory > 0)),
            "top_simmering_impulses": top_simmering
        }

    def reset(self):
        self.refractory = np.zeros(self.num_impulses, dtype=np.int64)
        self.category_last_fired = {}
        self.last_output = None
        self.last_fired = None
