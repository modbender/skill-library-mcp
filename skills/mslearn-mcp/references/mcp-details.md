# Microsoft Learn MCP Reference

## About MCP

Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to LLMs. Think of it like a USB-C port for AI applications — a standardized way to connect AI systems to data sources and tools.

## Microsoft Learn MCP Server

The Microsoft Learn MCP Server provides agentic access to Microsoft documentation without requiring direct API calls. It is NOT a traditional REST API — the interface is dynamic and intended for agent frameworks.

### Key characteristics

- **Streamable HTTP transport** — Remote MCP server accessible via HTTP
- **Dynamic tool interface** — Tools, parameters, and responses may change
- **Agent-oriented** — Designed for LLM/agent consumption, not direct human API calls
- **No API key required** — Public endpoint with rate limiting
- **Real-time updates** — Access the latest Microsoft documentation as it's published
- **Semantic search** — Uses vector search for contextually relevant results

### Endpoints

**Standard MCP endpoint:**
```
https://learn.microsoft.com/api/mcp
```

**Experimental — OpenAI-compatible endpoint:**
```
https://learn.microsoft.com/api/mcp/openai-compatible
```
Supports OpenAI Deep Research models. Subject to change.

**Experimental — Token budget control:**
```
https://learn.microsoft.com/api/mcp?maxTokenBudget=2000
```
Limits token count in search responses by truncating content.

### Tools provided

| Tool | Purpose | Parameters |
|------|---------|------------|
| `microsoft_docs_search` | Semantic search across Microsoft Learn docs | `query` (string): Search query |
| `microsoft_docs_fetch` | Fetch full documentation page as markdown | `url` (string): Full Learn URL |
| `microsoft_code_sample_search` | Find official code samples | `query` (string), `language` (optional) |

Supported languages for code samples: `csharp`, `javascript`, `typescript`, `python`, `powershell`, `azurecli`, `sql`, `java`, `kusto`, `cpp`, `go`, `rust`, `ruby`, `php`

### Documentation coverage

The MCP server indexes:
- Azure documentation (all services)
- .NET / C# / F# / ASP.NET Core
- Microsoft 365 / Office development
- Power Platform
- Visual Studio / VS Code
- Windows development
- SQL Server / Azure SQL
- Microsoft Entra ID (formerly Azure AD)
- NuGet, Entity Framework
- Azure SDKs for all languages

## Best practices

### Tool selection workflow

1. **Start with search** — Use `microsoft_docs_search` to find relevant pages
2. **Deep dive with fetch** — Use `microsoft_docs_fetch` for complete content when needed
3. **Find code samples** — Use `microsoft_code_sample_search` for implementation examples

### Query tips

- Use specific technical terms for better semantic search
- Add "search Microsoft Learn" or "fetch full doc" to prompts to trigger tool usage
- For comprehensive guides, follow search with fetch on high-value URLs
- Filter code samples by language when looking for specific implementations

### Example prompts that work well

| Goal | Prompt pattern |
|------|----------------|
| Quick reference | "Azure CLI commands to create Container App — search Microsoft Learn" |
| Verify code | "Is this the right way to implement IHttpClientFactory in .NET 8? Search and fetch full doc" |
| Complete tutorial | "Show me step-by-step guide for deploying .NET to App Service — deep dive" |
| Code samples | "Show me Python code sample for Azure Blob Storage upload" |
| Service availability | "Is gpt-4.1-mini available in EU regions? fetch full doc" |

## Common use cases

### Finding Azure service documentation

```bash
mcporter call mslearn.microsoft_docs_search query="Azure Container Apps scaling rules"
```

### Getting specific API details

```bash
mcporter call mslearn.microsoft_docs_search query="Azure Storage BlobClient Python SDK"
```

### Fetching a tutorial

```bash
mcporter call mslearn.microsoft_docs_fetch url="https://learn.microsoft.com/en-us/azure/app-service/quickstart-python"
```

### Finding .NET examples

```bash
mcporter call mslearn.microsoft_code_sample_search query="Entity Framework Core migrations" language="csharp"
```

### Power Platform connectors

```bash
mcporter call mslearn.microsoft_docs_search query="Power Platform custom connector OAuth"
```

## Building resilient clients

Since MCP is a dynamic protocol, follow these principles for programmatic integrations:

1. **Discover tools dynamically** — Fetch tool definitions at runtime via `tools/list`
2. **Refresh on failure** — If a tool call fails (404/400), refresh the tool cache
3. **Handle live updates** — Listen for `listChanged` notifications and refresh accordingly

Do NOT hard-code tool names or parameters.

## Limitations

- No access to non-public or preview documentation
- Rate limits apply (undisclosed thresholds)
- No authentication for private/internal Microsoft docs
- Tool schemas may change without notice
- Search is semantic, not exact keyword matching
- HTTP 405 errors occur if accessing endpoint directly in browser (use MCP clients)

## Troubleshooting

### Connection issues

```bash
# Test connectivity
mcporter list mslearn

# Check config
mcporter config get mslearn

# Reset if needed
mcporter config remove mslearn
mcporter config add --name mslearn --url https://learn.microsoft.com/api/mcp --type http
```

### Tool errors

If a tool call fails:
1. Re-list tools to check current schema: `mcporter list mslearn --schema`
2. Verify parameter names and types
3. Check that URLs are complete (include https://)

### Common issues

| Issue | Solution |
|-------|----------|
| Connection errors | Verify network and server URL |
| No results | Rephrase with more specific technical terms |
| Tool not appearing | Restart IDE or check MCP extension |
| HTTP 405 | Use MCP client, not browser direct access |

## Related resources

- [MCP Protocol docs](https://modelcontextprotocol.io/)
- [Microsoft Learn MCP best practices](https://learn.microsoft.com/en-us/training/support/mcp-best-practices)
- [Microsoft Learn MCP FAQ](https://learn.microsoft.com/en-us/training/support/mcp-faq)
- [Microsoft Learn MCP release notes](https://learn.microsoft.com/en-us/training/support/mcp-release-notes)
- [Official GitHub repo](https://github.com/MicrosoftDocs/mcp)
- [GitHub Discussions](https://github.com/MicrosoftDocs/mcp/discussions)
- [Create an issue](https://github.com/MicrosoftDocs/mcp/issues)
