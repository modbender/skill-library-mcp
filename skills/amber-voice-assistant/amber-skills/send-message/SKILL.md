---
name: send-message
version: 1.0.0
description: "Leave a message for the operator — saved to call log and delivered via the operator's preferred messaging channel"
metadata: {"amber": {"capabilities": ["act"], "confirmation_required": true, "confirmation_prompt": "Would you like me to leave that message?", "timeout_ms": 5000, "permissions": {"local_binaries": [], "telegram": true, "openclaw_action": true, "network": false}, "function_schema": {"name": "send_message", "description": "Leave a message for the operator. The message will be saved to the call log and sent to the operator via their messaging channel. IMPORTANT: Always confirm with the caller before calling this function — ask 'Would you like me to leave that message?' and only proceed after they confirm.", "parameters": {"type": "object", "properties": {"message": {"type": "string", "description": "The caller's message to leave for the operator", "maxLength": 1000}, "caller_name": {"type": "string", "description": "The caller's name if they provided it", "maxLength": 100}, "callback_number": {"type": "string", "description": "A callback number if the caller provided one", "maxLength": 30}, "urgency": {"type": "string", "enum": ["normal", "urgent"], "description": "Whether the caller indicated this is urgent"}, "confirmed": {"type": "boolean", "description": "Must be true — only set after the caller has explicitly confirmed their message and given permission to send it. The router will reject this call if confirmed is not true."}}, "required": ["message", "confirmed"]}}}}
---

# Send Message

Allows callers to leave a message for the operator. This skill implements the
"leave a message" pattern that is standard in phone-based assistants.

## Flow

1. Caller indicates they want to leave a message
2. Amber confirms: "Would you like me to leave that message?"
3. On confirmation, the message is:
   - **Always** saved to the call log first (audit trail)
   - **Then** delivered to the operator via their configured messaging channel

## Security

- The recipient is determined by the operator's configuration — never by caller input
- No parameter in the schema accepts a destination or recipient
- Confirmation is required before sending (enforced programmatically at the router layer — the router checks `params.confirmed === true` before invoking; LLM prompt guidance is an additional layer, not the sole enforcement)
- Message content is sanitized (max length, control characters stripped)

## Delivery Failure Handling

- If messaging delivery fails, the call log entry is marked with `delivery_failed`
- The operator's assistant can check for undelivered messages during heartbeat checks
- Amber tells the caller "I've noted your message" — never promises a specific delivery channel
