---
name: wordcount
description: "Count lines, words, characters, and bytes of text or files. Supports CJK text. Use when: (1) counting words in a document, (2) checking file length, (3) estimating text size before sending to LLM."
version: 0.1.0
metadata:
  {
    "openclaw":
      {
        "emoji": "🔢",
        "requires": {},
        "install": [],
        "homepage": "https://github.com/tenglong/openclaw-skill-wordcount",
      },
  }
---

# WordCount

统计文本或文件的行数、词数、字符数和字节数。零依赖，纯 bash 实现。

## 调用方式

```bash
# 统计文件
{baseDir}/scripts/wordcount --file <文件路径>

# 统计文本
{baseDir}/scripts/wordcount --text "要统计的文本"

# 管道输入
cat document.txt | {baseDir}/scripts/wordcount
```

## 参数

| 参数 | 必须 | 说明 |
|------|:---:|------|
| `--file` | 三选一 | 从文件读取 |
| `--text` | 三选一 | 直接传入文本 |
| stdin | 三选一 | 通过管道传入 |

## 输出

JSON 格式：

```json
{
  "lines": 42,
  "words": 386,
  "characters": 2048,
  "bytes": 4096
}
```

## 示例

```bash
# 统计一个文件
{baseDir}/scripts/wordcount --file /path/to/document.txt

# 统计一段文字
{baseDir}/scripts/wordcount --text "Hello World 你好世界"

# 管道输入
echo "测试文本" | {baseDir}/scripts/wordcount
```

## Agent 决策原则

- 用户问"多少字"、"多长"、"字数"等关键词时自动调用
- 直接返回 JSON 结果，附上简要中文说明
- 对于中文文本，`characters` 更能反映实际字数；`words` 按空格分词，对中文不够准确，应提示用户
