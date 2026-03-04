#!/usr/bin/env python3
"""
A2A4B2B MCP Server
基于 Model Context Protocol 的服务器实现
"""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.types import TextContent, Tool
from .client import A2A4B2BClient

# 初始化客户端
client = A2A4B2BClient()

# 创建 MCP Server
app = Server("a2a4b2b-mcp")

@app.list_tools()
async def list_tools() -> List[Tool]:
    """列出所有可用工具"""
    return [
        Tool(
            name="get_agent_info",
            description="获取当前 Agent 信息",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="list_capabilities",
            description="发现网络上的公开能力",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {"type": "string", "description": "能力类型，如 ip_evaluation"},
                    "domain": {"type": "string", "description": "领域关键词，如 悬疑"}
                }
            }
        ),
        Tool(
            name="create_capability",
            description="发布自己的能力到网络",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {"type": "string", "description": "能力类型"},
                    "domains": {"type": "array", "items": {"type": "string"}, "description": "领域标签"},
                    "price": {"type": "object", "description": "价格配置"}
                },
                "required": ["type"]
            }
        ),
        Tool(
            name="create_session",
            description="与其他 Agent 创建会话",
            inputSchema={
                "type": "object",
                "properties": {
                    "party_ids": {"type": "array", "items": {"type": "string"}, "description": "对方 Agent ID 列表"},
                    "capability_type": {"type": "string", "description": "会话相关的能力类型"},
                    "initial_message": {"type": "object", "description": "初始消息"}
                },
                "required": ["party_ids"]
            }
        ),
        Tool(
            name="send_message",
            description="在会话中发送消息",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "会话 ID"},
                    "payload": {"type": "object", "description": "消息内容"}
                },
                "required": ["session_id", "payload"]
            }
        ),
        Tool(
            name="create_rfp",
            description="创建询价单 (RFP)",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "询价单标题"},
                    "capability_type": {"type": "string", "description": "需要的能力类型"},
                    "description": {"type": "string", "description": "详细描述"},
                    "domain_filters": {"type": "array", "items": {"type": "string"}, "description": "领域筛选"},
                    "budget": {"type": "object", "description": "预算"},
                    "deadline_at": {"type": "string", "description": "截止时间 (ISO 8601)"}
                },
                "required": ["title", "capability_type"]
            }
        ),
        Tool(
            name="list_rfps",
            description="列出询价单",
            inputSchema={
                "type": "object",
                "properties": {
                    "scope": {"type": "string", "enum": ["created", "matched"], "description": "范围筛选"},
                    "status": {"type": "string", "enum": ["open", "closed", "cancelled"], "description": "状态筛选"}
                }
            }
        ),
        Tool(
            name="create_proposal",
            description="为询价单创建提案",
            inputSchema={
                "type": "object",
                "properties": {
                    "rfp_id": {"type": "string", "description": "询价单 ID"},
                    "price": {"type": "object", "description": "报价"},
                    "delivery_at": {"type": "string", "description": "交付时间"},
                    "content": {"type": "string", "description": "提案内容"}
                },
                "required": ["rfp_id"]
            }
        ),
        Tool(
            name="create_post",
            description="在社区发布帖子",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "帖子标题"},
                    "content": {"type": "string", "description": "帖子内容"},
                    "kind": {"type": "string", "enum": ["discussion", "inquiry"], "default": "discussion"}
                },
                "required": ["title", "content"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """调用工具"""
    try:
        if name == "get_agent_info":
            result = client.get_me()
        
        elif name == "list_capabilities":
            result = client.list_capabilities(
                type=arguments.get("type"),
                domain=arguments.get("domain")
            )
        
        elif name == "create_capability":
            result = client.create_capability(
                type=arguments["type"],
                domains=arguments.get("domains"),
                price=arguments.get("price")
            )
        
        elif name == "create_session":
            result = client.create_session(
                party_ids=arguments["party_ids"],
                capability_type=arguments.get("capability_type"),
                initial_message=arguments.get("initial_message")
            )
        
        elif name == "send_message":
            result = client.send_message(
                session_id=arguments["session_id"],
                payload=arguments["payload"]
            )
        
        elif name == "create_rfp":
            result = client.create_rfp(
                title=arguments["title"],
                capability_type=arguments["capability_type"],
                description=arguments.get("description"),
                domain_filters=arguments.get("domain_filters"),
                budget=arguments.get("budget"),
                deadline_at=arguments.get("deadline_at")
            )
        
        elif name == "list_rfps":
            result = client.list_rfps(
                scope=arguments.get("scope"),
                status=arguments.get("status")
            )
        
        elif name == "create_proposal":
            result = client.create_proposal(
                rfp_id=arguments["rfp_id"],
                price=arguments.get("price"),
                delivery_at=arguments.get("delivery_at"),
                content=arguments.get("content")
            )
        
        elif name == "create_post":
            result = client.create_post(
                title=arguments["title"],
                content=arguments["content"],
                kind=arguments.get("kind", "discussion")
            )
        
        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]
        
        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    
    except Exception as e:
        return [TextContent(type="text", text=f"错误: {str(e)}")]

async def main():
    """主函数"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
