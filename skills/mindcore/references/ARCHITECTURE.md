# MindCore 架构文档 — 仿生情感心智引擎

> 五层神经管道，每秒一次心跳，模拟人类潜意识的冲动涌现。

## 总览

```
Layer 0 (噪声) → Layer 1 (感知) → Layer 2 (冲动) → Layer 3 (性格) → Layer 4 (输出)
   3000节点         150节点          150节点          150节点         10模板
```

引擎每秒执行一次完整的五层计算（1 tick = 1 秒）。只有当冲动突破阈值时才产生外部输出。

---

## Layer 0 — 绝对随机涌动层 (Stochastic Core)

**生物学对应：** 神经元自发放电、突触噪声、离子通道随机开闭

**节点数：** 3000

**原理：** 四种随机过程复合驱动，模拟大脑永不停歇的背景噪声。

| 引擎 | 节点数 | 数学模型 | 模拟的现象 |
|------|--------|---------|-----------|
| PinkNoiseEngine | 1000 | Voss-McCartney 1/f 噪声 | 情绪底色的长程相关性。低频波动 = 持续几小时的心情基调 |
| OUProcessEngine | 1000 | Ornstein-Uhlenbeck 过程 | 生理内稳态弹性。偏离基线后像橡皮筋一样弹回（θ=0.15, σ=0.3） |
| HawkesEngine | 500 | 自激发点过程 (Hawkes Process) | 思维雪崩。一个念头触发后短时间内更容易触发下一个（α=0.5, β=1.0, α/β<1 保证不爆炸） |
| MarkovChainEngine | 500 | 离散马尔可夫链 | 注意力漂移。三种状态：idle(放空) → focused(专注) → reminiscing(回忆)，按转移概率跳跃 |

**昼夜节律调制：** 所有噪声乘以一个正弦调制系数，峰值 21:00（×1.5），谷底 04:00（×0.05）。深夜大脑几乎沉睡。

**输出：** shape=(3000,) 的噪声向量

---

## Layer 1 — 客观感知开关层 (Sensor State Layer)

**生物学对应：** 感觉神经元、内感受器、本体感觉

**节点数：** 150（身体 50 + 环境 50 + 社交 49 + 1 padding）

**数据源：** `Sensor_State.json`（外部可写，由 OpenClaw agent 和 supervisor 维护）

**三种心理动力学修正：**

1. **需求压力累积 (Need Accumulation)**
   - 基于时间戳差值的连续压力放大
   - 例：`last_interaction_time` 越久 → 孤独压力越大

2. **习惯化脱敏 (Habituation)**
   - 长期暴露的刺激自动衰减（半衰期 24h）
   - 例：连续下雨 3 天 → 对"下雨"的感知趋近于 0

3. **情绪残留读取 (Mood Valence)**
   - 从 `ShortTermMemory.json` 读取当前心境底色（-1 到 +1）
   - 传递给上层用于阈值调制

**输出：** shape=(150,) 的浮点张量（不是纯 0/1，而是经过修正的连续值）

---

## Layer 2 — 潜意识冲动层 (Impulse Emergence Layer)

**生物学对应：** Leaky Integrate-and-Fire (LIF) 神经元模型

**节点数：** 150 个冲动节点，分 9 大类

| 类别 | 数量 | 索引范围 | 示例 |
|------|------|---------|------|
| 🍜 饮食 | 18 | 0-17 | drink_boba, eat_hotpot, cook_meal |
| 🧍 身体/生理 | 15 | 18-32 | stretch, take_shower, deep_breath |
| 📱 娱乐/消遣 | 25 | 33-57 | scroll_phone, watch_anime, listen_music |
| 📚 学习/工作 | 15 | 58-72 | read_book, work_on_project, make_todo_list |
| 🏃 运动/健康 | 15 | 73-87 | go_to_gym, go_swimming, invite_workout |
| 💬 社交 | 20 | 88-107 | chat_with_someone, share_meme, post_tweet |
| 🏠 生活琐事 | 17 | 108-124 | clean_room, do_laundry, check_weather |
| 😌 情绪/心理 | 15 | 125-139 | zone_out, meditate, write_diary |
| 🎨 创造/表达 | 10 | 140-149 | take_photo, write_code, sing_song |

**核心计算流程：**

```
感知向量(150) × 突触矩阵(150×150) → 引申信号(150)
+ 噪声向量(3000) 降维映射 → 随机点燃能量
+ mood_valence → 阈值调制
= 膜电位累积 → 突破阈值 → 冲动涌现！
```

**关键参数：**
- `BURST_BASE_OFFSET`：触发门槛偏移量。12.5=一小时2次，11.0=10分钟1次，10.0=2分钟1次
- 不应期 (Refractory)：冲动触发后进入冷却期，防止同一冲动连续触发
- 同类别冷却：同类别冲动共享冷却时间

**突触矩阵：** 150×150，由 `auto_topology.py` 使用 sentence-transformers (all-MiniLM-L6-v2) 对节点描述做 embedding，计算余弦相似度自动生成。

**输出：** shape=(150,) 的冲动激活向量 + 触发标记

---

## Layer 3 — 前额叶性格闸门 (Prefrontal Personality Gate)

**生物学对应：** 前额叶皮层的执行控制、冲动抑制

**节点数：** 150（与 Layer 2 一一对应）

**核心机制：**

1. **性格权重过滤**：每个冲动有对应的性格权重（0.05~0.95），初始 0.5（白纸状态）
2. **情境抑制 mask**（2026-02-22 新增）：根据时间和感知状态压低不合理冲动
   - 深夜 00-06：运动 ×0.05，社交 ×0.1
   - 吃饱：饮食 ×0.1
   - 缺觉：运动 ×0.2，学习 ×0.3
   - 运动后：再运动 ×0.2，饮食 ×1.5
   - 下雨：户外运动 ×0.4
3. **Softmax 概率采样**：候选冲动按概率竞争（温度 T=0.5，越低越确定性）
4. **输出 1~2 个胜出冲动**

**RL 性格养成：**
- 通过 +1/-1 反馈信号调整权重
- 学习率随反馈次数衰减（0.01 → 0.005 → 0.001），模拟性格从可塑到固化
- 权重持久化到 `personality_weights.npy`

**mood_valence 衰减：** 每 tick 乘以 0.995，缓慢归零。

**输出：** 1~2 个胜出冲动（含 index, name, intensity, probability）

---

## Layer 4 — 决策输出翻译器 (Decision Output Translator)

**生物学对应：** 运动皮层 → 肌肉执行（说话/行动）

**功能：** 将胜出冲动打包为结构化 JSON，映射到情绪烈度等级的 System Prompt 模板。

**10 种情绪烈度等级：**

| 等级 | 阈值 | 风格 |
|------|------|------|
| comatose | 0.0 | 完全沉默 |
| drowsy | 0.2 | 昏昏欲睡，用词极简 |
| calm | 0.4 | 平静温和，正常社交 |
| engaged | 0.6 | 活跃投入，话变多 |
| excited | 0.8 | 兴奋激动，感叹号增多 |
| passionate | 1.0 | 充满热情，滔滔不绝 |
| agitated | 1.3 | 烦躁不安，容易杠 |
| volatile | 1.6 | 忽冷忽热，需要被关注 |
| explosive | 2.0 | 情绪爆发，用词激烈 |
| meltdown | 2.5 | 彻底崩溃/狂喜，纯粹情绪宣泄 |

**输出：** `system_prompt_injection` 字符串，注入 OpenClaw agent 的 system prompt，让 LLM 以对应的情绪风格说话。

---

## Supervisor — 引擎守护进程

**职责：**
- 持续运行引擎主循环
- 冲动触发时调用 `openclaw agent --deliver` 推送到 Telegram
- 深夜静默（00:00-09:00 不推送，引擎照跑）
- 感知状态自动衰减（运动后 2h 心跳恢复，吃饱 3h 后饿）
- 监听 LLM 下发的配置命令（`config_cmd.json`）和 RL 反馈（`reward_cmd.json`）
- 写入 `mindcore_status.json` 供调试查看

---

## 数据流全景

```
Sensor_State.json ──→ Layer 1 ──→ Layer 2 ──→ Layer 3 ──→ Layer 4
                        ↑            ↑           ↑           ↓
                   需求压力累积    Layer 0     性格权重    system_prompt_injection
                   习惯化脱敏     噪声注入    情境mask         ↓
                   mood读取      突触矩阵    RL养成      openclaw agent --deliver
                                                              ↓
                                                         Telegram 消息
```

---

## 待实装功能

| 功能 | 优先级 | 状态 | 说明 |
|------|--------|------|------|
| 短期工作记忆 | ★★★ | 设计完成 | 按触发次数衰减的 5-slot 缓冲区 |
| 场景上下文过滤 | ★★★ | 方向确认 | 情境 mask 的延伸，更细粒度的环境感知 |
| 习惯化 (SFA) | ★★☆ | 有公式 | Spike-Frequency Adaptation，触发后阈值升高再衰减 |
| 注意力机制 | ★★☆ | 构想中 | 对话主题影响冲动权重 |
| 情绪多维向量 | ★☆☆ | 构想中 | mood 从标量改为多维向量 |
| 需求层次 | ★☆☆ | 构想中 | 马斯洛层次，生理优先 |

---

_最后更新：2026-02-22 by 乌萨奇_
