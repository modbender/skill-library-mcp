"""
engine_loop.py — 仿生心智引擎主循环 (Mind Engine Main Loop)
仿生情感心智引擎 (Biomimetic Mind Engine)

将五层管道串联为一个完整的神经传导回路：
  Layer 0 (噪声) → Layer 1 (感知) → Layer 2 (冲动) → Layer 3 (性格) → Layer 4 (输出)

每 tick = 1 秒执行一次完整的五层计算。
"""

import time
import json
import numpy as np
from datetime import datetime
from engine.config import ENGINE_TIMEZONE

from engine.config import (
    TICK_INTERVAL_SEC, SHORT_TERM_MEMORY_PATH,
    MOOD_DECAY_RATE,
)
from engine.layer0_noise import Layer0Core
from engine.layer1_sensors import Layer1Sensors
from engine.layer2_impulses import Layer2Impulses
from engine.layer3_personality import Layer3Personality
from engine.layer4_output import Layer4Output


class MindEngine:
    """
    仿生心智引擎 — 五层神经管道的总控。

    这个类是整个系统的心脏。
    它不是脚本，不是定时器，而是一个持续跳动的脉搏。
    """

    def __init__(self, synapse_matrix: np.ndarray = None,
                 enable_circadian: bool = True,
                 save_outputs: bool = False):
        """
        Args:
            synapse_matrix: Layer 1→2 突触矩阵。None=随机(测试用)。
            enable_circadian: 是否启用昼夜节律调制。
            save_outputs: 是否将每次输出保存到文件。
        """
        if synapse_matrix is None:
            import os
            from engine.config import DATA_DIR
            matrix_path = os.path.join(DATA_DIR, "Synapse_Matrix.npy")
            if os.path.exists(matrix_path):
                synapse_matrix = np.load(matrix_path)
                print(f"[MindEngine] 🧠 成功加载自动生成的突触矩阵: {matrix_path}")
            else:
                print(f"[MindEngine] ⚠️ 未找到 Synapse_Matrix.npy，将使用随机突触矩阵")

        # 五层管道
        self.layer0 = Layer0Core(enable_circadian=enable_circadian)
        self.layer1 = Layer1Sensors()
        self.layer2 = Layer2Impulses(synapse_matrix=synapse_matrix)
        self.layer3 = Layer3Personality()
        self.layer4 = Layer4Output()

        self.save_outputs = save_outputs
        self.tick_count = 0
        self.total_fires = 0
        self.last_result = None

    def tick(self) -> dict:
        """
        执行一次完整的五层计算。

        Returns:
            result: 包含每层摘要 + 最终输出的完整状态报告
        """
        self.tick_count += 1

        # ── Layer 0: 噪声生成 ──
        noise_vector = self.layer0.tick()
        layer0_stats = self.layer0.get_stats()

        # ── Layer 1: 感知读取 ──
        sensor_vector = self.layer1.tick()
        mood_valence = self.layer1.get_mood_valence()
        active_sensors = self.layer1.get_active_sensors()

        # ── Layer 2: 冲动涌现 ──
        impulse_vector = self.layer2.tick(sensor_vector, noise_vector, mood_valence)
        fired_impulses = self.layer2.get_fired_impulses()
        membrane_state = self.layer2.get_membrane_state()

        # ── Layer 3: 性格裁决 ──
        winners = self.layer3.tick(impulse_vector, mood_valence)

        # ── Layer 4: 输出翻译 ──
        output = self.layer4.tick(
            winners, mood_valence,
            active_sensors=active_sensors,
            membrane_state=membrane_state,
        )

        if self.save_outputs and output.get("should_speak"):
            self.layer4.save_output(output)

        if fired_impulses:
            self.total_fires += len(fired_impulses)

        # 构建完整状态报告
        result = {
            "tick": self.tick_count,
            "timestamp": datetime.now(ENGINE_TIMEZONE).isoformat(),
            "layer0": {
                "circadian": layer0_stats.get("circadian_multiplier", 1.0),
                "hawkes_fires": layer0_stats.get("hawkes", {}).get("fired_count", 0),
            },
            "layer1": {
                "active_count": len(active_sensors),
                "active_sensors": active_sensors[:5],
                "mood_valence": round(mood_valence, 4),
            },
            "layer2": {
                "fired_count": len(fired_impulses),
                "fired": [f["name"] for f in fired_impulses],
                "membrane": membrane_state,
            },
            "layer3": {
                "winner_count": len(winners),
                "winners": [w["name"] for w in winners],
                "candidates": len(self.layer3.last_all_candidates),
            },
            "layer4": output,
        }

        self.last_result = result
        return result

    def run(self, num_ticks: int = None, realtime: bool = True,
            on_speak: callable = None, on_tick: callable = None):
        """
        启动引擎主循环。

        Args:
            num_ticks: 运行次数。None=无限运行。
            realtime: 是否按真实时间间隔运行。
            on_speak: 当 AI 决定说话时的回调 callback(output_dict)
            on_tick: 每 tick 的回调 callback(result_dict)
        """
        tick_num = 0
        try:
            while num_ticks is None or tick_num < num_ticks:
                tick_num += 1
                result = self.tick()

                if on_tick:
                    on_tick(result)

                if on_speak and result["layer4"].get("should_speak"):
                    on_speak(result["layer4"])

                if realtime:
                    time.sleep(TICK_INTERVAL_SEC)

        except KeyboardInterrupt:
            print("\n[MindEngine] 引擎停止。")

    def get_summary(self) -> dict:
        """返回引擎运行摘要。"""
        return {
            "total_ticks": self.tick_count,
            "total_impulse_fires": self.total_fires,
            "personality_profile": self.layer3.get_personality_profile(),
        }

    def reward(self, impulse_index: int, signal: float):
        """向性格层发送 RL 反馈信号。"""
        self.layer3.reward(impulse_index, signal)

    def reset(self):
        self.layer0.reset()
        self.layer2.reset()
        self.layer3.reset()
        self.layer4.reset()
        self.tick_count = 0
        self.total_fires = 0
        self.last_result = None
