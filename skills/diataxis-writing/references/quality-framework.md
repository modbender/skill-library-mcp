# Diataxis Quality Assessment Framework

Theory Source: https://diataxis.fr/quality/

---

## Two Types of Quality

Diataxis distinguishes two types of documentation quality:

1. **Functional Quality** - Objectively measurable standards
2. **Deep Quality** - Subjective experiential qualities

---

## Functional Quality

Standards documentation must meet:

### Accuracy
- Is information correct?
- Are code examples runnable?
- Is data up to date?

### Completeness
- Is all necessary content covered?
- Is any key information missing?
- Are edge cases explained?

### Consistency
- Is terminology unified?
- Is format standardized?
- Is style coherent?

### Usefulness
- Does it meet user needs?
- Does it solve practical problems?
- Is it easy to use?

### Precision
- Is expression precise?
- Is there any ambiguity?
- Are parameters and limitations clear?

### Characteristics

- **Independent**: Aspects are independent of each other (can be accurate but incomplete)
- **Objective**: Can be measured and verified
- **Constraining**: Burdens and constraints for creators
- **Necessary**: Prerequisite for Deep Quality

---

## Deep Quality

Excellence qualities of documentation:

### Flow
- Is the usage process smooth?
- Is there natural rhythm?
- Does it match user thinking flow?

### Fitting to Human Needs
- Does it fit actual user needs?
- Is user emotion considered?
- Is it humanized?

### Anticipating the User
- Does it anticipate user questions?
- Does it answer doubts in advance?
- Does it feel like a helper handing you tools?

### Beauty
- Is layout aesthetically pleasing?
- Is structure elegant?
- Is reading enjoyable?

### Feeling Good to Use
- Is the overall experience good?
- Are users satisfied?
- Do they want to use it again?

### Characteristics

- **Interdependent**: Aspects are interconnected (flow relates to anticipation)
- **Subjective**: Assessed based on human experience
- **Creative**: Requires invention rather than following constraints
- **Conditional**: Depends on Functional Quality

---

## Relationship Between Two Qualities

```
Functional Quality          Deep Quality
─────────────────          ────────────
Independent characteristics   Interdependent characteristics
Objective                     Subjective
Measured against the world    Assessed against the human
Condition for Deep Quality    Conditional on Functional Quality
Aspects of constraint         Aspects of liberation
```

### Key Insights

1. **Functional Quality deficiencies destroy Deep Quality**
   - Inaccurate documentation, no matter how beautiful, is useless
   - Incomplete information breaks the sense of flow

2. **Functional Quality sufficiency doesn't guarantee Deep Quality**
   - Can be accurate, complete, consistent, but still hard to use
   - Deep Quality requires additional creative work

3. **Diataxis mainly contributes to Deep Quality**
   - Helps documentation fit user needs through classification
   - Preserves flow by preventing type conflation

---

## Quality Assessment Methods

### Functional Quality Assessment

**Can be measured**:
- Accuracy: Verify information correctness
- Completeness: Check against requirement list
- Consistency: Check terminology and format
- Usability: User testing

**Assessment questions**:
- "Is this information correct?"
- "Is anything missing?"
- "Is terminology unified?"
- "Can users complete tasks?"

### Deep Quality Assessment

**Requires judgment**:
- Flow: Experience assessment
- Aesthetics: Aesthetic judgment
- Anticipation: Empathy judgment

**Assessment questions**:
- "Does this documentation feel good?"
- "Is the usage process smooth?"
- "Does it anticipate my needs?"
- "Do I want to read it again?"

---

## How Diataxis Improves Quality

### Exposing Functional Quality Problems

Diataxis helps discover problems:

1. **Structural problems**
   - Reference documentation structure doesn't reflect product architecture → Clearly visible
   - Type conflation → Problems stand out

2. **Content problems**
   - Explanation mixed into Tutorial → Breaks learning flow
   - Missing branches in How-to → Unrealistic

### Creating Deep Quality

Diataxis helps create excellence:

1. **Fitting user needs**
   - Categories based on user needs
   - Each type corresponds to specific needs

2. **Preserving flow**
   - Prevents type conflation
   - Avoids rhythm-disrupting digressions

3. **Organizational beauty**
   - Clear four-quadrant structure
   - Logically coherent framework

---

## Quality Improvement Process

### Step 1: Ensure Functional Quality

1. Verify accuracy
2. Check completeness
3. Ensure consistency
4. Test usability

### Step 2: Pursue Deep Quality

1. Assess flow
2. Check if it fits user needs
3. Add anticipatory elements
4. Optimize aesthetics

### Step 3: Continuous Iteration

1. Collect user feedback
2. Identify quality issues
3. Prioritize fixing Functional problems
4. Gradually improve Deep Quality

---

## Quick Diagnosis

### Functional Quality Problem Signals

- ❌ "This information is outdated"
- ❌ "This is unclear"
- ❌ "Terminology is inconsistent"
- ❌ "Following steps failed"

### Deep Quality Problem Signals

- ❌ "Reading is tiring"
- ❌ "Feels awkward"
- ❌ "Always can't find what's needed"
- ❌ "Don't know why it's like this"

---

## Usage Recommendations

### During Writing

Prioritize ensuring Functional Quality while paying attention to Deep Quality.

### After Writing

Check with Functional Quality first, then assess with Deep Quality.

### When Refactoring

Fix Functional problems first, then optimize Deep Quality.

---

**Version**: 1.0  
**Source**: https://diataxis.fr/quality/  
**Compiled by**: Zhua Zhua
