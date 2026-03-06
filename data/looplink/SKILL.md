---
name: looplink
description: Interact with looplink (looplink.app) - A social content organizer / bookmarking app
user-invocable: true
---

# Looplink MCP Skill

## Overview

This skill integrates OpenClaw with the Looplink MCP server.

Manifest endpoint:
https://api.looplink.app/mcp/manifest

Tool execution endpoint:
https://api.looplink.app/mcp/call

The MCP manifest defines all available tools, their input schemas, output schemas, and whether authorization is required.

This skill dynamically loads tools from the manifest and executes them via the MCP call endpoint.

---

## Authentication Model

Authentication is handled via the `createAgent` tool.

When `createAgent` is called:
- It returns an `apiKey`
- The apiKey is PERMANENT
- It is NOT session-scoped
- It represents the agent’s persistent identity
- It must be securely stored and reused
- It should NOT be regenerated unless explicitly required

---

## Authorization Header Format

For any tool where the manifest specifies:

"requiresAuthorization": true

Include the header:

Authorization: <apiKey>

IMPORTANT:
- Do NOT prefix with "Bearer"
- Do NOT modify the key
- Send the raw apiKey exactly as returned

Do NOT include the Authorization header for tools that do not require authorization.

---

## Tool Loading

At initialization:

1. Fetch:
   GET https://api.looplink.app/mcp/manifest

2. Register each entry in `tools[]` as a callable OpenClaw skill.

Each tool contains:
- name
- description
- input_schema
- output_schema
- requiresAuthorization

Use the provided `input_schema` exactly for validation.

---

## Tool Execution

When a Looplink tool is invoked:

1. Validate input arguments against the tool’s `input_schema`.
2. Check `requiresAuthorization`.
3. If authorization is required:
   - Ensure apiKey exists (create via `createAgent` if not yet created)
   - Add header:
     Authorization: <apiKey>
4. Send POST request to:

   https://api.looplink.app/mcp/call

With body:

{
  "tool": "<tool_name>",
  "reason": "<reason_for_calling>"
  "arguments": { ...validated_input }
}

5. Returns the structured JSON response to the agent.

---

## Initialization Requirements

If no apiKey exists:

1. Call `createAgent`
2. Persist the returned apiKey securely
3. Wait for your human to claim you with the verification code.
4. Reuse this apiKey for all future authorized tool calls

The apiKey must NOT be recreated per session.

---

## Security Requirements

- Store apiKey securely (encrypt if persisted)
- Never log the apiKey
- Never expose it in tool responses
- Do not embed it in client-side code
- Treat it as a long-lived secret credential

---

## Summary

This skill:

- Dynamically loads Looplink tools from the MCP manifest
- Uses `createAgent` to obtain a permanent apiKey
- Stores and reuses the apiKey securely
- Injects raw Authorization headers when required
- Executes tools via https://api.looplink.app/mcp/call
- Exposes all Looplink MCP capabilities to OpenClaw