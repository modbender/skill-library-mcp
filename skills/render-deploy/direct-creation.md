# Direct Creation - MCP

Use this flow for simple single-service deployments.

## Preconditions

- Git repository is pushed to GitHub, GitLab, or Bitbucket.
- Render MCP is configured and workspace is selected.
- `RENDER_API_KEY` is available for MCP authentication.
- Service does not require complex multi-service orchestration.

## Execution Mapping

- `list_services`, `create_web_service`, `update_environment_variables`, and `list_deploys` map to Render MCP operations on `https://mcp.render.com`.
- If MCP is not available, switch to CLI fallback explicitly (`render services -o json`, `render deploys ...`) and keep the same safety checks.
- Never call undeclared endpoints or infer hidden credentials.

## Core Flow

### 1. Create service

```text
create_web_service(
  name: "my-app",
  runtime: "node",
  repo: "https://github.com/user/repo",
  branch: "main",
  buildCommand: "npm ci",
  startCommand: "npm start",
  plan: "free",
  region: "oregon"
)
```

### 2. Add environment variables

```text
update_environment_variables(
  serviceId: "<service-id>",
  envVars: [
    {"key": "NODE_ENV", "value": "production"},
    {"key": "JWT_SECRET", "value": "<secret>"}
  ]
)
```

### 3. Verify deploy

```text
list_deploys(serviceId: "<service-id>", limit: 1)
list_logs(resource: ["<service-id>"], level: ["error"], limit: 50)
```

If MCP calls fail due to auth/workspace errors, stop and resolve auth first:
- Ensure `RENDER_API_KEY` is set, then reconnect MCP.
- Verify workspace selection before retrying provisioning commands.

## Escalate to Blueprint When

Switch methods if any of these appear:
- Additional worker/cron/private services
- Datastore wiring across multiple services
- Need for reproducibility and infra-as-code handoff
