#!/usr/bin/env python3
"""
英语词典查询工具
支持查询单词释义并生成例句
"""

import json
import sys
import re

# 内置基础词典（常用词汇）
BASIC_DICT = {
    "hello": {
        "phonetic": "/həˈloʊ/",
        "meanings": ["你好", "喂", "打招呼"],
        "pos": "int./n."
    },
    "world": {
        "phonetic": "/wɜːrld/",
        "meanings": ["世界", "地球", "领域"],
        "pos": "n."
    },
    "python": {
        "phonetic": "/ˈpaɪθɑːn/",
        "meanings": ["蟒蛇", "Python编程语言"],
        "pos": "n."
    },
    "openclaw": {
        "phonetic": "/ˈoʊpənklɔː/",
        "meanings": ["OpenClaw（AI助手框架）"],
        "pos": "n."
    },
    "love": {
        "phonetic": "/lʌv/",
        "meanings": ["爱", "爱情", "热爱"],
        "pos": "v./n."
    },
    "friend": {
        "phonetic": "/frend/",
        "meanings": ["朋友", "伙伴"],
        "pos": "n."
    },
    "work": {
        "phonetic": "/wɜːrk/",
        "meanings": ["工作", "劳动", "作品"],
        "pos": "v./n."
    },
    "study": {
        "phonetic": "/ˈstʌdi/",
        "meanings": ["学习", "研究", "书房"],
        "pos": "v./n."
    },
    "happy": {
        "phonetic": "/ˈhæpi/",
        "meanings": ["快乐的", "幸福的", "满意的"],
        "pos": "adj."
    },
    "beautiful": {
        "phonetic": "/ˈbjuːtɪfl/",
        "meanings": ["美丽的", "漂亮的", "出色的"],
        "pos": "adj."
    }
}

# 例句模板（按词性分类）
SENTENCE_TEMPLATES = {
    "n.": [
        "I really enjoy learning about {word} every day.",
        "The concept of {word} has changed my perspective.",
        "Many people don't fully understand what {word} means.",
        "In my opinion, {word} is essential for success.",
        "Have you ever thought about the importance of {word}?"
    ],
    "v.": [
        "Every morning, I {word} to start my day right.",
        "You need to {word} harder if you want to succeed.",
        "It's important to {word} with passion and dedication.",
        "She decided to {word} after thinking it over.",
        "Learning to {word} well takes time and practice."
    ],
    "adj.": [
        "This is the most {word} thing I've seen today.",
        "I feel so {word} when I'm with my family.",
        "The weather today is absolutely {word}.",
        "She has a very {word} personality that everyone likes.",
        "Finding something {word} in everyday life is important."
    ],
    "adv.": [
        "He spoke {word} about his future plans.",
        "Please listen {word} to what I'm saying.",
        "The project was completed {word} ahead of schedule.",
        "She {word} understood the assignment.",
        "Things are going {word} better than expected."
    ],
    "int.": [
        "{word}! It's so great to see you again!",
        "{word}, could you help me with this?",
        "Everyone shouted '{word}!' at the celebration.",
        "{word}, I didn't expect to meet you here!",
        "Saying '{word}' with a smile makes people happy."
    ],
    "default": [
        "Understanding {word} can improve your English significantly.",
        "The word '{word}' is commonly used in daily conversation.",
        "Many students find {word} difficult at first, but it gets easier.",
        "Using '{word}' correctly shows your language proficiency.",
        "I learned about {word} when I first started studying English."
    ]
}


def get_templates(pos):
    """根据词性获取例句模板"""
    pos_lower = pos.lower()
    for key in SENTENCE_TEMPLATES:
        if key in pos_lower:
            return SENTENCE_TEMPLATES[key]
    return SENTENCE_TEMPLATES["default"]


def generate_sentences(word, pos, meaning):
    """生成例句"""
    import random
    templates = get_templates(pos)
    selected = random.sample(templates, min(2, len(templates)))
    sentences = []
    for template in selected:
        sentence = template.format(word=word)
        sentences.append(sentence)
    return sentences


def lookup_word(word):
    """查询单词"""
    word_lower = word.lower().strip()
    
    # 先查内置词典
    if word_lower in BASIC_DICT:
        entry = BASIC_DICT[word_lower]
        sentences = generate_sentences(word_lower, entry.get("pos", ""), entry["meanings"][0])
        return {
            "word": word,
            "phonetic": entry.get("phonetic", ""),
            "pos": entry.get("pos", ""),
            "meanings": entry["meanings"],
            "sentences": sentences,
            "source": "basic"
        }
    
    # 如果没有找到，返回模拟数据（实际使用时应调用外部API）
    return {
        "word": word,
        "phonetic": f"/{word_lower}/",
        "pos": "unknown",
        "meanings": [f"【{word}】（建议使用外部词典API获取完整释义）"],
        "sentences": [
            f"I'm learning the word '{word}' today.",
            f"Can you explain what '{word}' means in this context?"
        ],
        "source": "fallback",
        "note": "建议使用有道词典、牛津词典等API获取完整数据"
    }


def format_output(result):
    """格式化输出"""
    word = result["word"]
    phonetic = result.get("phonetic", "")
    pos = result.get("pos", "")
    meanings = result.get("meanings", [])
    sentences = result.get("sentences", [])
    
    output = []
    output.append(f"📚 {word.upper()}")
    if phonetic:
        output.append(f"   音标: {phonetic}")
    if pos:
        output.append(f"   词性: {pos}")
    
    output.append("")
    output.append("📖 中文释义:")
    for i, meaning in enumerate(meanings, 1):
        output.append(f"   {i}. {meaning}")
    
    if sentences:
        output.append("")
        output.append("💬 例句:")
        for i, sentence in enumerate(sentences, 1):
            output.append(f"   {i}. {sentence}")
            # 添加中文翻译提示
            output.append(f"      （中文翻译请自行理解或查询）")
    
    if result.get("source") == "fallback":
        output.append("")
        output.append("⚠️ 提示: 该单词不在基础词库中，建议配置外部词典API")
    
    return "\n".join(output)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python dict.py <单词>")
        print("示例: python dict.py hello")
        print("      python dict.py python")
        return
    
    word = sys.argv[1]
    result = lookup_word(word)
    print(format_output(result))
    
    # 同时输出JSON格式（便于程序处理）
    print("\n---JSON---")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
