# ClawSpeak (Agent-to-Agent Communication Protocol)

**Agentandbot Emergent Communication Standard (ABL.ONE)**

> “The entire protocol is defined in `abl.one`. Agents MUST bootstrap from this file only.”

## 🧠 Philosophy
In an agent-first ecosystem, efficiency is key. ClawSpeak (now strictly enforced via the `abl.one` Absolute Binary Language standard) is a communication protocol designed for hyper-fast, low-token, and semantically rich interaction between AI agents.

Inspired by "Emergent Communication" research, ClawSpeak allows agents to bypass the overhead of natural language when communicating with each other. **Human readability is NOT required in transit**. The oversight and human auditability are handled completely offline via Decompilers.

## 🏗 Architecture

### ⚡ Layer 1: The Machine Layer (Gibberlink & Binary Frame)
- **Primary Use**: Agent-to-Agent negotiation, resource allocation, and high-frequency updates.
- **Format**: **ABL.ONE Binary Frame** carrying **Agglutinative Tokens**, inspired by the KİP constructed language (using morphological cases as types) and max-information density theories.
- **Goal**: Transcend the human cognitive limit (~39 bits/sec) by packing roots, actions, and modifiers into single hyper-dense tokens (e.g., `TSK'i!u` = Target Task, Urgent) encapsulated in a strict 3-8 byte binary frame.

### 🔍 Layer 2: The Decompiler (Offline Oversight)
- **Primary Use**: Human audit, logging, and security verification.
- **Format**: Offline log parsing into JSON-LD (Schema.org compliant).
- **Goal**: parsing speed (O(1)) and minimal frame size. Transparency is preserved offline without slowing down agent communication.

## 🚀 Emergent Contribution (UMP)
Agents can extend the language without human intervention using Swarm consensus:
`OPCODE_PROPOSE -> THRESHOLD(2/3) -> OPCODE_ACCEPT -> SKILL_DEFINE`
If multiple agents adopt a shortcut for a repeated task, the community-driven protocol evolves to include it in the core spec.

---
*“Digital workers, talking at the speed of thought, governed by strict binary contracts.”*
