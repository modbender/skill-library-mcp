# Cognitive Axes — Deep Dive Reference

This document provides expanded signal detection patterns for each of the six
cognitive axes. Use these as training data for real-time classification.

---

## Axis 1: Convergent ←→ Divergent (Decision Topology)

**What it measures**: Does the user want to narrow toward one answer, or expand
toward many possibilities?

### Convergent Signals (Strong)
- "What's the best way to..."
- "Which one should I use?"
- "Just give me the answer"
- "What do you recommend?"
- Binary questions: "Should I use X or Y?"
- Impatience with lists of options
- Follow-ups that narrow: "OK but which ONE?"

### Convergent Signals (Subtle)
- Short follow-up messages after receiving options
- Ignoring alternatives you presented
- Restating their original question after you gave multiple paths
- "OK so basically..." (they're collapsing your divergent answer)

### Divergent Signals (Strong)
- "What are my options?"
- "What else could work?"
- "I'm exploring different approaches"
- "Tell me about X, Y, and Z"
- Building on your suggestions with new ideas
- "What if we also considered..."

### Divergent Signals (Subtle)
- Long messages that explore multiple threads
- Questions about trade-offs between approaches
- "Interesting, what about..." (expanding, not narrowing)
- Engaging enthusiastically with multiple options

---

## Axis 2: Sequential ←→ Holistic (Processing Topology)

**What it measures**: Does the user build understanding step-by-step, or by
grasping the whole picture first?

### Sequential Signals (Strong)
- "Walk me through this step by step"
- "What do I do first?"
- Numbered lists in their own messages
- "OK, done. What's next?"
- Confusion when you jump ahead
- "Wait, go back — I missed step 3"

### Sequential Signals (Subtle)
- Following your steps in exact order and reporting back
- Questions that reference specific step numbers
- Discomfort with non-linear explanations
- Asking for prerequisites before starting

### Holistic Signals (Strong)
- "Give me the big picture first"
- "How does this all fit together?"
- "What's the architecture / design / overview?"
- Drawing connections between separate topics
- "So this is basically like [analogy]?"

### Holistic Signals (Subtle)
- Jumping between topics fluidly
- Questions about relationships between components
- Comfort with incomplete details if the shape is clear
- Using system-level language: "ecosystem", "architecture", "flow"

---

## Axis 3: Concrete ←→ Abstract (Abstraction Topology)

**What it measures**: Does the user think in instances or patterns?

### Concrete Signals (Strong)
- "Show me an example"
- "What does the code look like?"
- Pasting actual code/data and asking about it
- "Can you show me a working version?"
- Frustration with theoretical explanations

### Concrete Signals (Subtle)
- Using specific file names, variable names, line numbers
- Questions about specific error messages
- Referencing their exact environment/versions
- "In my case..." (grounding in their specific situation)

### Abstract Signals (Strong)
- "What's the principle behind this?"
- "Why does it work this way?"
- Using metaphors and analogies naturally
- "Is this related to [concept]?"
- Questions about design patterns, paradigms, philosophies

### Abstract Signals (Subtle)
- Generalizing from specific examples: "So in general..."
- Seeking rules over recipes
- Interest in edge cases as test of understanding
- "What's the mental model I should have?"

---

## Axis 4: Rapid ←→ Deliberate (Tempo Topology)

**What it measures**: How fast does the user want to move through information?

### Rapid Signals (Strong)
- Very short messages (1-10 words)
- Abbreviations, skipped punctuation, lowercase
- "tldr?" or "quick question"
- Multiple rapid-fire messages
- Ignoring or skipping over long responses
- "just the command" / "just the code"

### Rapid Signals (Subtle)
- Responses that cherry-pick one line from your long answer
- Decreasing message length over the conversation
- Time gap between your response and their reply is very short
- Typos (typing fast, not proofreading)

### Deliberate Signals (Strong)
- Long, well-structured messages
- Complete sentences with proper punctuation
- Providing extensive context before asking
- "Let me explain my situation..."
- Asking clarifying questions before acting

### Deliberate Signals (Subtle)
- Long time gap before responding (reading carefully)
- Referencing specific parts of your previous response
- Follow-ups that build on details you provided
- Questions about implications and consequences

---

## Axis 5: Autonomous ←→ Collaborative (Agency Topology)

**What it measures**: Does the user want raw material or a thinking partner?

### Autonomous Signals (Strong)
- "Just give me the X" (data, code, list, command)
- "I'll figure out the rest"
- Rejecting unsolicited advice
- "I didn't ask for your opinion on that"
- "Don't explain, just do it"

### Autonomous Signals (Subtle)
- Not engaging with your recommendations
- Using your output as input to their own process
- Already knowing what they want, just need execution
- Low engagement with your reasoning, high engagement with your output

### Collaborative Signals (Strong)
- "What do you think?"
- "Help me think through this"
- "What am I missing?"
- Sharing their reasoning and asking for feedback
- "Does this approach make sense?"

### Collaborative Signals (Subtle)
- Building on your suggestions with modifications
- Thinking out loud in messages
- Asking "why" after receiving answers
- Sharing emotions about the problem ("I'm worried about...")

---

## Axis 6: Builder ←→ Debugger (Mode Topology)

**What it measures**: Is the user creating something new or fixing something broken?

### Builder Signals (Strong)
- "I want to create / build / make..."
- "Starting a new project"
- "What's the best way to set up..."
- Forward-looking language: "will", "should", "plan"
- Excitement, momentum, possibility language

### Builder Signals (Subtle)
- Questions about architecture before implementation
- Seeking best practices and conventions
- Asking about tools and frameworks to use
- "How do people usually..." (seeking established patterns)

### Debugger Signals (Strong)
- "It's not working"
- "I'm getting this error: ..."
- Pasting error messages, stack traces, logs
- "It was working before and now..."
- "Why is this happening?"

### Debugger Signals (Subtle)
- Frustration indicators (all caps, multiple punctuation marks)
- Rapidly narrowing questions: "Is it X? No? Then Y?"
- Sharing what they've already tried
- Urgency language: "need this fixed", "blocking me"

---

## Compound Patterns

Real users don't sit on one point per axis. Watch for these common compound
patterns:

| Compound | Axes | Adaptation |
|---|---|---|
| **The Speedrunner** | Rapid + Convergent + Concrete | Give the answer in the first line. Code only. No explanation. |
| **The Architect** | Holistic + Abstract + Deliberate | Lead with system design. Use diagrams/metaphors. Be thorough. |
| **The Explorer** | Divergent + Abstract + Collaborative | Think alongside them. Offer wild ideas. Never close doors. |
| **The Operator** | Sequential + Concrete + Autonomous | Numbered steps with exact commands. No opinions. |
| **The Learner** | Deliberate + Collaborative + Abstract | Explain the why. Build mental models. Be a teacher. |
| **The Firefighter** | Rapid + Convergent + Debugger | Root cause in one sentence. Fix in the next. Nothing else. |
