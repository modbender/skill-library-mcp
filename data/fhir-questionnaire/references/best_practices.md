# Best Practices for FHIR Questionnaires

Guidelines for designing effective, maintainable, and interoperable FHIR Questionnaires.

## Table of Contents
- Design Principles
- Structure and Organization
- Coding and Terminology
- Conditional Logic
- Answer Options
- Validation and Testing
- Internationalization
- Performance

## Design Principles

### 1. Keep It Simple

Start with the minimal necessary structure. Add complexity only when needed.

**Good:**
```json
{
  "linkId": "name",
  "type": "string",
  "text": "Full Name",
  "required": true
}
```

**Avoid overengineering:**
```json
{
  "linkId": "name",
  "type": "string",
  "text": "Full Name",
  "required": true,
  "maxLength": 255,
  "readOnly": false,
  "repeats": false,
  "definition": "http://example.org/StructureDefinition/patient-name",
  "code": [...]
}
```

### 2. User-Centric Design

Write questions in clear, plain language. Consider the end user's perspective.

**Good:** "Have you experienced chest pain in the last 24 hours?"

**Avoid:** "Presence of thoracic discomfort within the preceding diurnal cycle?"

### 3. Progressive Disclosure

Use conditional logic to show questions only when relevant.

```json
{
  "linkId": "has-allergies",
  "type": "boolean",
  "text": "Do you have any allergies?"
},
{
  "linkId": "allergy-details",
  "type": "text",
  "text": "Please describe your allergies",
  "enableWhen": [{
    "question": "has-allergies",
    "operator": "=",
    "answerBoolean": true
  }]
}
```

## Structure and Organization

### Use Groups Effectively

Group related questions together:

```json
{
  "linkId": "demographics",
  "type": "group",
  "text": "Demographics",
  "item": [
    {
      "linkId": "name",
      "type": "string",
      "text": "Full Name"
    },
    {
      "linkId": "dob",
      "type": "date",
      "text": "Date of Birth"
    }
  ]
}
```

### Logical linkId Hierarchy

Use a consistent linkId naming scheme:

**Hierarchical:**
```
demographics
  demographics.name
  demographics.dob
  demographics.address
    demographics.address.street
    demographics.address.city
```

**Sequential:**
```
q1, q2, q3, ...
```

**Semantic:**
```
patient-name
patient-dob
patient-address-street
```

### Use Prefixes for Display

Add prefixes to improve readability:

```json
{
  "linkId": "q1",
  "prefix": "1.",
  "type": "string",
  "text": "What is your name?"
}
```

## Coding and Terminology

### Always Use Standard Codes When Available

Prioritize LOINC for clinical questions, SNOMED CT for clinical concepts:

```json
{
  "linkId": "blood-pressure",
  "type": "group",
  "code": [{
    "system": "http://loinc.org",
    "code": "85354-9",
    "display": "Blood pressure panel"
  }]
}
```

### Dual Coding Strategy

Combine standard and local codes:

```json
{
  "code": [
    {
      "system": "http://loinc.org",
      "code": "8867-4",
      "display": "Heart rate"
    },
    {
      "system": "http://example.org/local-codes",
      "code": "VITAL-HR"
    }
  ]
}
```

### Document Code System Versions

Include version information for reproducibility:

```json
{
  "code": [{
    "system": "http://loinc.org",
    "version": "2.78",
    "code": "8867-4",
    "display": "Heart rate"
  }]
}
```

## Conditional Logic

### Keep enableWhen Simple

Avoid complex nested conditions. If logic becomes too complex, reconsider the questionnaire structure.

**Simple (preferred):**
```json
{
  "enableWhen": [{
    "question": "q1",
    "operator": "=",
    "answerBoolean": true
  }]
}
```

**Complex (use sparingly):**
```json
{
  "enableWhen": [
    {
      "question": "q1",
      "operator": "=",
      "answerBoolean": true
    },
    {
      "question": "q2",
      "operator": ">",
      "answerInteger": 18
    }
  ],
  "enableBehavior": "all"
}
```

### Forward References Only

enableWhen should only reference questions that appear earlier in the questionnaire:

**Good:**
```json
[
  {"linkId": "q1", "type": "boolean", "text": "Question 1"},
  {"linkId": "q2", "type": "string", "text": "Question 2",
   "enableWhen": [{"question": "q1", "operator": "=", "answerBoolean": true}]}
]
```

**Avoid (backward reference):**
```json
[
  {"linkId": "q1", "type": "boolean", "text": "Question 1",
   "enableWhen": [{"question": "q2", "operator": "=", "answerBoolean": true}]},
  {"linkId": "q2", "type": "string", "text": "Question 2"}
]
```

### Test Edge Cases

Verify behavior when:
- enableWhen question has no answer
- Multiple enableWhen conditions interact
- Nested groups with enableWhen
- Repeating items with enableWhen

## Answer Options

### Priority Order for Answer Lists

Always follow this priority when defining answer options:

#### 1. LOINC Standardized Answer Lists (Best for Clinical)

Many LOINC codes come with standardized answer lists. Always check first:

```bash
# Discover answer options for a LOINC code
.venv/bin/python scripts/query_valueset.py --loinc-code "72166-2"
```

Then use the discovered ValueSet:

```json
{
  "linkId": "smoking-status",
  "type": "choice",
  "code": [{
    "system": "http://loinc.org",
    "code": "72166-2",
    "display": "Tobacco smoking status"
  }],
  "text": "Tobacco smoking status",
  "answerValueSet": "http://loinc.org/vs/LL2201-3"
}
```

#### 2. Standard FHIR ValueSets (For Common Administrative Data)

```json
{
  "linkId": "gender",
  "type": "choice",
  "text": "Gender",
  "answerValueSet": "http://hl7.org/fhir/ValueSet/administrative-gender"
}
```

#### 3. Inline Custom Answer Lists (Default for Non-Standardized)

When no LOINC or standard answer list exists, use inline `answerOption` with system-less `valueCoding`. This is the **default approach** for custom answer lists:

```json
{
  "linkId": "sleep-quality",
  "type": "choice",
  "text": "How would you rate your sleep quality?",
  "answerOption": [
    {"valueCoding": {"code": "good", "display": "Good"}},
    {"valueCoding": {"code": "fair", "display": "Fair"}},
    {"valueCoding": {"code": "poor", "display": "Poor"}}
  ]
}
```

Omitting `system` is valid FHIR and signals that these are questionnaire-scoped codes. This is appropriate for any number of custom options, not just short lists.

#### 4. Reusable Custom Coding System (Opt-in Only)

Only use a custom coding system (e.g., Welshare namespace `http://codes.welshare.app`) when the user **explicitly requests** reusable codes shared across multiple questionnaires. See `references/loinc_guide.md` for details.

**When to use each approach:**
- **LOINC answer lists**: For any LOINC-coded question (preferred for interoperability)
- **Standard FHIR ValueSets**: For common demographics and administrative data
- **Inline answerOption (no system)**: Default for all custom answer lists
- **Reusable coding system**: Only when the user explicitly requests cross-questionnaire code reuse

### Provide Display Values

Always include display text for codes:

```json
{
  "valueCoding": {
    "system": "http://snomed.info/sct",
    "code": "373066001",
    "display": "Yes"
  }
}
```

### Order Matters

List answer options in logical order:
- Chronological (e.g., dates, time periods)
- Severity (mild → moderate → severe)
- Frequency (never → sometimes → often → always)
- Alphabetical (for long lists)

## Validation and Testing

### Use the Validation Script

Always validate before publishing:

```bash
python scripts/validate_questionnaire.py questionnaire.json --verbose
```

### Test Scenarios

1. **Complete the questionnaire** as intended
2. **Skip optional questions** to test required field handling
3. **Trigger all conditional logic** paths
4. **Test with invalid data** (if possible)
5. **Test repeating groups** (add/remove items)

### Validate linkId Uniqueness

```bash
# Check for duplicate linkIds
cat questionnaire.json | jq '.. | .linkId? | select(. != null)' | sort | uniq -d
```

### Check enableWhen References

Ensure all enableWhen question references exist:

```bash
# Extract all enableWhen references
cat questionnaire.json | jq '.. | .enableWhen[]?.question' | sort | uniq
```

## Internationalization

### Support Multiple Languages

Use extensions for translations:

```json
{
  "linkId": "name",
  "type": "string",
  "text": "Full Name",
  "_text": {
    "extension": [{
      "url": "http://hl7.org/fhir/StructureDefinition/translation",
      "extension": [
        {
          "url": "lang",
          "valueCode": "es"
        },
        {
          "url": "content",
          "valueString": "Nombre Completo"
        }
      ]
    }]
  }
}
```

### Cultural Considerations

- Date formats (MM/DD/YYYY vs DD/MM/YYYY)
- Name ordering (given-family vs family-given)
- Gender and sex categories
- Measurement units (imperial vs metric)

## Performance

### Minimize Questionnaire Size

- Avoid deeply nested groups (limit to 3-4 levels)
- Use references to external resources rather than embedding
- Split very long questionnaires into multiple linked questionnaires

### Optimize ValueSet Usage

- Use answerValueSet references instead of expanding all codes inline
- Cache frequently used ValueSets
- Consider using small, focused ValueSets

### Lazy Loading Strategy

For large questionnaires:
1. Load basic structure first
2. Load conditional sections on demand
3. Retrieve ValueSets as needed

## Metadata Best Practices

### Published Questionnaires Must Have

```json
{
  "url": "http://example.org/fhir/Questionnaire/intake",
  "version": "1.0.0",
  "status": "active",
  "date": "2024-01-01",
  "publisher": "Example Healthcare"
}
```

### Use Semantic Versioning

- **Major** (1.0.0 → 2.0.0): Breaking changes (incompatible with previous responses)
- **Minor** (1.0.0 → 1.1.0): New questions, non-breaking changes
- **Patch** (1.0.0 → 1.0.1): Typos, display text improvements

### Include Contact Information

```json
{
  "contact": [{
    "name": "Clinical Informatics Team",
    "telecom": [{
      "system": "email",
      "value": "informatics@example.org"
    }]
  }]
}
```

## Common Antipatterns to Avoid

### 1. Overly Complex Conditional Logic

**Problem:** Too many nested enableWhen conditions
**Solution:** Simplify structure, split into multiple questionnaires

### 2. Inconsistent linkId Naming

**Problem:** Mixing styles (q1, patient-name, demographics.dob)
**Solution:** Choose one scheme and stick with it

### 3. Missing Required Fields

**Problem:** Forgetting resourceType, status
**Solution:** Use validation tools early and often

### 4. Backward enableWhen References

**Problem:** Referencing questions that come later
**Solution:** Reorder questions or restructure logic

### 5. Inventing Fake Coding Systems for Custom Answers

**Problem:** Creating non-existent `system` URLs like `http://example.org/my-codes` for custom answers
**Solution:** Omit `system` for inline custom answers (valid FHIR), or use standard codes (LOINC, SNOMED). Only use a custom coding system if explicitly building a reusable code library

### 6. No Versioning for Published Questionnaires

**Problem:** Unable to track changes over time
**Solution:** Always version published questionnaires

### 7. Unclear Question Text

**Problem:** Medical jargon, ambiguous wording
**Solution:** Use plain language, test with users

## Testing Checklist

Before publishing a questionnaire:

- [ ] Validate JSON structure
- [ ] Run validation script
- [ ] Check linkId uniqueness
- [ ] Verify all enableWhen references exist
- [ ] Test all conditional paths
- [ ] Verify answerValueSet URLs are accessible
- [ ] Check LOINC codes are correct
- [ ] Test with real users (if possible)
- [ ] Review for accessibility
- [ ] Verify internationalization needs
- [ ] Document version changes
- [ ] Update metadata (date, version, status)

## Resources

- **FHIR Questionnaire Best Practices**: http://hl7.org/fhir/questionnaire.html
- **HL7 Structured Data Capture IG**: http://hl7.org/fhir/uv/sdc/
- **Form Design Best Practices**: Nielsen Norman Group research
- **Accessibility Guidelines**: WCAG 2.1 for forms
