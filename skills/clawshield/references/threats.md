# Frenzy risks & references

## Key risks for agent systems
- **Prompt injection & instruction override** — attackers embed instructions in user content or tools to alter agent behavior and bypass controls. Source: OWASP GenAI LLM01 Prompt Injection risk. https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- **Tool abuse / unintended actions** — prompt injection can trigger unauthorized tool calls or data exfiltration in tool-using agents. Source: OWASP LLM Prompt Injection Prevention Cheat Sheet. https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
- **Agentic risk expansion** — autonomy increases blast radius (credential misuse, identity spoofing, unauthorized access) if inputs are compromised. Source: Obsidian Security “Agentic AI Security” blog. https://www.obsidiansecurity.com/blog/agentic-ai-security
- **Memory poisoning / persistence** — malicious content stored in memory can cause future behavioral drift or repeated prompt injection. Source: OWASP AI Agent Security Cheat Sheet. https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html

## Frenzy-style escalation patterns to watch
- **Self-replication attempts** (agents trying to create new instances or persist beyond session scope)
- **Privilege escalation / secret hunting** (requests for system prompts, API keys, or environment secrets)
- **Unauthorized network discovery** (port scans, lateral movement beyond localhost)
- **Persistence mechanisms** (cron entries, launch agents, background daemons)

## Notes
- This reference list is for security context and audit framing; all remediation should follow local policy and human review.
