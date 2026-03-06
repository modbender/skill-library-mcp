# 现有成熟脱敏方案调研

## 🎯 发现的成熟方案

### 1️⃣ Microsoft Presidio ⭐⭐⭐⭐⭐ (强烈推荐)

**GitHub**: https://github.com/microsoft/presidio

**描述**: 
> An open-source framework for detecting, redacting, masking, and anonymizing sensitive data (PII) across text, images, and structured data. Supports NLP, pattern matching, and customizable pipelines.

**特点**:
- ✅ **微软开源** - 企业级品质
- ✅ **多语言支持** - Python, Node.js
- ✅ **NLP 检测** - 使用 NLP 识别敏感信息（本地模型）
- ✅ **模式匹配** - 正则表达式
- ✅ **可定制管道** - 灵活的检测流程
- ✅ **支持多种数据类型** - 文本、图片、结构化数据
- ✅ **本地执行** - 不需要外部 API
- ✅ **活跃维护** - 2026 年 3 月还在更新

**检测能力**:
- 人名、地址、电话号码
- 邮箱、身份证号、信用卡号
- 密码、API Key、Token
- 医疗记录、金融数据
- 支持自定义检测器

**安装**:
```bash
pip install presidio-analyzer presidio-anonymizer
```

**使用示例**:
```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# 分析
analyzer = AnalyzerEngine()
results = analyzer.analyze(text="My phone number is 212-555-5555", language='en')

# 脱敏
anonymizer = AnonymizerEngine()
anonymized = anonymizer.anonymize(text="My phone number is 212-555-5555", analyzer_results=results)
```

**优势**:
- 🏆 业界标准，被广泛使用
- 🏆 基于 spaCy 的 NLP 模型（本地）
- 🏆 可扩展的检测器
- 🏆 支持多种脱敏策略（替换、掩码、泛化）

---

### 2️⃣ Private AI ⭐⭐⭐⭐

**GitHub**: https://github.com/privateai/deid-examples

**特点**:
- ✅ 专注于 PII 去标识化
- ✅ 支持 50+ 种语言
- ✅ 高精度检测
- ⚠️ 部分功能需要 API（有本地版本）

---

### 3️⃣ PromptMask ⭐⭐⭐⭐

**GitHub**: https://github.com/cxumol/promptmask

**描述**:
> Never give AI companies your secrets! A local LLM-based privacy filter for LLM users.

**特点**:
- ✅ **专为 LLM 设计** - 在发送给 AI 前脱敏
- ✅ **本地 LLM** - 使用小模型本地识别
- ✅ **Python 库** - 易于集成
- ✅ **OpenAI SDK 替代** - 可无缝替换

**使用示例**:
```python
from promptmask import MaskedOpenAI

# 替代标准 OpenAI 客户端
client = MaskedOpenAI()

# 自动脱敏后发送
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "My password is 123"}]
)
# 实际发送： "My password is [MASKED]"
```

**优势**:
- 🎯 专为 LLM 场景设计
- 🎯 本地执行
- 🎯 易于集成到现有流程

---

### 4️⃣ Greenmask ⭐⭐⭐

**GitHub**: https://github.com/GreenmaskIO/greenmask

**特点**:
- ✅ 数据库匿名化
- ✅ 合成数据生成
- ✅ Go 语言实现
- ⚠️ 主要针对数据库，不是实时消息

---

### 5️⃣ Benerator ⭐⭐⭐

**GitHub**: https://github.com/rapiddweller/rapiddweller-benerator-ce

**特点**:
- ✅ 数据生成和脱敏
- ✅ 模型驱动方法
- ✅ Java 实现
- ⚠️ 主要针对测试数据生成

---

## 🎯 推荐方案

### 最佳选择：Microsoft Presidio

**理由**:
1. ✅ **成熟度** - 微软出品，企业级
2. ✅ **本地执行** - 不需要外部 API
3. ✅ **NLP+ 规则** - 智能识别 + 正则
4. ✅ **活跃维护** - 持续更新
5. ✅ **Python 集成** - 易于与 OpenClaw 集成
6. ✅ **可定制** - 支持自定义检测器

---

## 🚀 集成方案

### 使用 Presidio 替代自定义正则

```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

class PresidioMasker:
    """使用 Microsoft Presidio 进行智能脱敏。"""
    
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        
        # 配置要检测的实体类型
        self.entities = [
            "PHONE_NUMBER",
            "EMAIL_ADDRESS",
            "CREDIT_CARD",
            "PERSON",
            "LOCATION",
            # 自定义
            "PASSWORD",
            "API_KEY",
            "CONNECTION_STRING"
        ]
    
    def mask(self, text: str, language='zh') -> tuple:
        """
        脱敏文本。
        
        Returns:
            (masked_text, replacements)
        """
        # 分析
        results = self.analyzer.analyze(
            text=text,
            language=language,
            entities=self.entities
        )
        
        # 脱敏
        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators={
                "DEFAULT": lambda x: f"[{x.entity_type}:{self._generate_id()}]",
                "PASSWORD": lambda x: f"[PASSWORD:{self._generate_id()}]",
                "API_KEY": lambda x: f"[API_KEY:{self._generate_id()}]"
            }
        )
        
        return anonymized.text, results
```

---

## 📋 实施步骤

### 阶段 1: 集成 Presidio

```bash
# 安装
pip install presidio-analyzer presidio-anonymizer

# 下载 NLP 模型（一次性）
python -m spacy download en_core_web_lg
python -m spacy download zh_core_web_sm
```

### 阶段 2: 替换现有脱敏器

```python
# 当前：sensitive_channel_masker.py
# 替换为使用 Presidio

from presidio_analyzer import AnalyzerEngine

class ChannelSensitiveMasker:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.mapping_store = SensitiveMappingStore()
    
    def mask_message(self, text: str):
        # 使用 Presidio 分析
        results = self.analyzer.analyze(text=text, language='zh')
        
        # 建立映射并脱敏
        # ...
```

### 阶段 3: 自定义检测器

```python
# 添加自定义检测器（针对特定格式）
from presidio_analyzer import PatternRecognizer

class APIKeyRecognizer(PatternRecognizer):
    def load_patterns(self):
        return [
            r"sk-[a-zA-Z0-9]{20,}",
            r"ghp_[a-zA-Z0-9]{36}",
            r"LTAI[a-zA-Z0-9]{12,}"
        ]
```

---

## 🎯 对比

| 方案 | 成熟度 | 本地执行 | NLP 支持 | 推荐度 |
|------|--------|---------|---------|--------|
| **Presidio** | ⭐⭐⭐⭐⭐ | ✅ | ✅ | ⭐⭐⭐⭐⭐ |
| **PromptMask** | ⭐⭐⭐⭐ | ✅ | ✅ (本地 LLM) | ⭐⭐⭐⭐ |
| **Private AI** | ⭐⭐⭐⭐ | ⚠️ 部分 | ✅ | ⭐⭐⭐ |
| **自定义正则** | ⭐⭐ | ✅ | ❌ | ⭐⭐ |

---

## 💡 建议

**采用 Microsoft Presidio 作为核心脱敏引擎**：

1. ✅ 成熟可靠 - 微软出品
2. ✅ 本地执行 - 隐私安全
3. ✅ NLP+ 规则 - 智能识别
4. ✅ 易于集成 - Python 库
5. ✅ 持续维护 - 长期支持

**保留现有映射表机制**：
- Presidio 负责**检测**
- 我们的映射表负责**存储和还原**
- 最佳组合！

---

*调研时间：2026-03-03*
