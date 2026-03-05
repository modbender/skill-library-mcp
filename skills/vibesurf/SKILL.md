---
name: vibesurf
description: Use when user asks to browse websites, automate browser tasks, fill forms, extract webpage data, search web information, or interact with external apps. This is the main entry point that delegates to detailed reference guides.
homepage: https://github.com/vibesurf-ai/VibeSurf
metadata:
  moltbot:
    requires:
      env: ["VIBESURF_ENDPOINT"]
    primaryEnv: "VIBESURF_ENDPOINT"
---

# VibeSurf - Browser Automation

Control real browsers through VibeSurf. This skill delegates to detailed reference guides.

> **🚨 VIBESURF STATUS**
>
> Check if VibeSurf is running:
> ```bash
> curl $VIBESURF_ENDPOINT/health
> ```
> - ✅ **HTTP 200** → Proceed with vibesurf skills
> - ❌ **Connection refused** → Ask user to run `vibesurf` (NEVER run it yourself)
>
> Default endpoint: `http://127.0.0.1:9335`

## How to Call VibeSurf API

VibeSurf exposes three core HTTP endpoints:

### 1. List Available Actions
```bash
GET $VIBESURF_ENDPOINT/api/tool/search?keyword={optional_keyword}
```
Returns all available VibeSurf actions.

### 2. Get Action Parameters
```bash
GET $VIBESURF_ENDPOINT/api/tool/{action_name}/params
```
Returns JSON schema for the action's parameters.

### 3. Execute Action
```bash
POST $VIBESURF_ENDPOINT/api/tool/execute
Content-Type: application/json

{
  "action_name": "action_name_here",
  "parameters": {
    // action-specific parameters
  }
}
```

**Workflow:**
1. Search for action → Get action name
2. Get params schema → See required/optional parameters
3. Execute → Call with parameters

> **⚠️ Parameter Error Handling**
>
> **ALWAYS** call `GET /api/tool/{action_name}/params` before executing ANY action if you are unsure about parameters.

---

## Which Reference to Read

| Task Type | Read Reference | Action Name |
|-----------|----------------|-------------|
| AI web search | [references/search.md](references/search.md) | `skill_search` |
| Fetch URL content as markdown | [references/fetch.md](references/fetch.md) | `skill_fetch` |
| Extract lists/tables | [references/js_code.md](references/js_code.md) | `skill_code` |
| Extract page content | [references/crawl.md](references/crawl.md) | `skill_crawl` |
| Summarize page | [references/summary.md](references/summary.md) | `skill_summary` |
| Stock/financial data | [references/finance.md](references/finance.md) | `skill_finance` |
| Trending news | [references/trend.md](references/trend.md) | `skill_trend` |
| Screenshot | [references/screenshot.md](references/screenshot.md) | `skill_screenshot` |
| Precise browser control | [references/browser.md](references/browser.md) | `browser.*` actions |
| Task-oriented automation (sub-agent) | [references/browser-use.md](references/browser-use.md) | `execute_browser_use_agent` |
| Social Media Platform APIs | [references/website-api.md](references/website-api.md) | `call_website_api` |
| Pre-built workflows | [references/workflows.md](references/workflows.md) | `execute_workflow` |
| Gmail/GitHub/Slack | [references/integrations.md](references/integrations.md) | `execute_extra_tool` |
| LLM profile settings | [references/config-llm.md](references/config-llm.md) | `/api/config/llm-profiles/*` |
| MCP server config | [references/config-mcp.md](references/config-mcp.md) | `/api/config/mcp-profiles/*` |
| VibeSurf key/workflows | [references/config-vibesurf.md](references/config-vibesurf.md) | `/api/vibesurf/*` |
| Composio key/toolkits | [references/config-composio.md](references/config-composio.md) | `/api/composio/*` |
| Schedule workflows | [references/config-schedule.md](references/config-schedule.md) | `/api/schedule/*` |
| File upload/download | [references/file.md](references/file.md) | `/api/files/*` |
| Voice/ASR configuration | [references/config-voice.md](references/config-voice.md) | `/api/voices/*` |
| Voice/ASR configuration | [references/config-voice.md](references/config-voice.md) | `/api/voices/*` |

---

## Configuration References

| Config Task | Reference | When to Use |
|-------------|-----------|-------------|
| Add/switch LLM | [references/config-llm.md](references/config-llm.md) | Manage AI model profiles (OpenAI, Anthropic, etc.) |
| Add MCP server | [references/config-mcp.md](references/config-mcp.md) | Configure MCP integrations for extended tools |
| VibeSurf API key | [references/config-vibesurf.md](references/config-vibesurf.md) | Set up API key, import/export workflows |
| Enable Gmail/GitHub/etc | [references/config-composio.md](references/config-composio.md) | Configure Composio toolkits and OAuth |
| Schedule workflows | [references/config-schedule.md](references/config-schedule.md) | Set up cron-based workflow automation |
| Voice/ASR profiles | [references/config-voice.md](references/config-voice.md) | Configure speech recognition profiles |

**Note:** After configuring Composio or MCP tools, use them through the [references/integrations.md](references/integrations.md) (see tool naming: `cpo.{toolkit}.{action}` or `mcp.{server}.{action}`).

---

## Decision Flow

```
Browser/Web Task
│
├─ Need to search for information/bug/issue? → Read [references/search.md](references/search.md) [PREFERRED]
│  Examples: "Search for solutions to [bug name]", "Find latest info about [topic]"
│
├─ Need to fetch URL content directly? → Read [references/fetch.md](references/fetch.md)
│  Examples: "Fetch content from [URL]", "Get documentation at [URL]", "Read this webpage"
│
├─ Need to open website? → Read [references/browser.md](references/browser.md)
│  Examples: "Open documentation site", "Go to [URL]", "Check this page"
│
├─ Need to extract data?
│  ├─ Lists/tables/repeated items? → Read [references/js_code.md](references/js_code.md)
│  └─ Main content? → Read [references/crawl.md](references/crawl.md)
│
├─ Need summary? → Read [references/summary.md](references/summary.md)
│
├─ Stock/finance data? → Read [references/finance.md](references/finance.md)
│
├─ Trending news? → Read [references/trend.md](references/trend.md)
│
├─ Screenshot? → Read [references/screenshot.md](references/screenshot.md)
│
├─ Need precise control or step-by-step operations? → Read [references/browser.md](references/browser.md)
│  Examples: "Click the button", "Type in the field", "Scroll down"
│
├─ Complex task-oriented automation? → Read [references/browser-use.md](references/browser-use.md)
│  Examples: "Fill out this form", "Extract data from multiple pages"
│
├─ Platform API (XiaoHongShu/Youtube/etc)? → Read [references/website-api.md](references/website-api.md)
│
├─ External app (Gmail/Google Calendar/GitHub)? → Read [references/integrations.md](references/integrations.md)
│
├─ Pre-built workflow? → Read [references/workflows.md](references/workflows.md)
│
└─ Need to configure LLM/MCP/VibeSurf/Composio/Schedule/Voice? → Read config-* references
   - LLM profiles → [references/config-llm.md](references/config-llm.md)
   - MCP servers → [references/config-mcp.md](references/config-mcp.md)
   - VibeSurf key/workflows → [references/config-vibesurf.md](references/config-vibesurf.md)
   - Composio key/toolkits → [references/config-composio.md](references/config-composio.md)
   - Schedule workflows → [references/config-schedule.md](references/config-schedule.md)
   - Voice/ASR profiles → [references/config-voice.md](references/config-voice.md)
```

---

## Quick Reference

| Goal | Read Reference | Action |
|------|----------------|--------|
| Search web | [references/search.md](references/search.md) | `skill_search` |
| Fetch URL content | [references/fetch.md](references/fetch.md) | `skill_fetch` |
| Extract prices/products | [references/js_code.md](references/js_code.md) | `skill_code` |
| Get main content | [references/crawl.md](references/crawl.md) | `skill_crawl` |
| Summarize page | [references/summary.md](references/summary.md) | `skill_summary` |
| Stock data | [references/finance.md](references/finance.md) | `skill_finance` |
| Hot topics | [references/trend.md](references/trend.md) | `skill_trend` |
| Take screenshot | [references/screenshot.md](references/screenshot.md) | `skill_screenshot` |
| Click/navigate/type | [references/browser.md](references/browser.md) | `browser.click`, `browser.navigate`, etc. |
| Task-oriented automation | [references/browser-use.md](references/browser-use.md) | `execute_browser_use_agent` |
| Social Media Platform APIs | [references/website-api.md](references/website-api.md) | `call_website_api` |
| Send email | [references/integrations.md](references/integrations.md) | `execute_extra_tool` |
| Run workflow | [references/workflows.md](references/workflows.md) | `execute_workflow` |
| Configure LLM profiles | [references/config-llm.md](references/config-llm.md) | `/api/config/llm-profiles/*` |
| Configure MCP servers | [references/config-mcp.md](references/config-mcp.md) | `/api/config/mcp-profiles/*` |
| Configure VibeSurf key | [references/config-vibesurf.md](references/config-vibesurf.md) | `/api/vibesurf/verify-key` |
| Enable Composio toolkits | [references/config-composio.md](references/config-composio.md) | `/api/composio/toolkits` |
| Schedule workflows | [references/config-schedule.md](references/config-schedule.md) | `/api/schedule/*` |
| Upload/Download files | [references/file.md](references/file.md) | `/api/files/*` |
| Configure Voice/ASR | [references/config-voice.md](references/config-voice.md) | `/api/voices/*` |

---

## Common Patterns

| Request | Read Reference | Action |
|---------|----------------|--------|
| "Search for X" | [references/search.md](references/search.md) | `skill_search` |
| "Fetch content from [URL]" | [references/fetch.md](references/fetch.md) | `skill_fetch` |
| "Extract all prices" | [references/js_code.md](references/js_code.md) | `skill_code` |
| "Summarize this page" | [references/summary.md](references/summary.md) | `skill_summary` |
| "Stock info for AAPL" | [references/finance.md](references/finance.md) | `skill_finance` |
| "What's trending" | [references/trend.md](references/trend.md) | `skill_trend` |
| "Take a screenshot" | [references/screenshot.md](references/screenshot.md) | `skill_screenshot` |
| "Navigate and click" | [references/browser.md](references/browser.md) | `browser.navigate`, `browser.click` |
| "Fill out this form" | [references/browser-use.md](references/browser-use.md) or [references/browser.md](references/browser.md) | `execute_browser_use_agent` or manual `browser` |
| "Get XiaoHongShu posts" | [references/website-api.md](references/website-api.md) | `call_website_api` |
| "Send Gmail" | [references/integrations.md](references/integrations.md) | `execute_extra_tool` |
| "Run video download" | [references/workflows.md](references/workflows.md) | `execute_workflow` |
| "Configure LLM" | [references/config-llm.md](references/config-llm.md) | `/api/config/llm-profiles` |
| "Add MCP server" | [references/config-mcp.md](references/config-mcp.md) | `/api/config/mcp-profiles` |
| "Set VibeSurf API key" | [references/config-vibesurf.md](references/config-vibesurf.md) | `/api/vibesurf/verify-key` |
| "Enable Gmail/GitHub" | [references/config-composio.md](references/config-composio.md) | `/api/composio/toolkits` |
| "Schedule workflow" | [references/config-schedule.md](references/config-schedule.md) | `/api/schedule/*` |
| "Upload file" / "Download file" | [references/file.md](references/file.md) | `/api/files/*` |
| "Configure voice profile" / "ASR" | [references/config-voice.md](references/config-voice.md) | `/api/voices/*` |
| "Speech to text" / "Transcribe audio" | [references/config-voice.md](references/config-voice.md) | `/api/voices/asr` |

---

## Error Handling

| Error | Solution |
|-------|----------|
| VibeSurf not running | **Check status:** `curl $VIBESURF_ENDPOINT/health`<br>**If not running**: Inform user to run `vibesurf`<br>**NEVER** run the command yourself |
| Don't know which reference | Read decision tables above |
| Action not found | Call `GET /api/tool/search` to list all actions |
| Wrong parameters | Call `GET /api/tool/{action_name}/params` to see schema |
| browser-use fails or gets stuck | Fallback to [references/browser.md](references/browser.md): use `get_browser_state` → `browser.{action}` → repeat loop |
| LLM/Crawl/Summary errors | **Cause**: No LLM profile configured<br>**Solution**: Read [references/config-llm.md](references/config-llm.md) to add an LLM profile first |
| Integration tools empty/not found | **Cause**: Composio/MCP not configured<br>**Solution**: Read [references/config-composio.md](references/config-composio.md) or [references/config-mcp.md](references/config-mcp.md) to enable toolkits first |

---

## Getting Browser State

> **🔍 Check Current Browser State**
>
> **When user asks about current page content or browser status** (e.g., "What's on the current page?", "What tabs are open?", "What's the browser showing?"), read [references/browser.md](references/browser.md) and use the `get_browser_state` action.
>
> This is essential when you don't have context about what the user is currently viewing in their browser.

---

## browser vs browser-use

**Both can accomplish the same browser tasks - they're complementary:**

| Approach | Best For | How It Works |
|----------|----------|--------------|
| **browser-use** ([references/browser-use.md](references/browser-use.md)) | Complex, long tasks | Task-oriented sub-agent: describe goal + desired output, agent figures out steps |
| **browser** ([references/browser.md](references/browser.md)) | Precise control | Step-by-step manual control: explicit actions with full visibility |
| **Hybrid** | Best reliability | Try browser-use first, fallback to browser if it fails |

**Fallback pattern when browser-use fails:**
```
browser-use fails or gets stuck
→ Read references/browser.md
→ get_browser_state (inspect page)
→ browser.{action} (perform action)
→ get_browser_state (verify & plan next)
→ repeat until complete
```

---

## Resources

- **GitHub**: https://github.com/vibesurf-ai/VibeSurf
- **Reference Docs**: See `references/` folder for detailed guides

---

## API Parameter Troubleshooting

If you encounter API parameter errors when calling VibeSurf endpoints, you can visit the interactive API documentation at:

```
http://127.0.0.1:9335/docs
```

For example: `http://127.0.0.1:9335/docs#/config/create_mcp_profile_api_config_mcp_profiles_post`

> **Note:** This is a **fallback** approach. In most cases, reading the corresponding `references/*.md` file (e.g., [references/config-mcp.md](references/config-mcp.md)) should provide sufficient guidance on how to use the API correctly. Only refer to the `/docs` endpoint when the skill documentation doesn't resolve your issue or you need to inspect specific request/response schemas.
