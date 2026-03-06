# Tools in CX Agent Studio

Tools connect agents to external systems or inline code to fetch, update, format, or analyze info.

## Tool Types
- **Client function**: Code executed client-side, not by the agent.
- **Data store**: AI-generated responses from website/uploaded data.
- **Website data store**: Search info from websites.
- **Cloud storage data store**: Search info from unstructured documents (RAG).
- **File search**: Upload files / RAG to agent.
- **Google Search**: Grounding with Google Search.
- **Integration Connector**: Pre-configured Connections.
- **MCP tools**: Connect to a Model Context Protocol server.
- **OpenAPI**: Connect to an external API using an OpenAPI schema.
- **Python code**: Provide Python code inline as a tool.
- **Salesforce / ServiceNow**: Connect to external SaaS platforms.
- **System tools**: Built-in common tasks.
- **Widget tools**: Flexible rich UI interaction.

## Best Practices
- **Wrap APIs**: Wrap complex external APIs with Python tools to obfuscate unnecessary data and reduce context tokens (Context Engineering).
- **Tool Chaining**: Don't instruct agents to call multiple tools sequentially. Instead, wrap them in a single Python tool that calls the others.
- **Clear Names/Descriptions**: Semantically meaningful distinct names, high-quality descriptions. Use flattened parameters in snake_case.