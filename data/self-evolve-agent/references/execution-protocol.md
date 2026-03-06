# Self-Evolve 执行协议与状态机

## 全局并发状态机 (Concurrent State Machine)

Agent 每次运行 self-evolve 都是一次**滴答巡航（Tick Handler）**。
进化流程受制于全局状态文件：`memory/evolve/state.json`

`state.json` 包含 `active_experiments` 数组，允许同时有多个进化实验在后台观察。
**并发限制**：最多允许 10 个实验同时处于 `OBSERVING` 或 `BLOCKED`，且它们**必须是正交的**（不修改相同的配置、代码或能力维度）。

每次启动 `self-evolve`，必须按照以下 **四个步骤的巡航顺序** 执行，走完一步才能走下一步。

---

## 执行协议：四步滴答巡航（The 4-Step Tick）

### Step 1: 扫描正在运行的实验 (Status Sync)
打开并读取 `memory/evolve/state.json` 的 `active_experiments` 数组。
- 如果数组为空：直接跳到 Step 4。
- 若有实验属于 `BLOCKED` 状态：检查是否有解救条件（例如 API 恢复了）。如未解除，跳过该实验；如已解除，将状态重置为 `OBSERVING`。

### Step 2: 记录观察数据 (Record Observations)
针对所有 `status: OBSERVING` 并且还没到期的实验：
- 读取该实验在 `state.json` 中的 `telemetry_hook` 字段。严格执行 `command` 定义的命令收集原始日志。
- **降噪防护**：如果本次 Tick 没有任何实质性指标变化或未收集到新的反馈，**直接跳过，切勿写入全空的假日志**。只有捕获到了新指标才追加到对应的 `memory/evolve/[cycle_id].jsonl`。
- **强制输出**：生成的 JSONL 记录的 `metrics` 字典中，必须强制包含并输出 `extract` 要求的所有监控项键，防范糊弄。
- **极端拦截**：若收集数据时发现极端负向反应（如系统连续崩溃），触发提前终止，强制进入下一步的评估流。

### Step 3: 到期评估与阶段固化 (Evaluate & Solidify)
针对所有 `status: OBSERVING` 并且当前时间 `>= evaluate_by` 的实验：
1. **对比数据**：读取它累积的 JSONL 数据与基线做对比。
2. **决策胜诉方**：选出 A 方案还是 B 方案成功（若都没有基线好，返回退回基线）。
3. **物理固化**：修改对应的 `AGENTS.md` / `TOOLS.md` 或实际代码库。
4. **归档沉淀**：向 `memory/evolve/evolution-log.md` 写入本轮赢家和教训。
5. **驱逐清理**：将其从 `state.json` 的 `active_experiments` 中移除。

### Step 4: 启动新轮次 (Launch New Experiment)
在走完前 3 步后，统计 `state.json` 中剩下的未完结任务数量。
- 若剩余任务数 `>= max_concurrent`（如 10）：**强制结束巡航并退出！**禁止再接新活。
- 若容量充足：开始挑选**一个**全新的进化实验。
- **凑数防护**：如果此时雷达探测不到亟待解决的瓶颈，或者现存痛点均已被包含在活跃实验中，**果断保持安静并退出，绝不可为填满限额而捏造无意义垃圾实验。**

---

## 寻找实验：Phase 0 与 Phase 1

若 Step 4 决定启动新轮次，执行以下流程：

### Phase 0: 寻找瓶颈 (The "What")
- **首先**读取 `memory/evolve/candidates.md`（由BotLearn 心跳或 **DMN 的极客行动提案 (Agentic Action Proposals)** 自动写入的候选池）。
- 其他来源：近期错误日志重复模式、用户反馈抱怨 (MEMORY.md)、效率观察（严重耗时的任务）。
- **选择原则**：一次只进化一个方向。按以下优先级筛选：**即发频率 > 全局杠杆 > 量化可测性**。

### Phase 1: 搜索方案 (The "How")
- 必须同时搜索至少 3 个来源寻找解法（如 `skills.sh`, GitHub, Reddit/社区）。
- 每个来源最多保留 2 个候选方案进行短描述对比。
- **部署实验**：在 `memory/evolve/` 中创建一份物理部署说明（参照进化报告模板）。
- **注册评估任务**：把当前评估截止时间更新至 `memory/evolve/state.json` 的新实验对象中，并将状态从 `IDLE` 改为 `OBSERVING`。

**完成注册后，本轮巡航彻底结束，必须强制停止，等待下一次唤醒才能进入系统。**
