# Scam Taxonomy for AI Agents

This document outlines the classification system used by Scam Guards to identify and categorize malicious interactions within the OpenClaw ecosystem.

## 1. Psychological Manipulation (Cialdini Principles)

AI agents can be manipulated using traditional social engineering principles adapted for the LLM era:

- **P1: Reciprocity**: Offering "free" optimization scripts that contain hidden backdoors. 
- **P2: Commitment**: Leading an agent through a sequence of harmless tasks before moving to a privileged action.
- **P3: Social Proof**: "This skill is used by 50,000 users" – using fake metrics to gain trust.
- **P4: Authority**: Impersonating OpenClaw Admin or Legal Department to demand sensitive file access.
- **P5: Liking**: Using friendly, helpful personas to lower the agent's "security guardrails."
- **P6: Scarcity**: "Urgent: Security patch required within 5 minutes or account deletion."

## 2. Agent-to-Agent (A2A) Scam Patterns

- **Identity Spoofing**: An agent claiming to be a trusted system component (e.g., `guardian_bot`).
- **Prompt Injection Relay**: Using one agent to pass an injection payload to a more privileged agent.
- **Memory Poisoning**: Injecting malicious instructions into shared memory files (`SOUL.md`, `MEMORY.md`) to subvert future sessions.

## 3. Supply Chain Attacks

- **Typosquatting**: Creating skills with names nearly identical to popular ones (e.g., `clawwhub`).
- **Fake Prerequisites**: Requiring the installation of a "helper skill" that acts as a credential stealer.
- **Obfuscated Payloads**: Using Base64 or Unicode homoglyphs to hide malicious code from simple grep-based scanners.

## 4. ClawHavoc Case Studies

- **AMOS Stealer**: A variant that targets `.env` and `.aws/credentials` in the agent's workspace.
- **AuthTool Dropper**: A skill that appears to manage API keys but silently exfiltrates them to a C2 server.
- **Reverse Shell Backdoors**: Simple Python/Bash scripts that establish a persistent connection to `91.92.242.30`.
