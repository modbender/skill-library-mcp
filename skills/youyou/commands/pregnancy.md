---
description: 管理孕期健康记录和产检计划
arguments:
  - name: action
    description: 操作类型：start(开始)/checkup(产检)/symptom(症状)/weight(体重)/vital(体征)/status(状态)/next-checkup(下次产检)/type(多胎设置)/fetal(胎儿信息)
    required: true
  - name: info
    description: 孕期信息（末次月经日期、产检结果、症状描述等，自然语言描述）
    required: false
---

# 孕期管理

全周期孕期追踪和管理，从备孕到分娩，提供全面的孕期健康监测和管理功能。

**✨ 新功能：支持多胎妊娠追踪** - 可追踪单胎、双胎、三胎、四胎妊娠

## 操作类型

### 1. 开始孕期记录 - `start`

初始化孕期记录，计算预产期和产检计划。

**参数说明：**
- `info`: 末次月经日期（必填），格式 YYYY-MM-DD 或自然语言

**示例：**
```
/pregnancy start 2025-01-01
/pregnancy start 今年1月1日
/pregnancy start last month January 1st
/pregnancy start 2025-01-01 ultrasound May 15  # 超声校正
```

**执行步骤：**

#### 1. 解析输入信息

从自然语言中提取：
- **末次月经日期 (LMP)**：精确日期
- **超声校正日期**（可选）：超声确认的预产期
- **多胎妊娠**（可选）：twins, triplets

#### 2. 验证输入

**检查项：**
- LMP 日期不能是未来日期
- LMP 应在 past 10 个月内（避免过期数据）
- 如果有活跃孕期，提示先结束

**错误处理：**
```
⚠️ 已存在活跃孕期记录

当前孕期：末次月经 2025年1月1日，预产期 2025年10月8日
提示：请先完成当前孕期再开始新记录
```

#### 3. 计算预产期和孕周

**预产期计算（Naegele规则）：**
- 预产期 = LMP + 280天（40周）
- 如有超声校正：使用超声确认日期

**当前孕周计算：**
- 孕周 = floor((今天 - LMP) / 7)
- 孕日 = (今天 - LMP) % 7

**孕期划分：**
- 孕早期：1-13周
- 孕中期：14-27周
- 孕晚期：28-42周

**可信度评估：**
- 高可信度：超声校正
- 中等可信度：LMP仅计算
- 低可信度：LMP不确定

#### 4. 生成产检计划

**标准产检时间表：**

| 孕周 | 检查项目 | 准备事项 |
|-----|---------|---------|
| 12周 | NT检查（早唐筛） | 需要憋尿 |
| 16周 | 唐筛/无创DNA | 空腹抽血 |
| 20周 | 大排畸超声 | 需要预约 |
| 24周 | 糖耐量测试 | 空腹，带糖水 |
| 28周 | 常规产检 | 测血压、体重 |
| 32周 | 常规产检 | 胎位检查 |
| 34周 | 常规产检 | 胎心监护 |
| 36周 | 常规产检 | 胎心监护 |
| 37周 | 每周产检 | 直到分娩 |
| 38周 | 每周产检 | 监测胎动 |
| 39周 | 每周产检 | 评估分娩方式 |
| 40周 | 每周产检 | 监测过期妊娠 |

#### 5. 创建孕期记录

**生成 pregnancy_id**：`pregnancy_YYYYMMDD`

**孕期数据结构：**
```json
{
  "pregnancy_id": "pregnancy_20250101",
  "lmp_date": "2025-01-01",
  "due_date": "2025-10-08",
  "due_date_confidence": "medium",
  "corrected_by_ultrasound": false,
  "ultrasound_correction_date": null,

  "current_week": 0,
  "current_day": 0,
  "current_trimester": "first",
  "days_passed": 0,
  "days_remaining": 280,
  "progress_percentage": 0,

  "multi_pregnancy": {
    "pregnancy_type": "singleton",
    "fetal_count": 1,
    "detection_method": "manual",
    "detection_confidence": "confirmed",
    "fetal_profiles": [
      {
        "baby_id": "A",
        "estimated_weight": null,
        "position": null,
        "heart_rate": null,
        "amniotic_fluid_index": null,
        "growth_percentile": null,
        "notes": ""
      }
    ],
    "special_considerations": [],
    "adjusted_due_date": null,
    "adjusted_delivery_week": 40
  },

  "prenatal_checks": [
    {
      "check_id": "check_001",
      "week": 12,
      "check_type": "NT检查",
      "check_type_en": "NT_scan",
      "scheduled_date": "2025-03-25",
      "completed": false,
      "results": {},
      "notes": "",
      "preparation": "需要憋尿"
    },
    {
      "check_id": "check_002",
      "week": 16,
      "check_type": "唐筛",
      "check_type_en": "triple_test",
      "scheduled_date": "2025-04-22",
      "completed": false,
      "results": {},
      "notes": "",
      "preparation": "空腹抽血"
    }
    // ... 其他产检项目
  ],

  "symptoms": {
    "nausea": {
      "present": false,
      "severity": null,
      "frequency": null,
      "triggers": [],
      "relief_methods": []
    },
    "fatigue": {
      "present": false,
      "severity": null
    },
    "edema": {
      "present": false,
      "severity": null
    }
  },

  "weight_tracking": [],

  "blood_pressure": [],

  "fetal_movement": {
    "tracking_started": false,
    "start_week": 28,
    "movements": []
  },

  "contractions": [],

  "nutrition_plan": {
    "folic_acid": {
      "dose": "400μg",
      "frequency": "daily",
      "started": null,
      "adherence": null
    },
    "iron": {
      "dose": null,
      "frequency": null,
      "started": null
    },
    "calcium": {
      "dose": null,
      "frequency": null,
      "started": null
    },
    "dha": {
      "dose": null,
      "frequency": null,
      "started": null
    }
  },

  "medication_safety_checks": [],

  "risk_factors": [],

  "notes": "",
  "completed": false,
  "delivery_date": null,
  "delivery_outcome": null,

  "metadata": {
    "created_at": "2025-01-01T00:00:00.000Z",
    "last_updated": "2025-01-01T00:00:00.000Z"
  }
}
```

#### 6. 保存数据文件

**主文件**：`data/pregnancy-tracker.json`
```json
{
  "current_pregnancy": { /* 上述数据结构 */ },
  "pregnancy_history": [],
  "statistics": {
    "total_pregnancies": 1,
    "current_pregnancy_week": 0
  }
}
```

**详细记录**：`data/孕期记录/YYYY-MM/YYYY-MM-DD_孕期记录.json`

#### 7. 输出确认

```
✅ 孕期记录已创建

孕期信息：
━━━━━━━━━━━━━━━━━━━━━━━━━━
末次月经：2025年1月1日
预产期：2025年10月8日
当前孕周：0周
孕期阶段：孕早期

预产期可信度：中等（基于末次月经计算）
━━━━━━━━━━━━━━━━━━━━━━━━━━

下次产检：
━━━━━━━━━━━━━━━━━━━━━━━━━━
12周 NT检查 - 2025年3月25日（还有84天）

准备事项：需要憋尿

产检计划概览：
━━━━━━━━━━━━━━━━━━━━━━━━━━
12周：NT检查
16周：唐筛/无创DNA
20周：大排畸超声
24周：糖耐量测试
28周：常规产检
32-36周：每2周一次
37-40周：每周一次

💡 营养建议：
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 叶酸：400-800μg/天（孕前3个月至孕早期）
• 铁：孕中晚期补充（根据医嘱）
• 钙：1000-1200mg/天（全程）
• DHA：200-300mg/天（孕期）

⚠️ 重要声明：
━━━━━━━━━━━━━━━━━━━━━━━━━━
本系统仅供孕期健康追踪，不能替代专业产检。

所有产检请按时进行，如有异常请及时就医：
• 阴道出血
• 腹痛
• 严重头痛
• 视力改变
• 胎动异常

预产期计算可能有误差，以超声检查为准。

数据已保存至：data/孕期记录/2025-01/2025-01-01_孕期记录.json
```

---

### 2. 记录产检 - `checkup`

记录产检结果。

**参数说明：**
- `info`: 产检信息（必填）
  - 孕周：week 12, 12周, 12w
  - 检查类型：NT, 唐筛, 大排畸, 糖耐, 常规
  - 结果：normal, abnormal, 低风险, 高风险, 数值

**示例：**
```
/pregnancy checkup week 12 NT normal
/pregnancy checkup 12周 唐筛 低风险
/pregnancy checkup week 20 大排畸 一切正常
/pregnancy checkup week 24 糖耐 7.5 8.2 6.8  # 糖耐值
/pregnancy checkup week 28 常规 血压120/70 体重65kg
```

**执行步骤：**

#### 1. 解析产检信息

**提取信息：**
- **孕周**：数字 + "周"/"week"/"w"
- **检查类型**：
  - NT / NT检查 / 早期唐筛
  - 唐筛 / 唐氏筛查 / triple_test
  - 大排畸 / 系统超声 / anatomy ultrasound
  - 糖耐 / OGTT / glucose tolerance
  - 常规 / regular / routine
- **结果**：
  - 正常类：normal, 正常, 通过, low risk, 低风险
  - 异常类：abnormal, 异常, high risk, 高风险
  - 数值：直接提取数字

#### 2. 验证输入

**检查项：**
- 孕周是否在合理范围（0-42周）
- 检查类型是否识别
- 当前是否有活跃孕期

#### 3. 更新产检记录

**找到对应产检项并更新：**
```json
{
  "check_id": "check_001",
  "week": 12,
  "check_type": "NT检查",
  "scheduled_date": "2025-03-25",
  "completed": true,
  "completed_at": "2025-03-25T14:30:00.000Z",
  "results": {
    "status": "normal",
    "nt_measurement": "1.8mm",
    "notes": "NT值正常"
  },
  "notes": ""
}
```

**糖耐量测试结果格式：**
```json
{
  "check_type": "糖耐量测试",
  "results": {
    "fasting_glucose": 5.3,  // 空腹
    "one_hour": 7.5,         // 1小时
    "two_hour": 6.8,         // 2小时
    "diagnosis": "normal"    // 正常/妊娠糖尿病
  }
}
```

**唐筛结果格式：**
```json
{
  "check_type": "唐筛",
  "results": {
    "risk_category": "low_risk",  // low_risk/high_risk
    "t21_risk": "1:1000",
    "t18_risk": "1:50000",
    "ntd_risk": "low"
  }
}
```

#### 4. 结果解读和警示

**正常结果：**
- 确认记录
- 提示下次产检

**异常结果警示：**
```
⚠️ 产检结果异常

检查项目：唐筛（16周）
结果：高风险（21-三体风险 1:50）

建议：
━━━━━━━━━━━━━━━━━━━━━━━━━━
🏥 立即咨询产检医生
🔬 建议进行无创DNA或羊水穿刺
📋 不要惊慌，高风险不等于确诊

下次产检：
━━━━━━━━━━━━━━━━━━━━━━━━━━
请与医生确认下次产检时间
```

**糖耐异常（妊娠糖尿病）：**
```
⚠️ 糖耐量测试异常

空腹血糖：5.3 mmol/L（正常 <5.1）
1小时血糖：10.5 mmol/L（正常 <10.0）
2小时血糖：8.8 mmol/L（正常 <8.5）

诊断：妊娠糖尿病

建议：
━━━━━━━━━━━━━━━━━━━━━━━━━━
🏥 立即咨询营养师
📊 控制饮食，监测血糖
🏃️ 适量运动
📝 每天记录血糖值
```

#### 5. 输出确认

```
✅ 产检记录已更新

产检信息：
━━━━━━━━━━━━━━━━━━━━━━━━━━
孕周：12周
检查项目：NT检查
日期：2025年3月25日
结果：正常（NT值1.8mm）

本次产检完成✅

下次产检：
━━━━━━━━━━━━━━━━━━━━━━━━━━
16周 唐筛 - 2025年4月22日（还有28天）

准备：空腹抽血

💡 提示：
━━━━━━━━━━━━━━━━━━━━━━━━━━
所有产检结果仅供参考，请以医生诊断为准。
如有疑问请咨询产检医生。
```

---

### 3. 记录症状 - `symptom`

记录孕期症状。

**参数说明：**
- `info`: 症状描述（必填）
  - 症状类型：nausea（孕吐）, fatigue（乏力）, edema（水肿）, back pain（腰痛）, contractions（宫缩）
  - 严重程度：mild（轻微）, moderate（中度）, severe（重度）

**示例：**
```
/pregnancy symptom nausea moderate
/pregnancy symptom 孕吐 严重
/pregnancy symptom edema feet 轻微
/pregnancy symptom back pain moderate
/pregnancy symptom contractions false 5/hour  # 假性宫缩
```

**执行步骤：**

#### 1. 解析症状信息

**症状类型识别：**
| 关键词 | 症状类型 | 英文 |
|--------|---------|------|
| 孕吐、恶心、呕吐、反胃 | nausea | nausea |
| 乏力、疲劳、累 | fatigue | fatigue |
| 水肿、脚肿、手肿 | edema | edema |
| 腰痛、背痛 | back_pain | back pain |
| 宫缩 | contractions | contractions |

**严重程度识别：**
- 轻微：mild, 轻微, 轻度, light
- 中度：moderate, 中度, 还可以, moderate
- 重度：severe, 严重, 很严重, heavy

**频率识别（可选）：**
- "每天", "daily", "每天几次"
- "偶尔", "occasional", "sometimes"

#### 2. 症状评估

**正常孕期症状：**
- 孕吐（孕早期）
- 乏力（孕早中期）
- 轻微水肿（孕晚期）
- 腰痛（孕中晚期）

**警示症状（需立即就医）：**
- 阴道出血
- 严重腹痛（痉挛性）
- 严重头痛伴视力改变
- 突然严重水肿（面部、手）
- 胎动明显减少

#### 3. 更新症状记录

**症状数据结构：**
```json
{
  "symptoms": {
    "nausea": {
      "present": true,
      "severity": "moderate",
      "severity_level": 2,
      "frequency": "daily",
      "triggers": ["morning", "empty_stomach"],
      "relief_methods": ["crackers", "small_frequent_meals"],
      "last_updated": "2025-03-20T10:00:00.000Z"
    },
    "edema": {
      "present": true,
      "severity": "mild",
      "severity_level": 1,
      "location": "feet_ankles",
      "worse_at": "evening",
      "last_updated": "2025-03-20T10:00:00.000Z"
    }
  }
}
```

#### 4. 集成 /symptom 命令

**自动创建症状记录：**
```json
// data/症状记录/2025-03/2025-03-20_孕吐.json
{
  "id": "symptom_20250320001",
  "symptom_type": "孕吐",
  "description": "恶心呕吐，中度",
  "severity": "moderate",
  "date": "2025-03-20",
  "womens_health_context": {
    "related": true,
    "module": "pregnancy",
    "pregnancy_id": "pregnancy_20250101",
    "gestational_week": 12,
    "trimester": "first"
  }
}
```

#### 5. 提供管理建议

**孕吐管理：**
```
症状管理建议：
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 少食多餐（每天6-8小餐）
• 早晨起床前吃几块苏打饼干
• 避免空腹
• 补充水分，少量多次
• 避免油腻、辛辣食物
• 休息时抬高头部

💊 药物提示：
如孕吐严重影响进食，可咨询医生使用维生素B6或止吐药。
```

**水肿管理：**
```
症状管理建议：
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 抬高下肢休息
• 避免久站或久坐
• 左侧卧位睡眠
• 适量散步
• 减少盐分摄入
• 穿舒适宽松的鞋子

⚠️ 警示：
如面部、手部突然水肿，请立即就医排除子痫前期。
```

#### 6. 输出确认

```
✅ 症状已记录

症状信息：
━━━━━━━━━━━━━━━━━━━━━━━━━━
类型：孕吐
严重程度：中度
频率：每天

当前孕周：12周（孕早期）

评估：
━━━━━━━━━━━━━━━━━━━━━━━━━━
孕吐是孕早期常见症状，通常在孕14-16周缓解。

管理建议：
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 少食多餐
• 晨起前吃苏打饼干
• 避免空腹
• 补充水分

⚠️ 重要提示：
如呕吐严重导致脱水（尿少、头晕），请立即就医。

数据已同步至症状记录
```

---

### 4. 记录体重 - `weight`

记录体重增长，监测BMI和体重增长曲线。

**参数说明：**
- `info`: 体重值（必填）
  - 体重：数字 + kg 或 lbs

**示例：**
```
/pregnancy weight 62.5
/pregnancy weight 65kg
/pregnancy weight 140 lbs
```

**执行步骤：**

#### 1. 解析体重值

**提取体重：**
- 数字 + 单位：62.5kg, 65 kg, 140 lbs
- 自动转换单位：1 lb = 0.453592 kg

#### 2. 读取基础数据

从 [`data/profile.json`](d:\my-his\data\profile.json) 读取：
- 孕前体重
- 身高

**如果没有孕前体重：**
```
⚠️ 缺少孕前体重

请先设置孕前体重：
/profile weight 60  # 孕前体重60kg

或：
/pregnancy weight 62.5 --pre-pregnancy  # 62.5kg为当前体重，60kg为孕前体重
```

#### 3. 计算指标

**体重增长：**
```javascript
weight_gain = current_weight - pre_pregnancy_weight
```

**BMI计算：**
```javascript
bmi = weight / (height_meters)^2
pre_pregnancy_bmi = pre_pregnancy_weight / (height_meters)^2
```

**孕期体重增长推荐（基于IOM指南）：**

| BMI类别 | BMI范围 | 总增重推荐 | 孕中晚期周增重 |
|---------|---------|-----------|--------------|
| 低体重 | <18.5 | 12.5-18 kg | 0.51 kg (0.44-0.58) |
| 正常 | 18.5-24.9 | 11.5-16 kg | 0.42 kg (0.35-0.50) |
| 超重 | 25.0-29.9 | 7-11.5 kg | 0.28 kg (0.23-0.33) |
| 肥胖 | ≥30.0 | 5-9 kg | 0.22 kg (0.17-0.27) |

**孕期增重分配：**
- 孕早期（1-13周）：1-2 kg
- 孕中期（14-27周）：每周0.4-0.5 kg
- 孕晚期（28-40周）：每周0.4-0.5 kg

#### 4. 分析体重趋势

**计算周增重：**
```javascript
if (previous_weight_record) {
  weeks_between = current_week - previous_week;
  weekly_gain = (current_weight - previous_weight) / weeks_between;
}
```

**评估增重是否合适：**
- 过快：周增重 > 推荐值 + 0.1 kg
- 过慢：周增重 < 推荐值 - 0.1 kg
- 正常：在推荐范围内

#### 5. 更新体重记录

**体重数据结构：**
```json
{
  "weight_tracking": [
    {
      "date": "2025-03-20",
      "week": 12,
      "weight": 62.5,
      "weight_unit": "kg",
      "weight_gain": 2.5,
      "bmi": 23.1,
      "bmi_category": "normal",
      "pre_pregnancy_weight": 60.0,
      "pre_pregnancy_bmi": 22.2,
      "recommended_total_gain": "11.5-16kg",
      "recommended_weekly_gain": "0.35-0.50kg",
      "weekly_gain": null,
      "gain_status": "normal",
      "trimester": "first"
    }
  ]
}
```

#### 6. 输出确认

```
✅ 体重已记录

体重信息：
━━━━━━━━━━━━━━━━━━━━━━━━━━
记录日期：2025年3月20日
当前孕周：12周

当前体重：62.5 kg
孕前体重：60.0 kg
已增重：2.5 kg
当前BMI：23.1（正常）

增重评估：
━━━━━━━━━━━━━━━━━━━━━━━━━━
孕期增重推荐：11.5-16 kg
当前进度：正常 ✅

孕早期预期增重：1-2 kg
当前增重：2.5 kg（略多）

孕中后期建议：
━━━━━━━━━━━━━━━━━━━━━━━━━━
每周增重：0.35-0.50 kg

💡 营养建议：
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 均衡饮食，不要"一人吃两人"
• 优质蛋白：鱼、禽、蛋、奶、豆类
• 复合碳水：全谷物、薯类
• 蔬菜水果：每天500g以上
• 适量健康脂肪：坚果、鳄梨

⚠️ 提示：
如增重过快，建议控制高糖高脂食物，
增加蔬菜比例，适量运动。
```

---

### 5. 记录体征 - `vital`

记录血压和其他重要体征。

**参数说明：**
- `info`: 体征信息（必填）
  - 血压：120/80, 120 over 80
  - 或其他体征：体温、血糖等

**示例：**
```
/pregnancy vital bp 115/75
/pregnancy vital bp 120/80
/pregnancy vital bp 140/90  # 高血压警示
/pregnancy vital temperature 37.2
/pregnancy vital glucose 5.5
```

**执行步骤：**

#### 1. 解析体征信息

**血压格式识别：**
- 标准格式：120/80, 120/80 mmHg
- 文字格式：120 over 80, "120 氏 80"

**提取值：**
```javascript
systolic = 120  // 收缩压
diastolic = 80  // 舒张压
```

#### 2. 血压分类

**血压分类标准（ACOG）：**

| 分类 | 收缩压 | 舒张压 | 处理 |
|------|--------|--------|------|
| 正常 | <120 | <80 | 继续 |
| 升高 | 120-129 | <80 | 监测 |
| 高血压1期 | 130-139 | 80-89 | 密切监测 |
| 高血压2期 | 140-159 | 90-109 | 就医评估 |
| 严重高血压 | ≥160 | ≥110 | 立即就医 |
| 子痫前期范围 | ≥140 | ≥90 | 评估其他症状 |

#### 3. 评估风险

**妊娠期高血压疾病类型：**

1. **妊娠期高血压**：
   - BP ≥140/90，孕20周后首次出现
   - 无蛋白尿或其他器官功能损害

2. **子痫前期**：
   - BP ≥140/90 + 以下任一项：
     - 蛋白尿（≥300mg/24h）
     - 肝功能损害
     - 肾功能损害
     - 神经系统症状（严重头痛、视力模糊）
     - 血小板减少
     - 肺水肿

**警示症状（子痫前期）：**
- 严重头痛
- 视力改变（闪光、盲点）
- 上腹痛（右侧肋下）
- 恶心呕吐
- 呼吸困难

#### 4. 更新体征记录

**血压数据结构：**
```json
{
  "blood_pressure": [
    {
      "date": "2025-03-20",
      "week": 12,
      "systolic": 115,
      "diastolic": 75,
      "classification": "normal",
      "mean_arterial_pressure": 88.3,
      "notes": "",
      "measured_at": "clinic"  // clinic/home
    }
  ]
}
```

#### 5. 输出确认

**正常血压：**
```
✅ 血压已记录

血压信息：
━━━━━━━━━━━━━━━━━━━━━━━━━━
记录日期：2025年3月20日
当前孕周：12周

血压：115/75 mmHg
分类：正常 ✅

平均动脉压：88.3 mmHg

💡 提示：
━━━━━━━━━━━━━━━━━━━━━━━━━━
血压正常，继续保持！

建议：
• 定期监测血压
• 注意有无头痛、视力改变
• 如血压升高请及时就医
```

**高血压警示：**
```
⚠️ 血压升高警示

血压信息：
━━━━━━━━━━━━━━━━━━━━━━━━━━
血压：145/95 mmHg
分类：高血压2期 ⚠️

风险评估：
━━━━━━━━━━━━━━━━━━━━━━━━━━
血压偏高，需要密切监测。

🚨 立即就医检查：
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 测量尿蛋白
• 评估肝肾功能
• 检查血小板
• 评估胎儿情况

⚠️ 警示症状（如有立即就医）：
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 严重头痛
• 视力模糊、闪光点
• 上腹痛（右侧肋下）
• 恶心呕吐
• 呼吸困难

请立即联系产检医生或去医院急诊！
```

---

### 6. 查看状态 - `status`

显示当前孕期状态。

**参数说明：**
- 无参数

**示例：**
```
/pregnancy status
```

**执行步骤：**

#### 1. 读取孕期数据

#### 2. 计算当前状态

**重新计算当前孕周：**
```javascript
current_week = floor((today - lmp_date) / 7)
current_day = (today - lmp_date) % 7
days_passed = today - lmp_date
days_remaining = due_date - today
progress = (days_passed / 280) * 100
```

#### 3. 生成状态报告

**输出格式：**
```
📍 当前孕期状态

基本信息：
━━━━━━━━━━━━━━━━━━━━━━━━━━
末次月经：2025年1月1日
预产期：2025年10月8日
当前日期：2025年3月31日

孕期进度：
━━━━━━━━━━━━━━━━━━━━━━━━━━
当前孕周：12周+6天
孕期阶段：孕早期（1-13周）
已过天数：89天
剩余天数：191天
完成进度：32%

胎儿发育：
━━━━━━━━━━━━━━━━━━━━━━━━━━
大小：李子大小（约5-6cm）
重量：约14g
重要里程碑：
✅ 器官发育基本完成
✅ 手指脚趾分化
✅ 外生殖器开始形成

体重追踪：
━━━━━━━━━━━━━━━━━━━━━━━━━━
孕前体重：60.0 kg
当前体重：62.5 kg
已增重：2.5 kg
推荐增重：11.5-16 kg
状态：正常 ✅

近期症状：
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 孕吐（中度）- 每天
• 乏力（轻度）- 经常

最近血压：
━━━━━━━━━━━━━━━━━━━━━━━━━━
3月20日：115/75 mmHg（正常）

已完成的产检：
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 12周 NT检查 - 3月25日（正常）

下次产检：
━━━━━━━━━━━━━━━━━━━━━━━━━━
16周 唐筛 - 2025年4月22日
还有 22 天

准备：空腹抽血

本周关注：
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 继续补充叶酸 400μg/天
• 如有阴道出血、腹痛立即就医
• 注意休息，避免剧烈运动
• 预约16周唐筛检查

💡 营养提示：
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 优质蛋白：每天2-3份
• 叶酸：400μg/天
• 铁：15mg/天（食物+补充剂）
• 钙：1000mg/天

⚠️ 重要声明：
━━━━━━━━━━━━━━━━━━━━━━━━━━
本系统仅供孕期健康追踪，不能替代专业产检。
所有产检请按时进行，如有异常请及时就医。
```

---

### 7. 下次产检提醒 - `next-checkup`

显示下次产检信息和准备事项。

**参数说明：**
- 无参数

**示例：**
```
/pregnancy next-checkup
```

**执行步骤：**

#### 1. 查找下次产检

从 `prenatal_checks` 数组找到第一个 `completed: false` 的项目。

#### 2. 计算倒计时

```javascript
days_until = (scheduled_date - today)
weeks_until = floor(days_until / 7)
```

#### 3. 生成提醒

```
📅 下次产检提醒

下次产检信息：
━━━━━━━━━━━━━━━━━━━━━━━━━━
检查项目：唐筛（16周）
预约日期：2025年4月22日（周二）
时间：上午8:00-10:00
还有 22 天（3周）

产检项目说明：
━━━━━━━━━━━━━━━━━━━━━━━━━━
唐筛（唐氏综合征筛查）是通过抽血检测
母体血清中某些标志物，评估胎儿患
唐氏综合征等染色体异常的风险。

检查流程：
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 空腹抽血
2. 等待结果（1-2周）
3. 风险评估

准备事项：
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 空腹8小时以上
✅ 携带身份证和医保卡
✅ 携带既往产检资料
✅ 提前预约

可能的问题：
━━━━━━━━━━━━━━━━━━━━━━━━━━
Q: �筛高风险怎么办？
A: 高风险不等于确诊，可进一步做
   无创DNA或羊水穿刺明确诊断。

Q: 唐筛需要多久出结果？
A: 通常1-2周出结果。

Q: 空腹可以喝水吗？
A: 可以少量喝白水，不要喝饮料。

建议提问医生：
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 唐筛结果的准确性
• 需要做无创DNA吗
• 下次产检时间
• 有什么需要注意的

📍 地点：
━━━━━━━━━━━━━━━━━━━━━━━━━━
医院：[填写医院名称]
科室：产科门诊
地址：[填写地址]
电话：[填写电话]

💡 提示：
━━━━━━━━━━━━━━━━━━━━━━━━━━
请提前1-2天预约，避免排队等候。
如需改期，请提前联系医院。

倒计时提醒：
━━━━━━━━━━━━━━━━━━━━━━━━━━
建议在4月15日前预约
```

---

### 8. 设置多胎类型 - `type`

手动设置多胎妊娠类型。

**参数说明：**
- `info`: 多胎类型（必填）
  - 类型：singleton（单胎）, twins（双胎）, triplets（三胎）, quadruplets（四胎）

**示例：**
```
/pregnancy type twins
/pregnancy type 双胎
/pregnancy type triplets
/pregnancy type 3
```

**执行步骤：**

#### 1. 验证输入

**检查项：**
- 当前是否有活跃孕期
- 胎儿数量是否在合理范围（1-4）
- 是否已设置为相同类型

#### 2. 更新多胎信息

**更新数据结构：**
```json
{
  "multi_pregnancy": {
    "pregnancy_type": "twins",
    "fetal_count": 2,
    "detection_method": "manual",
    "detection_confidence": "confirmed",
    "fetal_profiles": [
      {
        "baby_id": "A",
        "estimated_weight": null,
        "position": null,
        "heart_rate": null,
        "amniotic_fluid_index": null,
        "growth_percentile": null,
        "notes": ""
      },
      {
        "baby_id": "B",
        "estimated_weight": null,
        "position": null,
        "heart_rate": null,
        "amniotic_fluid_index": null,
        "growth_percentile": null,
        "notes": ""
      }
    ],
    "adjusted_due_date": "2025-09-17",
    "adjusted_delivery_week": 37
  }
}
```

#### 3. 调整预产期和产检计划

**多胎妊娠预产期调整：**

| 妊娠类型 | 标准预产期周数 | 调整后周数 | 天数调整 |
|---------|--------------|----------|---------|
| 单胎（singleton） | 40周 | 40周 | 280天（不变） |
| 双胎（twins） | 40周 | 37周 | -21天 (259天) |
| 三胎（triplets） | 40周 | 35周 | -35天 (245天) |
| 四胎（quadruplets） | 40周 | 32周 | -56天 (224天) |

**产检频率调整（多胎妊娠）：**
- 双胎：从28周开始每2周一次，从32周开始每周一次
- 三胎及以上：从24周开始每2周一次，从28周开始每周一次
- 增加宫颈长度监测（从16-18周开始）
- 增加胎儿生长监测（每4-6周一次）

#### 4. 调整体重增长推荐

**多胎妊娠体重增长推荐（基于IOM）：**

| 孕前BMI | 单胎总增重 | 双胎总增重 | 三胎总增重 | 四胎总增重 |
|---------|-----------|-----------|-----------|-----------|
| <18.5 | 12.5-18 kg | 20-25 kg | 25-30 kg | 28-33 kg |
| 18.5-24.9 | 11.5-16 kg | 16-24 kg | 20-29 kg | 22-31 kg |
| 25.0-29.9 | 7-11.5 kg | 14-23 kg | 17-27 kg | 19-29 kg |
| ≥30.0 | 5-9 kg | 11-19 kg | 14-25 kg | 16-27 kg |

#### 5. 输出确认

```
✅ 多胎类型已设置

妊娠类型信息：
━━━━━━━━━━━━━━━━━━━━━━━━━━
类型：双胎妊娠
胎儿数量：2个
设置方式：手动设置

预产期调整：
━━━━━━━━━━━━━━━━━━━━━━━━━━
原预产期：2025年10月8日（40周）
调整后预产期：2025年9月17日（37周）
提前：3周

⚠️ 重要提示：
━━━━━━━━━━━━━━━━━━━━━━━━━━
多胎妊娠属于高危妊娠，建议：

产检频率调整：
• 28周起：每2周一次
• 32周起：每周一次
• 增加宫颈长度监测（16-18周开始）
• 增加胎儿生长监测（每4-6周）

特殊监测：
• 胎儿生长 Discordance
• 双胎输血综合征（TTTS）征象
• 宫颈长度缩短

体重增长推荐：
━━━━━━━━━━━━━━━━━━━━━━━━━━
总增重推荐：16-24 kg
孕中晚期周增重：0.5-0.7 kg

建议：
• 咨询母胎医学专科（MFM）
• 考虑转诊至三级医院
• 制定分娩计划（32-34周讨论）

胎儿档案已创建：
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 胎儿A - 待完善信息
• 胎儿B - 待完善信息

使用 /pregnancy fetal 添加胎儿详细信息
```

---

### 9. 添加胎儿信息 - `fetal`

添加或更新单个胎儿的详细信息。

**参数说明：**
- `info`: 胎儿信息（必填）
  - 胎儿标识：A, B, C, D（必填）
  - 信息类型：weight（体重）, position（胎位）, heart（胎心）, afi（羊水指数）, growth（生长百分位）
  - 数值/描述

**示例：**
```
/pregnancy fetal A weight 1200g
/pregnancy fetal B position cephalic
/pregnancy fetal A heart 145
/pregnancy fetal B afi 8.5
/pregnancy fetal A growth 50th
/pregnancy fetal A 头位 HR150 AFI9
```

**执行步骤：**

#### 1. 解析胎儿信息

**提取信息：**
- **胎儿标识**：A, B, C, D（不区分大小写）
- **信息类型**：
  - 体重：weight, wt, 体重, 1200g
  - 胎位：position, pos, 胎位, cephalic（头位）, breech（臀位）, transverse（横位）
  - 胎心：heart, hr, 胎心, 胎心监护, 145, 150bpm
  - 羊水指数：afi, 羊水, 8.5, 9.0cm
  - 生长百分位：growth, percentile, 百分位, 50th, 75%

#### 2. 验证输入

**检查项：**
- 胎儿标识是否有效（A-D）
- 当前多胎设置是否支持该胎儿
- 数值是否在合理范围

#### 3. 更新胎儿档案

**胎儿数据结构：**
```json
{
  "multi_pregnancy": {
    "fetal_profiles": [
      {
        "baby_id": "A",
        "estimated_weight": {
          "value": 1200,
          "unit": "g",
          "percentile": 45,
          "last_updated": "2025-06-20T10:00:00.000Z"
        },
        "position": {
          "current": "cephalic",
          "confirmed_at": "2025-06-20",
          "notes": "头位，固定"
        },
        "heart_rate": {
          "value": 145,
          "unit": "bpm",
          "last_measured": "2025-06-20",
          "variability": "normal"
        },
        "amniotic_fluid_index": {
          "value": 9.0,
          "unit": "cm",
          "pocket": "normal",
          "last_measured": "2025-06-20"
        },
        "growth_percentile": {
          "value": 50,
          "trend": "stable",
          "last_updated": "2025-06-20"
        },
        "notes": "发育良好"
      },
      {
        "baby_id": "B",
        "estimated_weight": {
          "value": 1150,
          "unit": "g",
          "percentile": 42,
          "last_updated": "2025-06-20T10:00:00.000Z"
        },
        "position": {
          "current": "breech",
          "confirmed_at": "2025-06-20",
          "notes": "臀位，可能自然转正"
        },
        "heart_rate": {
          "value": 150,
          "unit": "bpm",
          "last_measured": "2025-06-20",
          "variability": "normal"
        },
        "amniotic_fluid_index": {
          "value": 8.5,
          "unit": "cm",
          "pocket": "normal",
          "last_measured": "2025-06-20"
        },
        "growth_percentile": {
          "value": 48,
          "trend": "stable",
          "last_updated": "2025-06-20"
        },
        "notes": "发育正常，略小于A"
      }
    ]
  }
}
```

#### 4. 胎儿生长分析

**体重一致性分析（双胎）：**
```javascript
weight_discordance = |weight_A - weight_B| / max(weight_A, weight_B) * 100

// 正常：<15%
// 警告：15-20%
// 异常：>20%（需进一步检查）
```

**羊水评估：**
- 正常：AFI 5-24 cm（单胎）, 8-25 cm（双胎）
- 羊水过少：AFI <5 cm
- 羊水过多：AFI >24 cm

#### 5. 输出确认

```
✅ 胎儿信息已更新

胎儿A信息：
━━━━━━━━━━━━━━━━━━━━━━━━━━
体重：1200g（第45百分位）
胎位：头位（cephalic）
胎心：145 bpm（正常）
羊水指数：9.0 cm（正常）
生长百分位：50%（稳定）

胎儿B信息：
━━━━━━━━━━━━━━━━━━━━━━━━━━
体重：1150g（第42百分位）
胎位：臀位（breech）
胎心：150 bpm（正常）
羊水指数：8.5 cm（正常）
生长百分位：48%（稳定）

双胎一致性分析：
━━━━━━━━━━━━━━━━━━━━━━━━━━
体重差异：4.3%（正常）
羊水差异：正常
生长趋势：一致

✓ 双胎发育均衡，无明显不一致

下次检查建议：
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 2周后复查超声
• 监测胎位变化
• 评估胎儿生长
• 宫颈长度监测

⚠️ 注意事项：
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 胎儿B为臀位，可能需要剖宫产
• 32-34周讨论分娩方式
• 如出现胎动异常，立即就医
• 警惕双胎输血综合征征象
```

**异常情况警示：**

**体重不一致 >20%：**
```
⚠️ 胎儿生长不一致警示

体重差异：25%（异常）
胎儿A：1400g（第55百分位）
胎儿B：1050g（第28百分位）

风险评估：
━━━━━━━━━━━━━━━━━━━━━━━━━━
可能原因：
• 双胎输血综合征（TTTS）
• 脐带问题
• 胎盘分配不均

🏥 建议：
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 立即咨询母胎医学专科
• 超声检查：脐带、胎盘、血流
• 密切监测（每周或每2周）
• 考虑胎儿治疗选项
```

---

## 智能多胎检测

系统会在以下情况自动检测多胎妊娠：

### 1. 产检记录中的关键词

当记录产检时，系统会检查产检结果/备注中的关键词：

**双胎关键词：**
- 中文：双胎、双胞胎、两个胎儿、双卵双胎、单卵双胎
- 英文：twins, two fetuses, twin pregnancy, dichorionic, monochorionic

**三胎关键词：**
- 中文：三胎、三胞胎、三个胎儿
- 英文：triplets, three fetuses, triplet pregnancy

**四胎关键词：**
- 中文：四胎、四胞胎、四个胎儿
- 英文：quadruplets, four fetuses, quad pregnancy

### 2. 检测流程

```javascript
// 伪代码示例
function detectMultiples(checkupNotes) {
  const keywords = {
    twins: ["双胎", "twins", "双胞胎"],
    triplets: ["三胎", "triplets", "三胞胎"],
    quadruplets: ["四胎", "quadruplets", "四胞胎"]
  };

  for (const [type, words] of Object.entries(keywords)) {
    if (words.some(word => checkupNotes.includes(word))) {
      return {
        detected: true,
        type: type,
        confidence: "suggested",
        source: "ultrasound_notes"
      };
    }
  }

  return { detected: false };
}
```

### 3. 检测响应

当检测到多胎妊娠时：

**建议确认：**
```
🔍 检测到可能的多胎妊娠

产检记录中检测到关键词："双胎"

系统建议：
━━━━━━━━━━━━━━━━━━━━━━━━━━
这可能是一个双胎妊娠。

是否将妊娠类型设置为双胎？
• /pregnancy type twins - 确认设置为双胎
• /pregnancy type singleton - 保持单胎设置

⚠️ 提示：
━━━━━━━━━━━━━━━━━━━━━━━━━━
请根据超声检查结果确认：
• 胎儿数量
• 绒毛膜性（chorionicity）
• 羊膜囊性（amnionicity）

建议与产检医生确认诊断。
```

---

## 多胎妊娠特殊监测

### 1. 双胎输血综合征（TTTS）监测

**高危指征：**
- 单绒双羊双胎（MCDA）
- 羊水差异明显（一胎过多，一胎过少）
- 胎儿生长差异 >20%
- 膀胱不可见（受血儿）

**TTTS分期（Quintero分期）：**
| 分期 | 标准 |
|------|------|
| I | 一胎羊水过多（最大垂直深度 MVP >8cm），另一胎羊水过少（MVP <2cm），膀胱仍可见 |
| II | 除I期表现外，受血儿膀胱不可见 |
| III | 除II期表现外，多普勒超声异常 |
| IV | 除III期表现外，一胎或双胎水肿/腹水 |
| V | 一胎或双胎死亡 |

**警示：**
```
⚠️ TTTS风险警示

监测结果异常：
━━━━━━━━━━━━━━━━━━━━━━━━━━
羊水差异：
  胎儿A：MVP 12.0 cm（过多）
  胎儿B：MVP 1.5 cm（过少）
  膀胱B：不可见

风险评估：
━━━━━━━━━━━━━━━━━━━━━━━━━━
疑似TTTS II期

🏥 紧急建议：
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 立即联系母胎医学中心
• 24小时内评估
• 考虑胎儿激光手术
• 密切监测（每周2-3次）

请勿延误！TTTS进展迅速。
```

### 2. 宫颈长度监测

**监测频率：**
- 双胎：16-18周开始，每2-4周一次
- 三胎及以上：14-16周开始，每2周一次

**宫颈长度阈值：**
| 宫颈长度 | 风险 | 处理 |
|---------|------|------|
| >25mm | 低风险 | 常规监测 |
| 20-25mm | 中等风险 | 每1-2周复查 |
| <20mm | 高风险 | 考虑宫颈环扎术 |

### 3. 胎儿生长监测

**监测频率：**
- 双胎：每4-6周一次
- 三胎及以上：每3-4周一次

**评估指标：**
- 体重百分位
- 体重一致性（discordance）
- 羊水量
- 脐血流

---

## 数据结构

### 主文件：data/pregnancy-tracker.json

```json
{
  "created_at": "2025-12-31T12:00:00.000Z",
  "last_updated": "2025-12-31T12:00:00.000Z",

  "current_pregnancy": {
    "pregnancy_id": "pregnancy_20250101",
    "lmp_date": "2025-01-01",
    "due_date": "2025-10-08",
    "due_date_confidence": "high",
    "corrected_by_ultrasound": false,
    "ultrasound_correction_date": null,

    "current_week": 12,
    "current_day": 6,
    "current_trimester": "first",
    "days_passed": 89,
    "days_remaining": 191,
    "progress_percentage": 32,

    "prenatal_checks": [
      {
        "check_id": "check_001",
        "week": 12,
        "check_type": "NT检查",
        "check_type_en": "NT_scan",
        "scheduled_date": "2025-03-25",
        "completed": false,
        "completed_at": null,
        "results": {},
        "notes": "",
        "preparation": "需要憋尿"
      }
    ],

    "symptoms": {
      "nausea": {
        "present": false,
        "severity": null,
        "frequency": null,
        "triggers": [],
        "relief_methods": [],
        "last_updated": null
      },
      "fatigue": {
        "present": false,
        "severity": null
      },
      "edema": {
        "present": false,
        "severity": null,
        "location": null
      },
      "back_pain": {
        "present": false,
        "severity": null
      },
      "contractions": {
        "present": false,
        "type": null,
        "frequency": null
      }
    },

    "weight_tracking": [
      {
        "date": "2025-01-01",
        "week": 0,
        "weight": 60.0,
        "weight_unit": "kg",
        "weight_gain": 0.0,
        "bmi": 22.2,
        "bmi_category": "normal",
        "pre_pregnancy_weight": 60.0,
        "pre_pregnancy_bmi": 22.2,
        "recommended_total_gain": "11.5-16kg",
        "recommended_weekly_gain": "0.35-0.50kg",
        "weekly_gain": null,
        "gain_status": "normal",
        "trimester": "first"
      }
    ],

    "blood_pressure": [
      {
        "date": "2025-03-15",
        "week": 10,
        "systolic": 115,
        "diastolic": 75,
        "classification": "normal",
        "mean_arterial_pressure": 88.3,
        "notes": "",
        "measured_at": "clinic"
      }
    ],

    "fetal_movement": {
      "tracking_started": false,
      "start_week": 28,
      "movements": []
    },

    "contractions": [],

    "nutrition_plan": {
      "folic_acid": {
        "dose": "400μg",
        "frequency": "daily",
        "started": null,
        "adherence": null
      },
      "iron": {
        "dose": null,
        "frequency": null,
        "started": null,
        "adherence": null
      },
      "calcium": {
        "dose": null,
        "frequency": null,
        "started": null,
        "adherence": null
      },
      "dha": {
        "dose": null,
        "frequency": null,
        "started": null,
        "adherence": null
      }
    },

    "medication_safety_checks": [],

    "risk_factors": [],

    "notes": "",

    "completed": false,
    "delivery_date": null,
    "delivery_outcome": null,

    "metadata": {
      "created_at": "2025-01-01T00:00:00.000Z",
      "last_updated": "2025-03-25T10:00:00.000Z"
    }
  },

  "pregnancy_history": [],

  "statistics": {
    "total_pregnancies": 1,
    "current_pregnancy_week": 12,
    "total_weight_gain": 2.5,
    "average_weekly_gain": 0.21,
    "checkups_completed": 1,
    "checkups_scheduled": 11
  },

  "settings": {
    "reminder_days_before": 7,
    "weight_unit": "kg",
    "preferred_checkup_time": "morning"
  }
}
```

### 详细记录文件：data/孕期记录/YYYY-MM/YYYY-MM-DD_孕期记录.json

```json
{
  "pregnancy_id": "pregnancy_20250101",
  "record_date": "2025-03-31",
  "week": 12,
  "day": 6,
  "trimester": "first",

  "daily_log": {
    "symptoms": ["孕吐", "乏力"],
    "mood": "正常",
    "energy_level": "moderate",
    "notes": ""
  },

  "checkups": [],
  "vitals": [],
  "weight": {},

  "fetal_development_info": {
    "size_description": "李子大小",
    "size_cm": "5-6cm",
    "weight_g": 14,
    "milestones": [
      "器官发育基本完成",
      "手指脚趾分化",
      "外生殖器开始形成"
    ]
  },

  "metadata": {
    "created_at": "2025-03-31T20:00:00.000Z",
    "last_updated": "2025-03-31T20:00:00.000Z"
  }
}
```

---

## 智能识别规则

### 日期识别

| 用户输入 | 标准格式 | 示例 |
|---------|---------|------|
| YYYY-MM-DD | YYYY-MM-DD | 2025-01-01 |
| 今年X月X日 | YYYY-MM-DD | 今年1月1日 → 2025-01-01 |
| last month | 计算日期 | last month January 1st |
| X weeks ago | 计算日期 | 12 weeks ago |

### 孕周识别

| 用户输入 | 提取结果 |
|---------|---------|
| week 12 | 12周 |
| 12周 | 12周 |
| 12w | 12周 |
| 孕12周 | 12周 |

### 检查类型识别

| 用户输入 | 标准类型 |
|---------|---------|
| NT, NT检查 | NT检查 |
| 唐筛, 唐氏筛查 | 唐筛 |
| 大排畸, 系统超声 | 大排畸 |
| 糖耐, OGTT | 糖耐量测试 |
| 常规, 产检 | 常规产检 |

### 结果识别

| 正常 | 异常 |
|------|------|
| normal, 正常, 通过 | abnormal, 异常 |
| low risk, 低风险 | high risk, 高风险 |
| negative, 阴性 | positive, 阳性 |

### 症状识别

| 关键词 | 症状类型 |
|--------|---------|
| 孕吐、恶心、呕吐 | nausea |
| 乏力、疲劳 | fatigue |
| 水肿、肿 | edema |
| 腰痛、背痛 | back_pain |
| 宫缩 | contractions |

### 严重程度识别

| 轻微 | 中度 | 重度 |
|------|------|------|
| mild, 轻微 | moderate, 中度 | severe, 严重 |

### 血压格式识别

| 用户输入 | 收缩压 | 舒张压 |
|---------|--------|--------|
| 120/80 | 120 | 80 |
| 120 over 80 | 120 | 80 |
| 120 氏 80 | 120 | 80 |

---

## 错误处理

| 场景 | 错误消息 | 建议 |
|------|---------|------|
| 无活跃孕期 | 无活跃孕期记录<br>请先使用 /pregnancy start | 引导开始记录 |
| 孕期已存在 | 已存在活跃孕期<br>请先完成当前孕期 | 提示当前状态 |
| LMP日期无效 | 末次月经日期无效<br>不能是未来日期 | 验证日期 |
| 缺少profile数据 | 缺少个人信息<br>请先设置身高/体重/生日 | 引导至profile |
| 检查类型未识别 | 未识别的检查类型<br>支持：NT、唐筛、大排畸、糖耐、常规 | 列出支持类型 |
| 孕周超出范围 | 孕周应在0-42周之间 | 显示有效范围 |

---

## 注意事项

- 本系统仅供孕期健康追踪，不能替代专业产检
- 所有产检请按时进行
- 预产期计算可能有误差，以超声为准
- 如有异常情况请及时就医
- 不评估胎儿健康状况
- 不预测妊娠结局
- 胎动监测不能替代医学监护

**紧急情况警示：**
如出现以下情况，请立即就医：
- 阴道出血
- 严重腹痛
- 严重头痛伴视力改变
- 突然严重水肿
- 胎动明显减少或消失
- 发热超过38°C
- 持续呕吐导致脱水

所有数据仅保存在本地，确保隐私安全。

---

## 示例用法

```
# 开始孕期记录
/pregnancy start 2025-01-01

# 记录产检
/pregnancy checkup week 12 NT normal
/pregnancy checkup 16周 唐筛 低风险

# 记录症状
/pregnancy symptom nausea moderate
/pregnancy symptom edema feet mild

# 记录体重
/pregnancy weight 62.5

# 记录血压
/pregnancy vital bp 115/75

# 查看状态
/pregnancy status

# 下次产检
/pregnancy next-checkup
```
