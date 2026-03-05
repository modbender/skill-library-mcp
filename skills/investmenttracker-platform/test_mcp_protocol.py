#!/usr/bin/env python3
"""
测试 MCP (Model Context Protocol) API 连接
MCP 使用 JSON-RPC 2.0 over SSE (Server-Sent Events)
"""

import json
import time

def test_mcp_protocol():
    """测试MCP协议连接"""
    print("测试 MCP (Model Context Protocol) API...")
    print("=" * 60)
    
    # MCP 使用 JSON-RPC 2.0 协议
    # 典型的 MCP 请求格式
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 1
    }
    
    print("MCP 请求示例:")
    print(json.dumps(mcp_request, indent=2))
    print()
    
    print("已知的 MCP 方法:")
    print("1. tools/list - 列出可用工具")
    print("2. tools/call - 调用工具")
    print("3. resources/list - 列出资源")
    print("4. resources/read - 读取资源")
    print("5. prompts/list - 列出提示")
    print()
    
    print("由于这是 SSE 流式 API，需要使用专门的客户端。")
    print("常见的 MCP 客户端实现方式:")
    print("1. 使用 eventsource 库处理 SSE")
    print("2. 使用 websocket 连接（如果支持）")
    print("3. 使用专门的 MCP 客户端库")
    print()
    
    print("错误分析:")
    print("之前的 'Unterminated string in JSON' 错误可能是由于:")
    print("1. 尝试解析 SSE 流为完整的 JSON（SSE是流式数据）")
    print("2. 响应被截断或网络中断")
    print("3. 使用了错误的 HTTP 方法或头部")
    print()
    
    print("正确的 MCP SSE 请求应该包含:")
    print("Accept: text/event-stream")
    print("Cache-Control: no-cache")
    print("Connection: keep-alive")
    print()
    
    return True

def create_mcp_client_example():
    """创建MCP客户端示例代码"""
    print("MCP 客户端示例代码:")
    print("=" * 60)
    
    example_code = '''#!/usr/bin/env python3
import json
import requests
import sseclient

class MCPClient:
    def __init__(self, url, auth_token):
        self.url = url
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    
    def list_tools(self):
        """列出可用工具"""
        request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }
        
        # 对于SSE，通常需要POST请求
        response = requests.post(
            self.url,
            headers=self.headers,
            json=request,
            stream=True
        )
        
        if response.status_code == 200:
            # 使用SSE客户端处理流式响应
            client = sseclient.SSEClient(response)
            for event in client.events():
                if event.data:
                    try:
                        data = json.loads(event.data)
                        yield data
                    except json.JSONDecodeError:
                        print(f"无法解析事件数据: {event.data}")
        else:
            print(f"请求失败: {response.status_code}")
            print(response.text)

# 使用示例
if __name__ == "__main__":
    client = MCPClient(
        url="https://investmenttracker-ingest-production.up.railway.app/mcp",
        auth_token="it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
    )
    
    print("获取可用工具...")
    for tool in client.list_tools():
        print(json.dumps(tool, indent=2))
'''
    
    print(example_code)
    print()
    
    print("安装所需库:")
    print("pip install requests sseclient-py")
    print()

def check_current_issue():
    """检查当前遇到的问题"""
    print("问题诊断:")
    print("=" * 60)
    
    print("1. 错误信息: 'Unterminated string in JSON at position 16738'")
    print("   这表示在解析JSON时，在第16738个字符处字符串没有正确终止")
    print()
    
    print("2. 可能的原因:")
    print("   a) JSON响应被截断（网络问题）")
    print("   b) 字符串中包含未转义的特殊字符")
    print("   c) 引号不匹配")
    print("   d) 尝试解析SSE流为完整JSON")
    print()
    
    print("3. 基于测试结果:")
    print("   - API返回406错误：要求 Accept: text/event-stream")
    print("   - 这是MCP SSE API的典型行为")
    print("   - 需要使用SSE客户端而不是普通的HTTP客户端")
    print()
    
    print("4. 解决方案:")
    print("   a) 使用专门的MCP客户端库")
    print("   b) 实现SSE流处理")
    print("   c) 检查API文档了解正确的使用方法")
    print()

if __name__ == "__main__":
    test_mcp_protocol()
    print("\n" + "=" * 60 + "\n")
    check_current_issue()
    print("\n" + "=" * 60 + "\n")
    create_mcp_client_example()
    
    print("\n下一步建议:")
    print("1. 查看 InvestmentTracker 的 MCP API 文档")
    print("2. 使用正确的 MCP 客户端实现")
    print("3. 或者联系 API 提供商获取使用示例")
    print("4. 考虑使用现有的 MCP 客户端库，如:")
    print("   - @modelcontextprotocol/sdk (JavaScript)")
    print("   - mcp-client (Python)")
    print("   - 或自己实现 SSE 客户端")