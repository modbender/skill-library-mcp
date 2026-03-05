#!/usr/bin/env python3
"""
QST Memory Auto-Tagging: Automatically detect and tag memory importance.
"""
import re
from datetime import datetime

# Patterns for automatic importance detection
CRITICAL_PATTERNS = [
    r"記住.*",
    r"記得.*",
    r"這點很重要",
    r"配置.*",
    r"設定.*",
    r"系統.*",
    r"偏好.*",
    r"不喜歡.*",
    r"always.*",
    r"never.*",
    r"always",
    r"never",
]

IMPORTANT_PATTERNS = [
    r"專案.*",
    r"project.*",
    r"待辦.*",
    r"todo.*",
    r"記得.*",
    r"提醒.*",
    r"約定.*",
    r"下次.*",
    r"應該.*",
    r"需要.*",
]

NORMAL_PATTERNS = [
    r"你好.*",
    r"再見.*",
    r"拜拜.*",
    r"thanks?.*",
    r"謝謝.*",
    r"只是.*",
    r"沒什麼.*",
]


def detect_importance(content: str) -> str:
    """
    Detect importance level from content.
    Returns: '[C]', '[I]', or '[N]'
    """
    content_lower = content.lower()

    # Check critical patterns first
    for pattern in CRITICAL_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return "[C]"

    # Check important patterns
    for pattern in IMPORTANT_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return "[I]"

    # Check if it's normal/ casual
    for pattern in NORMAL_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return "[N]"

    # Default to important if uncertain (prefer remembering)
    return "[I]"


def tag_memory(content: str, source: str = "auto") -> str:
    """
    Tag memory with importance level.
    """
    weight = detect_importance(content)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    return f"{weight} ({timestamp}, {source})\n{content}"


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        content = " ".join(sys.argv[1:])
        tagged = tag_memory(content)
        print(tagged)
    else:
        # Interactive mode
        print("Enter memory content (Ctrl+D to finish):")
        content = sys.stdin.read().strip()
        if content:
            print("\nTagged:")
            print(tag_memory(content))
