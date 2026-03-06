# Flows in CX Agent Studio

Dialogflow CX flows can be integrated into CX Agent Studio agents.
- Flow-based agents hand off conversation to the flow until `END_SESSION` is reached, returning to the steering agent.
- Agent apps send user input to flows using the `DetectIntent` API.
- Require permissions: `Customer Engagement Suite Service Agent` needs `Dialogflow API Client` role.

## Migration Best Practices
- **Isolate Agent Types**: Create new CX Agent Studio agents for new use cases and maintain Dialogflow CX agents for old ones via a routing layer.
- **Highly Deterministic Business Logic**: Use flows for sequential data collections and validations or authentication flows based on session parameters.
  - Do NOT use for canned responses or intent classification.
- **Flows as Blackboxes**: Treat flows as encapsulated black boxes. Convey info through explicit input/output parameters. Modification to parameter collection logic upstream should not disrupt downstream flows.