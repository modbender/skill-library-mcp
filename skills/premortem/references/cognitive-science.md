# The Science Behind Premortem

## Origin: Gary Klein's Premortem Technique (1998)

Psychologist Gary Klein developed the "premortem" as a decision-making tool for
teams. Unlike a post-mortem (analyzing failure after it happens), a premortem
assumes the project has already failed and asks "why?"

### Key Research Findings

- **Prospective hindsight** (imagining an event has already occurred) increases
  the ability to correctly identify reasons for future outcomes by **30%**
  (Mitchell, Russo & Pennington, 1989).

- Teams using premortems identified **more potential problems** than teams using
  standard risk assessment (Klein, 2007).

- The technique counters **groupthink** by legitimizing dissent — it gives
  permission to voice concerns without being seen as negative.

## Why This Works for AI Agents

### 1. Countering Confirmation Bias

LLMs exhibit a form of confirmation bias: once they begin generating a response,
they tend to reinforce their initial direction rather than course-correct. The
premortem forces a deliberate interruption in this pattern by requiring the model
to argue AGAINST its own emerging response.

### 2. Activating Adversarial Reasoning

Standard chain-of-thought prompting asks "How do I solve this?" — a convergent
thinking pattern. The premortem asks "How could this go wrong?" — a divergent
thinking pattern that surfaces different information and considerations.

### 3. Calibrating Confidence

LLMs are notoriously poorly calibrated — they express high confidence even when
wrong. The premortem forces a moment of deliberate uncertainty, which naturally
produces better-calibrated outputs.

### 4. Preventing Drift

Over long conversations, LLMs gradually drift from the user's original intent.
The premortem's "Snapshot the Intent" phase creates a recurring anchor point
that prevents this silent degradation.

## Related Cognitive Techniques

| Technique | Origin | Relationship to Premortem |
|-----------|--------|--------------------------|
| **Red Teaming** | Military | Premortems are a self-applied red team |
| **Inversion** | Charlie Munger | "Invert, always invert" — solve by avoiding failure |
| **Negative Visualization** | Stoicism | Premeditatio malorum — preparing for what could go wrong |
| **Devil's Advocate** | Catholic Church | Assigned opposition to surface weaknesses |
| **Defensive Pessimism** | Psychology | Using anxiety about failure as preparation fuel |

## Application to Common AI Failure Modes

| AI Failure Mode | How Premortem Prevents It |
|----------------|--------------------------|
| **Hallucination** | "Can I point to where I learned this?" check |
| **Sycophancy** | "Am I agreeing because it's right or because it's easy?" |
| **Verbosity** | "Would the user prefer a shorter answer?" |
| **Missing requirements** | "What hasn't been stated that I'm assuming?" |
| **Overengineering** | "Am I solving the stated problem or an imagined one?" |
| **Security vulnerabilities** | "What could an attacker do with this code?" |
| **Breaking changes** | "What existing code depends on what I'm changing?" |

## References

- Klein, G. (2007). "Performing a Project Premortem." Harvard Business Review.
- Mitchell, D.J., Russo, J.E., & Pennington, N. (1989). "Back to the future:
  Temporal perspective in the explanation of events." Journal of Behavioral
  Decision Making.
- Kahneman, D. (2011). "Thinking, Fast and Slow." Chapter on premortem analysis.
- Munger, C. (1994). "A Lesson on Elementary, Worldly Wisdom." USC Business
  School address on inversion thinking.
