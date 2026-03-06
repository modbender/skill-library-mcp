# The Diataxis Compass - Documentation Type Decision Tool

Theory Source: https://diataxis.fr/compass/

---

## Why the Compass is Needed

The Diataxis map is an effective reminder of the different kinds of documentation and their relationship, and it accords well with intuitions about documentation.

However, intuition is not always to be relied upon. Often when working with documentation, an author is faced with the question: 
- "What form of documentation is this?"
- "What form of documentation is needed here?"

Worse, sometimes intuition provides an immediate answer that is also **wrong**.

A map is most powerful in unfamiliar territory when we also have a **compass** to guide us.

---

## The Compass Table

The Diataxis compass is something like a truth-table or decision-tree of documentation. It reduces a more complex, two-dimensional problem to its simpler parts, and provides the author with a course-correction tool.

| If the content… | …serves the user's… | …then it must belong to… |
|----------------|-------------------|------------------------|
| informs action | acquisition of skill | **Tutorial** |
| informs action | application of skill | **How-to Guide** |
| informs cognition | application of skill | **Reference** |
| informs cognition | acquisition of skill | **Explanation** |

---

## How to Use the Compass

Ask only **two questions**:

### Question 1: Action or Cognition?

**Action**
- Practical steps, doing
- Guiding what the user does
- Contains serialized actions

**Cognition**
- Theoretical or propositional knowledge, thinking
- Providing facts, descriptions, context
- User consults rather than executes

### Question 2: Acquisition or Application?

**Acquisition = Study**
- User is learning new skills
- Needs learning experience
- Building competence and understanding

**Application = Work**
- User already has competence
- Needs to complete specific tasks
- Applying existing skills

---

## Usage Scenarios

### Scenario 1: Creating New Document

```
User question: "I want to write documentation about X technology"

Q1: Content type?
→ Guiding users to operate X technology → Action

Q2: User state?
→ User is learning X for the first time → Acquisition

Answer: Tutorial
```

### Scenario 2: Troubleshooting Record

```
User question: "I encountered X problem, solved it, want to record it"

Q1: Content type?
→ Guiding how to avoid/solve X problem → Action

Q2: User state?
→ Reader has basic competence, needs to solve specific problem → Application

Answer: How-to Guide
```

### Scenario 3: Technical Principle Analysis

```
User question: "I want to explain why we chose X architecture"

Q1: Content type?
→ Providing context, reasons, tradeoffs → Cognition

Q2: User state?
→ Reader wants to understand design decisions → Acquisition

Answer: Explanation
```

### Scenario 4: API Documentation

```
User question: "I need to write API endpoint documentation"

Q1: Content type?
→ Describing facts, parameters, return values → Cognition

Q2: User state?
→ Developer looks up while working → Application

Answer: Reference
```

---

## Use Terms Flexibly

When making preliminary judgments, use compass terms flexibly:

- **Action**: Practical steps, doing, guidance
- **Cognition**: Theoretical knowledge, thinking, facts, description
- **Acquisition**: Learning, study, building competence
- **Application**: Work, applying skills

---

## Application Levels

The compass can be applied at different levels:

### Sentence and Vocabulary Level

Check individual paragraphs or sentences:
- "Is this paragraph guiding action or providing knowledge?"
- "Is this sentence assuming the user is learning or working?"

### Document Level

Overall document assessment:
- "What is the main purpose of the entire document?"
- "What state is the target reader in?"

### Documentation Set Level

Planning documentation structure:
- "Does our documentation set cover all four types?"
- "Which types are missing or over-represented?"

---

## Common Confusion Scenarios

### Confusion 1: "Tutorial and How-to are similar, how to distinguish?"

**Key Difference**: Is the user learning or working?

| Tutorial | How-to |
|----------|--------|
| Learning experience | Task-oriented |
| Building basic competence | Assumes existing competence |
| Eliminates the unexpected | Prepares for the unexpected |
| Single path | Multiple branching paths |
| Teacher responsible | User responsible |

### Confusion 2: "Reference and Explanation both have theoretical knowledge"

**Key Difference**: Is the user looking up while working or understanding while learning?

| Reference | Explanation |
|-----------|-------------|
| Look up during work | Read while learning |
| Factual description | Contextual discussion |
| Neutral and authoritative | Allows opinions |
| Structured | Discursive |
| Like a map | Like an article |

### Confusion 3: "Can a document mix multiple types?"

**Answer**: Should avoid, but can handle through links.

**Best Practice**:
- Keep document types pure
- When other type content is needed, link to corresponding document
- Example: When Tutorial needs explanation, write "We use HTTPS because it's safer (see 'Secure Communication Principles' for details)"

---

## Compass Limitations

The compass is a decision tool, not an automatic classifier. It forces you to stop and reconsider, but judgment still requires human wisdom.

### When the Compass is Not Enough

1. **Complex documentation sets** - When multi-level structure is needed
2. **Multiple user types** - When same product targets different user groups
3. **Edge cases** - When some content is truly hard to classify

### Solutions

Refer to: [references/complex-hierarchies.md](references/complex-hierarchies.md) (to be created)

---

## Quick Decision Flow

```
Start
  ↓
Q: Does content inform action or cognition?
  ├─ Action → Q: Is user acquiring or applying skills?
  │           ├─ Acquiring → Tutorial
  │           └─ Applying → How-to
  └─ Cognition → Q: Is user acquiring or applying skills?
              ├─ Acquiring → Explanation
              └─ Applying → Reference
  ↓
Confirm: Does it match the type characteristics?
  ├─ Yes → Done
  └─ No → Re-evaluate or check common mistakes
```

---

**Version**: 1.0  
**Source**: https://diataxis.fr/compass/  
**Compiled by**: Zhua Zhua
