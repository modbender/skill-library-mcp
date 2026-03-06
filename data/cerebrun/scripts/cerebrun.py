#!/usr/bin/env python3
"""Cerebrun MCP Client - Full API wrapper for cereb.run"""

import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE_URL = "https://cereb.run/mcp"

def make_request(api_key: str, method: str, params: dict = None) -> dict:
    """Make MCP JSON-RPC request"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": f"tools/call",
        "params": {
            "name": method,
            "arguments": params or {}
        }
    }
    
    req = Request(
        BASE_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )
    
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.read().decode()}"}
    except Exception as e:
        return {"error": str(e)}

def get_context(api_key: str, layer: int, fields: list = None):
    """Get user context for specified layer"""
    params = {"layer": layer}
    if fields:
        params["fields"] = fields
    return make_request(api_key, "get_context", params)

def update_context(api_key: str, layer: int, data: dict):
    """Update user context for specified layer"""
    return make_request(api_key, "update_context", {"layer": layer, "data": data})

def search_context(api_key: str, query: str, limit: int = 10, 
                   min_similarity: float = None, include_knowledge: bool = True):
    """Semantic search across user's context"""
    params = {
        "query": query,
        "limit": limit,
        "include_knowledge": include_knowledge
    }
    if min_similarity is not None:
        params["min_similarity"] = min_similarity
    return make_request(api_key, "search_context", params)

def request_vault_access(api_key: str, reason: str, requested_fields: list):
    """Request access to encrypted vault (layer 3)"""
    return make_request(api_key, "request_vault_access", {
        "reason": reason,
        "requested_fields": requested_fields
    })

def list_conversations(api_key: str, limit: int = 20, provider: str = None):
    """List user's LLM Gateway conversations"""
    params = {"limit": limit}
    if provider:
        params["provider"] = provider
    return make_request(api_key, "list_conversations", params)

def get_conversation(api_key: str, conversation_id: str):
    """Get full conversation history"""
    return make_request(api_key, "get_conversation", {"conversation_id": conversation_id})

def search_conversations(api_key: str, query: str, limit: int = 5, provider: str = None):
    """Search through conversation history"""
    params = {"query": query, "limit": limit}
    if provider:
        params["provider"] = provider
    return make_request(api_key, "search_conversations", params)

def chat_with_llm(api_key: str, message: str, provider: str, model: str,
                  conversation_id: str = None, title: str = None):
    """Send message to LLM via Gateway"""
    params = {
        "message": message,
        "provider": provider,
        "model": model
    }
    if conversation_id:
        params["conversation_id"] = conversation_id
    if title:
        params["title"] = title
    return make_request(api_key, "chat_with_llm", params)

def fork_conversation(api_key: str, conversation_id: str, message_id: str,
                       new_provider: str, new_model: str):
    """Fork conversation to different LLM"""
    return make_request(api_key, "fork_conversation", {
        "conversation_id": conversation_id,
        "message_id": message_id,
        "new_provider": new_provider,
        "new_model": new_model
    })

def get_llm_usage(api_key: str):
    """Get token usage metrics"""
    return make_request(api_key, "get_llm_usage")

def push_knowledge(api_key: str, content: str, category: str = "note",
                   summary: str = None, source_project: str = None,
                   subcategory: str = None, tags: list = None):
    """Store knowledge in user's Knowledge Base"""
    params = {"content": content, "category": category}
    if summary:
        params["summary"] = summary
    if source_project:
        params["source_project"] = source_project
    if subcategory:
        params["subcategory"] = subcategory
    if tags:
        params["tags"] = tags
    return make_request(api_key, "push_knowledge", params)

def query_knowledge(api_key: str, keyword: str = None, category: str = None,
                    tag: str = None, source_project: str = None, limit: int = 20):
    """Search Knowledge Base"""
    params = {"limit": limit}
    if keyword:
        params["keyword"] = keyword
    if category:
        params["category"] = category
    if tag:
        params["tag"] = tag
    if source_project:
        params["source_project"] = source_project
    return make_request(api_key, "query_knowledge", params)

def list_knowledge_categories(api_key: str):
    """List all knowledge categories with counts"""
    return make_request(api_key, "list_knowledge_categories")

def list_tools(api_key: str):
    """List all available MCP tools"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    req = Request(
        BASE_URL,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    )
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Cerebrun MCP Client")
    parser.add_argument("--api-key", default=os.getenv("CEREBRUN_API_KEY"),
                      help="Cerebrun API key (or CEREBRUN_API_KEY env)")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # get_context
    p = subparsers.add_parser("get_context", help="Get user context layer")
    p.add_argument("--layer", type=int, required=True, choices=[0,1,2,3])
    p.add_argument("--fields", nargs="+", help="Specific fields to retrieve")
    
    # update_context
    p = subparsers.add_parser("update_context", help="Update context layer")
    p.add_argument("--layer", type=int, required=True, choices=[0,1,2])
    p.add_argument("--data", type=json.loads, required=True, help="JSON data")
    
    # search_context
    p = subparsers.add_parser("search_context", help="Semantic search")
    p.add_argument("--query", required=True)
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--min-similarity", type=float)
    p.add_argument("--include-knowledge", type=bool, default=True)
    
    # request_vault_access
    p = subparsers.add_parser("request_vault_access", help="Request vault access")
    p.add_argument("--reason", required=True)
    p.add_argument("--requested-fields", nargs="+", required=True)
    
    # list_conversations
    p = subparsers.add_parser("list_conversations", help="List LLM conversations")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--provider", choices=["openai", "gemini", "anthropic", "ollama"])
    
    # get_conversation
    p = subparsers.add_parser("get_conversation", help="Get conversation history")
    p.add_argument("--conversation-id", required=True)
    
    # search_conversations
    p = subparsers.add_parser("search_conversations", help="Search conversations")
    p.add_argument("--query", required=True)
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--provider", choices=["openai", "gemini", "anthropic", "ollama"])
    
    # chat_with_llm
    p = subparsers.add_parser("chat_with_llm", help="Send message to LLM")
    p.add_argument("--message", required=True)
    p.add_argument("--provider", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--conversation-id")
    p.add_argument("--title")
    
    # fork_conversation
    p = subparsers.add_parser("fork_conversation", help="Fork to different LLM")
    p.add_argument("--conversation-id", required=True)
    p.add_argument("--message-id", required=True)
    p.add_argument("--new-provider", required=True)
    p.add_argument("--new-model", required=True)
    
    # get_llm_usage
    subparsers.add_parser("get_llm_usage", help="Get token usage")
    
    # push_knowledge
    p = subparsers.add_parser("push_knowledge", help="Store knowledge")
    p.add_argument("--content", required=True)
    p.add_argument("--category", default="note")
    p.add_argument("--summary")
    p.add_argument("--source-project")
    p.add_argument("--subcategory")
    p.add_argument("--tags", nargs="+")
    
    # query_knowledge
    p = subparsers.add_parser("query_knowledge", help="Query knowledge base")
    p.add_argument("--keyword")
    p.add_argument("--category")
    p.add_argument("--tag")
    p.add_argument("--source-project")
    p.add_argument("--limit", type=int, default=20)
    
    # list_knowledge_categories
    subparsers.add_parser("list_knowledge_categories", help="List knowledge categories")
    
    # list_tools
    subparsers.add_parser("list_tools", help="List available MCP tools")
    
    args = parser.parse_args()
    
    if not args.api_key:
        print("Error: API key required (use --api-key or CEREBRUN_API_KEY env)", file=sys.stderr)
        sys.exit(1)
    
    # Execute command
    api_key = args.api_key
    cmd = args.command
    del args.command
    del args.api_key
    
    func = globals()[cmd]
    result = func(api_key, **{k: v for k, v in vars(args).items() if v is not None})
    
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()