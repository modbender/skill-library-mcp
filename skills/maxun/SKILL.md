---
name: maxun
description: List and run Maxun web scraping robots. Use when asked to list robots, run a robot, scrape a website, or get robot results.
argument-hint: "list | run <robotId> | runs <robotId> | result <robotId> <runId> | get <robotId>"
metadata:
  openclaw:
    version: 1.0.0
    homepage: https://www.maxun.dev
    emoji: "🤖"
    user-invocable: true
    files:
      - scripts/*
    requires:
      env:
        - MAXUN_API_KEY
      bins:
        - bash
        - curl
      anyBins:
        - python3
    primaryEnv: MAXUN_API_KEY
---

# Maxun Skill

Maxun is a web scraping platform. The user has robots that scrape websites.

## INSTRUCTIONS FOR THE AI MODEL

You have ONE job here: call the `exec` tool with the exact command strings below. Do not paraphrase. Do not guess. Copy the command string exactly.

### ACTION: List all robots

When the user says anything like "list my robots", "show robots", "what robots do I have":

Call the `exec` tool. The `command` parameter must be this exact string:
```
maxun list
```

IMPORTANT: Do NOT append any words from the user's message as arguments. The command is always exactly `maxun list` — nothing after `list`.

After exec returns output, display it directly to the user as-is. The output IS the robot list. Do not interpret it, ask clarifying questions about it, or treat it as a new request. Just show it.

### ACTION: Run a robot

When the user wants to run or scrape with a specific robot:

Step 1 — First get the robot ID by calling `exec` with:
```
maxun list
```

Step 2 — Find the robot ID from the output, then call `exec` with:
```
maxun run <robotId>
```
Replace `<robotId>` with the actual ID string from step 1.

### ACTION: List past runs

Call `exec` with:
```
maxun runs <robotId>
```

### ACTION: Get a run result

Call `exec` with:
```
maxun result <robotId> <runId>
```

### ACTION: Get robot details

Call `exec` with:
```
maxun get <robotId>
```

### ACTION: Abort a run

Call `exec` with:
```
maxun abort <robotId> <runId>
```

## Error Handling

- No robots found → tell user to create one at https://app.maxun.dev
- Robot still running → call exec with `maxun result <robotId> <runId>`

## Setup (for new installations)

Add to `~/.openclaw/openclaw.json`:

```json
"tools": {
  "exec": { "host": "gateway", "security": "full", "ask": "off" }
},
"env": {
  "MAXUN_API_KEY": "your-api-key-here"
}
```

For **self-hosted Maxun**, also set `MAXUN_BASE_URL`:

```json
"env": {
  "MAXUN_API_KEY": "your-api-key-here",
  "MAXUN_BASE_URL": "http://localhost:8080"
}
```

Cloud users (`app.maxun.dev`) do not need `MAXUN_BASE_URL` — it is the default.
