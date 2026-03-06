#!/usr/bin/env python3
"""
测试更新后的MCP API
"""

import json
import time

def test_mcp_api():
    """测试MCP API"""
    print("测试 InvestmentTracker MCP API")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        {
            "name": "测试 tools/list",
            "data": {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 1
            }
        },
        {
            "name": "测试 resources/list",
            "data": {
                "jsonrpc": "2.0",
                "method": "resources/list",
                "params": {},
                "id": 2
            }
        },
        {
            "name": "测试 prompts/list",
            "data": {
                "jsonrpc": "2.0",
                "method": "prompts/list",
                "params": {},
                "id": 3
            }
        }
    ]
    
    print("生成的curl测试命令：")
    print()
    
    for i, test in enumerate(test_cases, 1):
        print(f"{i}. {test['name']}:")
        print("-" * 40)
        
        # 保存请求数据到文件
        data_file = f"/tmp/mcp_test_{i}.json"
        with open(data_file, 'w') as f:
            json.dump(test['data'], f)
        
        # 生成curl命令
        cmd = f"""curl -v -X POST \\
  'https://investmenttracker-ingest-production.up.railway.app/mcp' \\
  -H 'Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes' \\
  -H 'Accept: application/json, text/event-stream' \\
  -H 'Content-Type: application/json' \\
  --data-binary @{data_file} \\
  2>&1"""
        
        print(cmd)
        print()
    
    return test_cases

def create_working_client():
    """创建可工作的客户端示例"""
    print("\n" + "=" * 60)
    print("可工作的MCP客户端示例：")
    print("=" * 60)
    
    client_code = '''#!/usr/bin/env python3
import json
import requests
from typing import Dict, Any, Generator

class InvestmentTrackerClient:
    """InvestmentTracker MCP客户端"""
    
    def __init__(self, auth_token: str):
        self.base_url = "https://investmenttracker-ingest-production.up.railway.app/mcp"
        self.auth_token = auth_token
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }
    
    def send_request(self, method: str, params: Dict = None) -> Dict[str, Any]:
        """发送MCP请求"""
        request_id = int(time.time() * 1000)
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": request_id
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=request,
                timeout=30
            )
            
            print(f"状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                # 尝试解析JSON
                try:
                    return response.json()
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
                    print(f"响应内容: {response.text[:200]}...")
                    return {"error": "Invalid JSON response"}
            else:
                print(f"错误响应: {response.text}")
                return {"error": f"HTTP {response.status_code}"}
                
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
            return {"error": str(e)}
    
    def list_tools(self) -> Dict[str, Any]:
        """列出可用工具"""
        return self.send_request("tools/list")
    
    def list_resources(self) -> Dict[str, Any]:
        """列出可用资源"""
        return self.send_request("resources/list")
    
    def call_tool(self, tool_name: str, arguments: Dict = None) -> Dict[str, Any]:
        """调用工具"""
        return self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments or {}
        })

# 使用示例
if __name__ == "__main__":
    import time
    
    client = InvestmentTrackerClient(
        auth_token="it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
    )
    
    print("1. 测试连接...")
    print("-" * 40)
    
    # 测试 tools/list
    print("获取工具列表...")
    tools_result = client.list_tools()
    print(json.dumps(tools_result, indent=2, ensure_ascii=False))
    
    print("\\n2. 测试资源列表...")
    print("-" * 40)
    
    # 测试 resources/list
    resources_result = client.list_resources()
    print(json.dumps(resources_result, indent=2, ensure_ascii=False))
    
    print("\\n3. 如果工具可用，测试调用...")
    print("-" * 40)
    
    # 如果有工具，测试调用
    if tools_result and "result" in tools_result and "tools" in tools_result["result"]:
        tools = tools_result["result"]["tools"]
        if tools:
            first_tool = tools[0]
            print(f"测试调用工具: {first_tool.get('name')}")
            
            # 根据工具定义构建参数
            call_result = client.call_tool(
                first_tool["name"],
                arguments={}  # 根据实际工具定义添加参数
            )
            print(json.dumps(call_result, indent=2, ensure_ascii=False))
'''
    
    print(client_code)

def update_skill_implementation():
    """更新skill实现建议"""
    print("\n" + "=" * 60)
    print("Skill更新建议：")
    print("=" * 60)
    
    print("基于测试结果，需要更新以下文件：")
    print()
    
    print("1. scripts/fetch_data.py → 更新为正确的MCP客户端")
    print("   修改内容：")
    print("   - 使用正确的Accept头部：'application/json, text/event-stream'")
    print("   - 使用POST方法而不是GET")
    print("   - 实现JSON-RPC 2.0请求格式")
    print()
    
    print("2. SKILL.md → 更新使用说明")
    print("   添加：")
    print("   - 正确的API端点：POST /mcp")
    print("   - 必需的头部信息")
    print("   - JSON-RPC请求格式示例")
    print()
    
    print("3. config.json → 更新配置")
    print("   添加：")
    print("   - MCP协议版本")
    print("   - 必需的头部配置")
    print("   - 请求超时设置")
    print()
    
    print("4. 创建示例请求文件")
    print("   在examples/目录下添加：")
    print("   - mcp_request_examples.json")
    print("   - api_test_guide.md")

def main():
    """主函数"""
    print("InvestmentTracker MCP API 测试和优化")
    print("生成时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # 测试API
    test_cases = test_mcp_api()
    
    # 创建客户端示例
    create_working_client()
    
    # 提供更新建议
    update_skill_implementation()
    
    print("\n" + "=" * 60)
    print("立即测试命令：")
    print("=" * 60)
    
    print("运行以下命令测试API：")
    print()
    print("1. 测试 tools/list:")
    print("""curl -X POST \\
  'https://investmenttracker-ingest-production.up.railway.app/mcp' \\
  -H 'Authorization: Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes' \\
  -H 'Accept: application/json, text/event-stream' \\
  -H 'Content-Type: application/json' \\
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'""")
    
    print("\n2. 如果成功，更新skill实现")
    print("   根据API响应调整客户端实现")

if __name__ == "__main__":
    main()