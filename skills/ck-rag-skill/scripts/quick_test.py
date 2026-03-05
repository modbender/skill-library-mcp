#!/usr/bin/env python3
"""
RAGFlow API 快速测试脚本
用于诊断API连接和基本功能
"""

import sys
import json
import requests
from time import time

# RAGFlow API配置
API_URL = "http://172.28.20.46:30001/v1/conversation/completion"
AUTHORIZATION = "IjQxYThhZGYyMDZlYjExZjFhZDE1ODJkYzljOWQ1YmJmIg.aYvfEw.ElppYHks0F5ETowUlvqA1Th-XHE"
COOKIE = "session=.elxVyzOegCAMAMC_dHagCgh8hIDaRleQyfh3jYmD4w13Qh5dWt4ZEizixBmNxgsbKkbknKkcxcy43siB/MyNqkb5CONuTR2yyWQKbarxVe7a9dNywRHnEaYvfEw66dir-0J0wYtii0IOGJ11861RtRtxp4"
CONVERSATION_ID = "0e18393f0b6042f2bbf6b391c82835d1"

def test_connection():
    """测试API连接"""
    print("=" * 60)
    print("测试1: API连接性")
    print("=" * 60)

    try:
        response = requests.head(API_URL, timeout=5)
        print(f"✓ API可达")
        print(f"  状态码: {response.status_code}")
        print(f"  Server: {response.headers.get('Server', 'N/A')}")
        return True
    except requests.exceptions.Timeout:
        print(f"✗ API连接超时 (>5秒)")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"✗ API连接失败")
        print(f"  错误: {e}")
        return False
    except Exception as e:
        print(f"✗ 未知错误: {e}")
        return False

def test_simple_query():
    """测试简单查询（预期快速响应）"""
    print("\n" + "=" * 60)
    print("测试2: 简单查询 '你好'")
    print("=" * 60)

    payload = {
        "conversation_id": CONVERSATION_ID,
        "messages": [
            {
                "content": "你好",
                "role": "user"
            }
        ]
    }

    headers = {
        "Authorization": AUTHORIZATION,
        "Content-Type": "application/json",
        "Cookie": COOKIE
    }

    start_time = time()

    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            stream=True,
            timeout=60
        )

        print(f"  状态码: {response.status_code}")
        print(f"  开始接收数据...")

        lines_count = 0
        chunks = 0
        for line in response.iter_lines(decode_unicode=True):
            lines_count += 1
            if line.startswith('data:'):
                chunks += 1
                print(f".", end="", flush=True)

            # 10秒后中断
            if time() - start_time > 10:
                print(f"\n  警告: 10秒超时，停止接收")
                break

        duration = time() - start_time
        print(f"\n  完成! 耗时: {duration:.2f}秒, 处理行数: {lines_count}, 数据块: {chunks}")
        return True

    except Exception as e:
        print(f"\n  ✗ 查询失败: {e}")
        return False

def test_network():
    """测试网络延迟"""
    print("\n" + "=" * 60)
    print("测试3: 网络延迟")
    print("=" * 60)

    import socket

    try:
        host = "172.28.20.46"
        port = 30001
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)

        start_time = time()
        result = sock.connect_ex((host, port))
        duration = (time() - start_time) * 1000

        sock.close()

        if result == 0:
            print(f"✓ 端口连接成功")
            print(f"  延迟: {duration:.1f}ms")
            return True
        else:
            print(f"✗ 端口连接失败 (错误码: {result})")
            return False

    except socket.timeout:
        print(f"✗ 连接超时 (>2秒)")
        return False
    except Exception as e:
        print(f"✗ 网络测试失败: {e}")
        return False

def main():
    print("\n🔍 RAGFlow API 诊断工具")
    print("")

    results = []

    # 运行测试
    results.append(("API连接", test_connection()))
    results.append(("网络延迟", test_network()))
    results.append(("简单查询", test_simple_query()))

    # 汇总
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:15s} {status}")

    # 建议
    all_passed = all(r[1] for r in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过！API工作正常。")
    else:
        print("❌ 存在问题，建议检查：")
        failed_tests = [r[0] for r in results if not r[1]]
        for test in failed_tests:
            if test == "API连接":
                print("  - 检查RAGFlow服务是否启动")
                print("  - 检查防火墙规则")
                print("  - 确认API地址正确")
            elif test == "网络延迟":
                print("  - 检查网络连接")
                print("  - 尝试ping服务器")
            elif test == "简单查询":
                print("  - 检查认证信息（token/cookie）")
                print("  - 查看RAGFlow服务日志")

if __name__ == "__main__":
    main()
