---
description: 管理疫苗接种记录和计划
arguments:
  - name: action
    description: 操作类型：add(添加接种)/record(记录接种)/schedule(查看计划)/due(待接种)/history(接种历史)/status(接种统计)/check(接种检查)
    required: true
  - name: info
    description: 疫苗信息（疫苗名称、剂次、日期等，自然语言描述）
    required: false
  - name: date
    description: 接种日期或查询日期（格式：YYYY-MM-DD，默认今天）
    required: false
---

# 疫苗接种管理

管理疫苗接种记录和计划，支持多剂次疫苗追踪、接种计划管理、不良反应记录和安全检查。

## 操作类型

### 1. 添加疫苗接种计划 - `add`

添加新的疫苗接种计划或记录已接种疫苗。

**参数说明：**
- `info`: 疫苗信息（必填），使用自然语言描述
- `date`: 接种日期（可选），格式：YYYY-MM-DD，默认今天

**示例：**
```
/vaccine add 乙肝疫苗 0-1-6程序 第一针已打昨天
/vaccine add HPV疫苗 第一针2025-10-15 第二针计划2025-12-15
/vaccine add 流感疫苗 2025-10-01已接种
/vaccine add COVID-19疫苗 第一剂今天接种
```

**支持的描述格式：**
- 疫苗名称 + 接种程序（0-1-6、2-6等）
- 已接种信息（第几针、接种日期、部位、接种单位）
- 计划信息（后续剂次的计划日期）
- 详细信息（厂家、批号、医生等）

### 2. 记录疫苗接种 - `record`

记录实际疫苗接种情况。

**参数说明：**
- `info`: 接种信息（必填），使用自然语言描述
- `date`: 接种日期（可选），格式：YYYY-MM-DD，默认今天

**示例：**
```
/vaccine record 乙肝疫苗 第2针 今天左上臂
/vaccine record 流感疫苗 今天社区卫生服务中心
/vaccine record HPV第2针 2025-12-15 右上臂 李医生
```

**支持的描述格式：**
- 疫苗名称 + 剂次 + 日期 + 接种部位
- 疫苗名称 + 日期 + 接种单位
- 疫苗名称 + 剂次 + 详细信息

### 3. 查看接种计划 - `schedule`

查看疫苗接种计划和即将接种的疫苗。

**示例：**
```
/vaccine schedule
/vaccine schedule 2025-12
/vaccine schedule 2026-01
```

### 4. 查看待接种疫苗 - `due`

快速查看待接种和逾期的疫苗。

**示例：**
```
/vaccine due
/vaccine due overdue
/vaccine due upcoming
```

### 5. 查看接种历史 - `history`

查看疫苗接种历史记录。

**参数说明：**
- 无参数：显示全部历史
- `date`: 月份（YYYY-MM格式）

**示例：**
```
/vaccine history
/vaccine history 2025-10
/vaccine history 2025-12
```

### 6. 查看接种统计 - `status`

查看疫苗接种统计和覆盖率。

**示例：**
```
/vaccine status
/vaccine status coverage
```

### 7. 接种前安全检查 - `check`

在接种前进行全面安全检查。

**参数说明：**
- `info`: 疫苗名称（必填）

**示例：**
```
/vaccine check 乙肝疫苗
/vaccine check 流感疫苗
/vaccine check HPV疫苗
```

## 执行步骤

### 添加疫苗接种计划 (add)

#### 1. 解析疫苗信息

从自然语言中提取：

**基本信息：**
- **疫苗名称**：中文或英文名称
- **接种程序**：0-1-6、2-6、单次等
- **剂次信息**：第几针、已接种剂次、总剂次数
- **接种日期**：已接种或计划接种的日期

**详细信息（可选）：**
- **生产厂家**：疫苗制造商
- **批号**：疫苗批号
- **接种部位**：左上臂、右上臂等
- **接种单位**：医疗机构名称
- **接种医生**：医生姓名
- **不良反应**：接种后的反应

#### 2. 查找疫苗数据库

从 `data/vaccine-database.json` 中匹配疫苗：

**匹配规则：**
- 完全匹配：疫苗名称完全相同
- 别名匹配：使用 aliases 字段
- 模糊匹配：部分名称匹配

#### 3. 接种前安全检查

**重要：在保存疫苗信息之前，必须进行全面安全检查。**

##### 3.1 过敏检查

检查流程：

```javascript
// 伪代码示例
function checkVaccineAllergies(vaccine) {
  const allergies = loadAllergies('data/allergies.json');
  const warnings = [];

  for (const allergy of allergies.allergies) {
    if (allergy.current_status.status !== 'active') continue;

    // 检查疫苗禁忌症中的过敏原
    const isContraindication = vaccine.contraindications.some(c =>
      c.type === 'allergy' && c.allergen === allergy.allergen.name
    );

    if (isContraindication) {
      warnings.push({
        allergen: allergy.allergen.name,
        severity: allergy.severity.level,
        reactions: allergy.reactions,
        recommendation: getRecommendation(allergy.severity.level)
      });
    }
  }

  return warnings;
}

function getRecommendation(severityLevel) {
  const recommendations = {
    'mild': '可接种，需观察',
    'moderate': '谨慎接种，建议咨询医生',
    'severe': '不建议接种，或咨询专科医生',
    'anaphylaxis': '绝对禁忌，禁止接种'
  };
  return recommendations[severityLevel];
}
```

**警示输出格式：**

```
🔍 疫苗接种前安全检查

疫苗：乙型肝炎疫苗（重组）
━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ 过敏史检查
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 通过

检查结果：
• 无相关过敏史
• 疫苗成分：重组HBsAg、氢氧化铝、硫柳汞
• 无匹配过敏原

2️⃣ 年龄适宜性检查
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 通过

当前年龄：35岁
推荐年龄：任何年龄均可接种
评估：适宜接种

3️⃣ 当前健康状况检查
━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 需注意

近期症状记录：
• 发热（2025-12-28）- 已恢复3天
评估：已痊愈，可接种

4️⃣ 药物相互作用检查
━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 发现1项潜在影响

当前用药：
• 环孢素 100mg 每日2次（免疫抑制剂）

影响：可能降低疫苗免疫效果
建议：
• 接种后2-3个月检测抗体滴度
• 如抗体滴度不足，考虑加强接种
• 咨询专科医生意见

5️⃣ 疫苗接种史检查
━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 已有接种记录

乙肝疫苗接种史：
• 第1针：2025-11-15 ✅
• 第2针：2025-12-15 ✅
• 第3针：待种（计划2026-05-15）

本次拟接种：第3针

6️⃣ 禁忌症检查
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 无禁忌

检查项目：
• 严重急性发热性疾病：❌ 无
• 对疫苗成分过敏：❌ 无
• 既往严重过敏史：❌ 无
• 妊娠期：❌ 否

━━━━━━━━━━━━━━━━━━━━━━━━━━
综合评估：✅ 可以接种
━━━━━━━━━━━━━━━━━━━━━━━━━━

注意事项：
• 接种后留观30分钟
• 如出现不良反应，及时记录
• 建议接种后2个月检测抗体
• 保持接种部位清洁干燥

是否继续添加疫苗计划？
A. 继续添加
B. 取消
```

**处理流程：**
- 用户选择 A：继续添加疫苗计划
- 用户选择 B：取消添加

##### 3.2 年龄适宜性检查

```javascript
function checkAgeAppropriateness(vaccine, birthDate) {
  const age = calculateAge(birthDate);
  const recommendation = vaccine.age_recommendations;

  if (age < recommendation.min_age) {
    return {
      appropriate: false,
      reason: `年龄不足，建议${recommendation.min_age}后再接种`
    };
  }

  if (recommendation.max_age && age > recommendation.max_age) {
    return {
      appropriate: false,
      reason: `超过推荐年龄上限`
    };
  }

  return {
    appropriate: true,
    recommended_age: recommendation.recommended_age
  };
}
```

##### 3.3 药物相互作用检查

```javascript
function checkVaccineInteractions(vaccine) {
  const medications = loadMedications();
  const interactions = [];

  for (const vaccineInteraction of vaccine.interactions) {
    const matchingMeds = medications.filter(med =>
      med.active && med.category === vaccineInteraction.drug_category
    );

    if (matchingMeds.length > 0) {
      interactions.push({
        drugs: matchingMeds.map(m => m.name),
        interaction: vaccineInteraction
      });
    }
  }

  return interactions;
}
```

#### 4. 生成接种计划

根据疫苗类型生成接种计划：

**多剂次疫苗（如乙肝0-1-6）：**
- 创建多个剂次记录
- 计算各剂次的应种日期
- 标记已接种和待接种剂次

**年度疫苗（如流感）：**
- 创建年度记录
- 标记下次接种时间（一年后）

**单次疫苗：**
- 创建单次记录
- 标记为已完成或计划中

**计划生成算法：**

```javascript
function generateVaccineSchedule(vaccine, firstDoseDate) {
  const schedule = [];

  const scheduleTypes = {
    '0-1-6': [
      { dose: 1, offset: 0, unit: 'months' },
      { dose: 2, offset: 1, unit: 'months' },
      { dose: 3, offset: 6, unit: 'months' }
    ],
    '0-2-6': [
      { dose: 1, offset: 0, unit: 'months' },
      { dose: 2, offset: 2, unit: 'months' },
      { dose: 3, offset: 6, unit: 'months' }
    ],
    '2-6': [
      { dose: 1, offset: 2, unit: 'months' },
      { dose: 2, offset: 6, unit: 'months' }
    ],
    'annual': [
      { dose: 1, offset: 1, unit: 'years' }
    ],
    'single': [
      { dose: 1, offset: 0, unit: 'days' }
    ]
  };

  const pattern = scheduleTypes[vaccine.standard_schedule];

  for (const doseInfo of pattern) {
    const scheduledDate = addOffset(firstDoseDate, doseInfo.offset, doseInfo.unit);
    const isFirstDose = doseInfo.dose === 1;

    schedule.push({
      dose_number: doseInfo.dose,
      scheduled_date: formatDate(scheduledDate),
      administered_date: isFirstDose && firstDoseDate <= new Date() ? formatDate(firstDoseDate) : null,
      status: isFirstDose && firstDoseDate <= new Date() ? 'completed' : 'scheduled'
    });
  }

  return schedule;
}
```

#### 5. 保存疫苗信息

**文件路径：**
`data/vaccinations.json`

**JSON 数据结构：**

```json
{
  "created_at": "2025-12-31T12:34:56.789Z",
  "last_updated": "2025-12-31T12:34:56.789Z",

  "vaccination_records": [
    {
      "id": "vax_20251231123456789",

      "vaccine_info": {
        "name": "乙型肝炎疫苗",
        "type": "recombinant",
        "trade_name": "重组乙型肝炎疫苗",
        "manufacturer": "北京生物制品研究所",
        "batch_number": "202512001",
        "dose_form": "injection",
        "dose_volume": {
          "value": 0.5,
          "unit": "ml"
        },
        "route": "intramuscular",
        "route_name": "肌肉注射"
      },

      "series_info": {
        "is_series": true,
        "series_type": "primary",
        "total_doses": 3,
        "current_dose": 2,
        "schedule_type": "0-1-6",
        "schedule_name": "0-1-6月程序"
      },

      "doses": [
        {
          "dose_number": 1,
          "scheduled_date": "2025-11-15",
          "administered_date": "2025-11-15",
          "administration_time": "2025-11-15T10:30:00",
          "site": "left_arm",
          "site_name": "左上臂三角肌",
          "facility": "社区卫生服务中心",
          "provider": "王医生",
          "lot_number": "202512001",
          "status": "completed"
        },
        {
          "dose_number": 2,
          "scheduled_date": "2025-12-15",
          "administered_date": "2025-12-16",
          "administration_time": "2025-12-16T09:00:00",
          "site": "right_arm",
          "site_name": "右上臂三角肌",
          "facility": "社区卫生服务中心",
          "provider": "李护士",
          "lot_number": "202512045",
          "status": "completed"
        },
        {
          "dose_number": 3,
          "scheduled_date": "2026-05-15",
          "administered_date": null,
          "administration_time": null,
          "site": null,
          "site_name": null,
          "facility": null,
          "provider": null,
          "lot_number": null,
          "status": "scheduled"
        }
      ],

      "adverse_reactions": [
        {
          "dose_number": 1,
          "reactions": [
            {
              "reaction": "注射部位疼痛",
              "severity": "mild",
              "onset_time": "接种后6小时",
              "duration": "2天",
              "treatment": "无需处理"
            }
          ]
        }
      ],

      "safety_checks": {
        "allergy_warnings": [],
        "drug_interactions": [],
        "age_appropriate": true,
        "contraindications": []
      },

      "status": {
        "series_status": "in_progress",
        "completion_percentage": 66.7,
        "next_dose_due": "2026-05-15",
        "is_overdue": false
      },

      "metadata": {
        "created_at": "2025-11-15T10:30:00.000Z",
        "last_updated": "2025-12-16T09:00:00.000Z",
        "notes": ""
      }
    }
  ],

  "statistics": {
    "total_vaccination_records": 15,
    "total_doses_administered": 42,
    "series_completed": 8,
    "series_in_progress": 4,
    "single_doses": 3,
    "overdue_count": 1,
    "upcoming_30_days": 3,
    "adverse_reactions_count": 5,
    "severe_reactions_count": 0,
    "last_updated": "2025-12-31T12:34:56.789Z"
  }
}
```

#### 6. 输出确认

```
✅ 疫苗接种计划已添加

疫苗信息：
━━━━━━━━━━━━━━━━━━━━━━━━━━
疫苗名称：乙型肝炎疫苗（重组）
接种程序：0-1-6月程序

已接种剂次：
━━━━━━━━━━━━━━━━━━━━━━━━━━
第1针：2025-11-15 ✅ 左上臂三角肌
第2针：2025-12-16 ✅ 右上臂三角肌

待接种剂次：
━━━━━━━━━━━━━━━━━━━━━━━━━━
第3针：2026-05-15（计划中）

进度：2/3 (66.7%)

💡 提示：
• 第3针建议在2026-05-15前后接种
• 可提前2周或延后1个月接种
• 接种后可检测抗体确认免疫效果
```

### 记录疫苗接种 (record)

#### 1. 识别疫苗接种信息

从自然语言中提取：
- **疫苗名称**：要记录的疫苗
- **剂次**：第几针
- **接种日期**：接种日期（默认今天）
- **接种部位**：左上臂、右上臂等
- **接种单位**：医疗机构名称
- **接种医生**：医生姓名

#### 2. 查找疫苗接种记录

根据疫苗名称和剂次查找对应的接种计划记录。

#### 3. 更新剂次信息

更新对应剂次的详细信息：
- 设置 `administered_date`
- 记录 `administration_time`
- 更新 `site`、`facility`、provider`
- 更改 `status` 为 "completed"

#### 4. 记录不良反应

```
📋 接种后反应记录

疫苗：乙型肝炎疫苗 - 第2针
接种时间：2025-12-31 10:30

是否有不良反应？
━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 无不良反应
2. 注射部位疼痛/红肿
3. 发热
4. 皮疹/瘙痒
5. 其他反应

请选择或描述反应：
```

根据用户选择记录不良反应信息。

#### 5. 计算进度和下一剂次

- 更新 `current_dose`
- 计算完成百分比
- 确定下一剂次应种日期
- 更新系列状态

#### 6. 输出确认

```
✅ 接种记录已更新

疫苗：乙型肝炎疫苗
剂次：第2针
接种时间：2025-12-31 10:30
接种部位：左上臂三角肌
接种单位：社区卫生服务中心

进度：2/3 (66.7%)
下一剂次：第3针，计划2026-05-15

💡 提示：
• 下一剂次可提前2周或延后1个月接种
• 建议在2026-04-15至2026-06-15之间完成接种
```

### 查看接种计划 (schedule)

#### 1. 加载所有疫苗接种记录

从 `data/vaccinations.json` 读取所有记录。

#### 2. 计算应种日期和状态

- 计算每个疫苗的下一剂次应种日期
- 判断是否逾期
- 按日期排序

#### 3. 输出格式

```
📅 疫苗接种计划

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 已逾期（1项）
━━━━━━━━━━━━━━━━━━━━━━━━━━

乙型肝炎疫苗 - 第3针
  ━━━━━━━━━━━━━━━━━━━━━━━━━━
  应种日期：2025-12-20（已逾期11天）
  状态：🔴 逾期

  建议：
  • 尽快补种，不必重新开始程序
  • 联系接种点预约时间

━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ 近期待种（30天内，2项）
━━━━━━━━━━━━━━━━━━━━━━━━━━

1. HPV疫苗 - 第2针
   ━━━━━━━━━━━━━━━━━━━━━━━━━━
   应种日期：2026-01-15（还有15天）
   接种部位：建议右臂
   预约建议：提前1周预约

2. 流感疫苗（年度加强）
   ━━━━━━━━━━━━━━━━━━━━━━━━━━
   应种日期：2026-01-30（还有30天）
   备注：流感季节前接种效果最佳

━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 后续计划
━━━━━━━━━━━━━━━━━━━━━━━━━━

• 乙肝疫苗 - 第3针：逾期待补种
• HPV疫苗 - 第3针：计划2026-04-15
• Tdap加强针：计划2026-06-01
```

### 查看待接种疫苗 (due)

快速查看待接种和逾期疫苗的简化视图。

**输出格式：**

```
⚠️ 待接种提醒

━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 紧急（已逾期）
━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 乙肝疫苗第3针
   逾期：11天（应种：2025-12-20）
   💡 建议尽快补种

━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ 即将到期（7天内）
━━━━━━━━━━━━━━━━━━━━━━━━━━
无

━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 近期待种（30天内）
━━━━━━━━━━━━━━━━━━━━━━━━━━

1. HPV疫苗第2针 - 还有15天
2. 流感疫苗 - 还有30天

━━━━━━━━━━━━━━━━━━━━━━━━━━
行动建议：
• 立即联系接种点补种逾期疫苗
• 为即将到期的疫苗预约接种时间
```

### 查看接种历史 (history)

#### 1. 加载接种记录

读取所有已完成的接种记录。

#### 2. 按时间排序

按接种日期倒序排列。

#### 3. 输出格式

```
📋 疫苗接种历史

━━━━━━━━━━━━━━━━━━━━━━━━━━
2025年12月（2次）
━━━━━━━━━━━━━━━━━━━━━━━━━━

12-31  HPV疫苗 第2针 ✅
       部位：右上臂三角肌
       地点：社区卫生服务中心
       反应：注射部位轻度疼痛（1天）

12-15  乙肝疫苗 第2针 ✅
       批号：202512045
       地点：社区卫生服务中心

━━━━━━━━━━━━━━━━━━━━━━━━━━
2025年11月（1次）
━━━━━━━━━━━━━━━━━━━━━━━━━━

11-15  乙肝疫苗 第1针 ✅
       批号：202512001
       地点：社区卫生服务中心

━━━━━━━━━━━━━━━━━━━━━━━━━━
2025年10月（2次）
━━━━━━━━━━━━━━━━━━━━━━━━━━

10-15  HPV疫苗 第1针 ✅
       批号：202510012
10-01  流感疫苗 ✅
       批号：202509088

━━━━━━━━━━━━━━━━━━━━━━━━━━
总计：42剂次
系列完成：8个
进行中：4个
```

### 查看接种统计 (status)

#### 1. 计算统计数据

- 总接种剂次
- 完成的系列数
- 进行中的系列数
- 不良反应统计
- 及时接种率

#### 2. 输出格式

```
📊 疫苗接种统计

总体情况：
━━━━━━━━━━━━━━━━━━━━━━━━━━
累计接种：42剂次
疫苗种类：15种
完成系列：8个
进行中：4个
单次疫苗：3种

━━━━━━━━━━━━━━━━━━━━━━━━━━
系列进度
━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 乙肝疫苗（3/3）100%
   完成：2025-11-15

✅ HPV疫苗（2/3）66.7%
   下次：2026-01-15

⚠️ 百白破疫苗（1/3）33.3%
   状态：已逾期，需尽快补种

━━━━━━━━━━━━━━━━━━━━━━━━━━
不良反应统计
━━━━━━━━━━━━━━━━━━━━━━━━━━
总反应数：5次
• 轻度：5次
• 中度：0次
• 重度：0次

常见反应：
• 注射部位疼痛：3次
• 发热：1次
• 疲乏：1次

━━━━━━━━━━━━━━━━━━━━━━━━━━
接种及时性
━━━━━━━━━━━━━━━━━━━━━━━━━━
按时接种：38次（90.5%）
延迟接种：4次（9.5%）
逾期未种：1剂次

━━━━━━━━━━━━━━━━━━━━━━━━━━
免疫覆盖评估
━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 儿童基础免疫：完成
✅ 成人常规免疫：良好
⚠️ 推荐疫苗：部分缺失
  • 带状疱疹疫苗：未接种（50岁以上推荐）
  • 肺炎球菌疫苗：未接种（65岁以上推荐）

💡 建议：
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 优先补种逾期的百白破疫苗
• 考虑接种带状疱疹疫苗（如符合年龄条件）
• 流感疫苗每年秋季接种
```

### 接种前安全检查 (check)

#### 1. 加载疫苗信息

从数据库中获取疫苗详细信息。

#### 2. 执行安全检查

- 过敏检查
- 年龄适宜性检查
- 当前健康状况检查
- 药物相互作用检查
- 疫苗接种史检查
- 禁忌症检查

#### 3. 输出格式

（参见前面的"接种前安全检查"示例输出）

## 疫苗数据库

### 数据结构

**文件路径：** `data/vaccine-database.json`

```json
{
  "version": "1.0.0",
  "created_at": "2025-12-31T12:34:56.789Z",
  "last_updated": "2025-12-31T12:34:56.789Z",

  "vaccines": [
    {
      "id": "hepb",
      "name": "乙型肝炎疫苗",
      "english_name": "Hepatitis B Vaccine",
      "aliases": ["乙肝疫苗", "HepB", "重组乙型肝炎疫苗"],
      "type": "recombinant",
      "manufacturers": ["北京生物", "康泰生物", "葛兰素史克"],

      "schedule": {
        "is_series": true,
        "series_type": "primary",
        "standard_schedule": "0-1-6",
        "doses": [
          {
            "dose_number": 1,
            "timing": "birth",
            "timing_description": "出生时24小时内",
            "recommended_age": "0月龄",
            "min_age": "0月",
            "max_age": null
          },
          {
            "dose_number": 2,
            "timing": "1_month_after_dose1",
            "timing_description": "第1剂后1个月",
            "interval_after_previous_dose": {
              "value": 1,
              "unit": "months"
            },
            "recommended_age": "1月龄",
            "min_interval": "4周"
          },
          {
            "dose_number": 3,
            "timing": "6_months_after_dose1",
            "timing_description": "第1剂后6个月",
            "interval_after_previous_dose": {
              "value": 5,
              "unit": "months"
            },
            "recommended_age": "6月龄",
            "min_interval": "16周",
            "grace_period": "4周"
          }
        ],
        "booster": {
          "required": false,
          "indications": ["高危人群", "免疫功能低下"],
          "interval": "5年"
        }
      },

      "contraindications": [
        {
          "type": "allergy",
          "allergen": "酵母",
          "severity": "severe",
          "description": "对疫苗任何成分（包括酵母）严重过敏者"
        },
        {
          "type": "disease",
          "condition": "严重急性发热性疾病",
          "severity": "temporary",
          "description": "发热期应暂缓接种"
        }
      ],

      "age_recommendations": {
        "recommended_age": "出生时",
        "min_age": "0月",
        "max_age": null,
        "catch_up_schedule": "任何年龄均可开始接种"
      },

      "interactions": [
        {
          "drug_category": "免疫抑制剂",
          "interaction_type": "reduced_efficacy",
          "severity": "moderate",
          "description": "免疫抑制剂可能降低疫苗免疫效果"
        }
      ],

      "common_adverse_reactions": [
        {
          "reaction": "注射部位疼痛",
          "frequency": "common",
          "severity": "mild",
          "onset": "接种后24小时内",
          "duration": "1-3天"
        },
        {
          "reaction": "发热",
          "frequency": "occasional",
          "severity": "mild_to_moderate",
          "onset": "接种后6-24小时",
          "duration": "1-2天"
        }
      ],

      "special_populations": {
        "pregnancy": {
          "recommendation": "safe",
          "notes": "妊娠期可安全接种"
        },
        "lactation": {
          "recommendation": "safe",
          "notes": "哺乳期可安全接种"
        },
        "immunocompromised": {
          "recommendation": "recommended",
          "notes": "免疫功能低下者更需接种"
        }
      }
    }
  ],

  "categories": {
    "routine_childhood": ["hepb", "bcg", "polio", "dpt", "mmr", "varicella"],
    "routine_adult": ["influenza", "tdap", "pneumococcal", "shingles", "covid"],
    "travel": ["hepa", "typhoid", "yellow_fever", "japanese_encephalitis"],
    "high_risk": ["pneumococcal", "meningococcal", "hib"]
  }
}
```

## 智能识别规则

### 疫苗名称识别

**常见疫苗：**
- 乙肝疫苗、HepB、乙型肝炎疫苗
- 流感疫苗、Flu vaccine、流行性感冒疫苗
- HPV疫苗、宫颈癌疫苗、人乳头瘤病毒疫苗
- COVID-19疫苗、新冠疫苗、冠状病毒疫苗
- 百白破疫苗、DPT
- 麻腮风疫苗、MMR
- 脊髓灰质炎疫苗、脊灰疫苗
- 卡介苗、BCG
- 肺炎球菌疫苗
- 带状疱疹疫苗

### 剂次识别

| 用户输入 | 标准化 |
|---------|--------|
| 第1针、第一针、第1剂、第一剂 | dose_number: 1 |
| 第2针、第二针、第2剂、第二剂 | dose_number: 2 |
| 第3针、第三针、第3剂、第三剂 | dose_number: 3 |

### 接种程序识别

| 用户输入 | 标准化 | 总剂次 |
|---------|--------|-------|
| 0-1-6、016程序 | 0-1-6 | 3剂 |
| 0-2-6、026程序 | 0-2-6 | 3剂 |
| 2剂、2次 | 2-dose | 2剂 |
| 3剂、3次 | 3-dose | 3剂 |
| 单次、1次 | single | 1剂 |

### 接种部位识别

| 用户输入 | 标准化 |
|---------|--------|
| 左上臂、左臂 | left_arm |
| 右上臂、右臂 | right_arm |
| 左大腿 | left_thigh |
| 右大腿 | right_thigh |
| 臀部、臀部注射 | buttock |

### 日期识别

| 用户输入 | 标准化 |
|---------|--------|
| 今天、当日 | 当日日期 |
| 昨天、昨日 | 当日-1天 |
| 明天、明日 | 当日+1天 |
| YYYY-MM-DD | 标准日期格式 |
| X月X日 | 当年的该日期 |
| X周后、X个月后 | 计算日期 |

## 数据结构更新

在全局索引 `data/index.json` 中添加：

```json
{
  "vaccination_records": "data/vaccinations.json",
  "vaccine_database": "data/vaccine-database.json",
  "statistics": {
    "vaccination_count": 0
  }
}
```

## 与其他系统的集成

### 与过敏系统集成

疫苗接种前自动检查 `data/allergies.json`：

1. 读取活跃的过敏记录
2. 检查疫苗禁忌症中的过敏原
3. 按严重程度显示警示
4. 提供接种建议

### 与档案系统集成

从 `data/profile.json` 获取出生日期用于：
- 年龄适宜性检查
- 年龄相关的疫苗推荐
- 接种程序判断

### 与药物系统交互

检查当前用药与疫苗的相互作用：
- 免疫抑制剂：可能降低疫苗效果
- 抗凝药物：接种部位护理建议
- 其他相互作用

## 统计计算

### 完成率计算

```javascript
completion_percentage = (current_dose / total_doses) * 100
```

### 逾期判断

```javascript
is_overdue = (scheduled_date < today) && (status === 'scheduled')
```

### 及时接种率

```javascript
timeliness_rate = (on_time_doses / total_doses) * 100
```

### 不良反应率

```javascript
reaction_rate = (doses_with_reactions / total_doses) * 100
```

## 注意事项

- 本系统仅供个人疫苗接种记录，不能替代专业医疗建议
- 接种前请咨询医生或接种点工作人员
- 如有严重过敏史，必须告知接种人员
- 接种后留观30分钟
- 所有数据仅保存在本地
- 重要疫苗接种记录建议与医生分享

## 示例用法

```bash
# 添加乙肝疫苗接种计划
/vaccine add 乙肝疫苗 0-1-6程序 第一针已打昨天

# 添加HPV疫苗计划
/vaccine add HPV疫苗 第一针2025-10-15 第二针计划2025-12-15

# 记录实际接种
/vaccine record 乙肝疫苗 第2针 今天左上臂
/vaccine record 流感疫苗 今天社区卫生服务中心

# 查看接种计划
/vaccine schedule

# 查看待接种疫苗
/vaccine due

# 查看接种历史
/vaccine history
/vaccine history 2025-10

# 查看接种统计
/vaccine status

# 接种前安全检查
/vaccine check 乙肝疫苗
```

## 错误处理

- **疫苗信息为空**: "请提供疫苗信息，例如：/vaccine add 乙肝疫苗 第1针"
- **无法识别疫苗**: "未识别该疫苗，请提供完整的疫苗名称"
- **疫苗接种计划已存在**: "该疫苗接种计划已存在，请使用 /vaccine record 记录接种"
- **无接种记录**: "暂无接种记录"
- **疫苗数据库不存在**: "疫苗数据库不存在，请先创建"
- **存储失败**: "保存记录失败，请检查存储空间"
