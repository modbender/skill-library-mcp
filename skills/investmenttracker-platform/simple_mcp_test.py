#!/usr/bin/env python3
"""
简单的 MCP SSE 测试
使用基本的SSE处理，不依赖外部库
"""

import json
import requests
import time

def simple_sse_test():
    """简单的SSE测试"""
    url = "https://investmenttracker-ingest-production.up.railway.app/mcp"
    headers = {
        "Authorization": "Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes",
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive"
    }
    
    # MCP 请求：列出可用工具
    request_data = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 1
    }
    
    print("发送 MCP 请求...")
    print(f"URL: {url}")
    print(f"请求: {json.dumps(request_data, indent=2)}")
    print()
    
    try:
        # 发送POST请求，启用流式响应
        response = requests.post(
            url,
            headers=headers,
            json=request_data,
            stream=True,
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print()
        
        if response.status_code != 200:
            print(f"错误响应: {response.text}")
            return
        
        print("开始接收SSE流...")
        print("-" * 60)
        
        # 简单的SSE解析
        buffer = ""
        event_count = 0
        
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk:
                buffer += chunk
                
                # 处理SSE事件（以\n\n分隔）
                while "\n\n" in buffer:
                    event, buffer = buffer.split("\n\n", 1)
                    
                    # 跳过空行和注释
                    if not event.strip() or event.startswith(":"):
                        continue
                    
                    event_count += 1
                    print(f"事件 #{event_count}:")
                    
                    # 解析SSE事件字段
                    lines = event.strip().split("\n")
                    for line in lines:
                        if line.startswith("data: "):
                            data = line[6:]  # 移除"data: "前缀
                            print(f"  数据: {data[:200]}..." if len(data) > 200 else f"  数据: {data}")
                            
                            # 尝试解析JSON
                            try:
                                if data.strip():
                                    json_data = json.loads(data)
                                    print(f"  JSON解析成功: {json.dumps(json_data, indent=2)[:200]}...")
                            except json.JSONDecodeError as e:
                                print(f"  JSON解析失败: {e}")
                                print(f"  数据长度: {len(data)}")
                                if len(data) > 50:
                                    print(f"  数据片段: {data[:50]}...")
                    
                    print()
                    
                    # 只显示前5个事件
                    if event_count >= 5:
                        print("已显示5个事件，停止接收...")
                        response.close()
                        break
        
        print(f"总共接收到 {event_count} 个事件")
        
        if event_count == 0:
            print("未接收到任何SSE事件")
            print("缓冲区内容:")
            print(buffer[:500])
        
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    except Exception as e:
        print(f"其他异常: {e}")

def test_different_methods():
    """测试不同的MCP方法"""
    print("\n" + "=" * 60)
    print("测试不同的 MCP 方法")
    print("=" * 60)
    
    methods = [
        {"method": "tools/list", "params": {}, "description": "列出可用工具"},
        {"method": "resources/list", "params": {}, "description": "列出可用资源"},
        {"method": "prompts/list", "params": {}, "description": "列出可用提示"},
    ]
    
    for i, method_info in enumerate(methods, 1):
        print(f"\n{i}. {method_info['description']} ({method_info['method']})")
        print("-" * 40)
        
        # 这里可以添加实际的测试代码
        # 由于是示例，只显示方法信息
        request = {
            "jsonrpc": "2.0",
            "method": method_info["method"],
            "params": method_info["params"],
            "id": i
        }
        print(f"请求: {json.dumps(request)}")

if __name__ == "__main__":
    print("InvestmentTracker MCP SSE 测试")
    print("=" * 60)
    
    simple_sse_test()
    test_different_methods()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("\n如果遇到 'Unterminated string in JSON' 错误，可能是由于:")
    print("1. SSE流被截断")
    print("2. 网络连接不稳定")
    print("3. API响应格式不符合SSE规范")
    print("4. 需要更完整的SSE客户端实现")
    print("\n建议使用专门的MCP客户端库或完整的SSE实现。")