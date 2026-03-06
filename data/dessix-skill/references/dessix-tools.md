# Dessix MCP Tool Quick Reference

Use these tool names with:

```bash
node scripts/dessix-bridge.mjs invoke --tool <TOOL_NAME> --args '<JSON>'
```

## Workspace

- `dessix_list_workspaces`
  - args: `{}`
- `dessix_get_current_workspace`
  - args: `{}`
- `dessix_create_workspace`
  - args: `{"title":"My Workspace","description":"optional","logo":"optional"}`
- `dessix_update_workspace`
  - args: `{"workspace_id":"<WS_ID>","patch":{"title":"New Title"}}`

## Block Search and Read

- `dessix_search_blocks`
  - keyword query: `{"query":"pricing","limit":20}`
  - semantic query: `{"semantic":"notes about user retention","limit":20}`
  - types only: `{"types":["Action","Scene"],"limit":100}`
- `dessix_read_block`
  - args: `{"block_id":"<BLOCK_ID>"}`

## Block Write

- `dessix_create_block`
  - args: `{"patch":{"type":"Note","title":"Weekly Note","content":"body text"}}`
- `dessix_update_block`
  - args: `{"block_id":"<BLOCK_ID>","patch":{"title":"Updated","content":"new body"}}`
- `dessix_delete_block`
  - args: `{"block_id":"<BLOCK_ID>"}`
- `dessix_restore_block`
  - args: `{"block_id":"<BLOCK_ID>"}`

## Topic and Skill

- `dessix_get_topic_context`
  - args: `{"topic_id":"<THREAD_BLOCK_ID>"}`
- `dessix_get_skill`
  - args: `{"block_id":"<ACTION_OR_SCENE_BLOCK_ID>"}`
