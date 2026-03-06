# Diataxis Four Documentation Types - Detailed Guide

Theory Source: https://diataxis.fr

---

## Core Framework

Diataxis identifies four documentation types based on two dimensions:

1. **Action vs Cognition** - Is the document guiding action or providing knowledge?
2. **Acquisition vs Application** - Is the user learning or working?

```
                    ACTION                 COGNITION
                    ───────                ─────────
        ACQUISITION │                      │              │
        (Study)     │   Tutorial           │  Explanation │
                    │                      │              │
                    ─────────────────────────────────────
        APPLICATION │                      │              │
        (Work)      │   How-to Guide       │  Reference   │
                    │                      │              │
```

---

## Tutorial

**User Need**: Acquire skills (study)  
**Document Purpose**: Provide learning experience  
**Core Characteristic**: Learning-oriented

### Definition

A tutorial is a lesson that takes a student by the hand through a learning experience. A tutorial is always practical: the user does something under the guidance of an instructor.

### Key Principles

1. **Show where you're going** - Tell learners what they'll accomplish upfront
2. **Deliver visible results early and often** - Each step produces comprehensible results
3. **Maintain a narrative of the expected** - Continuous feedback that learners are on the right track
4. **Point out what to notice** - Learning requires reflection
5. **Encourage repetition** - Repetition builds skill
6. **Ruthlessly minimize explanation** - Tutorials are not the place for explanation
7. **Focus on the concrete** - Focus on this problem, this action, this result
8. **Ignore options and alternatives** - Guide learners to successful completion
9. **Aspire to perfect reliability** - Tutorials must inspire confidence

### Language Style

- "We will..." - First-person plural affirms tutor-learner relationship
- "In this tutorial, we will..." - Describe what learners will accomplish
- "First, do x. Now, do y." - No room for ambiguity
- "The output should look like..." - Give learners clear expectations
- "Notice...", "Remember...", "Let's check..." - Give learners plenty of clues

### Common Mistakes

- Mixing in too much explanation
- Providing options and alternatives
- No visible results between steps
- Lacking expected narrative

### Example Scenarios

- Getting started guides for new technologies
- Step-by-step guidance for first-time tool use
- Practice projects for skill development

---

## How-to Guide

**User Need**: Apply skills (work)  
**Document Purpose**: Help complete tasks  
**Core Characteristic**: Goal-oriented

### Definition

A how-to guide is directions that guide the reader through a problem or towards a result. A how-to guide helps the user get something done, correctly and safely; it guides the user's action.

### Key Principles

1. **Address real-world complexity** - Adapt to real use cases
2. **Omit the unnecessary** - Practical usability over completeness
3. **Provide a set of instructions** - Describe executable solutions
4. **Describe a logical sequence** - Implies logical ordering in time
5. **Seek flow** - Ground sequences in user's activities and thinking
6. **Pay attention to naming** - Titles say exactly what the guide shows

### Language Style

- "This guide shows you how to..." - Clearly describe the problem or task
- "If you want x, do y" - Use conditional imperatives
- "Refer to the x reference guide for a full list of options" - Don't pollute your practical guide

### Common Mistakes

- Writing from machine perspective rather than user
- Mixing in explanatory content
- Lacking branches and alternative paths
- Inaccurate titles

### Example Scenarios

- Troubleshooting records (how to solve X problem)
- Best practices (how to do Y)
- Configuration guides
- Troubleshooting

---

## Reference

**User Need**: Apply skills (work)  
**Document Purpose**: Describe technical facts  
**Core Characteristic**: Information-oriented

### Definition

Reference guides are technical descriptions of the machinery and how to operate it. Reference material contains propositional or theoretical knowledge that a user looks to in their work.

### Key Principles

1. **Describe and only describe** - Neutral description is the key imperative
2. **Adopt standard patterns** - Consistency makes reference useful
3. **Respect the structure of the machinery** - Documentation structure should mirror product structure
4. **Provide examples** - Examples help understanding without distraction

### Language Style

- "Django's default logging configuration inherits Python's defaults" - State facts
- "Subcommands: a, b, c, d, e, f" - List commands, options, operations
- "You must use a. You must not apply b unless c" - Provide warnings

### Common Mistakes

- Mixing in instruction or explanation
- Lacking consistency
- Structure doesn't reflect product architecture
- Too verbose

### Example Scenarios

- API documentation
- Configuration option lists
- Command reference
- Parameter descriptions

---

## Explanation

**User Need**: Acquire skills (study)  
**Document Purpose**: Provide understanding context  
**Core Characteristic**: Understanding-oriented

### Definition

Explanation is a discursive treatment of a subject that permits reflection. Explanation is understanding-oriented.

### Key Principles

1. **Make connections** - Help weave a web of understanding
2. **Provide context** - Explain why things are so
3. **Talk about the subject** - Explanation guides are about a topic
4. **Admit opinion and perspective** - Can contain opinions
5. **Keep explanation closely bounded** - Avoid absorbing other content types

### Language Style

- "The reason for x is because historically, y..." - Explain
- "W is better than z, because..." - Offer judgements and opinions
- "An x in system y is analogous to a w in system z. However..." - Provide context
- "Some users prefer w (because z). This can be a good approach, but..." - Weigh alternatives

### Common Mistakes

- Mixing in instruction or technical description
- Lacking clear boundaries
- Too abstract
- No multiple perspective discussion

### Example Scenarios

- Technical principle analysis
- Design decision explanations
- Historical background introductions
- Concept comparison analysis
- Exploratory sharing

---

## Type Comparison Table

| Dimension | Tutorial | How-to | Reference | Explanation |
|-----------|----------|--------|-----------|-------------|
| **User Need** | Study | Work | Work | Study |
| **Content Type** | Action | Action | Cognition | Cognition |
| **Purpose** | Learning experience | Complete task | Look up facts | Understand context |
| **Form** | Lesson | Step sequence | Dry description | Discursive explanation |
| **Language** | "We will..." | "If X, do Y" | "X is..." | "X because..." |
| **Explanation** | Minimize | Link to Reference | None | Core content |
| **Options** | Ignore | Provide alternatives | Complete list | Discuss tradeoffs |
| **Analogy** | Teaching child to cook | Recipe | Food packet info | Culinary history article |

---

## Usage Recommendations

### When Creating Documents

1. Ask: What does the user need right now?
   - Learning new skills? → Tutorial or Explanation
   - Completing specific tasks? → How-to or Reference

2. Ask: What type is the content?
   - Guiding action? → Tutorial or How-to
   - Providing knowledge? → Reference or Explanation

3. Use the compass tool to confirm: [references/compass.md](references/compass.md)

### When Refactoring Documents

1. Identify current document type
2. Check if mixing other type content
3. Separate confused content to correct types
4. Apply corresponding checklist

---

**Version**: 1.0  
**Source**: https://diataxis.fr  
**Compiled by**: Zhua Zhua
