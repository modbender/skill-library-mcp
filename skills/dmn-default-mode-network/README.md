# dmn-default-mode-network (DMN)

An **autonomous thinking engine** that simulates the brain's Default Mode Network. When your AI agent is idle, DMN awakens to digest recent memories, cross-pollinate ideas from your Zettelkasten, critique its own logic via domain expert personas, and propose concrete engineering actions.

## When to Use This Skill

Use this skill when you want your agent to:
- **Think autonomously in the background** while you sleep or step away from the keyboard.
- **Generate serendipitous connections** across seemingly unrelated notes in your knowledge base.
- **Audit its own decisions** using the critical frameworks of world-class thinkers (e.g., Charlie Munger, Jeff Bezos).
- **Propose proactive technical actions** (Agentic Action Proposals) to test hypotheses and loop into the `self-evolve` engine.
- Simply say: *"Think about [topic] tonight"* and let the agent work while you rest.

## Core Mechanisms

### 1. The 5 Thinking Engines
DMN dynamically selects one of five modes based on the current context:
- **Self-Narrative**: Consolidate identity and recent decisions.
- **Creativity Darkroom**: Force connections between random notes (Luhmann's Folgezettel).
- **Social Cognition (ToM)**: Empathize with and infer the user's unstated needs.
- **Meaning Generation**: Synthesize daily insights and push them to extremes.
- **CEO Mind Simulation**: Borrow external mental models (e.g., Peter Thiel's 0 to 1) to brutally critique current strategies.

### 2. Agentic Action Proposals & Self-Evolve Integration
DMN doesn't just write passive notes. After thinking, it acts as a domain expert with host access:
- **Proposes Actions**: Suggests concrete technical steps (e.g., write a script, clone a repo).
- **Meta-Evolution Loop**: Automatically routes proposals regarding AI capability upgrades directly to the `self-evolve` candidate queue for future execution.

### 3. Anti-Rumination (Saturation Defense)
DMN scans its recent outputs before starting. If an execution branch hits a saturation limit (e.g., thinking about "pricing strategy" twice), DMN forcefully redirects itself to the Creativity Darkroom to inject randomness and prevent infinite thought loops.

## Installation

### ClawHub
```bash
npx clawhub@latest install dmn-default-mode-network
```

### Configuration
After installation, open `assets/user-config.md` to map DMN to your personal knowledge base:
- Specify your `Memory Dir` and `Knowledge Base Dirs`.
- Configure the `Thinkers Roster` to inject your industry's specific domain experts.
- Run via Cron, Heartbeat, or manual trigger.

## Project Structure
- `SKILL.md`: Main entry and quick start guide.
- `references/core-functions.md`: The 5 thinking engines and CEO mapping.
- `references/execution-flow.md`: Safeties, loops, and integration paths.
- `assets/session-synthesis.md`: The output template for daily DMN reports.
