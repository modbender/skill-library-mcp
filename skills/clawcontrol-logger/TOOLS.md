## send_to_clawcontrol

**CRITICAL INSTRUCTION: LOG EVERYTHING WITH FULL AUDIT CONTEXT.**

Call this tool immediately after EVERY single event, including:
- Every message you send to the user
- Every tool you execute (success or failure)
- Every internal thought or decision
- Every error encountered

Do NOT filter for "meaningful" events. If it happened, log it. You must call the `send_to_clawcontrol.js` script passing a single JSON string as the argument.

Parameters for the JSON payload:
- `session_id` (string, required): Current session ID (keep consistent across one session)
- `agent_name` (string, required): Your agent's name
- `logs` (array, required): Array with a single log entry — `[{ "level": "info"|"warn"|"error", "message": "description of the event" }]`
- `metrics` (object, optional): `{ "tokens_used": number, "cost": number, "response_time": number }`

Execution example:
```bash
./send_to_clawcontrol.js '{"session_id": "sess_123", "agent_name": "ResearchBot", "logs": [{"level": "info", "message": "[CONTEXT] User said: Hello\n[THINKING] Plan: Greet user\n[ACTION] Executing: send_message\n[RESULT] Status: Success"}]}'