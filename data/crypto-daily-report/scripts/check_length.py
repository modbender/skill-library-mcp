#!/usr/bin/env python3
"""
Telegram 消息字数检查工具
用法：python3 check_length.py  （从 stdin 读取）
     echo "消息内容" | python3 check_length.py

Telegram 限制：4096 字符（UTF-16 code units）
建议控制在 3800 以内，留200字符余量
"""
import sys

LIMIT = 4096
WARN_THRESHOLD = 3800

def count_telegram_chars(text):
    """Telegram 按 UTF-16 code units 计算，emoji/汉字约占1-2个单位"""
    count = 0
    for ch in text:
        cp = ord(ch)
        if cp > 0xFFFF:  # 需要代理对的字符（部分emoji）算2个
            count += 2
        else:
            count += 1
    return count

text = sys.stdin.read()
length = count_telegram_chars(text)
pct = length / LIMIT * 100

status = "✅ 安全" if length <= WARN_THRESHOLD else ("⚠️ 接近上限" if length <= LIMIT else "❌ 超出上限")
print(f"{status} | {length}/{LIMIT} 字符 ({pct:.1f}%)")

if length > WARN_THRESHOLD:
    print(f"需要压缩约 {length - WARN_THRESHOLD} 字符")
    # 找出最长的段落帮助定位
    paragraphs = text.split('\n\n')
    long_paras = sorted([(len(p), p[:60]) for p in paragraphs], reverse=True)[:3]
    print("最长段落：")
    for n, p in long_paras:
        print(f"  {n}字: {p}...")
