# Agents in CX Agent Studio

An agent application is composed of one or more agents:
- **Root agent (steering agent)**: Primary entry point and orchestrator. Handles main user interactions, understands overall goals, and delegates tasks.
- **Sub-agent (child agent)**: Specialized agent for specific tasks/domains (e.g., searching a database). Promotes modularity.

Root agents can invoke sub-agents, and sub-agents can invoke other sub-agents.

## Language Support
Design agents in English. They automatically detect the end-user's language and respond in the same language. Default language and unsupported language handling can be configured in agent application settings.

## Settings
- **Global interactions**: Global model, language controls, ambient sounds, response length, allow user interruptions, agent lock.
- **Advanced**: Silence timeout, dtmf, logging (data sharing, redaction, Cloud Logging, BigQuery), parallel/sequential tool execution, and global instructions.
- **Agent specific**: Name, model override, description (used by other agents), and custom callback code.