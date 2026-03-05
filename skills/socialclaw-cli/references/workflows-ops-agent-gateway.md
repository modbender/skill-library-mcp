# Ops, Agent, and Gateway Workflows

Use these playbooks for operations control-plane flows and local UI/gateway operations.

## Ops Workflow

### Workspace Readiness

```bash
social ops user show --workspace clientA
social ops roles show --workspace clientA --user bob
social ops alerts list --workspace clientA --open
```

### Morning Run and Follow-Through

```bash
social ops morning-run --all-workspaces --spend 320
social ops approvals list --workspace clientA --open
```

Treat approvals as write operations because they can trigger real downstream actions.

## Agent Workflow

Prefer plan-first execution when intent is broad or multi-step:

```bash
social agent --plan-only "check auth and list pages for clientA"
social agent --scope clientA "check auth and list pages"
```

If cloud model provider setup is requested, mention fallback planning behavior and ask the user to configure provider credentials through social-cli setup flows. Do not request raw secrets unless the user explicitly opts in.

## Gateway and Studio Workflow

Use local gateway for web UI driven operations:

```bash
social gateway --open
social studio
```

When security requirements are stated, include API-key and CORS options:

```bash
social gateway --host 127.0.0.1 --port 1310 --require-api-key
```

## Multi-Profile / Team Context

Keep commands profile/workspace explicit in team settings:

```bash
social --profile clientA query me
social ops activity list --workspace clientA --limit 50
social ops invite create --workspace clientA --role operator --expires-in 72
```
