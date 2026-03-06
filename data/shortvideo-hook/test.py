#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试脚本"""

import sys
import io

# 修复 Windows 编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from main import main

print("=" * 60)
print("🎬 短视频黄金 3 秒钩子生成器 - 功能测试")
print("=" * 60)

# 测试 1：基础生成
print("\n【测试 1】基础生成 - AI 工具教程")
print("-" * 60)
result = main("生成", {"topic": "AI 工具教程"})
print(result)

# 测试 2：指定类型
print("\n\n【测试 2】指定类型 - 痛点型")
print("-" * 60)
result = main("生成", {"topic": "电商带货", "类型": "痛点型"})
print(result)

# 测试 3：指定平台
print("\n\n【测试 3】指定平台 - 小红书")
print("-" * 60)
result = main("生成", {"topic": "美妆教程", "平台": "小红书"})
print(result)

# 测试 4：查看类型
print("\n\n【测试 4】查看钩子类型")
print("-" * 60)
result = main("类型", {})
print(result)

# 测试 5：查看统计
print("\n\n【测试 5】查看使用统计")
print("-" * 60)
result = main("统计", {})
print(result)

# 测试 6：付费版说明
print("\n\n【测试 6】付费版说明")
print("-" * 60)
result = main("升级", {})
print(result)

print("\n" + "=" * 60)
print("✅ 全部测试完成！")
print("=" * 60)
