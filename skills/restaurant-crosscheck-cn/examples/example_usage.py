#!/usr/bin/env python3
"""Example usage of the Restaurant Review Cross-Check skill."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from crosscheck import RestaurantCrossChecker

def main():
    """Run example search."""
    print("=" * 70)
    print("餐厅推荐交叉验证示例")
    print("=" * 70)
    print()

    # Example 1: Japanese cuisine in Jing'an District, Shanghai
    print("示例 1: 上海静安区日式料理\n")
    checker = RestaurantCrossChecker()
    results = checker.search("上海静安区", "日式料理")
    output = checker.format_output(results, "上海静安区", "日式料理")
    print(output)

    # Example 2: Hot pot in Chaoyang District, Beijing
    print("\n" + "=" * 70)
    print("示例 2: 北京朝阳区火锅\n")
    results2 = checker.search("北京朝阳区", "火锅")
    output2 = checker.format_output(results2, "北京朝阳区", "火锅")
    print(output2)

if __name__ == "__main__":
    main()
