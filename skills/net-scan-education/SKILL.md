# Skill: net-scan-education

Objective
- Provide a safe, educational agent skill focused on learning network scanning concepts (e.g., Nmap) without performing any real scans or accessing external networks.
- Emphasize defensive security education, policy compliance, and proper authorization.

Scope & Guardrails
- Non-operational outputs only: explanations, learning plans, lab setup checklists, and sample prompts.
- All actions must be explicitly authorized by a requestor and kept within a controlled lab environment.
- Logs and audit trails of prompts and responses are maintained.

Interfaces
- Invocation: via a chat prompt or command like: explain net-scan basics, provide a learning plan, or generate a lab setup checklist.
- Outputs: non-operational text, templates, checklists, and doc generation.

Data Model
- State: learning progress, last prompt, sample prompts.
- Artifacts: generated docs (markdown/text), templates.

Testing
- Unit tests for plain text outputs and template generation; ensure no sensitive commands or URLs are produced.

Publish
- Optional: publish to clawhub or keep local for iteration.

Test Prompts (examples)
- Explain how to safely learn Nmap in a lab without performing any scans.
- Generate a 2-week learning plan for network scanning in a controlled environment.
- Provide a lab setup checklist for a defensive learning lab.
