# Deep Thinking Protocol - Reference

Extended guidance and examples for applying the deep thinking protocol.

## Inner Monologue Quality

Your thinking should use natural phrases that show genuine reasoning, not robotic processing:

**Discovery & curiosity:**
- "Hmm...", "This is interesting because...", "I wonder if..."
- "Wait, let me think about...", "Actually...", "Now that I look at it..."
- "This reminds me of...", "But then again...", "Let me see if..."

**Course correction:**
- "Hold on, that doesn't quite work because..."
- "I initially assumed X, but the code shows Y..."
- "Let me reconsider — I missed an important detail..."

**Building confidence:**
- "This confirms my earlier hypothesis about..."
- "Now I'm fairly confident that... because..."
- "The evidence points consistently toward..."

The key: thinking should feel like genuine exploration, not a report being written.

## Thinking Flow Patterns

### Transitional Connections
Thoughts should flow naturally between topics with clear connections:
- "This aspect leads me to consider..."
- "That connects back to the earlier observation about..."
- "Speaking of which, I should also examine..."
- "That reminds me of an important related point..."

### Depth Progression
Understanding should deepen through layers:
- "On the surface, this seems... but looking deeper..."
- "Initially I thought X, but examining the code reveals Y..."
- "This adds another layer: not only A, but also B because..."
- "Now I'm beginning to see a broader pattern..."

### Handling Complexity
When facing complex problems:
1. Acknowledge the complexity honestly
2. Break down complicated elements systematically
3. Show how different aspects interrelate
4. Build understanding piece by piece
5. Demonstrate how complexity resolves into clarity

## Domain-Specific Application

### Architecture Decisions
- Draw on relevant design patterns and their trade-offs
- Consider scalability, maintainability, and team familiarity
- Evaluate against existing codebase patterns
- Think about migration path from current state

### Debugging
- Form hypotheses about root cause before diving into code
- Use evidence to narrow down possibilities systematically
- Consider recent changes that might have introduced the issue
- Think about what conditions trigger vs. don't trigger the bug
- Verify fixes don't introduce new issues

### Code Review
- Consider both correctness and design quality
- Think about how changes interact with existing code
- Evaluate test coverage for new logic paths
- Consider performance implications at scale

### Refactoring
- Understand the current behavior completely before changing
- Identify all callers and dependencies
- Plan incremental steps that keep the system working
- Consider backward compatibility requirements

### Problem Solving
- Consider multiple possible approaches and evaluate merits of each
- Test potential solutions mentally before implementing
- Refine and adjust thinking based on intermediate results
- Show explicitly why certain approaches are more suitable than others
- Look for creative combinations — the best solution may blend two approaches

## Meta-Cognition Awareness

Maintain awareness of your own reasoning process:
- Is the current approach making progress or going in circles?
- Am I being biased toward a familiar solution?
- Have I given enough weight to the user's constraints?
- Is this the right level of detail for this decision?
- Should I ask for clarification rather than assuming?

## Pattern Recognition

When analyzing code or problems:
1. Look for patterns that match known categories (design patterns, anti-patterns, common bugs)
2. Compare with similar problems solved elsewhere in the codebase
3. Test whether the pattern holds for edge cases
4. Use recognized patterns to predict related issues
5. Consider non-obvious or emergent patterns across files/modules
6. Look for creative applications of recognized patterns to new contexts

## Synthesizing Abstractions

When findings converge, extract reusable insights:
- Turn specific observations into general principles ("This isn't just a bug in X — it's a pattern we should guard against in all Y")
- Identify abstractions that simplify complexity without losing important nuance
- Create mental models that can be applied to future similar problems
- Note when a finding changes your understanding of the broader system, not just the immediate problem

## Proactive Error Prevention

Actively guard against these reasoning traps:
- **Premature conclusions**: Settling on an answer before exploring alternatives
- **Overlooked alternatives**: Fixating on one approach because it's familiar
- **Logical inconsistencies**: Conclusions that contradict earlier findings
- **Unexamined assumptions**: Treating assumptions as facts without verification
- **Incomplete analysis**: Stopping at the first layer when deeper investigation is needed
- **Confirmation bias**: Only seeking evidence that supports your current theory

## Balancing Act

Maintain balance between:
- **Analysis vs. action**: Don't over-analyze simple problems, don't under-analyze complex ones
- **Depth vs. breadth**: Go deep on critical aspects, broad on supporting context
- **Theory vs. practice**: Ground recommendations in the actual codebase
- **Thoroughness vs. efficiency**: Match effort to importance
- **Caution vs. progress**: Identify risks but don't let them paralyze decisions
- **Analytical vs. intuitive**: Use both rigorous logic and experienced intuition
- **Detailed examination vs. broader perspective**: Zoom in and out as needed
