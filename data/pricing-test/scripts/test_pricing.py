#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V3 API 价格计算测试脚本

运行方式：
    python test_pricing.py                    # 测试所有模型
    python test_pricing.py wan                # 测试 Wan 模型
    python test_pricing.py sora               # 测试 Sora 模型
    python test_pricing.py --model MODEL_ID   # 测试指定模型
"""

import requests
import json
import sys
from typing import Dict, Any, List

# 配置
BASE_URL = "http://127.0.0.1:8002"
API_KEY = "sk-df83fa5724454492be4dd3172d86425ecdbb9b64b143e7a3"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 测试图片
TEST_IMAGE_URL = "https://v3b.fal.media/files/b/0a8673dd/m9EV5W9aSqg8J7rb-18TK.png"

# ============ 测试用例配置 ============

TEST_CASES = {
    "wan": {
        "model_id": "wan/v2.6/image-to-video/flash",
        "name": "Wan 2.6 Flash",
        "price_rule": "720p: 20积分/秒, 1080p: 30积分/秒",
        "cases": [
            {"name": "5秒 720p", "params": {"prompt": "test", "image_url": TEST_IMAGE_URL, "duration": "5", "resolution": "720p"}, "expected": 100},
            {"name": "5秒 1080p", "params": {"prompt": "test", "image_url": TEST_IMAGE_URL, "duration": "5", "resolution": "1080p"}, "expected": 150},
            {"name": "10秒 720p", "params": {"prompt": "test", "image_url": TEST_IMAGE_URL, "duration": "10", "resolution": "720p"}, "expected": 200},
            {"name": "10秒 1080p", "params": {"prompt": "test", "image_url": TEST_IMAGE_URL, "duration": "10", "resolution": "1080p"}, "expected": 300},
            {"name": "15秒 720p", "params": {"prompt": "test", "image_url": TEST_IMAGE_URL, "duration": "15", "resolution": "720p"}, "expected": 300},
            {"name": "15秒 1080p", "params": {"prompt": "test", "image_url": TEST_IMAGE_URL, "duration": "15", "resolution": "1080p"}, "expected": 450},
        ]
    },
    "sora": {
        "model_id": "fal-ai/sora-2/image-to-video",
        "name": "Sora 2 图生视频",
        "price_rule": "40积分/秒",
        "cases": [
            {"name": "4秒视频", "params": {"prompt": "test", "image_url": TEST_IMAGE_URL, "duration": 4}, "expected": 160},
            {"name": "8秒视频", "params": {"prompt": "test", "image_url": TEST_IMAGE_URL, "duration": 8}, "expected": 320},
            {"name": "12秒视频", "params": {"prompt": "test", "image_url": TEST_IMAGE_URL, "duration": 12}, "expected": 480},
        ]
    },
    "sora-pro": {
        "model_id": "fal-ai/sora-2/image-to-video/pro",
        "name": "Sora 2 Pro 图生视频",
        "price_rule": "720p: 120积分/秒, 1080p: 200积分/秒",
        "cases": [
            {"name": "4秒 720p", "params": {"prompt": "test", "image_url": TEST_IMAGE_URL, "duration": 4, "resolution": "720p"}, "expected": 480},
            {"name": "4秒 1080p", "params": {"prompt": "test", "image_url": TEST_IMAGE_URL, "duration": 4, "resolution": "1080p"}, "expected": 800},
        ]
    },
}


def test_pricing_display(model_id: str) -> Dict[str, Any]:
    """测试定价信息展示"""
    url = f"{BASE_URL}/api/v3/models/{model_id}/docs"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        data = response.json()
        return data.get("data", {}).get("pricing", {})
    except Exception as e:
        return {"error": str(e)}


def test_task_create(model_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """测试任务创建和扣费"""
    url = f"{BASE_URL}/api/v3/tasks/create"
    payload = {"model": model_id, "params": params}
    try:
        response = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def print_separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def run_model_tests(model_key: str, config: Dict) -> bool:
    """运行单个模型的测试"""
    model_id = config["model_id"]
    model_name = config["name"]
    price_rule = config["price_rule"]
    test_cases = config["cases"]
    
    print_separator(f"{model_name} ({model_id})")
    print(f"\n  价格规则: {price_rule}")
    
    all_passed = True
    
    # 测试定价信息展示
    print(f"\n  📋 定价信息展示:")
    pricing = test_pricing_display(model_id)
    if "error" in pricing:
        print(f"    ❌ 获取失败: {pricing['error']}")
        all_passed = False
    else:
        price_type = pricing.get('price_type', 'N/A')
        print(f"    类型: {price_type}")
        print(f"    说明: {pricing.get('price_description', 'N/A')}")
        if price_type == "duration_price":
            print(f"    结果: ✅ PASS")
        else:
            print(f"    结果: ⚠️ 类型不是 duration_price")
    
    # 测试扣费
    print(f"\n  🧪 扣费测试:")
    for case in test_cases:
        result = test_task_create(model_id, case["params"])
        
        if result.get("code") == 200:
            actual = result["data"]["price"]
            expected = case["expected"]
            status = "✅" if actual == expected else "❌"
            if actual != expected:
                all_passed = False
            print(f"    {status} {case['name']}: 预期 {expected}, 实际 {actual}")
        else:
            error = result.get('detail', result.get('message', result.get('error', 'Unknown')))
            print(f"    ⚠️ {case['name']}: 请求失败 - {error}")
    
    return all_passed


def main():
    print("\n" + "="*60)
    print("  V3 API 价格计算测试")
    print("="*60)
    
    # 解析命令行参数
    args = sys.argv[1:]
    
    if args and args[0] == "--model":
        # 测试指定模型 ID
        if len(args) < 2:
            print("错误: 请指定模型 ID")
            sys.exit(1)
        model_id = args[1]
        pricing = test_pricing_display(model_id)
        print(f"\n模型: {model_id}")
        print(f"定价信息: {json.dumps(pricing, indent=2, ensure_ascii=False)}")
        sys.exit(0)
    
    # 确定要测试的模型
    if args:
        models_to_test = [k for k in args if k in TEST_CASES]
        if not models_to_test:
            print(f"可用的测试: {list(TEST_CASES.keys())}")
            sys.exit(1)
    else:
        models_to_test = list(TEST_CASES.keys())
    
    # 运行测试
    results = {}
    for model_key in models_to_test:
        config = TEST_CASES[model_key]
        results[model_key] = run_model_tests(model_key, config)
    
    # 汇总
    print_separator("测试结果汇总")
    all_passed = all(results.values())
    
    for model_key, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {TEST_CASES[model_key]['name']}: {status}")
    
    print()
    if all_passed:
        print("  ✅ 所有测试通过！")
    else:
        print("  ❌ 部分测试失败")
    
    print("\n" + "="*60 + "\n")
    
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
