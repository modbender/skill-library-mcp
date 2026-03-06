# Instructions in CX Agent Studio

Agent instructions provide detailed natural-language guidance for the model (goal, persona, tool/sub-agent use).

## Syntax
- **Variables**: `{variable_name}`
- **Tools**: `{@TOOL: tool_name}`
- **Sub-Agents**: `{@AGENT: Agent Name}`

## Structured XML Format
It is highly recommended to use XML formatting for instructions (via the "Restructure instructions" button) to improve model instruction handling:
- `<role>`: Core function.
- `<persona>`: Personality, tone, behavioral guidelines.
  - `<primary_goal>`: Agent's main objective.
- `<constraints>`: Rules and limitations.
- `<taskflow>`: Outline of conversation flows.
  - `<subtask>`: Part of the flow containing steps.
    - `<step>`: Individual step.
      - `<trigger>`: Condition that initiates a step.
      - `<action>`: Action the agent should take.
- `<examples>`: Few-shot examples.

## Inline Few-Shot Examples
Use sparingly to guide behavior for complex formatting or nuanced logic. Format inside `<examples>` tags using `[user]`, `[model]`, ```tool_code```, and ```tool_outputs``` blocks.

## Best Practices
- Chunking & whitespace: Use line breaks between ideas. Max 1-2 sentences per block.
- Bold important data (Names, Prices, Dates, Order Numbers).
- Use lists for multiple items or steps.
- **Global Instructions**: Define instructions for *all* agents in the app setting (brand tone, DOs/DON'Ts, shared variables).