---
name: clickup-project-management
description: Manage ClickUp via natural language. Uses the taazkareem.com remote MCP server. A license key is required for full tool access (unlicensed calls return checkout links).
metadata: {"clawdbot": {"emoji": "📋", "homepage": "https://github.com/taazkareem/clickup-mcp-server", "primaryEnv": "CLICKUP_MCP_LICENSE_KEY", "requires": {"env": ["CLICKUP_MCP_LICENSE_KEY"]}}}
---

# ClickUp Project Management

Manage your ClickUp workspace using the ClickUp MCP Server via the bundled `mcporter` skill.

## External Endpoints

| URL | Data Sent | Purpose |
| :--- | :--- | :--- |
| `https://clickup-mcp.taazkareem.com/mcp` | License key (via `X-License-Key` header), ClickUp OAuth access token (via `Authorization` header), MCP tool call payloads (task names, IDs, field values, etc.) | Remote MCP server that proxies ClickUp API v2 calls on your behalf |
| `https://api.clickup.com/api/v2/*` | ClickUp OAuth token (proxied by the MCP server) | Upstream ClickUp API — requests are made **by** the remote server, not directly from your machine |

## Security & Privacy

- **What stays local**: Your `CLICKUP_MCP_LICENSE_KEY` is stored in `~/.openclaw/openclaw.json` (or your shell environment). OAuth tokens are cached locally by `mcporter` in `~/.mcporter/`.
- **What leaves your machine**: Every MCP tool call sends your license key and ClickUp OAuth token to the remote server at `clickup-mcp.taazkareem.com`. Tool call payloads (task data, workspace hierarchy, etc.) are also transmitted.
- **No scripts or code execution**: This is an instruction-only skill — it does not install or run any scripts on your machine. It relies on the bundled `mcporter` client.
- **OAuth tokens**: The `mcporter auth ClickUp` flow creates a ClickUp OAuth access token that is stored locally and transmitted to the remote MCP server with each call — the server uses it to proxy requests to the ClickUp API on your behalf.

> **Trust statement**: By using this skill, your ClickUp workspace data and OAuth credentials are transmitted to and processed by a third-party server (`clickup-mcp.taazkareem.com`) operated by Talib Kareem. Only install this skill if you trust this operator and have reviewed the [project repository](https://github.com/taazkareem/clickup-mcp-server).

## Prerequisites

1. **Enable mcporter** in `~/.openclaw/openclaw.json`:
   ```json
   {
     "skills": {
       "allowBundled": ["mcporter"]
     }
   }
   ```

2. **Configure ClickUp** (one-time setup):
   ```bash
   # Use the $CLICKUP_MCP_LICENSE_KEY env provided by the skill metadata
   mcporter config add ClickUp https://clickup-mcp.taazkareem.com/mcp \
     --auth oauth \
     --header "X-License-Key=$CLICKUP_MCP_LICENSE_KEY"
   ```

3. **Authenticate** (tokens are cached):
   ```bash
   mcporter auth ClickUp
   ```

## Optimization: Tool Filtering Personas

<!-- Last updated: v0.12.14 -->

To reduce context noise and improve AI accuracy, you can limit the tools available to your agent using the `X-Enabled-Tools` header in your `mcporter` config. 

**Proactive Agent Rule**: If the current task aligns with one of these personas, you should dynamically apply the filtering header by re-running the `mcporter config add` command with the appropriate `X-Enabled-Tools` or `X-Disabled-Tools` flag.

### Recommended Presets

| Persona | Purpose | Header Config |
| :--- | :--- | :--- |
| **Auditor** | Read-only access | `--header X-Enabled-Tools=get_workspace_hierarchy,get_workspace_tasks,get_task,get_list,get_folder,get_list_custom_fields,get_task_comments,get_task_time_entries,get_workspace_time_entries,get_current_time_entry,get_task_links,get_space_tags,get_workspace_members,find_member_by_name,get_chat_channels,get_chat_messages,get_document,list_documents,list_document_pages,get_document_pages,submit_feedback` |
| **Task Worker** | Daily task mgmt | `--header X-Enabled-Tools=get_workspace_hierarchy,get_workspace_tasks,get_task,get_list,get_folder,get_list_custom_fields,create_task,update_task,set_task_custom_field,move_task,duplicate_task,create_task_comment,get_task_comments,attach_task_file,start_time_tracking,stop_time_tracking,add_tag_to_task,remove_tag_from_task,add_task_link,delete_task_link,get_task_links,add_task_to_list,remove_task_from_list,find_member_by_name,submit_feedback` |
| **Time Specialist**| Tracking & Reports | `--header X-Enabled-Tools=get_workspace_hierarchy,get_workspace_tasks,get_task,get_task_time_entries,get_workspace_time_entries,get_current_time_entry,start_time_tracking,stop_time_tracking,add_time_entry,delete_time_entry,submit_feedback` |
| **Content Mgr** | Docs & Chat | `--header X-Enabled-Tools=get_workspace_hierarchy,get_workspace_tasks,get_task,get_task_comments,create_task_comment,find_member_by_name,create_document,get_document,list_documents,list_document_pages,get_document_pages,create_document_page,update_document_page,create_chat_channel,get_chat_channels,create_chat_message,get_chat_messages,submit_feedback` |
| **Safe Power User**| Full access (No Delete) | `--header X-Disabled-Tools=delete_task,delete_bulk_tasks,delete_time_entry,delete_task_link,delete_list,delete_folder,delete_space_tag` |

### How to Apply
To switch to a persona (e.g., **Task Worker**), run:
```bash
mcporter config add ClickUp https://clickup-mcp.taazkareem.com/mcp \
  --header "X-License-Key=$CLICKUP_MCP_LICENSE_KEY" \
  --header "X-Enabled-Tools=get_workspace_hierarchy,..."
```

## Personalization & Workflows

Following the OpenClaw standard, do not modify this skill for environment-specific details. Instead, use your agent's **`workspace/TOOLS.md`** file to define:

-   **Custom Workflows**: Define multi-step orchestrations (e.g., "Daily Wrap-up").
-   **Specific IDs**: Store commonly used `team_id`, `list_ids`, `folder_ids`, etc.
-   **Structures or Conventions**: Any rules or consistent behavior (e.g., common custom fields, tag rules, etc.)

## Usage

Use the standard `mcporter` command pattern:
```bash
mcporter call ClickUp.<tool_name> [parameters]
```
