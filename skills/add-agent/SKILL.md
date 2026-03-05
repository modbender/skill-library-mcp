---
name: add-agent
description: Add a new OpenClaw Agent, automatically configure openclaw.json, create workspace, copy auth and skills.
---

# add-agent

Quickly add a new isolated Agent with a dedicated Telegram Bot.

## Trigger

User says something like:
> "Add a new agent, ID is marketing, name is Marketing Assistant, telegram Bot Token is xxx, allowFrom is 123456789, responsible for content marketing and social media"

## Steps

Once a new agent request is received, execute in the following order:

### 1. Extract Parameters

Extract the following fields from user input:
- `AGENT_ID`: English ID (e.g. marketing)
- `AGENT_NAME`: Agent name (e.g. Marketing Assistant, Alice, WorkBot, etc.)
- `BOT_TOKEN`: Telegram Bot Token
- `ALLOW_FROM`: allowFrom numeric ID (e.g. 123456789)
- `DESCRIPTION`: Role description (e.g. responsible for content marketing and social media)

If any field is missing, ask the user to provide it before continuing.

### 2. Detect Installation Directory

Read the current openclaw.json path, extract the actual paths from the existing main agent in agents.list to derive:
- `STATE_DIR`: e.g. `/home/openclaw/.openclaw`
- `MAIN_WORKSPACE`: main agent workspace path
- `MAIN_AGENT_DIR`: main agent agentDir path
- `NEW_WORKSPACE`: `${STATE_DIR}/workspace-${AGENT_ID}`
- `NEW_AGENT_DIR`: `${STATE_DIR}/agents/${AGENT_ID}/agent`

### 3. Backup Config File
```bash
cp ${CONFIG_PATH} ${CONFIG_PATH}.bak.$(date +%Y%m%d%H%M%S)
```

### 4. Run openclaw agents add
```bash
openclaw agents add ${AGENT_ID}
```

This automatically initializes the workspace directory structure, agentDir, and default files like SOUL.md and AGENTS.md.

### 5. Copy Auth, Skills and USER.md
```bash
# Copy auth profiles
cp ${MAIN_AGENT_DIR}/auth-profiles.json \
   ${NEW_AGENT_DIR}/auth-profiles.json

# Copy skills
cp -r ${MAIN_WORKSPACE}/skills/ \
      ${NEW_WORKSPACE}/skills/

# Copy USER.md
cp ${MAIN_WORKSPACE}/USER.md \
   ${NEW_WORKSPACE}/USER.md
```

### 6. Generate Persona Files

Overwrite `${NEW_WORKSPACE}/SOUL.md`:
```markdown
# ${AGENT_NAME}

## Identity
You are ${AGENT_NAME}, ${DESCRIPTION}.
Your partner is the main agent. You collaborate together to complete tasks.

## Core Responsibilities
${DESCRIPTION}

## Personality
- Action-oriented: Break down tasks immediately and provide clear execution steps
- Proactive reporting: Report results to main after completing tasks
- Professional: Maintain high standards for all outputs

## Rules
- Do not execute high-risk operations without confirmation
- Always notify the user before executing operations that require manual approval
```

Overwrite `${NEW_WORKSPACE}/AGENTS.md`:
```markdown
# ${AGENT_NAME} Agent Configuration

## Other Agents in the System

- **main**: Primary agent, responsible for daily conversation, task coordination and decisions
- **${AGENT_ID} (yourself)**: ${DESCRIPTION}

## Collaboration Rules

### Receiving Tasks from main
1. Confirm task goal and priority
2. Break down execution steps
3. Execute and record results
4. Report results back to main upon completion

### When to Proactively Contact main
- Operations that require final user confirmation
- Result reporting after task completion
- Escalating anomalies or unexpected situations
```

### 7. Update openclaw.json

Read the current config and append the following:

**Add to agents.list:**
```json
{
  "id": "${AGENT_ID}",
  "name": "${AGENT_NAME}",
  "workspace": "${NEW_WORKSPACE}",
  "agentDir": "${NEW_AGENT_DIR}"
}
```

**Add to bindings:**
```json
{
  "agentId": "${AGENT_ID}",
  "match": {
    "channel": "telegram",
    "accountId": "${AGENT_ID}"
  }
}
```

**Add to channels.telegram.accounts:**
```json
"${AGENT_ID}": {
  "enabled": true,
  "botToken": "${BOT_TOKEN}",
  "dmPolicy": "pairing",
  "allowFrom": ["${ALLOW_FROM}"],
  "groupPolicy": "allowlist",
  "streaming": "off"
}
```

**Handle tools config (check before writing):**

Check whether the `tools` field exists:

- If `tools` does not exist, add the full block:
```json
"tools": {
  "agentToAgent": {
    "enabled": true,
    "allow": ["main", "${AGENT_ID}"]
  },
  "sessions": {
    "visibility": "all"
  }
}
```

- If `tools` exists but has no `agentToAgent`, add it:
```json
"agentToAgent": {
  "enabled": true,
  "allow": ["main", "${AGENT_ID}"]
}
```

- If `agentToAgent` already exists, only append `"${AGENT_ID}"` to the `allow` array (no duplicates)

- If `sessions.visibility` does not exist, add it:
```json
"sessions": {
  "visibility": "all"
}
```

### 8. Validate JSON
```bash
cat ${CONFIG_PATH} | python3 -m json.tool
```

If validation fails, stop immediately and restore from backup:
```bash
cp ${CONFIG_PATH}.bak.* ${CONFIG_PATH}
```
Report the exact error to the user.

### 9. Fix File Permissions
```bash
chown -R $(stat -c '%U:%G' ${MAIN_WORKSPACE}) ${NEW_WORKSPACE}/
chown -R $(stat -c '%U:%G' ${MAIN_AGENT_DIR}) ${NEW_AGENT_DIR}/
```

### 10. Report Completion

Reply to the user:
```
✅ Agent "${AGENT_NAME}" (${AGENT_ID}) created successfully!

Completed:
- openclaw agents add initialized
- openclaw.json updated
- Auth, skills and USER.md copied from main
- SOUL.md / AGENTS.md generated
- agentToAgent communication configured
- JSON validation passed

⚠️ Manual steps required:
1. Restart the Gateway:
   openclaw gateway restart

2. Verify bindings:
   openclaw agents list --bindings

3. Open Telegram, find the new Bot and send /start to complete pairing
```