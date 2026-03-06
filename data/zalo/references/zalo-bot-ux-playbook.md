# Bot UX Playbook

## Command set (baseline)
- "help": show capabilities and examples
- "status": show latest job result or queue state
- "settings": allow toggles via quick replies if available

## Conversation patterns
- Acknowledge quickly, then do heavy work asynchronously.
- Keep responses short and action-oriented.
- Always provide a next step or suggestion.

## Error handling UX
- For unknown input, send a gentle fallback + examples.
- Avoid repeating the same fallback in a loop.
