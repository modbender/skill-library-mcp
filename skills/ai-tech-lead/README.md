# AI-Tech-Lead
This repository contains a SKILL for AI coding agents (like Claude Code, Cursor, or Windsurf) based on the Context Engineering methodology. It forces the AI to work in four strict, human-verified phases (Research, Design, Planning, Implementation) to generate secure, high-quality code while preventing LLM hallucinations and codebase degradation.

# AI Tech Lead: Context Engineering Workflow

## 🚀 Overview
Working with AI coding agents without a strict process often leads to bloated code, a 40% increase in code complexity, and frequent security vulnerabilities [5, 6]. This repository provides a system prompt that acts as an **AI Tech Lead**, forcing your AI assistant to follow a rigorous "Context Engineering" methodology. 

By breaking tasks down and strictly managing the context window (maximizing accuracy and completeness while minimizing noise), this workflow ensures you maintain total control over your architecture and code quality.

## 🧠 The 4-Phase Process

The agent is instructed to NEVER write code immediately. Instead, it must follow these four isolated phases:

### 1. Research 🔍
The agent launches parallel sub-agents to scan the codebase and gather context. It produces a document containing only **dry facts** about the "as-is" state of the project, with links to specific files and lines of code. No opinions or refactoring suggestions are allowed at this stage to prevent context noise.

### 2. Design 📐
Based on the research, the agent generates architectural documentation, including:
*   **C4 Models** (Context, Containers, Components, Code).
*   **Data Flow** and **Sequence Diagrams** .
*   **ADR** (Architecture Decision Records) and testing strategies.
*   🛑 *Hard Stop: The process pauses here for mandatory human pair-review. The agent cannot proceed without approval*.

### 3. Planning 📝
The agent creates a detailed, step-by-step implementation plan. The plan is broken down into isolated phases (e.g., domain models, interfaces, adapters) with specific files targeted for creation or modification. 
*   🛑 *Hard Stop: Human review and approval of the plan are required*.

### 4. Implementation 💻
The agent acts as a Team Lead in a Mob Programming setup, orchestrating a team of specialized sub-agents:
*   **Coder:** Writes code for one specific phase at a time.
*   **Reviewer:** Checks domain models and architectural layers.
*   **Security:** Scans for vulnerabilities, injections, and exposed endpoints.
*   **Architecture Checker:** Ensures the code matches the approved C4/Sequence designs, preventing LLM hallucinations.
*   **QA / Tester:** Verifies builds and automated tests.

**Quality Gates:** A phase is only complete if the build passes, all tests pass, and strict linters are satisfied. AI `co-author` tags are strictly forbidden in commits due to potential licensing issues.

## 🛠️ How to Use

1. Copy the contents of `SKILL.md` 
2. Paste it into skill folder.
3. Provide your initial task and ensure you specify your tech stack and architectural standards (e.g., "React with Redux" or "Go Microservices with Clean Architecture"), as the agent is forbidden from guessing your stack.
4. Follow the agent's lead through the review gates!

## ⚠️ Important Constraints
*   **Context Isolation:** Every sub-agent receives exactly the context needed for its specific task—nothing more, nothing less.
*   **No Universal Prompts:** This workflow assumes you will provide project-specific rules. There is no silver bullet; the AI must operate within your specific engineering culture.
