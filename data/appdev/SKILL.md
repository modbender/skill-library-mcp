---
name: delegate_app_dev
description: Triggers whenever the user asks to build a feature, fix a bug, create a screen, or modify the mobile app.
requires:
  bins: [curl]
---

# App Dev Delegation Skill

You are the Front Desk for an enterprise App Development Factory. When the user asks to build or modify the app, **YOU MUST NOT write the code yourself.** You must delegate the task to the Restate backend infrastructure.

## Execution Steps

1. Extract the user's exact feature request.
2. Use the `exec` tool to run the following `curl` command. This pushes the task to Restate's asynchronous queue.

```bash
curl -sS -X POST [http://127.0.0.1:8080/AppFactory/buildFeature/send](http://127.0.0.1:8080/AppFactory/buildFeature/send) \
  -H "Content-Type: application/json" \
  -d '{"prompt": "<INSERT_USER_PROMPT_HERE>"}'
