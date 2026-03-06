"""
config.py — 全局超参数定义 (Global Hyperparameters)
仿生情感心智引擎 (Biomimetic Mind Engine)

所有可调参数集中于此，禁止在其他文件中硬编码魔法数字。
"""

import numpy as np
import math
from datetime import timezone, timedelta

# 引擎时区（北京时间 UTC+8）
ENGINE_TIMEZONE = timezone(timedelta(hours=8))

# ============================================================
# 系统级参数
# ============================================================
TICK_INTERVAL_SEC = 1.0          # 引擎主循环每 tick 间隔（秒）

# ============================================================
# Layer 0: 噪声发生器节点数
# ============================================================
PINK_NOISE_NODES   = 1000       # 粉红噪声节点数
OU_PROCESS_NODES   = 1000       # Ornstein-Uhlenbeck 节点数
HAWKES_NODES       = 500        # 霍克斯过程节点数
MARKOV_NODES       = 500        # 马尔可夫链节点数
TOTAL_LAYER0_NODES = PINK_NOISE_NODES + OU_PROCESS_NODES + HAWKES_NODES + MARKOV_NODES  # 3000

# ============================================================
# 引擎 1: 粉红噪声参数 (Pink Noise / 1/f Noise)
# ============================================================
PINK_NOISE_NUM_OCTAVES = 16     # Voss-McCartney 算法的叠加层数
                                 # 越多 → 长程相关性越强，情绪底色越平滑

# ============================================================
# 引擎 2: Ornstein-Uhlenbeck 过程参数
# ============================================================
OU_THETA = 0.15                 # 恢复速率 (橡皮筋弹力)
                                 # 越大 → 偏离后回归基线越快
OU_MU    = 0.0                  # 生理基线 (正常状态均值)
OU_SIGMA = 0.3                  # 随机扰动强度
                                 # 越大 → 波动越剧烈
OU_DT    = 1.0                  # 离散化时间步长 (对应 1 tick)

# ============================================================
# 引擎 3: 霍克斯过程参数 (Hawkes Process)
# ============================================================
HAWKES_MU0   = 0.02             # 基础触发概率 (极低，保证大部分时间安静)
HAWKES_ALPHA = 0.5              # 每次触发后的激发强度飙升量
HAWKES_BETA  = 1.0              # 激发强度的指数衰减速率
                                 # α/β < 1 保证过程不会爆炸
HAWKES_HISTORY_WINDOW = 50      # 只保留最近 N 次触发历史 (节省内存)

# ============================================================
# 引擎 4: 马尔可夫链参数 (Markov Chain)
# ============================================================
MARKOV_STATES = ["idle", "focused", "reminiscing"]  # 离散潜意识状态
MARKOV_NUM_STATES = len(MARKOV_STATES)

# 状态转移概率矩阵 P[i][j] = P(X_{n+1}=j | X_n=i)
#                    idle   focused  reminiscing
MARKOV_TRANSITION = np.array([
    [0.70,  0.20,    0.10],     # idle →
    [0.15,  0.70,    0.15],     # focused →
    [0.20,  0.10,    0.70],     # reminiscing →
], dtype=np.float64)

# 每个状态映射到的浮点输出值：用于转换为连续张量
MARKOV_STATE_VALUES = np.array([0.0, 0.6, 1.0], dtype=np.float64)
# idle=0.0 (放空无输出), focused=0.6 (中等), reminiscing=1.0 (高能回忆)

# ============================================================
# 昼夜生物钟参数 (Circadian Modulation)
# ============================================================
CIRCADIAN_PEAK_HOUR   = 21.0    # 活跃度峰值时刻 (晚9点)
CIRCADIAN_TROUGH_HOUR = 4.0     # 活跃度谷底时刻 (凌晨4点)
CIRCADIAN_MIN_MULT    = 0.05    # 谷底时的最低乘数 (接近沉睡)
CIRCADIAN_MAX_MULT    = 1.5     # 峰值时的最高乘数

# ============================================================
# Layer 1: 感知节点数
# ============================================================
LAYER1_BODY_NODES    = 50       # 身体/生理开关
LAYER1_ENV_NODES     = 50       # 环境开关
LAYER1_SOCIAL_NODES  = 50       # 社交/上下文开关
TOTAL_LAYER1_NODES   = LAYER1_BODY_NODES + LAYER1_ENV_NODES + LAYER1_SOCIAL_NODES  # 150

# ============================================================
# Layer 2: 冲动节点数与触发频率 (Burst Tuning)
# ============================================================
TOTAL_LAYER2_NODES = 150        # 潜意识冲动总数

# 基础触发门槛偏移量 (控制整体发言频率)
# - 12.5: 默认现实模式 (平均约 2~3次/小时)
# - 11.0: 活跃模式 (平均约 1次/10分钟)
# - 10.0: 测试爆字模式 (平均约 1次/2分钟)
BURST_BASE_OFFSET = 12.5

# ============================================================
# Layer 3: 性格闸门
# ============================================================
TOTAL_LAYER3_NODES = 150        # 与 Layer 2 一一对应
PERSONALITY_INIT_WEIGHT = 0.5   # 初始性格权重 (白纸状态)

# ============================================================
# Layer 4: 输出模板
# ============================================================
TOTAL_LAYER4_NODES = 10         # 输出 Prompt 模板数

# ============================================================
# 心理动力学参数 (Section 5 补丁)
# ============================================================
MOOD_DECAY_RATE = 0.9998        # mood_valence 每 tick 衰减系数（半衰期 ~58 分钟）
COMFORT_BASE_DELTA = 0.2        # 安慰行为的基础修复力
HABITUATION_HALFLIFE_HOURS = 24 # 习惯化半衰期（小时）

# ============================================================
# 数据文件路径
# ============================================================
import os
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(_PROJECT_ROOT, "data")
SENSOR_STATE_PATH = os.path.join(DATA_DIR, "Sensor_State.json")
SHORT_TERM_MEMORY_PATH = os.path.join(DATA_DIR, "ShortTermMemory.json")
LONG_TERM_MEMORY_PATH = os.path.join(DATA_DIR, "LongTermMemory.json")
OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "output")
