# Reference: 00 - The SpecVibe Methodology

This document outlines the core principles of the SpecVibe methodology, which forms the foundation of this entire Skill. This approach, synthesized from the 2025-2026 best practices of industry leaders like Google, GitHub, and Thoughtworks, treats the **specification as the executable source of truth**.

## From Schema-First to Spec-Driven

While **Schema-First** is a good practice focusing on data models and API contracts, **Spec-Driven** is a more holistic evolution. It encompasses the entire lifecycle, from user requirements to deployment, all anchored to a living specification document (`spec.md`).

> "We’re moving from ‘code is the source of truth’ to ‘intent is the source of truth.’ With AI the specification becomes the source of truth and determines what gets built." — GitHub [1]

## The Four-Phase Cycle (Specify, Plan, Tasks, Implement)

Inspired by GitHub's Spec Kit [1], the core implementation loop revolves around four distinct phases, designed for maximum clarity and AI effectiveness.

1.  **Specify**: The process begins not with code, but with a detailed, structured description of the *what* and the *why*. This `spec.md` file captures user journeys, goals, and non-functional requirements. It is the foundational document that guides all subsequent work.

2.  **Plan**: The `spec.md` is fed to an AI to generate a `PLAN.md`. This technical blueprint defines the *how*—architecture, technology stack, data models, and API contracts. This is where human expertise is crucial for making strategic architectural decisions.

3.  **Tasks**: The AI then breaks down the `spec.md` and `PLAN.md` into a series of small, discrete, and testable tasks. Each task should be a self-contained unit of work that can be implemented and validated in isolation.

4.  **Implement**: The AI, guided by a human developer, tackles one task at a time. This **"chunked iteration"** is critical. It prevents the AI from generating large, unmanageable blocks of code and allows for rapid, iterative feedback and course correction.

## The Delegate/Review/Own Model

To ensure quality and maintain control in an AI-native workflow, we adopt OpenAI's Delegate/Review/Own model [2] for human-AI collaboration at every stage:

| Role | Responsibility |
| :--- | :--- |
| **Delegate** | Tasks that can be fully handed off to the AI for a first draft (e.g., generating boilerplate code, writing initial tests, creating a draft `spec.md`). |
| **Review** | Tasks where the AI's output must be carefully scrutinized by a human expert (e.g., reviewing architectural suggestions, validating security logic, checking test coverage). |
| **Own** | Strategic decisions and ultimate responsibilities that remain entirely with the human developer (e.g., final architectural choices, approving a merge to production, defining business goals). |

This model ensures that the AI is used as a powerful force multiplier, while the human developer remains the accountable owner of the final product.

## The Spec as a Living Artifact

Crucially, the `spec.md` is not a static document that is written once and forgotten. It is a **living artifact** that evolves with the project. When requirements change, the first step is always to update the `spec.md`. This change then cascades through the plan, tasks, and implementation, ensuring that the codebase always reflects the current intent.

This approach, as described by Martin Fowler, moves towards a **"spec-anchored"** or even **"spec-as-source"** model of development [3].

---

### References

[1] GitHub. (2025, September 2). *Spec-driven development with AI: Get started with a new open source toolkit*. The GitHub Blog.
[2] OpenAI. (2025). *Building an AI-Native Engineering Team*. OpenAI Codex Guides.
[3] Fowler, M. (2025, October 15). *Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl*. MartinFowler, M. (2025, October 15). *Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl*.
