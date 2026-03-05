# Logic-Hunter 测试用例

## 测试结果 (2026-03-02)

### ✅ 测试 1: 置信度计算
**输入**:
```python
evidence = [
    {'type': 'primary', 'count': 2},
    {'type': 'secondary', 'count': 3},
    {'type': 'tertiary', 'count': 1}
]
```
**输出**: `置信度 = 0.99`  
**状态**: ✅ 通过

---

### ✅ 测试 2: 红队攻击
**假设**: "AI 将在 2030 年取代所有程序员"  
**证据**: `['某博客文章']`  
**输出**:
- 孤证风险：结论高度依赖单一路径
- 信源单一：所有证据来自同一类型信源
- 缺乏一手信源：结论无官方/学术/原始数据支撑

**状态**: ✅ 通过

---

### ✅ 测试 3: 信源分类
| URL | 预期 | 实际 | 状态 |
|-----|------|------|------|
| gov.cn | primary | primary | ✅ |
| arxiv.org | primary | primary | ✅ |
| twitter.com | tertiary | tertiary | ✅ |
| news.example.com | secondary | secondary | ✅ |

**状态**: ✅ 通过

---

### ✅ 测试 4: 熵因子计算
**输入**:
```python
factors = {
    'conflict_of_interest': True,
    'semantic_drift': True,
    'time_sensitivity': False,
    'emotional_language': True
}
```
**输出**: `熵因子 = 2.2`  
**状态**: ✅ 通过

---

### ✅ 测试 5: 完整报告生成
**假设**: "AI 将在 2030 年取代所有程序员"  
**证据**: 2 个二手信源 + 3 个三手信源  
**熵因子**: 利益相关 + 语义漂移 = 2.0  

**输出**:
```json
{
  "hypothesis": "AI 将在 2030 年取代所有程序员",
  "confidence": 0.9,
  "entropy": 2.0,
  "source_stats": {"secondary": 2, "tertiary": 3},
  "vulnerabilities": ["缺乏一手信源：结论无官方/学术/原始数据支撑"],
  "evidence_count": 5
}
```

**状态**: ✅ 通过

---

## 运行测试

```bash
cd ~/.openclaw/workspace/skills/logic-hunter
python3 logic_engine.py test
```

或运行完整测试：

```bash
python3 -m pytest test_logic_engine.py -v
```

---

## 性能基准

| 操作 | 耗时 |
|------|------|
| 置信度计算 | <1ms |
| 红队攻击 | <5ms |
| 信源分类 | <1ms |
| 完整报告生成 | <10ms |

---

*最后更新：2026-03-02*
