#!/usr/bin/env python3
"""
完整的 MCP API 调试客户端
"""

import json
import sys
import time

def debug_mcp_connection():
    """调试MCP连接"""
    print("=" * 70)
    print("InvestmentTracker MCP API 深度调试")
    print("=" * 70)
    
    # 测试不同的请求方法和参数
    test_cases = [
        {
            "name": "基本SSE连接测试",
            "method": "GET",
            "url": "https://investmenttracker-ingest-production.up.railway.app/mcp",
            "headers": {
                "Authorization": "Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes",
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache"
            },
            "data": None
        },
        {
            "name": "JSON-RPC tools/list",
            "method": "POST",
            "url": "https://investmenttracker-ingest-production.up.railway.app/mcp",
            "headers": {
                "Authorization": "Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes",
                "Accept": "text/event-stream",
                "Content-Type": "application/json",
                "Cache-Control": "no-cache"
            },
            "data": json.dumps({
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 1
            })
        },
        {
            "name": "JSON-RPC resources/list",
            "method": "POST",
            "url": "https://investmenttracker-ingest-production.up.railway.app/mcp",
            "headers": {
                "Authorization": "Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes",
                "Accept": "text/event-stream",
                "Content-Type": "application/json",
                "Cache-Control": "no-cache"
            },
            "data": json.dumps({
                "jsonrpc": "2.0",
                "method": "resources/list",
                "params": {},
                "id": 2
            })
        },
        {
            "name": "尝试REST风格端点",
            "method": "GET",
            "url": "https://investmenttracker-ingest-production.up.railway.app/mcp/tools",
            "headers": {
                "Authorization": "Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes",
                "Accept": "application/json"
            },
            "data": None
        }
    ]
    
    print("将使用curl命令测试以下场景：")
    print()
    
    for i, test in enumerate(test_cases, 1):
        print(f"{i}. {test['name']}")
        print(f"   方法: {test['method']}")
        print(f"   URL: {test['url']}")
        print(f"   头部: {json.dumps(test['headers'], indent=6)}")
        if test['data']:
            print(f"   数据: {test['data'][:100]}...")
        print()
    
    return test_cases

def generate_curl_commands(test_cases):
    """生成curl测试命令"""
    print("=" * 70)
    print("生成的curl测试命令：")
    print("=" * 70)
    
    commands = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}:")
        print("-" * 40)
        
        # 构建curl命令
        cmd = f"curl -v -X {test['method']} \\\n"
        cmd += f"  '{test['url']}' \\\n"
        
        # 添加头部
        for key, value in test['headers'].items():
            cmd += f"  -H '{key}: {value}' \\\n"
        
        # 添加数据
        if test['data']:
            # 将数据保存到临时文件
            data_file = f"/tmp/mcp_test_{i}.json"
            with open(data_file, 'w') as f:
                f.write(test['data'])
            cmd += f"  --data-binary @{data_file} \\\n"
        
        cmd += "  2>&1 | head -100"
        
        print(cmd)
        commands.append(cmd)
    
    return commands

def analyze_error_pattern():
    """分析错误模式"""
    print("\n" + "=" * 70)
    print("错误模式分析：")
    print("=" * 70)
    
    error = "Unterminated string in JSON at position 16738 (line 1 column 16739)"
    
    print(f"原始错误: {error}")
    print()
    
    print("可能的原因分析：")
    print("1. 位置分析:")
    print(f"   - 错误发生在第16738个字符处")
    print(f"   - 大约在第16739列")
    print(f"   - 这表明响应至少有16KB大小")
    print()
    
    print("2. 字符串未终止的可能原因:")
    print("   a) 缺少闭合引号")
    print("   b) 字符串中包含未转义的特殊字符")
    print("   c) 编码问题（非UTF-8字符）")
    print("   d) 响应被截断")
    print()
    
    print("3. 针对MCP SSE的特殊情况:")
    print("   a) SSE流格式错误")
    print("   b) 事件分隔符不正确")
    print("   c) 部分事件数据不完整")
    print("   d) 网络连接中断")
    print()
    
    print("4. 调试建议:")
    print("   a) 捕获完整的原始响应")
    print("   b) 检查第16738个字符附近的上下文")
    print("   c) 验证JSON语法")
    print("   d) 检查SSE事件格式")

def create_fix_suggestions():
    """创建修复建议"""
    print("\n" + "=" * 70)
    print("MCP API 技能修改建议：")
    print("=" * 70)
    
    suggestions = [
        {
            "优先级": "高",
            "修改点": "协议处理",
            "当前问题": "使用普通HTTP客户端处理SSE流",
            "建议方案": "实现专门的SSE/MCP客户端",
            "代码示例": """
class MCPSSEClient:
    def __init__(self, url, auth_token):
        self.url = url
        self.auth_token = auth_token
        self.session = None
    
    async def connect(self):
        # 使用aiohttp或专门的SSE库
        import aiohttp
        self.session = aiohttp.ClientSession()
        
        headers = {
            'Authorization': f'Bearer {self.auth_token}',
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache'
        }
        
        async with self.session.get(self.url, headers=headers) as resp:
            async for line in resp.content:
                # 处理SSE事件
                yield self._parse_sse_event(line)
            """
        },
        {
            "优先级": "高",
            "修改点": "错误处理",
            "当前问题": "尝试解析不完整的SSE流为JSON",
            "建议方案": "实现流式JSON解析和错误恢复",
            "代码示例": """
def parse_streaming_json(stream):
    \"\"\"解析流式JSON响应\"\"\"
    buffer = ""
    decoder = json.JSONDecoder()
    
    for chunk in stream:
        buffer += chunk
        try:
            # 尝试解析缓冲区中的完整JSON对象
            while buffer:
                obj, idx = decoder.raw_decode(buffer)
                yield obj
                buffer = buffer[idx:].lstrip()
        except json.JSONDecodeError:
            # 等待更多数据
            continue
            """
        },
        {
            "优先级": "中",
            "修改点": "请求格式",
            "当前问题": "可能使用了错误的JSON-RPC格式",
            "建议方案": "验证和调整JSON-RPC请求",
            "代码示例": """
# MCP标准请求格式
mcp_request = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {
        # 可能需要特定的参数
    },
    "id": "unique_request_id"
}
            """
        },
        {
            "优先级": "中",
            "修改点": "超时和重试",
            "当前问题": "SSE连接可能超时",
            "建议方案": "实现连接保持和自动重连",
            "代码示例": """
class ResilientMCPClient:
    def __init__(self, max_retries=3):
        self.max_retries = max_retries
    
    async def connect_with_retry(self):
        for attempt in range(self.max_retries):
            try:
                return await self._connect()
            except (TimeoutError, ConnectionError) as e:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # 指数退避
            """
        }
    ]
    
    for suggestion in suggestions:
        print(f"\n{suggestion['优先级']}优先级 - {suggestion['修改点']}:")
        print(f"  问题: {suggestion['当前问题']}")
        print(f"  方案: {suggestion['建议方案']}")
        print(f"  示例:\n{suggestion['代码示例']}")

def main():
    """主函数"""
    print("InvestmentTracker MCP API 调试报告")
    print("生成时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # 生成测试用例
    test_cases = debug_mcp_connection()
    
    # 生成curl命令
    commands = generate_curl_commands(test_cases)
    
    # 分析错误
    analyze_error_pattern()
    
    # 提供修改建议
    create_fix_suggestions()
    
    print("\n" + "=" * 70)
    print("下一步行动建议：")
    print("=" * 70)
    
    print("1. 立即测试:")
    print("   运行上面的curl命令，查看实际响应")
    print()
    
    print("2. 技能修改方向:")
    print("   a) 实现SSE客户端替代普通HTTP客户端")
    print("   b) 添加流式JSON解析")
    print("   c) 改进错误处理和重试机制")
    print()
    
    print("3. 备选方案:")
    print("   a) 寻找MCP客户端库（如@modelcontextprotocol/sdk）")
    print("   b) 联系API提供商获取正确示例")
    print("   c) 考虑使用WebSocket如果可用")
    print()
    
    print("4. 调试工具:")
    print("   保存完整响应到文件进行分析:")
    print("   curl ... > response.txt")
    print("   然后检查第16738个字符附近的内容")

if __name__ == "__main__":
    main()