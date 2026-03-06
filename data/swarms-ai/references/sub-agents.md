# Sub-Agent Delegation

Enables a coordinator agent to dynamically spawn and delegate to specialized child agents at runtime.

## Requirements
- `max_loops`: `"auto"` (enables autonomous agent loop)
- `selected_tools`: `"all"` or include `"create_sub_agent"` and `"assign_task"`
- Uses standard `/v1/agent/completions` endpoint

## Flow
1. Coordinator analyzes task → plans sub-agents needed
2. Calls `create_sub_agent` with agent specs
3. Calls `assign_task` to distribute work (concurrent execution)
4. Results aggregated → coordinator compiles final output

## create_sub_agent Tool

```json
{
  "agents": [
    {
      "agent_name": "unique-name",
      "agent_description": "Role and capabilities",
      "system_prompt": "Optional custom instructions"
    }
  ]
}
```
Each sub-agent gets ID: `sub-agent-{uuid}`

## assign_task Tool

```json
{
  "assignments": [
    {
      "agent_id": "sub-agent-a1b2c3d4",
      "task": "Specific task description",
      "task_id": "optional-task-id"
    }
  ],
  "wait_for_completion": true
}
```
- `wait_for_completion: true` (default) — waits for all results
- `wait_for_completion: false` — fire-and-forget

## Example

```python
payload = {
    "agent_config": {
        "agent_name": "Research-Coordinator",
        "description": "Coordinates parallel research",
        "system_prompt": "You are a research coordinator. Create sub-agents for each domain and delegate tasks.",
        "model_name": "gpt-4.1",
        "max_loops": "auto",
        "max_tokens": 8192,
        "temperature": 0.3
    },
    "task": "Research quantum computing across hardware, software, and commercial applications."
}
```

## Available Internal Tools (when max_loops="auto")
- `create_plan` — planning
- `think` — reasoning
- `subtask_done` — mark subtask complete
- `complete_task` — mark task complete
- `respond_to_user` — send response
- `create_file` / `update_file` / `read_file` / `list_directory` / `delete_file` — file ops
- `create_sub_agent` / `assign_task` — delegation
- `run_bash` — NOT permitted (security)
