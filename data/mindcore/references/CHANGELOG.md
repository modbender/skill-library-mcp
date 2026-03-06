# CHANGELOG — MindCore 引擎改动记录

## v0.1.0 — 初始提交前的所有改动 (2026-02-22)

### 架构文档
- 新建 `ARCHITECTURE.md`，记录 Layer 0-4 完整架构、数据流、参数说明

### Layer 1 — 感知层

#### 饥饱互斥逻辑
- **文件**: `engine/layer1_sensors.py` → `_compute_continuous_drives()`
- **问题**: `full_stomach` 和 `empty_stomach` 同时为 1，矛盾
- **原因**: 连续驱动的饥饿周期（正弦波）会注入 `empty_stomach`，不管 JSON 里 `full_stomach` 是否为 1
- **修复**: 加了互斥判断——`full_stomach > 0.5` 时不注入 `empty_stomach`，反之亦然

#### 身体底噪识别
- **文件**: `engine/layer1_sensors.py` → `_compute_continuous_drives()`
- **发现**: `jaw_clenched`、`restless_legs`、`joint_stiffness` 不是 bug，是连续驱动的生理波动（正弦周期注入）
- **值**: jaw_clenched=0.011, restless_legs=0.016, joint_stiffness=0.1（固定值）
- **处理**: 不改 Layer 1，在 Layer 4 展示端过滤（见下方）

### Layer 4 — 输出层

#### 感知展示阈值过滤
- **文件**: `engine/layer4_output.py` → `_build_prompt()`
- **问题**: system_prompt_injection 里展示了所有 > 0 的感知，包括 0.011 的底噪
- **修复**: 只展示强度 > 0.3 的感知，过滤掉身体微小波动
- **效果**: 感知列表从 `jaw_clenched, restless_legs, joint_stiffness, full_stomach, empty_stomach` 变为 `full_stomach, dim_lighting, quiet_environment`

### Layer 2 — 冲动层

#### 突触权重比例调整
- **文件**: `engine/layer2_impulses.py` → `tick()`
- **改动**: `instant_power = synapse_input * 0.05 + noise_coupling * 0.5` → `synapse_input * 0.3 + noise_coupling * 0.3`
- **原因**: 感知权重只占 5%，噪声占 50%，导致冲动触发 95% 靠随机，embedding 突触矩阵形同虚设
- **效果**: 感知状态现在能实质影响冲动选择（饿了更容易触发饮食冲动）

### Layer 3 — 性格层

#### 冲动软砍（性格权重调整）
- **文件**: `engine/layer3_personality.py` 性格权重
- **改动**: 把 43 个不相关冲动（chew_gum、foot_bath、jump_rope 等）的性格权重压到 0.05
- **保留高权重**: 健身/攀岩/运动、喝咖啡/奶茶、看动漫/电影、画画/写东西、散步/伸懒腰、发呆/放空、刷手机、聊天

#### 场景上下文 Mask（9 条规则）
- **文件**: `engine/layer3_personality.py`
- **新增规则**:
  - `alone_at_home`: 户外社交类压低
  - `crowded_place`: 独处类压低
  - `quiet_environment`: 嘈杂类压低
  - `noisy_environment`: 安静类压低
  - `deep_conversation`: 娱乐类压低
  - `weekend`: 工作类压低，娱乐类提升
  - `caffeine_high`: 学习/工作类提升
  - `sunny_outside`: 户外类提升
  - `is_raining`: 户外类压低，室内类提升

### Supervisor

#### 睡眠模式
- **文件**: `engine_supervisor.py`
- **改动**: 支持 `data/sleep_mode.flag` 文件开关，存在时引擎照跑但不推送冲动
- **原有**: 深夜静默 00:00-09:00
- **新增**: 手动睡眠模式（乌萨奇说"睡觉了"时创建 flag，醒来时删除）

#### 状态写入频率
- **文件**: `engine_supervisor.py`
- **改动**: `mindcore_status.json` 写入频率从每分钟降到每 5 分钟，减少 SSD 损耗

#### 感知衰减表
- **文件**: `engine_supervisor.py`
- **新增**: `jaw_clenched`、`restless_legs`、`joint_stiffness` 加入衰减表

### 已知遗留问题
1. **matmul NaN/overflow 警告** — 突触矩阵或感知向量有极端值，被 `nan_to_num` 兜住但不干净
2. **embedding 突触矩阵只有正权重** — 缺少抑制关系（sleep_deprived 不会压低 go_running）
3. **冲动不知道对话上下文** — 刚聊完攀岩不会提高 go_climbing 的权重
4. **情绪惯性太弱** — mood_valence 几乎一直是 0
