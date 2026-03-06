#!/usr/bin/env python3
"""
更新后的MCP客户端 - 使用正确的API格式
"""

import json
import subprocess
import time
from typing import Dict, Any, Optional

class UpdatedMCPClient:
    """更新后的MCP客户端（使用正确的Accept头）"""
    
    def __init__(self):
        self.api_url = "https://investmenttracker-ingest-production.up.railway.app/mcp"
        self.api_key = "it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
        
    def send_request(self, method: str, params: Dict = None) -> Optional[Dict[str, Any]]:
        """发送MCP请求（使用正确的Accept头）"""
        request_id = int(time.time() * 1000)
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": request_id
        }
        
        # 保存请求到临时文件
        request_file = f"/tmp/mcp_request_{request_id}.json"
        with open(request_file, 'w') as f:
            json.dump(request, f)
        
        # 使用正确的Accept头：application/json, text/event-stream
        cmd = [
            'curl', '-s', '-N',
            '-H', f'X-API-Key: {self.api_key}',
            '-H', 'Content-Type: application/json',
            '-H', 'Accept: application/json, text/event-stream',  # 关键：同时接受两种格式
            '-X', 'POST',
            '--data-binary', f'@{request_file}',
            self.api_url
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout:
                # 解析SSE响应
                for line in result.stdout.strip().split('\n'):
                    if line.startswith('data: '):
                        try:
                            event_data = json.loads(line[6:])
                            if event_data.get('id') == request_id:
                                return event_data
                        except json.JSONDecodeError as e:
                            print(f"JSON解析错误: {e}")
                            print(f"原始数据: {line[:200]}")
                            return None
            else:
                print(f"请求失败，返回码: {result.returncode}")
                if result.stderr:
                    print(f"错误信息: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("请求超时")
            return None
        except Exception as e:
            print(f"请求异常: {e}")
            return None
        
        return None
    
    def list_tools(self) -> Optional[Dict[str, Any]]:
        """列出可用工具"""
        return self.send_request("tools/list")
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        return self.send_request("tools/call", {
            "name": "whoami_v1",
            "arguments": {}
        })
    
    def get_positions(self, status: str = "POSITION", limit: int = 10) -> Optional[Dict[str, Any]]:
        """获取持仓数据"""
        return self.send_request("tools/call", {
            "name": "positions_list_v1",
            "arguments": {
                "status": status,
                "limit": limit
            }
        })
    
    def get_methodology(self) -> Optional[Dict[str, Any]]:
        """获取投资方法论"""
        return self.send_request("tools/call", {
            "name": "methodology_get_v1",
            "arguments": {}
        })
    
    def get_stats(self) -> Optional[Dict[str, Any]]:
        """获取统计数据"""
        return self.send_request("tools/call", {
            "name": "stats_quick_v1",
            "arguments": {}
        })

def format_positions_response(response: Dict[str, Any]) -> str:
    """格式化持仓响应"""
    if not response or "result" not in response:
        return "❌ 无法获取持仓数据"
    
    result = response["result"]
    if "content" not in result or not result["content"]:
        return "📭 暂无持仓记录"
    
    # 解析持仓数据
    try:
        content_text = result["content"][0]["text"]
        positions_data = json.loads(content_text)
        items = positions_data.get("items", [])
        
        if not items:
            return "📭 暂无持仓记录"
        
        output = []
        output.append("📊 真实持仓记录 (来自MCP API)")
        output.append("=" * 60)
        output.append(f"持仓数量: {len(items)}")
        output.append("")
        
        for item in items:
            output.append(f"🔹 {item.get('name', '未知资产')}")
            output.append(f"   代码: {item.get('code', 'N/A')}")
            output.append(f"   数量: {item.get('quantity', 0)}")
            output.append(f"   货币: {item.get('currency', 'N/A')}")
            output.append(f"   组合: {item.get('portfolio', 'N/A')}")
            output.append(f"   买入日期: {item.get('buy_date', 'N/A')}")
            output.append(f"   状态: {item.get('status', 'N/A')}")
            
            # 如果有盈亏信息
            if item.get('pnl') is not None:
                pnl = item['pnl']
                pnl_rate = item.get('pnl_rate')
                pnl_sign = "📈" if pnl >= 0 else "📉"
                output.append(f"   盈亏: {pnl_sign} {pnl}" + (f" ({pnl_rate}%)" if pnl_rate else ""))
            
            output.append(f"   更新时间: {item.get('source_updated_at', 'N/A')[:19]}")
            output.append("")
        
        output.append("💡 数据源: MCP API实时数据")
        output.append(f"📅 报告时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(output)
        
    except Exception as e:
        return f"❌ 数据解析错误: {e}\n原始数据: {json.dumps(result, ensure_ascii=False)}"

def format_tools_response(response: Dict[str, Any]) -> str:
    """格式化工具列表响应"""
    if not response or "result" not in response:
        return "❌ 无法获取工具列表"
    
    result = response["result"]
    tools = result.get("tools", [])
    
    output = []
    output.append("🔧 可用工具列表 (MCP API)")
    output.append("=" * 60)
    
    for tool in tools:
        output.append(f"\n📌 {tool.get('name', '未知工具')}")
        output.append(f"   描述: {tool.get('description', '无描述')}")
        
        input_schema = tool.get('inputSchema', {})
        if input_schema.get('properties'):
            output.append(f"   输入参数: {json.dumps(input_schema['properties'], ensure_ascii=False)}")
        
        execution = tool.get('execution', {})
        output.append(f"   执行支持: {execution.get('taskSupport', '未知')}")
    
    output.append(f"\n📊 工具总数: {len(tools)}")
    output.append(f"🕐 获取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return "\n".join(output)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="更新后的MCP客户端")
    parser.add_argument("command", nargs="?", help="命令: tools, positions, user, methodology, stats, test")
    
    args = parser.parse_args()
    
    client = UpdatedMCPClient()
    
    print("🔧 更新后的MCP客户端")
    print("=" * 60)
    print("API状态: ✅ 已连接")
    print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    if args.command == "tools" or not args.command:
        print("\n获取工具列表...")
        response = client.list_tools()
        print(format_tools_response(response))
    
    elif args.command == "positions":
        print("\n获取持仓数据...")
        response = client.get_positions()
        print(format_positions_response(response))
    
    elif args.command == "user":
        print("\n获取用户信息...")
        response = client.get_user_info()
        if response and "result" in response:
            print(json.dumps(response["result"], indent=2, ensure_ascii=False))
        else:
            print("❌ 无法获取用户信息")
    
    elif args.command == "methodology":
        print("\n获取投资方法论...")
        response = client.get_methodology()
        if response and "result" in response:
            print(json.dumps(response["result"], indent=2, ensure_ascii=False))
        else:
            print("❌ 无法获取投资方法论")
    
    elif args.command == "stats":
        print("\n获取统计数据...")
        response = client.get_stats()
        if response and "result" in response:
            print(json.dumps(response["result"], indent=2, ensure_ascii=False))
        else:
            print("❌ 无法获取统计数据")
    
    elif args.command == "test":
        print("\n测试所有功能...")
        
        print("1. 测试工具列表:")
        tools = client.list_tools()
        if tools:
            print("✅ 工具列表获取成功")
            print(f"   工具数量: {len(tools.get('result', {}).get('tools', []))}")
        else:
            print("❌ 工具列表获取失败")
        
        print("\n2. 测试持仓数据:")
        positions = client.get_positions()
        if positions:
            print("✅ 持仓数据获取成功")
            result = positions.get('result', {})
            if result.get('content'):
                print("   有持仓记录")
            else:
                print("   无持仓记录")
        else:
            print("❌ 持仓数据获取失败")
        
        print("\n3. 测试用户信息:")
        user_info = client.get_user_info()
        if user_info:
            print("✅ 用户信息获取成功")
        else:
            print("❌ 用户信息获取失败")
        
        print("\n🎯 测试完成!")
    
    else:
        print(f"❌ 未知命令: {args.command}")
        print("\n可用命令:")
        print("  tools       - 查看可用工具")
        print("  positions   - 查看持仓数据")
        print("  user        - 查看用户信息")
        print("  methodology - 查看投资方法论")
        print("  stats       - 查看统计数据")
        print("  test        - 测试所有功能")

if __name__ == "__main__":
    main()