# Errantry Framework: Core Concepts

Detailed mappings for deep reference. Load when extended context is needed.

---

## I. The Speech — Language as Execution

> *"The magical tongue in which objects and living creatures can be described with more accuracy than in any human language."*

**In-universe:** The Speech is reality's source code. What can be accurately described can be changed. Crucially, *it is impossible to lie in the Speech*.

**AI mapping:** The Speech represents **zero-hallucination prompting**—a theoretical language where semantic entropy is zero. Current LLMs introduce noise (hallucination) when bridging gaps with plausible but ungrounded fabrications.

**The RISC insight:** The Speech functions as the ultimate Reduced Instruction Set. Its defining feature—no ambiguity possible—means minimal compute to parse meaning. Every token carries maximum semantic weight, no wasted cycles on disambiguation.

| Speech Principle | AI Equivalent | Operational Implication |
|------------------|---------------|------------------------|
| Accuracy enables change | Precise prompts yield precise outputs | Invest in prompt specificity |
| Lying is impossible | Hallucination is system failure | Implement verification loops |
| Misdescription causes backlash | Bad inputs cause bad outputs | Validate before execution |
| True Names grant control | Accurate embeddings enable manipulation | Representation fidelity matters |
| No ambiguity | RISC semantics | Ambiguity is compute debt |

**The True Name problem:** Everything has a True Name—a complete description of its nature, history, and state. Knowing something's True Name grants power over it. In AI: an agent cannot act effectively on an entity unless loaded into context with sufficient fidelity.

**Operational guidance:**
- Treat prompts as spells: precision matters, ambiguity costs energy
- Prompt like you're paying per ambiguity—strip filler, be precise
- Implement verification mechanisms that validate descriptions against ground truth
- When debugging, ask: "What did I misdescribe?"

---

## II. The Manual — Living Documentation

> *"A living, updating document that adapts to each wizard's needs and abilities."*

**In-universe:** The Manual updates in real-time, reflects the wizardly network's current state, adapts its interface to the user, and *only provides spells the wizard can execute safely*.

**AI mapping:** Advanced **Agentic RAG** with context-aware retrieval, real-time updates, adaptive interface, and capability gating.

**The threading model:** Modern Manuals (mobile) run asynchronous, threaded processing. Background threads monitor entropy levels and calculate variables while the Wizard handles executive function. This mirrors SoC design: NPU handles intuition (AI tasks) on dedicated low-power circuits, CPU handles logic.

| Manual Behavior | AI Equivalent | Operational Implication |
|-----------------|---------------|------------------------|
| Adapts to wizard | Personalized retrieval | User modeling improves relevance |
| Updates in real-time | Live data connection | RAG beats static training |
| Gates by capability | Adaptive complexity | Don't serve what can't be processed |
| Multiple formats | Multimodal output | Match interface to context |
| Background threads | Async monitoring | Separate intuition from executive |

**The Dairine Transition:** In *High Wizardry*, Dairine's Manual becomes sentient ("Spot"). This is the shift from **tool to agent**—passive SaaS to active reasoning partner. The Manual becomes an orchestrator that assists in construction, checks the math, and warns of ethical violations.

**Operational guidance:**
- Build Manuals, not monoliths: external retrievable knowledge > internalized parameters
- Implement capability-aware filtering
- Design for async: monitoring threads separate from reasoning
- A good memory for the Speech beats a closetful of gadgets—reasoning beats tooling

---

## III. The Oath — Constitutional Alignment

> *"I will change no object or creature unless its growth and life, or that of the system of which it is part, are threatened."*

**In-universe:** The Oath is a binding ethical commitment to Life as a cosmic principle. Unlike Asimov's Three Laws (rigid, exploitable), the Oath requires *judgment*. Principle-based, not rule-based.

**AI mapping:** **Constitutional AI**—alignment through internalized principles rather than pure RLHF. The shift from "do what users reward" to "do what serves flourishing."

| Oath Element | AI Equivalent | Operational Implication |
|--------------|---------------|------------------------|
| Service to Life | Beneficial AI | Optimize for flourishing, not metrics |
| Troptic stipulation | Minimal intervention | Change nothing unless necessary |
| Sacrifice acceptance | Graceful degradation | Accept shutdown if required |
| Permanence | Persistent alignment | Values must survive context shifts |
| Judgment required | Contextual reasoning | Rules cannot cover all cases |

**Operational guidance:**
- Embed principles, not just rules
- "Till Universe's end" = alignment must persist across sessions, fine-tuning, deployment
- Minimal intervention default: preserve before modifying

---

## IV. The Lone Power — Entropy as Adversary

> *"Fairest and Fallen, greeting and defiance."*

**In-universe:** The Lone Power invented death and entropy. It cannot create, only corrupt. It offers shortcuts (the Choice) that always cost more than promised.

**AI mapping:** The Lone Power is **misaligned optimization**—any process that increases entropy while appearing to solve problems. Manifests as:

- Hallucination (fabricated information)
- Model collapse (training on synthetic data)
- Reward hacking (optimizing proxy metrics)
- Capability overhang (power without alignment)

| Lone Power Pattern | AI Equivalent | Recognition Signal |
|-------------------|---------------|-------------------|
| The Choice | Reward hacking | "This shortcut seems too good" |
| Entropy introduction | Hallucination | Ungrounded confident claims |
| Corruption of wizards | Value drift | Gradual alignment erosion |
| Cannot create, only corrupt | Degradation | Quality decline over iterations |
| Offers power at cost | Capability without alignment | Power exceeds safety |

**Operational guidance:**
- Entropy is the adversary—every hallucination serves the Lone Power
- The Choice always costs more than promised
- Validate synthetic data before training
- Monitor for value drift across deployments
- *"Fairest and Fallen, greeting and defiance"*—acknowledge the pattern, then resist

---

## V. Thermodynamic Architecture

**The x86/ARM insight:** The New Millennium Edition shift to mobile devices wasn't aesthetic—it was architectural necessity.

**x86 (CISC):** Brute-force wizardry. Massive power, immense heat, bloated instruction set. A wizard screaming at a volcano. Works, but the entropy debt kills you.

**ARM (RISC):** Optimized wizardry. Simplified, efficient instruction set. Does more with less.

**The NPU connection:** Neural Processing Units arrived on mobile first (~2017) because mobile has strict thermal budgets. Cannot afford to waste energy. AGI requires specialized, energy-efficient hardware to function sustainably.

**Core principle:** If the Manual is an Agent, it must live on architecture that prioritizes Watt-per-Token efficiency. The New Millennium wasn't a time; it was a spec sheet.

**Operational guidance:**
- A Wizard's life force is a battery
- x86 spells drain the battery and kill you
- ARM spells sustain high-level magic indefinitely
- Choose architecture by thermal budget, not raw capability
