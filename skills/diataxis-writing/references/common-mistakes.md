# Diataxis Common Mistake Patterns

Theory Source: https://diataxis.fr/

---

## Mistake 1: Type Conflation

### Problem Description

Mixing content from different types together, causing boundary blur.

### Common Manifestations

- Mixing大量 explanation into Tutorial
- Mixing Reference content into How-to
- Mixing instructional language into Reference
- Mixing operational steps into Explanation

### Why It's Harmful

1. **Destroys flow** - Readers forced to switch thinking modes
2. **Reduces usability** - Hard to find needed content
3. **Confuses purpose** - Unclear what document is trying to do

### Fix Methods

1. Identify confused content
2. Separate to corresponding type documents
3. Use links to connect related documents
4. Maintain purity of each type

### Example

**❌ Wrong (Explanation mixed into Tutorial)**:
```markdown
## Creating Django Project

First, we need to understand Django is an MTV framework,
its design philosophy is... (500 words of explanation)

Now run: django-admin startproject mysite
```

**✅ Correct**:
```markdown
## Creating Django Project

Run the following command:

```
django-admin startproject mysite
```

This will create a project structure containing...

> Want to understand Django's design philosophy? Read [Django Architecture Explanation](...)
```

---

## Mistake 2: Tutorial vs How-to Confusion

### Problem Description

Unable to distinguish Tutorial (learning-oriented) from How-to (task-oriented).

### Common Manifestations

**Tutorial written as How-to**:
- Assumes reader has competence
- Lacks learning guidance
- No expected narrative
- Lacks checkpoints

**How-to written as Tutorial**:
- Teaches basic knowledge
- Over-explains
- Single path
- Eliminates all surprises

### Fix Methods

Ask: **Is the user learning or working?**

- Learning → Tutorial
- Working → How-to

### Example

**❌ Tutorial written as How-to**:
```markdown
## Installing Python

Download Python installer, run, done.
```

**✅ Tutorial correct**:
```markdown
## Installing Python

In this tutorial, we will install Python and verify installation success.

### Step 1: Download Installer

Visit python.org, click download button...
You will see an installer file.

### Step 2: Run Installer

Double-click the installer. Note to check "Add Python to PATH" option.
...
```

---

## Mistake 3: Reference vs Explanation Confusion

### Problem Description

Unable to distinguish Reference (factual description) from Explanation (understanding discussion).

### Common Manifestations

**Reference written as Explanation**:
- Contains "why" explanations
- Discusses design decisions
- Adds opinions and judgments

**Explanation written as Reference**:
- Pure fact lists
- Lacks context and connections
- No multi-angle discussion

### Fix Methods

Ask: **Is user looking up while working or understanding while learning?**

- Looking up while working → Reference
- Understanding while learning → Explanation

### Example

**❌ Reference written as Explanation**:
```markdown
## API Parameters

`timeout` parameter set to 30 seconds, this is because we found through testing that
most requests complete within 30 seconds, and this value achieves good balance
between performance and reliability...
```

**✅ Reference correct**:
```markdown
## API Parameters

`timeout` (integer, default: 30)
Request timeout time (seconds). Requests not completed within this time will be terminated.
Valid range: 1-300
```

---

## Mistake 4: Structural Misalignment

### Problem Description

Document structure doesn't reflect content type or product architecture.

### Common Manifestations

**Reference structure doesn't reflect product architecture**:
- Organizing API reference by functionality
- Rather than by module/class

**Documentation set lacks four types**:
- Only Tutorial and Reference
- Missing How-to and Explanation

### Fix Methods

1. Reference organized by product architecture
2. Ensure all four types are covered
3. Use Diataxis map to check completeness

---

## Mistake 5: Boundary Blur

### Problem Description

Allowing boundaries between adjacent types to blur.

### Natural Affinity Relationships

```
Tutorial ←→ How-to (both guide action)
     ↓           ↓
Serve study   Serve work
     ↑           ↑
Explanation ←→ Reference (both provide knowledge)
```

### Common Manifestations

- Tutorial and How-to completely merged
- Explanation seeps into Reference
- How-to becomes Tutorial

### Fix Methods

1. Use compass tool to clearly classify
2. Keep type boundaries clear
3. Handle cross-needs through links rather than mixing

---

## Mistake 6: Misplacement

### Problem Description

Placing content in wrong type.

### Common Manifestations

**Explanation as Tutorial**:
- Reader wants to learn, but gets theoretical explanation
- Lacks practical steps

**Reference as Guide**:
- Reader wants to complete task, but sees parameter lists
- Lacks operational guidance

### Fix Methods

Use compass to reclassify:
1. Determine content type (action/cognition)
2. Determine user state (acquisition/application)
3. Move to correct type

---

## Mistake 7: Lacking Type Awareness

### Problem Description

Creator unaware of the four type distinctions.

### Common Manifestations

- Writing randomly, not considering type
- One document tries to meet all needs
- Chaotic structure

### Fix Methods

1. Learn Diataxis basic theory
2. Determine document type before writing
3. Apply corresponding type specifications

---

## Error Diagnosis Flow

```
Discover document problem
    ↓
Ask: What type of problem?
    ├─ Content mixed? → Type conflation
    ├─ Tutorial/How-to confused? → Mistake 2
    ├─ Reference/Explanation confused? → Mistake 3
    ├─ Structure chaotic? → Structural misalignment
    ├─ Boundaries unclear? → Boundary blur
    └─ Placement wrong? → Mistake 6
    ↓
Use compass to reclassify
    ↓
Separate confused content
    ↓
Move to correct type
```

---

## Prevention Strategies

### Before Writing

1. Use compass to determine type
2. Check corresponding checklist
3. Clarify document goal

### During Writing

1. Always pay attention to type boundaries
2. Avoid temptations (explanation, options, etc.)
3. Use links rather than mixing

### After Writing

1. Verify with checklist
2. Identify type conflation
3. Separate and reorganize

---

## Usage Recommendations

### When Diagnosing

Identify problems against mistake patterns.

### When Refactoring

Prioritize fixing type conflation and misplacement.

### When Preventing

Clarify type before writing, stay alert during writing.

---

**Version**: 1.0  
**Source**: https://diataxis.fr/  
**Compiled by**: Zhua Zhua
