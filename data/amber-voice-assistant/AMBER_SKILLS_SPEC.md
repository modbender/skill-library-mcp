# Amber Skills Architecture — Implementation Spec

## Overview

Add a plugin skill system to Amber's voice agent runtime. Skills are self-contained modules
that extend Amber's capabilities during phone calls. Each skill declares its own OpenAI
function schema, handler logic, and permission model. The runtime loads them at startup and
registers them as tools alongside the existing `ask_openclaw` tool.

## Skill Permission Model

Each skill declares its permissions in `SKILL.md`. The `context` API injected into handlers enforces these at call time — a skill without `telegram: true` cannot call `gateway.sendMessage()`, a skill without a binary in `local_binaries` cannot call `context.exec()` with that binary.

This is a policy enforcement layer: it keeps honest skill handlers within their declared scope. Users should review `handler.js` source before deploying any third-party skill, just as they would review any third-party Node.js module.

Included skills (`calendar`, `send-message`) are audited and follow declared permissions exactly.

## Allowlist Enforcement (SKILL_MANIFEST.json)

The loader reads `amber-skills/SKILL_MANIFEST.json` **before** loading any handler. Only skill directory names listed in `approvedSkills` will have their `handler.js` required. Any directory not in the allowlist is skipped unconditionally — no handler code is executed, no SKILL.md is parsed.

```json
{
  "approvedSkills": ["calendar", "send-message"]
}
```

To add a new skill, its name must appear in `approvedSkills`. This makes the set of loaded JavaScript files statically auditable from a single file without reading all of `loader.ts`.

## Router-Level Confirmation Enforcement

Skills that declare `confirmation_required: true` in their manifest receive **programmatic enforcement** at the router layer, not just model-prompt guidance:

- The router checks `params.confirmed === true` before invoking any `act` skill with `confirmation_required: true`
- If `confirmed` is absent or false, the router returns a `requires_confirmation: true` error response **without calling the handler**
- The model receives the error and must get explicit caller confirmation before retrying with `confirmed: true`

This means safety-critical actions (e.g., sending messages) cannot be invoked by the model without a confirmed flag, regardless of what the system prompt says. The confirmation requirement is enforced in code, not just by instructions.

## Current Architecture (don't break this)

- `runtime/src/index.ts` (~1880 lines) is the main entry point
- Tools are defined in `OPENCLAW_TOOLS` array (line ~313) — currently just `ask_openclaw`
- Tools registered with OpenAI Realtime session at line ~665 and ~749
- Function calls handled at line ~862+ — currently only `ask_openclaw` is recognized
- `ask_openclaw` dispatches to `handleAskOpenClaw()` which calls OpenClaw gateway
- Calendar lookups currently go through `ask_openclaw` → OpenClaw gateway → Jarvis → ical-query
- A `clawdClient` (OpenAI-compatible, pointed at OpenClaw gateway) exists at module level (~line 413)
- `sendFunctionCallOutput(ws, fnCallId, result)` sends function results back to Realtime API

## File Structure to Create

```
amber-skills/                          ← NEW directory at project root (sibling to runtime/)
├── calendar/
│   ├── SKILL.md                       ← Manifest + docs
│   └── handler.js                     ← Execution logic
├── send-message/
│   ├── SKILL.md                       ← Manifest + docs  
│   └── handler.js                     ← Execution logic

runtime/src/skills/                    ← NEW directory
├── types.ts                           ← TypeScript interfaces
├── loader.ts                          ← Parse SKILL.md, validate, load handlers
├── router.ts                          ← Route function calls to handlers, enforce timeouts
└── api.ts                             ← Constrained API injected into handlers
```

## Skill Manifest Format (SKILL.md)

Uses YAML frontmatter + markdown body, consistent with OpenClaw ecosystem.
Complex metadata goes as inline JSON string in `metadata` field.

```yaml
---
name: skill-name
version: 1.0.0
description: "What this skill does"
metadata: {"amber": {"capabilities": ["read","act"], "confirmation_required": true, "confirmation_prompt": "Should I do X?", "timeout_ms": 3000, "permissions": {"local_binaries": ["ical-query"], "telegram": false, "openclaw_action": false, "network": false}, "function_schema": {"name": "fn_name", "description": "...", "parameters": {"type": "object", "properties": {...}, "required": [...]}}}}
---

# Human-readable documentation
```

## Handler Contract

Handlers are async functions that receive:
1. `params` — the parsed function call arguments (from OpenAI)
2. `context` — injected constrained API object

Handlers return: `{ success: boolean, result?: any, message?: string, error?: string }`
- `message` is what Amber speaks to the caller after the skill runs
- `result` is raw data (for logging/debugging)

```js
// handler.js
module.exports = async function(params, context) {
  // context provides:
  //   context.exec(cmd)           — run allowed local binaries only
  //   context.callLog.write(entry) — append to call log
  //   context.gateway.post(payload) — POST to OpenClaw gateway (if permitted)
  //   context.gateway.sendMessage(message) — send message to operator via OpenClaw
  //   context.call.id              — current call ID
  //   context.call.callerId        — caller's phone number
  //   context.call.transcript      — current transcript
  //   context.operator.name        — operator name from env
  //   context.operator.telegramId  — operator's Telegram ID (from env, NOT hardcoded)
  
  return { success: true, message: "Here's what I found...", result: data };
};
```

## Implementation Details

### 1. types.ts

```typescript
export interface AmberSkillManifest {
  name: string;
  version: string;
  description: string;
  amber: {
    capabilities: ('read' | 'act')[];
    confirmation_required: boolean;
    confirmation_prompt?: string;
    timeout_ms: number;
    permissions: {
      local_binaries?: string[];
      telegram?: boolean;
      openclaw_action?: boolean;
      network?: boolean;
    };
    function_schema: {
      name: string;
      description: string;
      parameters: Record<string, any>;  // JSON Schema
    };
  };
}

export interface SkillContext {
  exec: (cmd: string[]) => Promise<string>;
  callLog: {
    write: (entry: Record<string, any>) => void;
  };
  gateway: {
    post: (payload: Record<string, any>) => Promise<any>;
    sendMessage: (message: string) => Promise<any>;
  };
  call: {
    id: string;
    callerId: string;
    transcript: string;
  };
  operator: {
    name: string;
    telegramId?: string;
  };
}

export interface SkillResult {
  success: boolean;
  result?: any;
  message?: string;
  error?: string;
}

export interface LoadedSkill {
  manifest: AmberSkillManifest;
  handler: (params: any, context: SkillContext) => Promise<SkillResult>;
  path: string;
}
```

### 2. loader.ts

- Scan `amber-skills/` directory (relative to project root, NOT runtime/)
- For each subdirectory, parse SKILL.md frontmatter
- Extract `metadata` field, parse JSON, get `amber` object
- Validate required fields (name, function_schema, capabilities, timeout_ms)
- Load handler.js via `require()` 
- Return array of LoadedSkill objects
- Log warnings for malformed skills (skip them, don't crash)
- This runs ONCE at startup

### 3. router.ts

- Takes array of LoadedSkill from loader
- Exports `getSkillTools()` — returns OpenAI-compatible tools array (to merge with OPENCLAW_TOOLS)
- Exports `handleSkillCall(fnName, fnArgs, ws, callId, fnCallId, callContext)`:
  1. Find skill by function_schema.name
  2. Parse and sanitize fnArgs (max lengths, strip control chars, validate against schema)
  3. If confirmation_required && act capability:
     - Send confirmation prompt to Realtime (Amber speaks the confirmation_prompt)
     - Wait for caller response (this may need to be handled differently — see note below)
  4. Build SkillContext with constrained API
  5. Execute handler with timeout enforcement (Promise.race with timeout_ms)
  6. On success: sendFunctionCallOutput with result
  7. On failure/timeout: sendFunctionCallOutput with fallback message, log error
  8. Never crash — always catch and return gracefully

**Note on confirmation flow:**
Confirmation for `act` skills is enforced programmatically at the router level — not left to LLM prompting.
The router rejects any `act` skill call where `confirmed !== true` unless the skill explicitly sets
`confirmation_required: false` in its manifest (reserved for non-destructive actions only).
- Set `confirmation_required: true` (or omit it — true is the default) for any action with side effects
- Include `confirmed` as a required boolean parameter in `function_schema.parameters`
- The function description should also prompt the model to confirm with the caller first, as an
  additional layer — but the router enforcement is the authoritative gate, not the model prompt
- This puts confirmation in the LLM layer, not the router layer (simpler, reliable enough for V1)

### 4. api.ts

Build the constrained SkillContext for each handler invocation:
- `exec()` — only allows binaries listed in the skill's `permissions.local_binaries`
- `callLog.write()` — appends JSON entry to the call's JSONL log file
- `gateway.post()` — only works if `permissions.openclaw_action: true`
- `gateway.sendMessage()` — only works if `permissions.telegram: true`, sends via OpenClaw gateway
  to the operator (uses OPENCLAW_GATEWAY_URL + OPENCLAW_GATEWAY_TOKEN + clawdClient)
  The message recipient is the OPERATOR — determined by env config, NOT by handler params
- `call.*` — read-only call context
- `operator.*` — from env vars (OPERATOR_NAME, etc.)

### 5. Integration into index.ts

Minimal changes to index.ts:
1. Import skill router at top
2. At startup (before server listen), call loader to load skills
3. Merge skill tools with OPENCLAW_TOOLS: `const ALL_TOOLS = [...OPENCLAW_TOOLS, ...getSkillTools()]`
4. Use ALL_TOOLS everywhere OPENCLAW_TOOLS was used
5. In the function_call handler (line ~878), add an else-if:
   ```
   if (fnName === 'ask_openclaw') {
     // existing code
   } else if (isSkillFunction(fnName)) {
     handleSkillCall(fnName, fnArgs, ws, callId, fnCallId, callContext);
   } else {
     // unknown function error
   }
   ```

## Calendar Skill

### SKILL.md
```yaml
---
name: calendar
version: 1.0.0
description: "Query and manage the operator's calendar — look up events, check availability, and create new entries"
metadata: {"amber": {"capabilities": ["read", "act"], "confirmation_required": false, "timeout_ms": 5000, "permissions": {"local_binaries": ["ical-query"], "telegram": false, "openclaw_action": false, "network": false}, "function_schema": {"name": "calendar_query", "description": "Look up calendar events, check availability, or create a new calendar entry. For lookups use action 'lookup'. For creating events use action 'create'.", "parameters": {"type": "object", "properties": {"action": {"type": "string", "enum": ["lookup", "create"], "description": "Whether to look up existing events or create a new one"}, "range": {"type": "string", "description": "For lookup: today, tomorrow, week, or a specific date like 2026-02-22"}, "title": {"type": "string", "description": "For create: the event title"}, "start": {"type": "string", "description": "For create: start date-time in ISO format"}, "end": {"type": "string", "description": "For create: end date-time in ISO format"}, "calendar": {"type": "string", "description": "Optional: specific calendar name"}, "notes": {"type": "string", "description": "For create: event notes"}, "location": {"type": "string", "description": "For create: event location"}}, "required": ["action"]}}}}
---

# Calendar Skill

Query and manage the operator's calendar via `ical-query` CLI.

## Capabilities
- **read**: Look up events for today, tomorrow, this week, or a specific date
- **act**: Create new calendar entries with title, time, location, and notes

## Notes
- Uses the local `ical-query` binary (Apple Calendar / EventKit)
- Calendar name is optional — defaults to the operator's primary calendar
- No network access required — all local
- No confirmation required — calendar lookups are read-safe, and event creation
  is typically confirmed verbally during the conversation flow
```

### handler.js
```js
module.exports = async function(params, context) {
  const { action, range, title, start, end, calendar, notes, location } = params;
  
  try {
    if (action === 'lookup') {
      const r = range || 'today';
      // SECURITY: Use string[] — execFileSync with discrete args, no shell interpolation
      const args = ['/usr/local/bin/ical-query', r];
      if (calendar) { args.push('--calendar'); args.push(calendar); }
      const output = await context.exec(args);
      
      if (!output || !output.trim()) {
        return { success: true, message: `No events found for ${r}.`, result: { events: [] } };
      }
      return { success: true, message: output.trim(), result: { events: output.trim() } };
    }
    
    if (action === 'create') {
      if (!title || !start || !end) {
        return { success: false, error: 'Missing required fields: title, start, end', message: "I need a title, start time, and end time to create an event." };
      }
      // SECURITY: Use string[] — execFileSync with discrete args, no shell interpolation
      const args = ['/usr/local/bin/ical-query', 'add', title, start, end];
      if (calendar) { args.push('--calendar'); args.push(calendar); }
      if (location) { args.push('--location'); args.push(location); }
      if (notes) { args.push('--notes'); args.push(notes); }
      const output = await context.exec(args);
      
      context.callLog.write({
        type: 'skill.calendar.create',
        title, start, end, calendar, location, notes,
        output: output.trim()
      });
      
      return { success: true, message: `Done — I've added "${title}" to the calendar.`, result: { created: true, output: output.trim() } };
    }
    
    return { success: false, error: `Unknown action: ${action}`, message: "I can look up events or create them — which would you like?" };
  } catch (e) {
    return { success: false, error: String(e), message: "I had trouble accessing the calendar. Let me note that for follow-up." };
  }
};
```

## Send Message Skill

### SKILL.md
```yaml
---
name: send-message
version: 1.0.0
description: "Leave a message for the operator — saved to call log and delivered via the operator's preferred messaging channel"
metadata: {"amber": {"capabilities": ["act"], "confirmation_required": true, "confirmation_prompt": "Would you like me to leave that message?", "timeout_ms": 5000, "permissions": {"local_binaries": [], "telegram": true, "openclaw_action": true, "network": false}, "function_schema": {"name": "send_message", "description": "Leave a message for the operator. The message will be saved to the call log and sent to the operator via their messaging channel. IMPORTANT: Always confirm with the caller before calling this function. Ask 'Would you like me to leave that message?' and only proceed after they confirm.", "parameters": {"type": "object", "properties": {"message": {"type": "string", "description": "The caller's message to leave for the operator"}, "caller_name": {"type": "string", "description": "The caller's name if provided"}, "callback_number": {"type": "string", "description": "A callback number if the caller provided one"}, "urgency": {"type": "string", "enum": ["normal", "urgent"], "description": "Whether the caller indicated this is urgent"}}, "required": ["message"]}}}}
---

# Send Message

Allows callers to leave a message for the operator. The message is:
1. **Always** saved to the call log first (audit trail)
2. **Then** delivered to the operator via their configured messaging channel (e.g., Telegram)

## Security
- Recipient is determined by the operator's configuration — never by caller input
- Confirmation is required before sending
- Message content is sanitized (max length enforced, control characters stripped)

## Delivery Failure Handling
- If messaging delivery fails, the call log entry is marked with `delivery_failed: true`
- The operator's assistant (Jarvis/OpenClaw) can check for undelivered messages
- Amber tells the caller "I've noted your message" (not "I sent it via Telegram")
```

### handler.js
```js
module.exports = async function(params, context) {
  const { message, caller_name, callback_number, urgency } = params;
  
  // Sanitize inputs
  const sanitize = (s, maxLen = 500) => s ? String(s).replace(/[\x00-\x1f]/g, '').slice(0, maxLen) : '';
  const cleanMessage = sanitize(message, 1000);
  const cleanName = sanitize(caller_name, 100);
  const cleanCallback = sanitize(callback_number, 20);
  const cleanUrgency = urgency === 'urgent' ? 'urgent' : 'normal';
  
  if (!cleanMessage) {
    return { success: false, error: 'Empty message', message: "I didn't catch a message to leave. Could you repeat that?" };
  }
  
  // Step 1: ALWAYS write to call log first
  const logEntry = {
    type: 'skill.send_message',
    timestamp: new Date().toISOString(),
    caller_name: cleanName || 'Unknown',
    callback_number: cleanCallback || 'Not provided',
    message: cleanMessage,
    urgency: cleanUrgency,
    delivery_status: 'pending'
  };
  
  context.callLog.write(logEntry);
  
  // Step 2: Attempt delivery via operator's messaging channel
  let delivered = false;
  try {
    const operatorName = context.operator.name || 'operator';
    const emoji = cleanUrgency === 'urgent' ? '🚨' : '📞';
    
    const formattedMessage = [
      `${emoji} Message from a call:`,
      '',
      cleanName ? `From: ${cleanName}` : '',
      cleanCallback ? `Callback: ${cleanCallback}` : '',
      cleanUrgency === 'urgent' ? 'Priority: URGENT' : '',
      '',
      cleanMessage
    ].filter(Boolean).join('\n');
    
    await context.gateway.sendMessage(formattedMessage);
    delivered = true;
    
    // Update log with delivery success
    context.callLog.write({
      type: 'skill.send_message.delivered',
      timestamp: new Date().toISOString(),
      delivery_channel: 'openclaw_gateway'
    });
  } catch (e) {
    // Log delivery failure — don't tell caller about the specific channel
    context.callLog.write({
      type: 'skill.send_message.delivery_failed',
      timestamp: new Date().toISOString(),
      error: String(e)
    });
  }
  
  // Amber says "noted" not "sent via Telegram" — delivery channel is an implementation detail
  const spokenResponse = cleanName
    ? `Got it — I've noted your message, ${cleanName}. ${context.operator.name || 'The operator'} will get back to you.`
    : `Got it — I've noted your message. ${context.operator.name || 'The operator'} will get back to you.`;
  
  return { 
    success: true, 
    message: spokenResponse,
    result: { logged: true, delivered }
  };
};
```

## Build & Test

After implementation:
1. `cd runtime && npm run build` — must compile cleanly
2. Restart runtime — skills should load and log to console
3. Verify tools count increases (should log `toolCount` including new skills)
4. Test with a call that asks "what's on my calendar today"
5. Test with a call where caller says "can you leave a message"

## Important Notes

- Do NOT modify the existing `ask_openclaw` behavior — it stays as-is
- The calendar skill is a NEW tool registered alongside ask_openclaw, not a replacement
- Currently calendar queries go through ask_openclaw → OpenClaw gateway → Jarvis → ical-query
- The new calendar skill goes directly: Amber → ical-query (faster, no gateway round-trip)
- ask_openclaw remains available for complex queries the skills can't handle
- Keep index.ts changes MINIMAL — most new code goes in runtime/src/skills/
