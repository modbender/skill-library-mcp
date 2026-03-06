# FHIR Questionnaire Reference Documentation

This document provides a navigation guide to all reference materials for the FHIR Questionnaire skill.

## Table of Contents

### Core Specification
- **[fhir_questionnaire_spec.md](references/fhir_questionnaire_spec.md)** - Complete FHIR R4 Questionnaire specification
  - Element definitions and data types
  - Item types (string, boolean, choice, group, etc.)
  - Conditional logic (enableWhen)
  - Answer options (answerOption, answerValueSet)
  - Validation rules and constraints

### Clinical Terminology
- **[loinc_guide.md](references/loinc_guide.md)** - LOINC coding guide and reference
  - Common LOINC questionnaire codes (PHQ-9, GAD-7, vital signs, demographics)
  - Search strategies and best practices
  - LOINC code structure and anatomy
  - Creating custom codes when LOINC isn't suitable
  - Answer list discovery

- **[snomed_guide.md](references/snomed_guide.md)** - SNOMED CT usage for clinical concepts (conditions, findings, procedures)

### Best Practices
- **[best_practices.md](references/best_practices.md)** - Design principles and guidelines
  - Questionnaire design principles
  - Coding and terminology guidelines
  - Conditional logic patterns
  - Validation checklist
  - Common antipatterns to avoid

### Examples
- **[examples.md](references/examples.md)** - Complete working examples
  - Simple patient intake questionnaire
  - PHQ-2 depression screening (standardized clinical instrument)
  - Conditional logic patterns
  - Repeating groups (medications, allergies)
  - Complex medical history questionnaire

### Schema
- **[schema/questionnaire.schema.json](references/schema/questionnaire.schema.json)** - JSON Schema definition
  - Authoritative source for FHIR R4 Questionnaire structure
  - Used by validation scripts
  - Machine-readable specification

## When to Read Each Reference

### Planning Phase
Start with:
1. **best_practices.md** - Understand design principles
2. **examples.md** - See complete working examples

### Implementation Phase
Reference as needed:
1. **fhir_questionnaire_spec.md** - Look up specific element definitions
2. **loinc_guide.md** - Find appropriate clinical codes
3. **schema/questionnaire.schema.json** - Verify structure requirements

### Validation Phase
Use:
1. **best_practices.md** - Review validation checklist
2. **fhir_questionnaire_spec.md** - Confirm conformance requirements
