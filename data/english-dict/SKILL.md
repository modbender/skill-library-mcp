---
name: english-dict
description: English dictionary lookup tool. Query English words to get Chinese definitions and generate two example sentences. Use when user needs to look up English word meanings, get translations, or see example sentences for vocabulary learning.
---

# 英语词典 (English Dictionary)

查询英语单词的中文释义，并自动生成两个例句。

## 功能

- 🔍 查询英语单词释义
- 📝 输出中文翻译
- 💬 自动生成两个例句
- 🔊 显示音标和词性

## 使用方式

### 命令行查询

```bash
python3 scripts/dict.py <单词>
```

示例：
```bash
python3 scripts/dict.py hello
python3 scripts/dict.py python
python3 scripts/dict.py beautiful
```

### 输出格式

```
📚 HELLO
   音标: /həˈloʊ/
   词性: int./n.

📖 中文释义:
   1. 你好
   2. 喂
   3. 打招呼

💬 例句:
   1. Hello! It's so great to see you again!
      （中文翻译请自行理解或查询）
   2. Hello, could you help me with this?
      （中文翻译请自行理解或查询）
```

## 内置词库

当前包含以下基础词汇：
- hello, world, python, openclaw
- love, friend, work, study
- happy, beautiful

## 扩展配置

如需查询更多单词，建议配置外部词典API：

### 有道词典 API
```python
# 在 dict.py 中添加
import requests

def youdao_lookup(word):
    url = f"https://dict.youdao.com/jsonresult?q={word}"
    response = requests.get(url)
    return response.json()
```

### 牛津词典 API
需要在 https://developer.oxforddictionaries.com/ 申请 API Key

## 自定义词库

编辑脚本中的 `BASIC_DICT` 字典，添加新单词：

```python
BASIC_DICT = {
    "yourword": {
        "phonetic": "/pronunciation/",
        "meanings": ["意思1", "意思2"],
        "pos": "词性"
    }
}
```

## 例句生成

脚本根据词性自动选择合适的例句模板：
- 名词 (n.) → 描述事物
- 动词 (v.) → 描述动作
- 形容词 (adj.) → 描述特征
- 副词 (adv.) → 描述方式

## 注意事项

1. 当前使用内置基础词库，词汇量有限
2. 建议配置外部词典API以获取更全面的释义
3. 例句由模板生成，实际使用时应参考权威例句
