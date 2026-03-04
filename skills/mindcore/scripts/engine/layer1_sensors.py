"""
layer1_sensors.py — Layer 1: 客观感知开关层 (Sensor State Layer)
仿生情感心智引擎 (Biomimetic Mind Engine)

从 Sensor_State.json 读取 50 个感知节点的状态。
不是简单的二进制读取，而是集成了三种高级心理动力学修正：

1. 需求压力累积 (Need Accumulation)
   - 基于时间戳差值的连续压力放大
   - 如 last_interaction_time 越久 → 孤独压力越大

2. 习惯化脱敏 (Habituation)
   - 长期暴露的刺激自动衰减
   - 如下雨持续3天 → 影响力趋近于0

3. 情绪残留读取 (Mood Valence)
   - 从 ShortTermMemory.json 读取当前心境底色
   - 传递给上层用于阈值调制

输出：shape=(50,) 的浮点张量（不再是纯 0/1）
"""

import json
import time
import math
import numpy as np
from engine.config import (
    SENSOR_STATE_PATH, SHORT_TERM_MEMORY_PATH,
    TOTAL_LAYER1_NODES, LAYER1_BODY_NODES, LAYER1_ENV_NODES, LAYER1_SOCIAL_NODES,
    HABITUATION_HALFLIFE_HOURS, MOOD_DECAY_RATE,
)


# ================================================================
# 节点注册表 (定义 50 个节点的顺序与 JSON 映射)
# ================================================================

# 身体/生理开关 (50 个)
BODY_KEYS = [
    "muscle_soreness", "eye_fatigue", "headache", "back_pain", "neck_stiff",
    "cold_hands", "heavy_eyelids", "jaw_clenched", "restless_legs", "joint_stiffness",
    "overall_fatigue", "high_energy", "feverish", "chills", "sweating",
    "dizziness", "nausea", "heart_racing", "slow_heartbeat", "adrenaline_spike",
    "full_stomach", "empty_stomach", "thirsty", "dehydrated", "caffeine_high",
    "sugar_crash", "sugar_high", "protein_craving", "salt_craving", "carb_craving",
    "sleep_deprived", "well_rested", "post_workout_soreness", "post_workout_high", "yawning",
    "groggy_morning", "insomnia_feeling", "deep_sleep_hangover", "over_slept", "physical_exhaustion",
    "shallow_breathing", "deep_breathing", "shortness_of_breath", "dry_eyes", "dry_mouth",
    "tinnitus_ringing", "sensitive_hearing", "light_sensitivity", "smell_sensitivity", "touch_sensitivity"
]

# 环境开关 (50 个)
ENV_KEYS = [
    "is_raining", "is_snowing", "sunny_outside", "cloudy_overcast", "stormy_weather",
    "windy_outside", "foggy_outside", "humid_air", "dry_air", "thunderstorm",
    "cold_room", "hot_room", "comfortable_temperature", "drafty_breeze", "stuffy_room",
    "dim_lighting", "bright_lighting", "fluorescent_lights", "natural_sunlight", "pitch_black",
    "noisy_environment", "quiet_environment", "white_noise_hum", "sudden_loud_noise", "background_music",
    "crowded_place", "alone_at_home", "spacious_room", "cramped_space", "messy_environment",
    "early_morning", "midday", "late_afternoon", "sunset_time", "late_night",
    "monday_morning", "friday_evening", "weekend", "holiday", "work_hours",
    "screen_glare", "notification_spam", "offline_peace", "in_transit_moving", "at_desk_sitting",
    "nature_surroundings", "urban_surroundings", "familiar_place", "unfamiliar_place", "fresh_air"
]

# 社交/上下文开关 (49 个)
SOCIAL_KEYS = [
    "ignored_long_time", "just_praised", "receiving_comfort", "deep_conversation", "shared_meme", 
    "mentioned_by_name", "friendly_banter", "received_gift", "mutual_understanding", "flirting_received", 
    "complimented_appearance", "invited_to_event", "warm_greeting", "gratitude_received", "inside_joke_shared", 
    "just_criticized", "seen_but_no_reply", "awkward_silence", "interrupted", "passive_aggressive_remark",
    "rejected_proposal", "gaslit_feeling", "argument_escalated", "betrayal_sensed", "publicly_embarrassed",
    "left_out_of_group", "unfairly_blamed", "condescending_tone", "gossiped_about", 
    "small_talk", "someone_online", "group_chat_active", "asked_personal_question", "long_voice_message",
    "professional_email", "formal_meeting", "stranger_eye_contact", "background_chatter", 
    "liked_my_post", "unfollowed_me", "typing_indicator_active", "read_receipt_on", "voice_call_ringing",
    "video_call_started", "emoji_reaction_received", "link_shared_with_me", 
    "missing_someone", "feeling_smothered", "social_battery_low"
]

# 带时间戳的特殊节点（用于需求累积和习惯化）
TIMESTAMP_KEYS = {
    "last_interaction_time": "social",    # 需求累积：孤独感
    "raining_start_time": "environment",  # 习惯化：下雨脱敏
}

ALL_KEYS = BODY_KEYS + ENV_KEYS + SOCIAL_KEYS
assert len(ALL_KEYS) == TOTAL_LAYER1_NODES - 1, \
    f"Node count mismatch: {len(ALL_KEYS)} vs expected {TOTAL_LAYER1_NODES - 1}"
# Note: social has 14 regular keys + ignored_long_time is computed, total = 49 regular + 1 computed = 50


# ================================================================
# Layer 1 感知读取器
# ================================================================
class Layer1Sensors:
    """
    从本地 JSON 读取感知状态，输出增强后的浮点张量。

    输出 shape=(TOTAL_LAYER1_NODES,)
    值域 [0.0, ∞) — 大部分为 0 或 1，但时间压力可超过 1。
    """

    def __init__(self, sensor_path: str = SENSOR_STATE_PATH,
                 memory_path: str = SHORT_TERM_MEMORY_PATH):
        self.sensor_path = sensor_path
        self.memory_path = memory_path
        self.last_output = None
        self.mood_valence = 0.0  # 从 ShortTermMemory 同步

    def _load_json(self, path: str) -> dict:
        """安全加载 JSON 文件。"""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[Layer1] WARNING: Failed to load {path}: {e}")
            return {}

    def _compute_need_pressure(self, last_interaction_time) -> float:
        """
        需求压力累积：孤独感随时间单调递增。

        公式：pressure = sqrt(hours_since_interaction)
        - 1小时: 1.0
        - 4小时: 2.0
        - 9小时: 3.0
        - 16小时: 4.0

        使用平方根以避免无限暴涨，同时保证足够的压力增长。
        """
        if last_interaction_time is None:
            return 0.0

        now = time.time()
        elapsed_sec = max(0, now - last_interaction_time)
        elapsed_hours = elapsed_sec / 3600.0

        # 封顶机制：最大压力为 1.0
        return min(1.0, math.sqrt(elapsed_hours) / 4.0)

    def _compute_habituation(self, start_time, halflife_hours: float = HABITUATION_HALFLIFE_HOURS) -> float:
        """
        习惯化脱敏：长期暴露后刺激效果指数衰减。

        公式：factor = 2^(-elapsed_hours / halflife)
        - 0小时: 1.0 (全效)
        - 24小时: 0.5 (半衰)
        - 48小时: 0.25
        - 72小时: 0.125
        """
        if start_time is None:
            return 1.0  # 无起始时间，不做衰减

        now = time.time()
        elapsed_hours = max(0, now - start_time) / 3600.0

        return math.pow(2.0, -elapsed_hours / halflife_hours)

    def tick(self) -> np.ndarray:
        """
        读取 JSON 文件，构建增强后的 Layer 1 输出张量。

        Returns:
            sensor_vector: shape=(TOTAL_LAYER1_NODES,)
        """
        sensor_data = self._load_json(self.sensor_path)
        memory_data = self._load_json(self.memory_path)

        # 更新心境底色
        self.mood_valence = memory_data.get("mood_valence", 0.0)

        output = np.zeros(TOTAL_LAYER1_NODES, dtype=np.float64)

        # --- 身体/生理节点 (0~19) ---
        body = sensor_data.get("body", {})
        for i, key in enumerate(BODY_KEYS):
            output[i] = float(body.get(key, 0))

        # --- 环境节点 (20~34) ---
        env = sensor_data.get("environment", {})
        offset = LAYER1_BODY_NODES
        for i, key in enumerate(ENV_KEYS):
            val = float(env.get(key, 0))

            # 习惯化修正：如果有对应的 start_time 字段
            start_key = f"{key}_start_time"
            if start_key in TIMESTAMP_KEYS or f"{key.replace('is_', '')}_start_time" in env:
                # 尝试获取开始时间
                start_time = env.get(f"{key.replace('is_', '')}_start_time") or env.get(start_key)
                if start_time is not None and val > 0:
                    val *= self._compute_habituation(start_time)

            output[offset + i] = val

        # --- 社交/上下文节点 (35~49) ---
        social = sensor_data.get("social", {})
        offset = LAYER1_BODY_NODES + LAYER1_ENV_NODES

        # 特殊处理：ignored_long_time 从时间戳计算需求压力
        last_interaction = social.get("last_interaction_time")
        need_pressure = self._compute_need_pressure(last_interaction)

        for i, key in enumerate(SOCIAL_KEYS):
            if key == "ignored_long_time":
                # 用连续压力值替代二值开关
                output[offset + i] = need_pressure
            else:
                output[offset + i] = float(social.get(key, 0))

        # 最后一个节点位留给全局需求压力的备用信号
        if TOTAL_LAYER1_NODES > len(ALL_KEYS):
            output[-1] = need_pressure

        # 叠加生命体征连续底座感知（生物钟、饥饿、自然呼吸等默认开启的感知）
        self._compute_continuous_drives(output)

        self.last_output = output
        return output

    def _compute_continuous_drives(self, output: np.ndarray):
        """
        计算那些不需要外部事件触发、一直处于开机状态并随时间起伏的“连续感知”。
        使用正弦函数和物理世界时间构建心智引擎底层的生机。
        """
        from datetime import datetime
        from engine.config import ENGINE_TIMEZONE
        now = datetime.now(ENGINE_TIMEZONE)
        hour = now.hour + now.minute / 60.0
        time_elapsed = time.time()

        all_keys_dict = {key: i for i, key in enumerate(ALL_KEYS)}

        def set_drive(key, val):
            if key in all_keys_dict:
                i = all_keys_dict[key]
                # 仅当外界没有显式强行覆盖（即 output[i] 接近 0）时，才叠加基础波动
                if output[i] < 0.01:
                    output[i] += max(0.0, min(1.0, val))

        # ----------------------------------------
        # 1. 昼夜节律 (Circadian / Time of Day)
        # ----------------------------------------
        if 6 <= hour <= 10:
            set_drive("groggy_morning", 1.0 - abs(hour - 8)/2.0)
            set_drive("early_morning", 1.0 - abs(hour - 8)/2.0)
            set_drive("natural_sunlight", 0.4)
        elif 11 <= hour <= 14:
            set_drive("midday", 1.0 - abs(hour - 12.5)/1.5)
            set_drive("natural_sunlight", 0.8)
            set_drive("high_energy", 0.5)
        elif 15 <= hour <= 18:
            set_drive("late_afternoon", 1.0 - abs(hour - 16.5)/1.5)
            set_drive("sunset_time", 1.0 - abs(hour - 18)/1.0)
            set_drive("natural_sunlight", 0.3)
            
        # --- 睡眠节律：余弦曲线，凌晨2点峰值，上午10点谷值 ---
        # cos((hour - 2) / 24 * 2π) → 2:00 = 1.0, 14:00 = -1.0
        sleep_raw = math.cos((hour - 2.0) / 24.0 * 2.0 * math.pi)
        sleepiness = max(0.0, (sleep_raw + 1.0) / 2.0)  # 归一化到 [0, 1]
        # 午后小低谷 (14:00-15:30)
        afternoon_dip = math.exp(-0.5 * ((hour - 14.5) / 0.8) ** 2) * 0.3
        sleepiness = min(1.0, sleepiness + afternoon_dip)

        if sleepiness > 0.3:
            set_drive("sleep_deprived", sleepiness * 0.7)
            set_drive("heavy_eyelids", sleepiness * 0.6)
            set_drive("overall_fatigue", sleepiness * 0.5)
        if sleepiness > 0.5:
            set_drive("yawning", sleepiness * 0.5)

        # 深夜环境感知
        if hour >= 22 or hour <= 5:
            night_depth = sleepiness
            set_drive("late_night", night_depth)
            set_drive("pitch_black", 0.6)
            set_drive("quiet_environment", 0.5)

        if 8 <= hour <= 18:
            set_drive("sunny_outside", 0.6)
            set_drive("bright_lighting", 0.5)

        # ----------------------------------------
        # 2. 生理波动 (Biological Oscillators) — 基于真实时钟
        # ----------------------------------------

        # --- 饥饿节律：三餐制 (8:00, 12:30, 18:30 为饭点) ---
        # 饭前1.5-2小时开始饿，饭后不饿，用三个高斯峰叠加
        meal_times = [8.0, 12.5, 18.5]  # 三餐时间点
        hungry_val = 0.0
        for mt in meal_times:
            # 饭前饿：峰值在饭点前1小时，sigma=1.5小时
            dist = abs(hour - mt)
            if dist > 12:
                dist = 24 - dist  # 跨午夜
            hungry_val = max(hungry_val, math.exp(-0.5 * ((dist + 1.0) / 1.5) ** 2))

        # 时间戳衰减：如果最近吃过饭，压低饥饿值
        sensor_json = self._load_json(self.sensor_path)
        last_meal = sensor_json.get("_meta", {}).get("last_meal_time")
        if last_meal is not None:
            try:
                hours_since_meal = (time.time() - float(last_meal)) / 3600.0
                if hours_since_meal < 3.0:
                    meal_suppression = 1.0 - math.exp(-0.5 * (hours_since_meal / 1.5) ** 2)
                    hungry_val *= meal_suppression
            except (ValueError, TypeError):
                pass  # 时间戳无效，忽略，退回纯节律

        full_idx = all_keys_dict.get("full_stomach")
        empty_idx = all_keys_dict.get("empty_stomach")
        is_full = (full_idx is not None and output[full_idx] > 0.5)
        is_empty = (empty_idx is not None and output[empty_idx] > 0.5)

        if not is_full:
            set_drive("empty_stomach", hungry_val * 0.8)
        if not is_empty and hungry_val > 0.6:
            set_drive("carb_craving", 0.5)

        # --- 口渴节律：基于真实时钟，白天渴得多 ---
        # 10:00, 14:00, 17:00, 21:00 四个小波峰
        thirst_times = [10.0, 14.0, 17.0, 21.0]
        thirsty_val = 0.0
        for tt in thirst_times:
            dist = abs(hour - tt)
            if dist > 12:
                dist = 24 - dist
            thirsty_val = max(thirsty_val, math.exp(-0.5 * (dist / 1.5) ** 2) * 0.7)

        set_drive("thirsty", thirsty_val * 0.6)
        if thirsty_val > 0.5:
            set_drive("dry_mouth", 0.4)

        # 呼吸与微小动作 (分钟级循环)
        breath_val = (math.sin(time_elapsed / 60.0 * (2 * math.pi / 5.0)) + 1.0) / 2.0
        set_drive("shallow_breathing", breath_val * 0.3)
        set_drive("deep_breathing", (1.0 - breath_val) * 0.3)
        
        fidget_val = (math.sin(time_elapsed / 60.0 * (2 * math.pi / 12.0)) + 1.0) / 2.0
        set_drive("restless_legs", fidget_val * 0.3)
        set_drive("jaw_clenched", fidget_val * 0.2)
        set_drive("joint_stiffness", 0.1)

        # ----------------------------------------
        # 3. 基础心理防线感知 (Background Constants)
        # ----------------------------------------
        set_drive("background_chatter", 0.15)
        set_drive("white_noise_hum", 0.25)
        set_drive("familiar_place", 0.6)
        
        # (社交电量已移除，等有社交事件追踪再做)

    def get_active_sensors(self) -> list:
        """返回当前激活的传感器名称列表（用于调试）。"""
        if self.last_output is None:
            return []
        active = []
        for i, val in enumerate(self.last_output):
            if val > 0.01:
                if i < len(ALL_KEYS):
                    active.append((ALL_KEYS[i], round(float(val), 3)))
                else:
                    active.append((f"node_{i}", round(float(val), 3)))
        return active

    def get_mood_valence(self) -> float:
        """返回当前心境底色值。"""
        return self.mood_valence
