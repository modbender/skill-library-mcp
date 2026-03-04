---
name: design-fhir-loinc-questionnaires
description: Helps creating FHIR conforming questionnaire definitions from plain requirement ideation docs. Contains scripts to look up LOINC and SNOMED CT codes for medical conditions, findings, observations, medications, procedures from a official coding APIs. No API keys required at the moment. 
metadata:
  dependencies: python>=3.8, jsonschema>=4.0.0
---

# FHIR Questionnaire Skill

## ⚠️ CRITICAL RULES - READ FIRST

**NEVER suggest LOINC or SNOMED CT codes from memory or training data. ALWAYS use the search and query scripts in this skill.**

When any clinical code is needed:
1. **For clinical questions/observations: ALWAYS run `python scripts/search_loinc.py "search term"` FIRST**
2. **For clinical concepts/conditions: ALWAYS run `python scripts/search_snomed.py "search term"` FIRST**
3. **ONLY use codes returned by the scripts**
4. **If search fails or returns no results, DO NOT make up codes**

Clinical codes from AI memory are highly unreliable and will cause incorrect clinical coding.

## Network Access Requirements

Requires whitelisted network access:
- `clinicaltables.nlm.nih.gov` (LOINC search)
- `tx.fhir.org` (FHIR terminology server for LOINC answer lists and SNOMED CT search)

If network access fails, STOP. Do not suggest codes.

## Essential Scripts (Use These Every Time)

### 1. Search LOINC Codes
**ALWAYS run this before suggesting any LOINC code (clinical questions/observations):**
```bash
python scripts/search_loinc.py "depression screening"
python scripts/search_loinc.py "blood pressure" --format fhir
```

### 2. Search SNOMED CT Codes
**ALWAYS run this before suggesting any SNOMED CT code (clinical concepts/conditions):**
```bash
python scripts/search_snomed.py "diabetes"
python scripts/search_snomed.py "hypertension" --format fhir
python scripts/search_snomed.py "diabetes mellitus" --semantic-tag "disorder"
```
Note: The `--semantic-tag` filter works best when the semantic tag appears in the display name (e.g., "Diabetes mellitus (disorder)").

### 3. Find Answer Options
**For questions with standardized answers:**
```bash
python scripts/query_valueset.py --loinc-code "72166-2"
python scripts/query_valueset.py --loinc-code "72166-2" --format fhir
```

### 4. Validate Questionnaire
**Before finalizing:**
```bash
python scripts/validate_questionnaire.py questionnaire.json
```

## Templates

Start with `assets/templates/`:
- `minimal.json` - Bare bones structure
- `basic.json` - Simple questionnaire
- `advanced.json` - Complex with conditional logic

## Workflows

### Standardized Clinical Instruments (PHQ-9, GAD-7, etc.)
```bash
# Step 1: Find panel code (NEVER skip this)
python scripts/search_loinc.py "PHQ-9 panel"

# Step 2: Find answer options
python scripts/query_valueset.py --loinc-code "FOUND-CODE" --format fhir

# Step 3: See examples/templates
# Check references/examples.md for complete implementations
```

### Custom Organizational Questionnaires
```bash
# Step 1: Start with template
cp assets/templates/advanced.json my-questionnaire.json

# Step 2: For any clinical questions, search LOINC
python scripts/search_loinc.py "body weight"

# Step 3: Add answer options if available
python scripts/query_valueset.py --loinc-code "FOUND-CODE"

# Step 4: For custom questions without LOINC results, use inline answerOptions
# (no coding system needed - just code + display)

# Step 5: Validate
python scripts/validate_questionnaire.py my-questionnaire.json
```

### Custom Answer Lists (When LOINC Has No Match)

When LOINC search returns no suitable answer list, use **inline answerOption with system-less valueCoding** by default. This is the simplest, spec-compliant approach for custom answer lists:

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

**Do NOT invent a coding system URI.** Omitting `system` is valid FHIR and signals that these are local, questionnaire-scoped codes.

#### Opt-in: Reusable Welshare Coding System

If the user explicitly requests reusable codes that can be shared across questionnaires, use the Welshare namespace (`http://codes.welshare.app`) via the helper script:

```bash
python scripts/create_custom_codesystem.py --interactive
```

This creates a CodeSystem + ValueSet pair. To convert an inline answer list to the reusable format, add `"system": "http://codes.welshare.app/CodeSystem/<category>/<id>.json"` to each `valueCoding` and optionally reference the ValueSet via `answerValueSet`. See `references/loinc_guide.md` for details.

## Common Patterns

- **Conditional display**: Use `enableWhen` to show/hide questions
- **Repeating groups**: Set `"repeats": true` for medications, allergies, etc.
- **Standardized answers**: Use `query_valueset.py --loinc-code "CODE"` for LOINC-backed answer lists
- **Custom answers**: Use inline `answerOption` with `valueCoding` (no `system`) for non-standardized choices

See `references/examples.md` for complete working examples.

## Script Reference

### search_loinc.py - Find LOINC Codes
```bash
python scripts/search_loinc.py "blood pressure"
python scripts/search_loinc.py "depression" --limit 10 --format fhir
```

### search_snomed.py - Find SNOMED CT Codes
```bash
python scripts/search_snomed.py "diabetes"
python scripts/search_snomed.py "hypertension" --limit 10 --format fhir
python scripts/search_snomed.py "asthma" --format table
python scripts/search_snomed.py "diabetes mellitus" --semantic-tag "disorder"
```
**Formats:** `json` (default), `table`, `fhir`
**Semantic tags (when present in results):** `disorder`, `finding`, `procedure`, `body structure`, `substance`, `organism`
Note: Semantic tag filtering only works when tags are included in the display name from the terminology server.

### query_valueset.py - Find Answer Options
```bash
python scripts/query_valueset.py --loinc-code "72166-2"
python scripts/query_valueset.py --loinc-code "72166-2" --format fhir
python scripts/query_valueset.py --search "smoking"
```
**Alternative servers** (if tx.fhir.org fails):
- `--server https://hapi.fhir.org/baseR4`
- `--server https://r4.ontoserver.csiro.au/fhir`

### validate_questionnaire.py - Validate Structure
```bash
python scripts/validate_questionnaire.py questionnaire.json
python scripts/validate_questionnaire.py questionnaire.json --verbose
```

### extract_loinc_codes.py - Analyze Codes
```bash
python scripts/extract_loinc_codes.py questionnaire.json
python scripts/extract_loinc_codes.py questionnaire.json --validate
```

### create_custom_codesystem.py - Reusable Custom Codes (Opt-in)
```bash
python scripts/create_custom_codesystem.py --interactive
```
Only use when the user explicitly requests reusable codes across questionnaires. Uses the Welshare namespace: `http://codes.welshare.app`. Default for custom answers is inline `answerOption` without a coding system.

## Troubleshooting

- **No LOINC results**: Use broader search terms (e.g., "depression" not "PHQ-9 question 1")
- **Network errors**: Try alternative servers with `--server` flag
- **Validation errors**: Check `references/fhir_questionnaire_spec.md` for requirements
- **No answer list found**: Use inline `answerOption` with system-less `valueCoding` (code + display only). Do NOT fall back to a custom coding system unless the user explicitly requests it

## Deep Knowledge References

We've assembled deep knowledge for you to consult on specific topics. Checkout the index file on See [REFERENCE.md](REFERENCE.md) and drill down the knowledge path for highly detailed instructions on modelling questionnaires.

## Reference Links

- [FHIR Questionnaire Spec](https://hl7.org/fhir/questionnaire.html)
- [LOINC Database](https://loinc.org)
- [Complete Documentation](REFERENCE.md)
