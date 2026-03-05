# SpecKit for OpenClaw 🦞

### *The Professional Engineering Lifecycle for your Agent.*

**SpecKit for OpenClaw** is a master orchestrator that brings the power of Spec-Driven Development (SDD) to the OpenClaw ecosystem. It transforms your agent from a simple chat interface into a structured engineering partner that can autonomously navigate complex software projects.

---

## 🤖 How it Works

The `speckit-workflow` skill acts as the "brain" for your **OpenClaw agent**. Once activated, it directs the agent to follow a rigorous, industry-standard engineering lifecycle. Instead of jumping straight into code, the agent is guided to:

1.  📜 **Constitution**: Establish project principles, code quality standards, and architectural constraints.
2.  📝 **Specify**: Transform high-level requirements into formal, technical `spec.md` files.
3.  🔍 **Clarify**: Proactively identify and resolve ambiguities through structured questioning.
4.  🏗️ **Plan**: Derive detailed technical architecture and step-by-step implementation plans.
5.  📋 **Tasks**: Break the plan into atomic, dependency-aware micro-tasks.
6.  👷 **Implement**: Execute code changes in isolated, focused sessions with dynamic task grouping and atomic commits.

---

## 🏗️ Advanced Orchestration

This skill is designed for maximum agent autonomy and reliability:

- **Workflow State Awareness**: The agent automatically detects current progress by checking for existing artifacts (`constitution.md`, `spec.md`, etc.), allowing it to resume seamlessly from where it left off.
- **Sub-Agent Delegation**: The master skill directs the main agent to spawn or delegate tasks to specialized sub-agents for each phase, maintaining clean context boundaries.
- **Session Isolation**: It instructs the agent to use fresh sessions for implementation, preventing context bloat and ensuring high-precision code output.
- **Atomic Commits & Pushes**: The agent is directed to commit and push changes after every successfully completed task chunk, ensuring a clean and recoverable project history.

---

## 📂 Requirements

- **OpenClaw Agent**
- **Git Access**: The agent requires Read/Write access to the repository to save specifications, plans, and code changes. Ensure your environment is authenticated (e.g., via SSH keys or a credential helper).

## ⚙️ Project Setup

This skill package comes pre-bundled with all necessary templates and sub-skills. No external downloads are required.

To initialize a new project:
1.  Ensure this skill is installed/available to your agent.
2.  Activate the `speckit-workflow` skill.
3.  The agent will automatically detect if the project is uninitialized and offer to copy the bundled `.specify/` templates to your project root.

---

*Powered by [github/spec-kit](https://github.com/github/spec-kit). Optimized for OpenClaw.*
