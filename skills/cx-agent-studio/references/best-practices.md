# Best Practices in CX Agent Studio

This guide provides best practices for designing reliable agent applications.

## General
- **Start simple**: Begin with simple use cases and scale up to complicated ones.
- **Specific instructions**: Unambiguous, well-organized, grouped by topics, and easy for a human to follow.
- **Structured instructions**: Use the restructure feature for XML formatted instructions (more reliable).

## Tools
- **Wrap APIs**: Wrap external APIs with Python tools to obfuscate unnecessary data. Return only relevant fields to reduce context and latency (Context Engineering).
- **Deterministic behavior**: Use tools and callbacks for deterministic behavior (e.g., canned responses or sequential validations).
- **Chaining tool calls**: Avoid instructing the agent to call multiple tools sequentially. Define a single tool that calls the others to reduce token usage and hallucination probability.
- **Clear definitions**: Distinct names, unused tools removed, flattened snake_case parameters. Avoid abbreviations (`pnum` -> `phone_number`).

## Development Workflow
- **Collaboration**: Define a clear development process using third-party version control (import/restore) or built-in version control (snapshots).
- **Versions**: Create immutable snapshots of the agent. Use Semantic Versioning (`v1.0.0`) or descriptive names (`pre-prod-instruction-changes`). Include detailed descriptions.
- **End-to-End testing**: Test external system integrations.

## Evaluations
- **Use evaluations**: Ensure agent reliability by setting expectations on agents and their APIs.