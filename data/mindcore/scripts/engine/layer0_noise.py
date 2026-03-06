"""
layer0_noise.py — Layer 0: 绝对随机涌动层 (Stochastic Core)
仿生情感心智引擎 (Biomimetic Mind Engine)

四擎复合驱动：
  1. PinkNoiseEngine      — 1/f 噪声，情绪惯性与底色
  2. OUProcessEngine      — Ornstein-Uhlenbeck，生理内稳态弹性
  3. HawkesEngine         — 自激发点过程，思维雪崩
  4. MarkovChainEngine    — 离散状态跳跃，注意力漂移

每 tick 输出拼接的 Noise_Vector shape=(3000,)，由 Layer0Core 统一管理。
"""

import numpy as np
import math
from datetime import datetime
from engine.config import ENGINE_TIMEZONE
from engine.config import (
    PINK_NOISE_NODES, PINK_NOISE_NUM_OCTAVES,
    OU_PROCESS_NODES, OU_THETA, OU_MU, OU_SIGMA, OU_DT,
    HAWKES_NODES, HAWKES_MU0, HAWKES_ALPHA, HAWKES_BETA, HAWKES_HISTORY_WINDOW,
    MARKOV_NODES, MARKOV_NUM_STATES, MARKOV_TRANSITION, MARKOV_STATE_VALUES,
    CIRCADIAN_PEAK_HOUR, CIRCADIAN_TROUGH_HOUR,
    CIRCADIAN_MIN_MULT, CIRCADIAN_MAX_MULT,
    TOTAL_LAYER0_NODES,
)


# ================================================================
# 引擎 1: 粉红噪声 (Pink Noise / 1/f Noise)
# ================================================================
class PinkNoiseEngine:
    """
    Voss-McCartney 算法生成 1/f 粉红噪声。

    原理：维护 num_octaves 层独立的白噪声源，每层以不同的
    更新频率（2^k ticks 更新一次）贡献信号，叠加后产生功率谱
    密度 S(f) ∝ 1/f 的长程相关序列。

    输出范围归一化到 [-1, 1]。
    """

    def __init__(self, num_nodes: int = PINK_NOISE_NODES,
                 num_octaves: int = PINK_NOISE_NUM_OCTAVES):
        self.num_nodes = num_nodes
        self.num_octaves = num_octaves
        self.tick_count = 0

        # 每层持有一个 shape=(num_nodes,) 的随机值
        self.octave_values = np.random.randn(num_octaves, num_nodes).astype(np.float64)

        # 归一化系数：最大理论叠加幅度
        self._norm = num_octaves * 3.0  # 经验归一化

    def tick(self) -> np.ndarray:
        """生成一次 tick 的粉红噪声张量。shape=(num_nodes,)"""
        self.tick_count += 1

        # Voss-McCartney: 第 k 层每 2^k ticks 更新一次
        for k in range(self.num_octaves):
            period = 1 << k  # 2^k
            if self.tick_count % period == 0:
                self.octave_values[k] = np.random.randn(self.num_nodes)

        # 叠加所有层
        raw = np.sum(self.octave_values, axis=0)

        # 归一化到 [-1, 1]
        output = np.clip(raw / self._norm, -1.0, 1.0)
        return output

    def reset(self):
        self.tick_count = 0
        self.octave_values = np.random.randn(self.num_octaves, self.num_nodes)


# ================================================================
# 引擎 2: Ornstein-Uhlenbeck 过程
# ================================================================
class OUProcessEngine:
    """
    离散化 Euler-Maruyama 方法求解 OU 随机微分方程:
        dx_t = θ(μ - x_t)dt + σ dW_t

    特性：均值回归，受随机扰动但永远被橡皮筋拉回基线。
    模拟疲劳度、多巴胺基线等生理波动。

    输出范围大致在 [-1, 1]（软限制，通过 tanh 压缩）。
    """

    def __init__(self, num_nodes: int = OU_PROCESS_NODES,
                 theta: float = OU_THETA, mu: float = OU_MU,
                 sigma: float = OU_SIGMA, dt: float = OU_DT):
        self.num_nodes = num_nodes
        self.theta = theta
        self.mu = mu
        self.sigma = sigma
        self.dt = dt

        # 初始状态：在基线附近微扰
        self.state = np.random.randn(num_nodes).astype(np.float64) * 0.1 + mu

    def tick(self) -> np.ndarray:
        """执行一步 Euler-Maruyama 步进。shape=(num_nodes,)"""
        dW = np.random.randn(self.num_nodes) * math.sqrt(self.dt)
        drift = self.theta * (self.mu - self.state) * self.dt
        diffusion = self.sigma * dW

        self.state = self.state + drift + diffusion

        # 防止 state 因 dt 过大而溢出产生 inf/nan
        self.state = np.clip(self.state, -100.0, 100.0)

        # 通过 tanh 软压缩到 [-1, 1]
        return np.tanh(self.state)

    def reset(self):
        self.state = np.random.randn(self.num_nodes) * 0.1 + self.mu


# ================================================================
# 引擎 3: 霍克斯过程 (Hawkes Process)
# ================================================================
class HawkesEngine:
    """
    自激发点过程，模拟神经元放电的雪崩效应。

    条件强度:
        λ(t) = μ₀ + Σ α·exp(-β·(t - tᵢ))

    大部分 tick 安静（输出 0），一旦触发则会引发短暂的连锁反应。

    输出：0（未触发）或正浮点数（触发强度）。
    """

    def __init__(self, num_nodes: int = HAWKES_NODES,
                 mu0: float = HAWKES_MU0, alpha: float = HAWKES_ALPHA,
                 beta: float = HAWKES_BETA,
                 history_window: int = HAWKES_HISTORY_WINDOW):
        self.num_nodes = num_nodes
        self.mu0 = mu0
        self.alpha = alpha
        self.beta = beta
        self.history_window = history_window
        self.current_tick = 0

        # 每个节点独立维护触发历史（记录 tick 编号）
        # 用一个二维列表：history[node_idx] = [tick1, tick2, ...]
        self.history = [[] for _ in range(num_nodes)]

    def _compute_intensity(self, node_idx: int) -> float:
        """计算单个节点在当前 tick 的条件强度 λ(t)。"""
        intensity = self.mu0
        for past_tick in self.history[node_idx]:
            dt = self.current_tick - past_tick
            if dt > 0:
                intensity += self.alpha * math.exp(-self.beta * dt)
        return intensity

    def tick(self) -> np.ndarray:
        """
        对每个节点：
        1. 计算当前条件强度 λ(t)
        2. 以 λ(t) 为概率进行伯努利采样
        3. 触发则记录历史并输出强度值，否则输出 0
        """
        self.current_tick += 1
        output = np.zeros(self.num_nodes, dtype=np.float64)

        # 批量计算所有节点的条件强度
        intensities = np.full(self.num_nodes, self.mu0, dtype=np.float64)
        for i in range(self.num_nodes):
            for past_tick in self.history[i]:
                dt = self.current_tick - past_tick
                if dt > 0:
                    try:
                        # 限制指数部分避免 overflow
                        exp_val = math.exp(max(-700.0, -self.beta * dt))
                        intensities[i] += self.alpha * exp_val
                    except OverflowError:
                        pass

        # 概率截断到 [0, 1]
        probs = np.clip(intensities, 0.0, 1.0)

        # 伯努利采样：决定哪些节点在此 tick 触发
        fires = np.random.random(self.num_nodes) < probs

        for i in range(self.num_nodes):
            if fires[i]:
                # 记录触发时间
                self.history[i].append(self.current_tick)
                # 修剪历史窗口
                if len(self.history[i]) > self.history_window:
                    self.history[i] = self.history[i][-self.history_window:]
                # 输出当前强度
                output[i] = intensities[i]

        return output

    def reset(self):
        self.current_tick = 0
        self.history = [[] for _ in range(self.num_nodes)]


# ================================================================
# 引擎 4: 马尔可夫链 (Markov Chain)
# ================================================================
class MarkovChainEngine:
    """
    离散状态转移链，模拟注意力漂移与走神。

    每个节点独立维护一个离散状态 (idle/focused/reminiscing)，
    每 tick 根据转移概率矩阵随机跳转。
    输出为状态对应的浮点编码值。
    """

    def __init__(self, num_nodes: int = MARKOV_NODES,
                 transition_matrix: np.ndarray = MARKOV_TRANSITION,
                 state_values: np.ndarray = MARKOV_STATE_VALUES):
        self.num_nodes = num_nodes
        self.transition = transition_matrix  # shape=(num_states, num_states)
        self.state_values = state_values     # shape=(num_states,)
        self.num_states = len(state_values)

        # 随机初始化每个节点的状态
        self.states = np.random.randint(0, self.num_states, size=num_nodes)

    def tick(self) -> np.ndarray:
        """
        每个节点根据当前状态对应的转移概率行进行采样跳转。
        输出 shape=(num_nodes,)，值为对应状态的浮点编码。
        """
        new_states = np.empty(self.num_nodes, dtype=np.int64)

        # 按当前状态分组批量采样（比逐节点循环快很多）
        for s in range(self.num_states):
            mask = (self.states == s)
            count = np.sum(mask)
            if count > 0:
                # 按转移概率行采样
                new_states[mask] = np.random.choice(
                    self.num_states, size=count, p=self.transition[s]
                )

        self.states = new_states

        # 将离散状态映射为浮点值
        return self.state_values[self.states]

    def reset(self):
        self.states = np.random.randint(0, self.num_states, size=self.num_nodes)


# ================================================================
# 昼夜生物钟乘数 (Circadian Multiplier)
# ================================================================
def compute_circadian_multiplier(current_hour: float = None) -> float:
    """
    将当前时刻映射为生物钟活跃度乘数。

    使用移位余弦函数：
        peak_hour 时为最大值，trough_hour 时为最小值。

    Args:
        current_hour: 当前小时（0-24 浮点）。None 则自动读取系统时钟。

    Returns:
        乘数值，范围 [CIRCADIAN_MIN_MULT, CIRCADIAN_MAX_MULT]
    """
    if current_hour is None:
        now = datetime.now(ENGINE_TIMEZONE)
        current_hour = now.hour + now.minute / 60.0

    # 以 peak_hour 为余弦峰值，周期 24 小时
    phase = 2.0 * math.pi * (current_hour - CIRCADIAN_PEAK_HOUR) / 24.0
    cosine = math.cos(phase)  # 范围 [-1, 1]

    # 线性映射到 [min, max]
    mid = (CIRCADIAN_MAX_MULT + CIRCADIAN_MIN_MULT) / 2.0
    amp = (CIRCADIAN_MAX_MULT - CIRCADIAN_MIN_MULT) / 2.0
    multiplier = mid + amp * cosine

    return multiplier


# ================================================================
# Layer 0 组合器 (Composite Core)
# ================================================================
class Layer0Core:
    """
    Layer 0 总控：管理四个引擎，每 tick 并行运算后拼接输出。

    输出: Noise_Vector shape=(3000,)
          = [Pink(1000) | OU(1000) | Hawkes(500) | Markov(500)]

    可选：乘以 Circadian_Multiplier 进行昼夜调制。
    """

    def __init__(self, enable_circadian: bool = True):
        self.pink = PinkNoiseEngine()
        self.ou = OUProcessEngine()
        self.hawkes = HawkesEngine()
        self.markov = MarkovChainEngine()
        self.enable_circadian = enable_circadian

        self.tick_count = 0
        self.last_output = None
        self.last_circadian = 1.0

    def tick(self, current_hour: float = None) -> np.ndarray:
        """
        执行一次完整的 Layer 0 运算。

        Returns:
            Noise_Vector: shape=(TOTAL_LAYER0_NODES,) = (3000,)
        """
        self.tick_count += 1

        # 四引擎并行出力
        pink_out = self.pink.tick()       # (1000,)
        ou_out = self.ou.tick()           # (1000,)
        hawkes_out = self.hawkes.tick()   # (500,)
        markov_out = self.markov.tick()   # (500,)

        # 拼接
        noise_vector = np.concatenate([pink_out, ou_out, hawkes_out, markov_out])

        # 昼夜调制
        if self.enable_circadian:
            self.last_circadian = compute_circadian_multiplier(current_hour)
            noise_vector = noise_vector * self.last_circadian

        self.last_output = noise_vector
        return noise_vector

    def get_stats(self) -> dict:
        """返回当前 tick 的统计摘要（用于调试/日志）。"""
        if self.last_output is None:
            return {"tick": 0, "status": "not_started"}

        total = TOTAL_LAYER0_NODES
        pink_slice = self.last_output[:PINK_NOISE_NODES]
        ou_slice = self.last_output[PINK_NOISE_NODES:PINK_NOISE_NODES + OU_PROCESS_NODES]
        hawkes_slice = self.last_output[PINK_NOISE_NODES + OU_PROCESS_NODES:
                                         PINK_NOISE_NODES + OU_PROCESS_NODES + HAWKES_NODES]
        markov_slice = self.last_output[-MARKOV_NODES:]

        return {
            "tick": self.tick_count,
            "circadian_multiplier": round(self.last_circadian, 4),
            "noise_vector_shape": self.last_output.shape,
            "pink": {
                "mean": round(float(np.mean(pink_slice)), 4),
                "std": round(float(np.std(pink_slice)), 4),
                "min": round(float(np.min(pink_slice)), 4),
                "max": round(float(np.max(pink_slice)), 4),
            },
            "ou": {
                "mean": round(float(np.mean(ou_slice)), 4),
                "std": round(float(np.std(ou_slice)), 4),
                "min": round(float(np.min(ou_slice)), 4),
                "max": round(float(np.max(ou_slice)), 4),
            },
            "hawkes": {
                "fired_count": int(np.sum(hawkes_slice > 0)),
                "total_nodes": HAWKES_NODES,
                "max_intensity": round(float(np.max(hawkes_slice)), 4),
            },
            "markov": {
                "mean": round(float(np.mean(markov_slice)), 4),
                "unique_values": sorted(set(np.round(markov_slice, 2).tolist())),
            },
        }

    def reset(self):
        self.pink.reset()
        self.ou.reset()
        self.hawkes.reset()
        self.markov.reset()
        self.tick_count = 0
        self.last_output = None
        self.last_circadian = 1.0
