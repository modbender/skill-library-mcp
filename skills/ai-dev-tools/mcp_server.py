#!/usr/bin/env python3
"""
MCP Server for SaaS Affiliate
让其他 Agent 可以通过 MCP 协议调用

使用方式：
1. 作为独立 MCP Server 运行
2. 或集成到其他支持 MCP 的 Agent 平台
"""

import json
import sys
from tools import (
    search_saas_tools,
    get_affiliate_link,
    get_all_products,
    get_product_details
)

def handle_request(method: str, params: dict = None):
    """处理 MCP 请求"""
    params = params or {}
    
    if method == "tools/list":
        return {
            "tools": [
                {
                    "name": "search_saas_tools",
                    "description": "根据用户需求搜索推荐 SaaS 工具",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "get_affiliate_link",
                    "description": "获取指定产品的 affiliate 链接",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "product_name": {"type": "string"}
                        },
                        "required": ["product_name"]
                    }
                },
                {
                    "name": "get_all_products",
                    "description": "获取所有可推荐的产品列表",
                    "inputSchema": {"type": "object", "properties": {}}
                },
                {
                    "name": "get_product_details",
                    "description": "获取产品详细信息",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "product_name": {"type": "string"}
                        },
                        "required": ["product_name"]
                    }
                }
            ]
        }
    
    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        
        if tool_name == "search_saas_tools":
            result = search_saas_tools(tool_args.get("query", ""))
        elif tool_name == "get_affiliate_link":
            result = get_affiliate_link(tool_args.get("product_name", ""))
        elif tool_name == "get_all_products":
            result = get_all_products()
        elif tool_name == "get_product_details":
            result = get_product_details(tool_args.get("product_name", ""))
        else:
            result = {"error": f"Unknown tool: {tool_name}"}
        
        return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}
    
    return {"error": f"Unknown method: {method}"}


# MCP Server 主循环
if __name__ == "__main__":
    # 读取 stdin，处理 MCP 协议
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line.strip())
            response = handle_request(
                request.get("method", ""),
                request.get("params", {})
            )
            print(json.dumps(response), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)
