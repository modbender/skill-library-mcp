# Reference Checklist

Theory Source: https://diataxis.fr/reference/

---

## Core Checklist Items

### Content Nature

- [ ] Is it purely descriptive?
- [ ] Is instruction and explanation avoided?
- [ ] Does it only state facts?

### Accuracy

- [ ] Is all information accurate?
- [ ] Are there any ambiguous or uncertain statements?
- [ ] Has it been verified?

### Completeness

- [ ] Are all necessary information covered?
- [ ] Are any parameters, options, or features missing?
- [ ] Are edge cases explained?

### Structure

- [ ] Does structure reflect product architecture?
- [ ] Are standard patterns used?
- [ ] Is it easy to look up?

### Consistency

- [ ] Is terminology consistent?
- [ ] Is format uniform?
- [ ] Is naming standardized?

### Conciseness

- [ ] Is it as concise as possible?
- [ ] Is redundancy avoided?
- [ ] Is decorative language removed?

### Examples

- [ ] Are usage examples provided?
- [ ] Are examples concise and non-distracting?
- [ ] Do examples illustrate typical usage?

### Warnings and Limitations

- [ ] Are usage limitations explained?
- [ ] Are necessary warnings provided?
- [ ] Are error conditions described?

---

## Language Style Checklist

### ✅ Correct Statements

- "Django's default logging configuration inherits Python's defaults"
- "Subcommands: a, b, c, d, e, f"
- "Must use X"
- "Must not apply Y unless Z"
- "Parameter X type is string"

### ❌ Avoid Statements

- "We recommend using debug=False because it's more secure" (advice - delete or move to How-to)
- "The history of this feature dates back to..." (explanation - link to Explanation)
- "To use run(), first create app..." (instruction - link to How-to)

---

## Common Mistakes Checklist

### ❌ Mistake: Mixing in Instruction

**Problem**: "To use this feature, you need to first..."

**Fix**: 
- Remove instruction parts
- Link to How-to Guide
- Keep purely descriptive

### ❌ Mistake: Mixing in Explanation

**Problem**: "This design is because of historical reasons..."

**Fix**:
- Remove explanation
- Link to Explanation
- Only describe "what it is"

### ❌ Mistake: Lacking Structure

**Problem**: Information organized chaotically

**Fix**:
- Organize by product architecture
- Use standard patterns
- Add clear hierarchy

### ❌ Mistake: Inconsistency

**Problem**: Inconsistent terminology or format

**Fix**:
- Unify terminology
- Unify format
- Establish naming conventions

### ❌ Mistake: Too Verbose

**Problem**: Contains unnecessary descriptions

**Fix**:
- Remove redundant information
- Keep concise
- Only retain necessary facts

---

## Quality Assessment

### Functional Quality

- [ ] **Accuracy**: Is information 100% accurate?
- [ ] **Completeness**: Is all necessary information covered?
- [ ] **Consistency**: Is terminology and format completely consistent?
- [ ] **Usability**: Can users quickly find needed information?

### Deep Quality

- [ ] **Lookup Flow**: Is it intuitive like consulting a map?
- [ ] **Structure Clarity**: Does structure reflect product architecture?
- [ ] **Trust**: Is information authoritative and reliable?
- [ ] **Aesthetics**: Is layout clear and readable?

---

## Quick Diagnosis

### If Reference Feels Wrong, Check:

1. **Users can't find information?** → Improve structure and index
2. **Information inaccurate?** → Verify and update
3. **Users ask "how to use"?** → Link to How-to
4. **Users ask "why"?** → Link to Explanation
5. **Content verbose?** → Remove non-essential information

---

## Reference Organization Patterns

### API Reference

```
Module/Class Name
├── Overview (one-sentence description)
├── Parameters/Attributes
│   ├── Name
│   ├── Type
│   ├── Description
│   └── Default Value
├── Methods
│   ├── Method Name
│   ├── Parameters
│   ├── Return Value
│   └── Example
└── Related Links
```

### Command Reference

```
Command Name
├── Syntax
├── Description (one sentence)
├── Subcommands/Options
│   ├── Name
│   ├── Description
│   └── Example
├── Return Value/Output
├── Error Conditions
└── Related Commands
```

### Configuration Reference

```
Configuration Item
├── Name
├── Type
├── Default Value
├── Valid Range
├── Description
└── Example
```

---

## Usage Recommendations

### During Writing

Always ask: "Is this purely descriptive?"

### After Writing

Verify accuracy of all information.

### When Refactoring

Identify and remove mixed instruction and explanation.

---

**Version**: 1.0  
**Source**: https://diataxis.fr/reference/  
**Compiled by**: Zhua Zhua
