# Guardrails in CX Agent Studio

Guardrails are checks and balances protecting agent applications (model input and output).

## Prompt Guard
Protection against prompt attacks ("ignore your instructions").
- Outcomes: Say exactly, Handoff to an agent, Generate a response, or Custom.

## Blocklist
Prevent certain words/phrases.
- Matches: Whole words, Any mention, Regex pattern.
- Blocked content from: User input, Agent response.
- Outcomes: Say exactly, Handoff, Generate response.

## Safety
Enforce Responsible AI practices.
- Levels: Relaxed, Balanced, Strict.
- Outcomes: Say exactly, Handoff, Generate response, Custom.

## Rules
Build your own using:
- Natural language instructions.
- Code (after_model_callback python code).
- Outcomes: Say exactly, Handoff, Generate response.