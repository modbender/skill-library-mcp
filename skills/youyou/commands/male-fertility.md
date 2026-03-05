---
description: 男性生育健康和精液分析记录
arguments:
  - name: action
    description: 操作类型：semen(精液分析)/hormone(激素)/varicocele(精索静脉曲张)/infection(感染)/status(状态)/diagnosis(诊断)
    required: true
  - name: info
    description: 生育健康信息（精液分析结果、激素水平、检查结果等，自然语言描述）
    required: false
---

# 男性不育管理

男性生育健康追踪和管理,包括精液分析记录、激素水平监测、不育因素评估。

## 操作类型

### 1. 记录精液分析 - `semen`

记录精液分析结果,WHO 2021标准。

**参数说明:**
- `info`: 精液分析信息(必填)
  - 参数类型: volume(精液量)/concentration(密度)/motility(活力)/morphology(形态)/ph(pH)/liquefaction(液化)
  - 数值: 根据参数类型提供相应数值
  - 精子活力: pr(前向运动), np(非前向运动)

**示例:**
```
/fertility semen volume 2.5
/fertility semen concentration 45
/fertility semen motility pr 35 np 20
/fertility semen morphology 4
/fertility semen ph 7.5
/fertility semen complete    # 完整记录
```

**执行步骤:**

#### 1. 精液分析标准(WHO 2021)

**精液量:**
- 正常: ≥ 1.5 mL
- 异常: < 1.5 mL(精液减少)
- 无精: 0 mL

**精子密度:**
- 正常: ≥ 15 × 10⁶/mL
- 少精症: < 15 × 10⁶/mL
- 无精症: 0 × 10⁶/mL

**精子总数:**
- 正常: ≥ 39 × 10⁶/每次射精

**精子活力:**
- PR(前向运动,progressive): ≥ 32%
- NP(非前向运动,non-progressive): ≥ 40%
- 弱精症: PR < 32%

**精子形态:**
- 正常形态率: ≥ 4%
- 畸形精子症: < 4%

**精液pH值:**
- 正常: 7.2-8.0
- 异常: < 7.2 或 > 8.0

**液化时间:**
- 正常: ≤ 60分钟

#### 2. 解析精液分析信息

**参数识别:**
```javascript
// 精液量
volume_patterns = [
  /volume[:\s]+(\d+\.?\d*)/i,
  /精液量[:\s]+(\d+\.?\d*)/i,
  /(\d+\.?\d*)\s*ml/i
]

// 精子密度
concentration_patterns = [
  /concentration[:\s]+(\d+)/i,
  /密度[:\s]+(\d+)/i,
  /(\d+)\s*10.*6.*ml/i
]

// 活力
motility_patterns = [
  /pr[:\s]+(\d+)/i,
  /前向运动[:\s]+(\d+)/i,
  /np[:\s]+(\d+)/i
]

// 形态
morphology_patterns = [
  /morphology[:\s]+(\d+)/i,
  /形态[:\s]+(\d+)/i
]
```

#### 3. 诊断评估

**精液分析结果分类:**

| 结果 | 诊断 |
|------|------|
| 所有参数正常 | 正常精液(normospermia) |
| 精子密度<15 | 少精症(oligozoospermia) |
| 精子密度=0 | 无精症(azoospermia) |
| PR<32% | 弱精症(asthenozoospermia) |
| 正常形态<4% | 畸形精子症(teratozoospermia) |
| 精液量<1.5mL | 精液减少(hypospermia) |
| 多个异常 | 混合异常 |

#### 4. 更新精液分析记录

**精液分析数据结构:**
```json
{
  "semen_analysis": {
    "date": "2025-06-20",
    "abstinence_period": "3_days",

    "volume": {
      "value": 2.5,
      "unit": "mL",
      "reference": "≥1.5",
      "result": "normal"
    },

    "concentration": {
      "value": 45,
      "unit": "10⁶/mL",
      "reference": "≥15",
      "result": "normal"
    },

    "total_count": {
      "value": 112.5,
      "unit": "10⁶",
      "reference": "≥39",
      "result": "normal"
    },

    "motility": {
      "pr": {
        "value": 35,
        "reference": "≥32",
        "result": "normal"
      },
      "np": {
        "value": 20,
        "reference": "≥40",
        "result": "normal"
      },
      "im": {
        "value": 45,
        "result": "normal"
      }
    },

    "morphology": {
      "value": 4,
      "unit": "%",
      "reference": "≥4",
      "result": "normal"
    },

    "ph": {
      "value": 7.5,
      "reference": "7.2-8.0",
      "result": "normal"
    },

    "liquefaction": {
      "value": 30,
      "unit": "minutes",
      "reference": "≤60",
      "result": "normal"
    },

    "diagnosis": "normospermia"
  }
}
```

#### 5. 输出确认

**正常精液分析:**
```
✅ 精液分析已记录

精液分析报告:
━━━━━━━━━━━━━━━━━━━━━━━━━━
检测日期: 2025年6月20日
禁欲时间: 3天 ✓

精液参数:
━━━━━━━━━━━━━━━━━━━━━━━━━━
精液量: 2.5 mL ✓ (参考: ≥1.5)
精子密度: 45 × 10⁶/mL ✓ (参考: ≥15)
精子总数: 112.5 × 10⁶ ✓ (参考: ≥39)

精子活力:
  PR(前向运动): 35% ✓ (参考: ≥32)
  NP(非前向): 20% ✓ (参考: ≥40)
  总活力: 55% ✓

精子形态: 4% ✓ (参考: ≥4)
精液pH: 7.5 ✓ (参考: 7.2-8.0)
液化时间: 30分钟 ✓ (参考: ≤60)

诊断结果:
━━━━━━━━━━━━━━━━━━━━━━━━━━
正常精液 (Normospermia) ✅

所有参数均在正常范围内。

评估:
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 精子数量充足
✅ 精子活力正常
✅ 精子形态正常
✅ 精液质量良好

建议:
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 继续尝试自然受孕
✅ 保持健康生活方式
✅ 避免高温环境(桑拿、热水澡)
✅ 戒烟限酒
✅ 均衡饮食
✅ 规律运动

⚠️ 重要提示:
━━━━━━━━━━━━━━━━━━━━━━━━━━
本次精液分析正常。

精液质量会有波动,
建议2-3个月后复查确认。

如果伴侣未能在6-12个月内
受孕,建议进一步检查。

数据已保存至: data/生育记录/2025-06/2025-06-20_精液分析.json
```

**异常精液分析警示:**
```
⚠️ 精液分析异常提示

精液分析报告:
━━━━━━━━━━━━━━━━━━━━━━━━━━
检测日期: 2025年6月20日
禁欲时间: 3天

精液参数:
━━━━━━━━━━━━━━━━━━━━━━━━━━
精液量: 1.2 mL ⚠️ (参考: ≥1.5)
精子密度: 12 × 10⁶/mL ⚠️ (参考: ≥15)
精子总数: 14.4 × 10⁶ ⚠️ (参考: ≥39)

精子活力:
  PR(前向运动): 25% ⚠️ (参考: ≥32)
  NP(非前向): 15% ⚠️ (参考: ≥40)
  总活力: 40% ⚠️

精子形态: 3% ⚠️ (参考: ≥4)
精液pH: 7.3 ✓
液化时间: 45分钟 ✓

诊断结果:
━━━━━━━━━━━━━━━━━━━━━━━━━━
少精症 + 弱精症 + 畸形精子症
⚠️ 精液质量异常

评估:
━━━━━━━━━━━━━━━━━━━━━━━━━━
多个参数低于正常值,
可能影响生育能力。

可能原因:
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 精索静脉曲张
• 内分泌异常
• 生殖道感染
• 免疫因素
• 遗传因素
• 环境因素
• 生活方式

🏥 建议就医:
━━━━━━━━━━━━━━━━━━━━━━━━━━
建议咨询泌尿外科或
男性科医生进一步评估:

进一步检查:
• 精索静脉超声
• 激素水平检测
• 生殖道感染筛查
• 遗传学检测(如需要)

生活方式调整:
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 戒烟(非常重要)
✅ 限制酒精
✅ 避免高温环境
✅ 减少紧身裤
✅ 均衡营养
✅ 规律运动
✅ 充足睡眠
✅ 减轻压力

⚠️ 重要提示:
━━━━━━━━━━━━━━━━━━━━━━━━━━
精液质量异常不等于绝对不育。

轻度异常可通过生活方式改善
和医学治疗得到纠正。

建议2-3个月后复查,
同时咨询男性科医生。

数据已保存
```

---

### 2. 记录激素水平 - `hormone`

记录性激素检查结果。

**参数说明:**
- `info`: 激素检测结果(必填)
  - 激素类型: testosterone(睾酮)/lh(促黄体生成素)/fsh(促卵泡刺激素)/prl(泌乳素)/e2(雌二醇)
  - 数值: 数字

**示例:**
```
/fertility hormone testosterone 15.5
/fertility hormone lh 5.2
/fertility hormone fsh 8.1
/fertility hormone prl 12.5
/fertility hormone complete  # 完整激素检测
```

**执行步骤:**

#### 1. 激素参考值

**睾酮(T):**
- 总睾酮: 10-35 nmol/L
- 游离睾酮: 0.22-0.65 nmol/L

**促黄体生成素(LH):**
- 正常: 1.7-8.6 IU/L

**促卵泡刺激素(FSH):**
- 正常: 1.5-12.4 IU/L

**泌乳素(PRL):**
- 正常: < 15 ng/mL(男性)

**雌二醇(E2):**
- 正常: < 70 pg/mL(男性)

#### 2. 解析激素信息

**激素识别:**
```javascript
hormones = {
  testosterone: {
    patterns: [/testosterone[:\s]+(\d+\.?\d*)/i, /睾酮[:\s]+(\d+\.?\d*)/i],
    unit: "nmol/L",
    reference: "10-35"
  },
  lh: {
    patterns: [/\blh\b[:\s]+(\d+\.?\d*)/i, /促黄体生成素[:\s]+(\d+\.?\d*)/i],
    unit: "IU/L",
    reference: "1.7-8.6"
  },
  fsh: {
    patterns: [/\bfsh\b[:\s]+(\d+\.?\d*)/i, /促卵泡刺激素[:\s]+(\d+\.?\d*)/i],
    unit: "IU/L",
    reference: "1.5-12.4"
  },
  prl: {
    patterns: [/prl[:\s]+(\d+\.?\d*)/i, /泌乳素[:\s]+(\d+\.?\d*)/i],
    unit: "ng/mL",
    reference: "<15"
  },
  e2: {
    patterns: [/e2[:\s]+(\d+\.?\d*)/i, /雌二醇[:\s]+(\d+\.?\d*)/i],
    unit: "pg/mL",
    reference: "<70"
  }
}
```

#### 3. 激素评估

**异常模式:**

**原发性睾丸功能不全:**
- 睾酮: 低
- LH: 高
- FSH: 高

**继发性睾丸功能不全:**
- 睾酮: 低
- LH: 低或正常
- FSH: 低或正常

**高泌乳素血症:**
- 泌乳素: >15 ng/mL
- 睾酮: 可降低
- LH/FSH: 可降低

#### 4. 更新激素记录

**激素数据结构:**
```json
{
  "hormones": {
    "date": "2025-06-15",
    "testosterone": {
      "total": 15.5,
      "reference": "10-35",
      "unit": "nmol/L",
      "result": "normal"
    },
    "lh": {
      "value": 5.2,
      "reference": "1.7-8.6",
      "unit": "IU/L",
      "result": "normal"
    },
    "fsh": {
      "value": 8.1,
      "reference": "1.5-12.4",
      "unit": "IU/L",
      "result": "normal"
    },
    "prl": {
      "value": 12.5,
      "reference": "<15",
      "unit": "ng/mL",
      "result": "normal"
    },
    "e2": {
      "value": 35,
      "reference": "<70",
      "unit": "pg/mL",
      "result": "normal"
    }
  }
}
```

#### 5. 输出确认

```
✅ 激素检测已记录

激素检测报告:
━━━━━━━━━━━━━━━━━━━━━━━━━━
检测日期: 2025年6月15日

激素水平:
━━━━━━━━━━━━━━━━━━━━━━━━━━
睾酮(T): 15.5 nmol/L ✓ (参考: 10-35)
LH: 5.2 IU/L ✓ (参考: 1.7-8.6)
FSH: 8.1 IU/L ✓ (参考: 1.5-12.4)
泌乳素(PRL): 12.5 ng/mL ✓ (参考: <15)
雌二醇(E2): 35 pg/mL ✓ (参考: <70)

评估:
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 所有激素水平在正常范围
✅ 下丘脑-垂体-睾丸轴功能正常
✅ 无明显内分泌异常

激素-精子关系:
━━━━━━━━━━━━━━━━━━━━━━━━━━
正常激素水平提示:
• 睾丸产生精子功能正常
• 内分泌调节正常
• 精子质量问题可能与睾丸
  局部因素有关

建议:
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 激素水平正常
✅ 重点关注精子质量
✅ 考虑精索静脉曲张检查
✅ 生殖道感染筛查

⚠️ 重要提示:
━━━━━━━━━━━━━━━━━━━━━━━━━━
激素正常不能排除所有不育原因。

需结合精液分析、体格检查等
综合评估。

数据已保存
```

---

### 3. 记录精索静脉曲张 - `varicocele`

记录精索静脉曲张检查结果。

**参数说明:**
- `info`: 精索静脉曲张信息(必填)
  - 是否存在: none(无)/left(左侧)/right(右侧)/bilateral(双侧)
  - 分级: I/II/III(可选)

**示例:**
```
/fertility varicocele none
/fertility varicocele left grade II
/fertility varicocele bilateral
/fertility varicocele 左侧 II级
```

**执行步骤:**

#### 1. 精索静脉曲张分级

**临床分级:**
- **I级**: 触不到,Valsalva试验可见
- **II级**: 触得到,Valsalva试验加重
- **III级**: 视诊可见

#### 2. 更新记录

**精索静脉曲张数据结构:**
```json
{
  "varicocele": {
    "present": true,
    "side": "left",
    "grade": "II",
    "confirmed_by": "ultrasound",
    "surgery": false,
    "surgery_date": null,
    "notes": ""
  }
}
```

#### 3. 输出确认

```
✅ 精索静脉曲张已记录

检查结果:
━━━━━━━━━━━━━━━━━━━━━━━━━━
部位: 左侧
分级: II级
确诊方式: 超声

评估:
━━━━━━━━━━━━━━━━━━━━━━━━━━
左侧精索静脉曲张 II级

精索静脉曲张影响:
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 可能导致精子质量下降
• 常见不育原因之一
• 可手术治疗

⚠️ 建议就医:
━━━━━━━━━━━━━━━━━━━━━━━━━━
建议咨询泌尿外科评估:

治疗选择:
• 观察(轻度)
• 手术治疗(中重度)
• 显微外科精索静脉结扎术
• 介入栓塞术

手术适应症:
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 精液质量异常
• 睾丸体积缩小
• 睾丸疼痛
• 不孕2年以上

⚠️ 重要提示:
━━━━━━━━━━━━━━━━━━━━━━━━━━
精索静脉曲张是可治疗的
不育原因。

手术可改善精液质量,
提高自然受孕率。

数据已保存
```

---

### 4. 记录感染检查 - `infection`

记录生殖道感染检查结果。

**参数说明:**
- `info`: 感染检查结果(必填)
  - 病原体: chlamydia(衣原体)/gonorrhea(淋病)/mycoplasma(支原体)
  - 结果: positive(阳性)/negative(阴性)

**示例:**
```
/fertility infection chlamydia negative
/fertility infection gonorrhea negative
/fertility infection 支原体阳性
```

**执行步骤:**

#### 1. 常见病原体

**衣原体(Chlamydia trachomatis):**
- 可导致尿道炎、前列腺炎、附睾炎
- 影响精子质量

**淋球菌(Neisseria gonorrhoeae):**
- 导致尿道炎、附睾炎
- 影响精子输送

**支原体/解脲支原体:**
- 可能影响精子活力
- 与不育有关

#### 2. 更新感染记录

**感染数据结构:**
```json
{
  "infections": {
    "chlamydia": "negative",
    "gonorrhea": "negative",
    "mycoplasma": "not_tested",
    "ureaplasma": "not_tested",
    "date": "2025-06-10",
    "treated": false
  }
}
```

#### 3. 输出确认

```
✅ 感染检查已记录

检查结果:
━━━━━━━━━━━━━━━━━━━━━━━━━━
检查日期: 2025年6月10日

衣原体: 阴性 ✓
淋球菌: 阴性 ✓
支原体: 未检测
解脲支原体: 未检测

评估:
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 无常见生殖道感染证据

建议:
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 感染筛查阴性
✅ 不需要抗感染治疗

⚠️ 注意:
━━━━━━━━━━━━━━━━━━━━━━━━━━
未检测支原体/解脲支原体,
如有需要建议补充检测。

数据已保存
```

---

### 5. 查看状态 - `status`

显示生育健康追踪状态。

**参数说明:**
- 无参数

**示例:**
```
/fertility status
```

**执行步骤:**

#### 1. 读取生育健康数据

#### 2. 生成状态报告

```
📍 男性生育健康状态

基本信息:
━━━━━━━━━━━━━━━━━━━━━━━━━━
年龄: 35岁
不育类型: 原发性不育
伴侣年龄: 32岁
尝试受孕时间: 18个月

精液分析:
━━━━━━━━━━━━━━━━━━━━━━━━━━
最近检测: 2025年6月20日

精液量: 2.5 mL ✓
精子密度: 45 × 10⁶/mL ✓
精子活力: PR 35% ✓
精子形态: 4% ✓

诊断: 正常精液

激素水平:
━━━━━━━━━━━━━━━━━━━━━━━━━━
睾酮: 15.5 nmol/L ✓
LH: 5.2 IU/L ✓
FSH: 8.1 IU/L ✓
泌乳素: 12.5 ng/mL ✓

评估: 激素水平正常

其他检查:
━━━━━━━━━━━━━━━━━━━━━━━━━━
精索静脉曲张: 无 ✓
衣原体: 阴性 ✓
淋球菌: 阴性 ✓

综合评估:
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 精液分析正常
✅ 激素水平正常
✅ 无明显不育原因

可能因素:
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 特发性不育
• 伴侣因素(需检查)
• 免疫因素
• 遗传因素

建议行动:
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 继续尝试自然受孕
✅ 伴侣妇科检查(如未做)
✅ 2-3个月后复查精液
✅ 考虑染色体检测(如需要)
✅ 考虑Y染色体微缺失检测

💡 本周关注:
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 健康生活方式
• 避免高温环境
• 戒烟限酒
• 规律作息

⚠️ 重要声明:
━━━━━━━━━━━━━━━━━━━━━━━━━━
本系统仅供生育健康追踪,不能替代专业医疗建议。

建议咨询男性科或生殖医学中心
进行全面评估和指导。

数据已保存
```

---

### 6. 查看诊断 - `diagnosis`

显示不育诊断和评估。

**参数说明:**
- 无参数

**示例:**
```
/fertility diagnosis
```

**执行步骤:**

#### 1. 不不育分类

**原发性不育:**
- 从未使伴侣怀孕

**继发性不育:**
- 曾使伴侣怀孕,现在无法

**不育原因分类:**
- 精子因素
- 精索静脉曲张
- 内分泌异常
- 生殖道感染
- 免疫因素
- 遗传因素
- 特发性(原因不明)

#### 2. 生成诊断报告

```
📋 男性不育诊断报告

评估日期: 2025年12月31日

不育类型:
━━━━━━━━━━━━━━━━━━━━━━━━━━
类型: 原发性不育
尝试受孕时间: 18个月

精液分析评估:
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 精液量正常
✅ 精子密度正常
✅ 精子活力正常
✅ 精子形态正常

结论: 精子分析正常

激素评估:
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 睾酮正常
✅ LH正常
✅ FSH正常
✅ 泌乳素正常

结论: 内分泌功能正常

其他检查:
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 无精索静脉曲张
✅ 无生殖道感染

综合诊断:
━━━━━━━━━━━━━━━━━━━━━━━━━━
特发性不育
(Idiopathic Infertility)

诊断说明:
━━━━━━━━━━━━━━━━━━━━━━━━━━
精液分析和激素水平均正常,
未发现明显不育原因。

特发性不育约占
男性不育的30-40%。

可能因素(未证实):
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 精子DNA碎片率增加
• 氧化应激
• 线粒体功能异常
• 隐匿精子质量缺陷
• 免疫因素

建议进一步检查:
━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 精子DNA碎片率检测
📋 抗精子抗体检测
📋 Y染色体微缺失检测
📋 染色体核型分析
📋 伴侣妇科检查

治疗建议:
━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 继续尝试自然受孕
✅ 改善生活方式
✅ 抗氧化剂治疗(如需要)
✅ 辅助生殖技术(如需要)

辅助生殖技术选择:
━━━━━━━━━━━━━━━━━━━━━━━━━━
• 人工授精(IUI)
• 体外受精(IVF)
• 卵胞浆内单精子注射(ICSI)
• 如果持续不孕建议咨询

生殖医学中心:

预后:
━━━━━━━━━━━━━━━━━━━━━━━━━━
特发性不育预后:
• 仍有自然受孕可能
• 辅助生殖成功率良好
• 不影响后代健康

⚠️ 重要提示:
━━━━━━━━━━━━━━━━━━━━━━━━━━
不育不等于绝对不能生育。

现代生殖医学技术可帮助
大多数不育夫妇实现生育。

建议咨询生殖医学中心
制定个体化治疗方案。

数据已保存
```

---

## 数据结构

### 主文件: data/fertility-tracker.json

```json
{
  "created_at": null,
  "last_updated": null,

  "fertility_assessment": {
    "user_id": null,
    "age": null,
    "infertility_type": null,
    "partner_age": null,
    "trying_to_conceive_months": null,

    "semen_analysis": {
      "date": null,
      "abstinence_period": null,
      "volume": {},
      "concentration": {},
      "total_count": {},
      "motility": {},
      "morphology": {},
      "ph": {},
      "liquefaction": {},
      "diagnosis": null
    },

    "hormones": {
      "date": null,
      "testosterone": {},
      "lh": {},
      "fsh": {},
      "prl": {},
      "e2": {}
    },

    "varicocele": {
      "present": null,
      "side": null,
      "grade": null,
      "surgery": null,
      "surgery_date": null
    },

    "infections": {
      "chlamydia": null,
      "gonorrhea": null,
      "mycoplasma": null,
      "date": null,
      "treated": null
    },

    "genetic_testing": {
      "karyotype": null,
      "y_chromosome_microdeletion": null,
      "cftr_mutation": null
    },

    "recommendations": []
  },

  "statistics": {
    "total_semen_analyses": 0,
    "last_analysis_date": null,
    "diagnosis": null,
    "tracking_duration_months": 0
  }
}
```

### 详细记录: data/生育记录/YYYY-MM/YYYY-MM-DD_精液分析.json

```json
{
  "record_id": "fertility_20250620_001",
  "record_type": "精液分析",
  "date": "2025-06-20",

  "semen_analysis": {
    "volume": 2.5,
    "concentration": 45,
    "motility_pr": 35,
    "motility_np": 20,
    "morphology": 4,
    "ph": 7.5,
    "liquefaction": 30
  },

  "diagnosis": "normospermia",

  "notes": "",
  "metadata": {
    "created_at": "2025-06-20T10:00:00.000Z"
  }
}
```

---

## 智能识别规则

### 精液参数识别

| 参数 | 关键词 | 提取 |
|------|--------|------|
| 精液量 | volume, 精液量, ml, 毫升 | 数字 + mL |
| 精子密度 | concentration, 密度, 10⁶/mL | 数字 |
| 前向运动 | pr, 前向运动, progressive | 百分比 |
| 形态 | morphology, 形态, % | 百分比 |
| pH | ph, 酸碱度 | 7.0-8.0 |

### 激素识别

| 激素 | 关键词 | 单位 |
|------|--------|------|
| 睾酮 | testosterone, 睾酮, T | nmol/L |
| LH | LH, 促黄体生成素 | IU/L |
| FSH | FSH, 促卵泡刺激素 | IU/L |
| 泌乳素 | PRL, 泌乳素 | ng/mL |
| 雌二醇 | E2, 雌二醇 | pg/mL |

---

## 错误处理

| 场景 | 错误消息 | 建议 |
|------|---------|------|
| 精子密度=0 | 无精症<br>建议进一步检查 | 转诊男性科 |
| 睾酮过低 | 睾酮显著偏低<br>建议内分泌科评估 | 检查垂体功能 |
| 泌乳素过高 | 高泌乳素血症<br>需进一步检查 | 检查垂体瘤 |

---

## 注意事项

- 本系统仅供生育健康追踪,不能替代专业医疗诊断
- 精液分析需2-3次确认
- 禁欲3-7天后检查
- 不育建议夫妻双方同时检查
- 特发性不育仍有自然受孕可能

**需要立即就医的情况:**
- 无精症
- 激素显著异常
- 精索静脉曲张III度
- 生殖道感染阳性

所有数据仅保存在本地,确保隐私安全。

---

## 示例用法

```
# 记录精液分析
/fertility semen volume 2.5
/fertility semen concentration 45
/fertility semen motility pr 35 np 20
/fertility semen morphology 4

# 记录激素
/fertility hormone testosterone 15.5
/fertility hormone lh 5.2

# 记录检查
/fertility varicocele none
/fertility infection chlamydia negative

# 查看状态
/fertility status
/fertility diagnosis
```
