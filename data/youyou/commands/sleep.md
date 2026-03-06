---
description: 记录睡眠、评估睡眠质量、识别睡眠问题、提供睡眠卫生建议
arguments:
  - name: action
    description: 操作类型：record(记录睡眠)/history(历史记录)/stats(统计)/psqi(PSQI评估)/epworth(Epworth评估)/isi(ISI评估)/problem(睡眠问题)/hygiene(睡眠卫生)/recommendations(建议)
    required: true
  - name: info
    description: 详细信息（睡眠时间、质量评估、问题描述等，自然语言描述）
    required: false
---

# 睡眠质量管理命令

⚠️ **重要医学免责声明**

本系统提供的睡眠评估、问题识别和建议仅供参考，不构成医疗诊断或治疗方案。

**本系统能够做到的**：
- ✅ 记录和追踪睡眠数据
- ✅ 评估睡眠质量趋势
- ✅ 识别睡眠问题风险
- ✅ 提供睡眠卫生建议
- ✅ 分析睡眠模式和影响因素

**本系统不能做的**：
- ❌ 诊断失眠、睡眠呼吸暂停等睡眠疾病
- ❌ 开具助眠药物或调整药物剂量
- ❌ 替代专业睡眠医学治疗（如CBT-I、CPAP等）
- ❌ 处理严重睡眠障碍或紧急情况

**何时需要就医**：
- 🏥 失眠持续超过3个月，严重影响日常生活
- 🏥 出现呼吸暂停症状（打鼾、憋醒、白天嗜睡）
- 🏥 不宁腿症状严重影响睡眠
- 🏥 严重嗜睡影响工作、学习或驾驶安全
- 🏥 任何突发的、严重的睡眠问题

---

## 使用方法

### 记录睡眠

```bash
# 快速记录
/sleep record 23:00 07:00 good
/sleep record 22:30 06:30 excellent
/sleep record 23:30 07:00 fair

# 详细记录
/sleep record bedtime 23:00 onset 23:30 wake 07:00 outbed 07:15
/sleep record 23:00 07:00 good quality 8 efficiency 95

# 记录觉醒情况
/sleep record 23:00 07:00 fair 2 awakenings
/sleep record 23:00 07:00 poor 3 awakenings bathroom noise

# 记录影响因素
/sleep record 23:00 07:00 good exercise evening no_caffeine
/sleep record 23:00 07:00 fair caffeine_after_2pm screen_time 90

# 记录睡前例行活动
/sleep record 23:00 07:00 good routine 30min reading relaxation
```

**睡眠质量描述**：
- excellent（优秀）/ very good（很好）/ good（好）
- fair（一般）/ poor（差）/ very poor（很差）

**影响因素**：
- caffeine_after_2pm（下午2点后摄入咖啡因）
- alcohol（饮酒）
- exercise（运动时间：morning/afternoon/evening/none）
- screen_time（睡前屏幕时间，分钟数）
- stress（压力水平：low/medium/high）

---

### 查看睡眠历史

```bash
# 查看最近记录
/sleep history
/sleep history 7                       # 最近7晚

# 查看本周/本月
/sleep history week
/sleep history month

# 查看特定日期
/sleep history 2025-06-20
/sleep history today
/sleep history yesterday

# 查看日期范围
/sleep history 2025-06-01 to 2025-06-30
/sleep history last 7 days
/sleep history last 30 days
```

**输出内容**：
- 睡眠时间（上床、入睡、起床、起床离床）
- 睡眠指标（时长、潜伏期、效率）
- 睡眠质量评分
- 夜间觉醒详情
- 影响因素
- 睡前例行活动

---

### 睡眠统计分析

```bash
# 综合统计
/sleep stats
/sleep stats week
/sleep stats month

# 特定统计
/sleep average                         # 平均睡眠时长
/sleep efficiency                      # 睡眠效率
/sleep latency                         # 入睡潜伏期
/sleep pattern                         # 睡眠模式分析

# 睡眠质量分布
/sleep quality distribution
/sleep quality trend                   # 质量趋势

# 作息规律性
/sleep consistency                     # 作息一致性
/sleep schedule                        # 作息时间分析
```

**输出内容**：
- 平均睡眠时长、入睡时间、起床时间
- 平均睡眠潜伏期、睡眠效率
- 睡眠质量分布（好/中/差）
- 工作日vs周末对比
- 作息规律性评分
- 最佳上床/起床时间
- 社会时差

---

### PSQI 评估（匹兹堡睡眠质量指数）

```bash
# 进行 PSQI 评估
/sleep psqi

# 记录 PSQI 分数
/sleep psqi score 8
/sleep psqi score 10 date 2025-06-15

# 查看 PSQI 历史
/sleep psqi history
/sleep psqi trend                      # PSQI 分数趋势

# PSQI 分数说明
/sleep psqi explain
```

**PSQI 量表说明**：

PSQI 评估 7 个成分（每个 0-3 分）：

1. **主观睡眠质量**（C1）：
   - 0分：很好
   - 1分：较好
   - 2分：较差
   - 3分：很差

2. **入睡时间**（C2）：
   - 0分：≤15分钟
   - 1分：16-30分钟
   - 2分：31-60分钟
   - 3分：>60分钟

3. **睡眠时间**（C3）：
   - 0分：>7小时
   - 1分：6-7小时
   - 2分：5-6小时
   - 3分：<5小时

4. **睡眠效率**（C4）：
   - 0分：>85%
   - 1分：75-84%
   - 2分：65-74%
   - 3分：<65%

5. **睡眠障碍**（C5）：
   - 0分：无问题
   - 1分：轻度问题（<1次/周）
   - 2分：中度问题（1-2次/周）
   - 3分：重度问题（≥3次/周）

6. **催眠药物使用**（C6）：
   - 0分：无
   - 1分：<1次/周
   - 2分：1-2次/周
   - 3分：≥3次/周

7. **日间功能障碍**（C7）：
   - 0分：无
   - 1分：轻度（<1次/周）
   - 2分：中度（1-2次/周）
   - 3分：重度（≥3次/周）

**总分范围**：0-21 分
- ≤5分：睡眠质量好
- 6-10分：睡眠质量一般
- ≥11分：睡眠质量差

---

### Epworth 嗜睡量表评估

```bash
# 进行 Epworth 评估
/sleep epworth

# 记录 Epworth 分数
/sleep epworth score 6
/sleep epworth score 12 date 2025-06-10

# 查看 Epworth 历史
/sleep epworth history
```

**Epworth 量表说明**：

评估 8 种情况下打瞌睡的可能（0-3 分）：
- 0分：不会打瞌睡
- 1分：打瞌睡可能性很小
- 2分：打瞌睡可能性中等
- 3分：很可能打瞌睡

**8 种情境**：
1. 坐着阅读时
2. 看电视时
3. 在公共场所坐着不动时（如剧场、会议）
4. 连续坐1小时乘车时
5. 下午躺下休息时（条件允许时）
6. 坐着与人交谈时
7. 午饭后静坐时（未饮酒）
8. 等红绿灯驾车时

**总分范围**：0-24 分
- 0-7分：正常
- 8-10分：轻度嗜睡
- 11-15分：中度嗜睡
- 16-24分：重度嗜睡

⚠️ **注意**：Epworth 分数≥11 分建议就医评估睡眠呼吸暂停等疾病。

---

### ISI 失眠严重度评估

```bash
# 进行 ISI 评估
/sleep isi

# 记录 ISI 分数
/sleep isi score 11
/sleep isi score 18 date 2025-06-05

# 查看 ISI 历史
/sleep isi history
```

**ISI 量表说明**：

评估 7 个问题（每个 0-4 分）：
1. 入睡困难
2. 维持睡眠困难
3. 早醒
4. 对睡眠模式满意程度
5. 白天疲劳程度
6. 日间功能受损程度
7. 睡眠问题对生活质量的影响

**总分范围**：0-28 分
- 0-7分：无临床显著失眠
- 8-14分：轻度失眠
- 15-21分：中度失眠
- 22-28分：重度失眠

⚠️ **注意**：ISI 分数≥15 分建议就医咨询睡眠专科。

---

### 查看所有评估结果

```bash
# 查看所有评估
/sleep assessments
/sleep assessments list                # 所有评估列表

# 查看睡眠质量趋势
/sleep trend
/sleep trend quality                   # 睡眠质量趋势
/sleep trend psqi                      # PSQI 分数趋势
```

---

### 睡眠问题识别

```bash
# 失眠评估
/sleep problem insomnia
/sleep problem insomnia type mixed      # 记录失眠类型
/sleep problem insomnia cause stress    # 记录原因

# 呼吸暂停筛查
/sleep apnea screening
/sleep apnea stop-bang                 # STOP-BANG 问卷
/sleep snoring loud                    # 记录打鼾

# 其他睡眠问题
/sleep problem rls                     # 不宁腿评估
/sleep problem plmd                    # 周期性肢体运动

# 查看所有问题
/sleep problems
/sleep problems list
```

**失眠类型**：
- onset（入睡困难）：入睡时间>30分钟
- maintenance（睡眠维持困难）：夜间觉醒>2次或总觉醒时间>30分钟
- mixed（混合型）：入睡困难和睡眠维持困难
- early_awakening（早醒）：比预期提前醒来>30分钟且无法再入睡

**STOP-BANG 问卷**（呼吸暂停风险筛查）：
- **S**nore（打鼾）：响亮打鼾？
- **T**ired（疲劳）：白天疲劳或嗜睡？
- **O**bserved（观察到呼吸暂停）：有人观察到你呼吸暂停？
- **P**ressure（血压）：高血压？
- **B**MI（体重指数）：BMI > 28？
- **A**ge（年龄）：年龄 > 50岁？
- **N**eck（颈围）：颈围 > 40cm（男）或 > 37cm（女）？
- **G**ender（性别）：男性？

**风险分级**：
- 低风险：0-2分
- 中等风险：3-4分
- 高风险：5-8分

⚠️ **注意**：STOP-BANG ≥3 分建议进行睡眠检查（PSG）。

---

### 睡眠卫生评估

```bash
# 评估当前睡眠卫生
/sleep hygiene

# 记录睡眠环境
/sleep hygiene temperature 22
/sleep hygiene light dim
/sleep hygiene noise quiet
/sleep hygiene mattress good

# 记录睡前习惯
/sleep hygiene screen-time 60
/sleep hygiene caffeine 4pm
/sleep hygiene exercise evening
/sleep hygiene routine inconsistent

# 查看睡眠卫生评分
/sleep hygiene score
```

**睡眠环境评估**：
- temperature（温度）：18-22℃ 为理想
- light（光线）：dark（黑暗）、dim（昏暗）、bright（明亮）
- noise（噪音）：quiet（安静）、moderate（适中）、loud（嘈杂）
- mattress（床垫）：good（舒适）、fair（一般）、poor（差）
- pillow（枕头）：good（舒适）、fair（一般）、poor（差）

**睡前习惯评估**：
- screen_time（屏幕时间）：睡前30-60分钟
- caffeine_cutoff（咖啡因截止时间）：下午2点后避免
- exercise_time（运动时间）：morning/afternoon/evening/none
- routine（睡前例行）：consistent（一致）、inconsistent（不一致）、none（无）

---

### 获取睡眠建议

```bash
# 获取所有建议
/sleep recommendations

# 特定类型建议
/sleep recommendations schedule         # 作息建议
/sleep recommendations environment      # 环境建议
/sleep recommendations lifestyle        # 生活方式建议
/sleep recommendations bedtime_routine  # 睡前例行建议

# 创建行动计划
/sleep action-plan
/sleep action-plan priority 1 establish_consistent_schedule
```

**作息建议**：
- 固定起床时间（包括周末）
- 固定上床时间
- 限制午睡（<30分钟，下午3点前）
- 逐步调整作息（每次15分钟）

**环境建议**：
- 优化温度（18-22℃）
- 使用遮光窗帘
- 使用白噪音机器
- 移除卧室时钟

**生活方式建议**：
- 将运动移至早晨或下午
- 下午2点后停止咖啡因
- 睡前避免饮酒
- 睡前3小时避免大餐

**睡前例行建议**：
- 提前1小时开始例行程序
- 睡前30分钟避免屏幕
- 调暗灯光
- 练习放松技巧
- 温水澡

---

## 数据结构

### 主数据文件：`data-example/sleep-tracker.json`

```json
{
  "sleep_tracking": {
    "user_profile": {
      "typical_bedtime": "23:00",
      "typical_wake_time": "07:00",
      "ideal_sleep_duration": 7.5,
      "sleep_schedule": "regular",
      "bedtime_routine_established": false,
      "sleep_environment_score": 6,
      "risk_factors": [],
      "medical_conditions": [],
      "medications_affecting_sleep": []
    },
    "baseline_metrics": {
      "average_sleep_duration": 6.8,
      "average_sleep_latency": 30,
      "average_sleep_efficiency": 83.5,
      "baseline_period_start": "2025-01-01",
      "baseline_period_end": "2025-03-31"
    },
    "goals": {},
    "statistics": {},
    "metadata": {}
  },
  "sleep_assessments": {
    "psqi": {},
    "epworth": {},
    "isi": {},
    "assessment_schedule": {}
  },
  "sleep_problems": {
    "insomnia": {},
    "sleep_apnea": {},
    "rls": {},
    "circadian_rhythm": {}
  },
  "sleep_hygiene": {
    "current_practices": {},
    "recommendations": {},
    "action_plan": {}
  },
  "sleep_analytics": {
    "last_analysis": "",
    "weekly_summary": {},
    "monthly_summary": {},
    "patterns": {}
  }
}
```

### 每日日志：`data-example/sleep-logs/YYYY-MM/YYYY-MM-DD.json`

```json
{
  "date": "2025-06-20",
  "sleep_records": [
    {
      "id": "sleep_20250620001",
      "timestamp": "2025-06-20T07:15:00.000Z",
      "sleep_times": {
        "bedtime": "23:00",
        "sleep_onset_time": "23:30",
        "wake_time": "07:00",
        "out_of_bed_time": "07:15"
      },
      "sleep_metrics": {
        "sleep_duration_hours": 7.0,
        "time_in_bed_hours": 8.25,
        "sleep_latency_minutes": 30,
        "sleep_efficiency": 84.8
      },
      "sleep_stages": {
        "light_sleep_hours": 3.5,
        "deep_sleep_hours": 1.5,
        "rem_sleep_hours": 2.0,
        "awake_hours": 0.5
      },
      "awakenings": {
        "count": 2,
        "total_duration_minutes": 15,
        "causes": ["bathroom", "noise"]
      },
      "sleep_quality": {
        "subjective_quality": "fair",
        "quality_score": 5,
        "rested_feeling": "somewhat",
        "morning_mood": "neutral"
      },
      "factors": {
        "caffeine_after_2pm": false,
        "alcohol": false,
        "exercise": true,
        "screen_time_before_bed_minutes": 60
      },
      "notes": ""
    }
  ]
}
```

---

## 医学安全原则

### ⚠️ 安全红线

1. **不诊断睡眠疾病**
   - 不诊断失眠、睡眠呼吸暂停、不宁腿综合征等
   - 诊断需睡眠专科医生通过多导睡眠图（PSG）等检查

2. **不开具助眠药物**
   - 不推荐具体的助眠药物
   - 不调整药物剂量
   - 药物治疗需医生处方和监控

3. **不替代睡眠治疗**
   - CBT-I（失眠认知行为疗法）需专业人员指导
   - OSA（阻塞性睡眠呼吸暂停）需CPAP等治疗
   - 不替代任何睡眠医学治疗

4. **不处理紧急情况**
   - 严重嗜睡影响驾驶安全需立即就医
   - 呼吸暂停导致憋醒需紧急处理
   - 突发严重睡眠问题需就医评估

### ✅ 系统能做到的

- **数据记录和追踪**：记录每日睡眠信息，追踪睡眠模式
- **睡眠质量评估**：使用标准化量表评估睡眠质量
- **睡眠问题识别**：识别失眠、呼吸暂停等风险因素
- **睡眠卫生建议**：提供作息、环境、生活方式改善建议
- **睡眠趋势分析**：分析睡眠时长、质量、效率的变化趋势
- **相关性分析**：分析与运动、情绪、慢性病的关联

---

## 参考资源

### 睡眠评估标准
- [AASM（美国睡眠医学学会）睡眠评分标准](https://aasm.org/)
- [失眠诊疗指南（AASM）](https://aasm.org/clinical-resources/insomnia/)
- [PSQI（匹兹堡睡眠质量指数）](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3455216/)

### 睡眠呼吸暂停
- [STOP-BANG 问卷（睡眠呼吸暂停筛查）](https://www.stopbang.ca/)
- [OSA 诊疗指南（AASM）](https://aasm.org/clinical-resources/osahs/)

### 睡眠卫生
- [CDC 睡眠卫生建议](https://www.cdc.gov/sleep/about_sleep.html)
- [CBT-I 治疗方法（NIH）](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3455216/)
- [睡眠健康建议（NHLBI）](https://www.nhlbi.nih.gov/health/sleep-deprivation)

### 就医建议
- [何时需要看睡眠专科医生（Sleep Foundation）](https://www.sleepfoundation.org/sleep-disorders/when-to-see-a-doctor)
- [睡眠中心查找（AASM）](https://sleepeducation.org/sleep-center/)

---

**命令版本**: v1.0
**创建日期**: 2026-01-02
**维护者**: WellAlly Tech
