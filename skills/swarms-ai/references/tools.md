# Tools Integration

Extend agent capabilities with custom tool definitions using OpenAPI-style function specs.

## Defining Tools

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_topic",
            "description": "Search for information on a topic",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "depth": {
                        "type": "integer",
                        "description": "Search depth (1-3)"
                    }
                },
                "required": ["query"]
            }
        }
    }
]
```

## Usage in Agent Config

```python
payload = {
    "agent_config": {
        "agent_name": "ToolAgent",
        "system_prompt": "You have access to search tools...",
        "model_name": "gpt-4o",
        "tools_list_dictionary": tools,
        "max_loops": 1
    },
    "task": "Research AI trends"
}
```

## MCP (Model Context Protocol) Integration

Connect agents to MCP servers for extended tool access:

```python
# Single MCP server
"mcp_url": "https://your-mcp-server.com"

# Or with config
"mcp_config": {
    "url": "https://your-mcp-server.com",
    "headers": {"Authorization": "Bearer ..."}
}

# Multiple MCP servers
"mcp_configs": {
    "servers": [
        {"url": "https://mcp1.com"},
        {"url": "https://mcp2.com"}
    ]
}
```

## Selected Tools (Autonomous Mode)

When `max_loops="auto"`, restrict available tools:

```python
"selected_tools": ["think", "create_plan", "create_sub_agent", "assign_task"]
```

Available: `create_plan`, `think`, `subtask_done`, `complete_task`, `respond_to_user`, `create_file`, `update_file`, `read_file`, `list_directory`, `delete_file`, `create_sub_agent`, `assign_task`

NOT available: `run_bash` (security restriction)
