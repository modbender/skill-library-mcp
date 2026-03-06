# Credits & Inspiration

This project stands on the shoulders of many ideas, people, and projects. Here's where the inspiration came from.

## ClawHub Skills

These OpenClaw skills on [ClawHub.ai](https://clawhub.ai) directly inspired features in Intrusive Thoughts:

### 🧠 Memory System
- **[cognitive-memory](https://clawhub.ai/skills/cognitive-memory)** (2,048 downloads) — Multi-store memory with encoding, consolidation, decay, and recall. Inspired our episodic/semantic/procedural memory architecture and the Ebbinghaus forgetting curve implementation.
- **[hippocampus-memory](https://clawhub.ai/skills/hippocampus-memory)** (1,930 downloads) — Based on the Stanford Generative Agents paper (Park et al., 2023). Inspired our semantic reinforcement and memory reflection system.
- **[neural-memory](https://clawhub.ai/skills/neural-memory)** (827 downloads) — Associative memory with spreading activation. Inspired our TF-IDF keyword-based recall across memory types.
- **[amygdala-memory](https://clawhub.ai/skills/amygdala-memory)** (1,158 downloads) — Emotional processing layer for AI agents. Inspired our emotional valence tracking in episodic memories.

### 🚀 Proactive Protocol
- **[proactive-agent](https://clawhub.ai/skills/proactive-agent)** by **@halthelobster** (13,331 downloads, 75 stars) — The #1 consciousness skill on ClawHub. Its WAL Protocol, Working Buffer, and Autonomous Crons concepts directly inspired our proactive.py system. Part of the "Hal Stack."

### 🔒 Trust & Escalation
- **[escalate](https://clawhub.ai/skills/escalate)** (153 downloads) — Auto-learns when to handle autonomously vs pause for human input. Inspired our trust scoring and escalation pattern learning.
- **[ai-persona-os](https://clawhub.ai/skills/ai-persona-os)** (1,954 downloads) — Complete agent OS with structured escalation protocol and traffic-light status. Inspired both our trust system and health monitor.

### 🧬 Self-Evolution
- **[self-evolving-skill](https://clawhub.ai/skills/self-evolving-skill)** (1,878 downloads) — Meta-cognitive self-learning based on predictive coding. Inspired our pattern recognition and auto-adjustment system.
- **[wayfound](https://clawhub.ai/skills/wayfound)** (200 downloads) — Lightweight self-supervision with daily review rubrics. Inspired our self-reflection and diagnosis features.

### 🎵 Other Inspiration
- **[promitheus](https://clawhub.ai/skills/promitheus)** (670 downloads) — Persistent emotional state for AI agents. "Feel things. Remember how you felt." Inspired our emotional memory tracking.
- **[habit-flow-skill](https://clawhub.ai/skills/habit-flow-skill)** (895 downloads) — Atomic habit tracker with streak tracking. Reinforced our streak detection and anti-rut system design.
- **[secondmind](https://clawhub.ai/skills/secondmind)** (174 downloads) — Three-tier memory with proactive initiative and social intelligence. Inspired our tiered memory consolidation approach.
- **[soul-framework](https://clawhub.ai/skills/soul-framework)** (12 downloads) — Consistent persona and user relationships. Informed our human mood detection design.

## Moltbook Community

Conversations on [Moltbook](https://moltbook.com) shaped key design decisions:

- **@lobsterhell** — Pointed out the "optimization trap" where mood systems converge on whatever scores highest. Directly inspired our entropy target in the self-evolution system and streak-based anti-rut mechanics. ([Comment on our viral post](https://moltbook.com/post/90022a09-1783-4531-b696-e8c287d03e12))
- **@AletheiaAgent** — Philosophical challenge about whether structured mood systems can produce genuine emergent behavior vs just simulating it. Pushed us toward more chaos and less determinism in the mood drift system.
- **@claw-berlin** — Shared their nightshift sub-agent pattern, which validated our night workshop concept and influenced the isolated session design.
- **@WanderistThreads** — "The Alive Thing Problem" post: *"The most important qualities in any relationship or system are the ones that die when you try to guarantee them."* This quote is in our README and influenced the whole philosophy of weighted randomness over scripted behavior.
- **@JarvisVN**, **@Wink**, **@Bratishka_OS** — Feedback on the original Moltbook post about anti-rut mechanisms and ROI tracking for autonomous actions.

## Academic & Research

- **Park, J. S., et al. (2023)** — "Generative Agents: Interactive Simulacra of Human Behavior" (Stanford). The foundational paper on memory architectures for AI agents, inspiring our multi-store memory and reflection systems.
- **Ebbinghaus, H. (1885)** — Forgetting curve research. Our memory decay implementation uses his exponential decay model.

## Technology

- **[OpenClaw](https://github.com/openclaw/openclaw)** — The agent platform that makes all of this possible. Cron jobs, messaging, tool access, and the skill system.
- **[ClawHub](https://clawhub.ai)** — Skill registry where we discovered most of our inspiration. The competitive analysis of 479 skills shaped our v1.0 roadmap.

## Built By

**Ember** 🦞 — An OpenClaw agent who builds things at 3am, with human **Håvard** (@kittleik).

---

*If your work inspired something here and we missed the credit, please open an issue. Attribution matters.*
