
## SNOMED CT for Clinical Concepts

While LOINC is ideal for clinical questions and observations, **SNOMED CT** is the preferred terminology for clinical concepts like conditions, findings, and procedures.

### When to Use SNOMED CT vs LOINC

**Use LOINC for:**
- Clinical questions (e.g., "Do you have diabetes?")
- Observations and measurements (e.g., blood pressure, body weight)
- Standardized assessment instruments (PHQ-9, GAD-7)
- Answer lists for coded responses

**Use SNOMED CT for:**
- Clinical conditions and diagnoses (e.g., Diabetes mellitus, Hypertension)
- Clinical findings (e.g., Fever, Cough)
- Procedures (e.g., Appendectomy, Blood draw)
- Body structures (e.g., Heart, Lung)
- Answer options representing clinical concepts

### Searching for SNOMED CT Codes

**ALWAYS use the search script - NEVER suggest SNOMED codes from memory:**

```bash
# Search for a condition
python scripts/search_snomed.py "diabetes"

# Search with semantic tag filter
python scripts/search_snomed.py "appendectomy" --semantic-tag "procedure"

# Get FHIR-formatted output
python scripts/search_snomed.py "hypertension" --format fhir
```

### Using SNOMED CT in Questionnaires

Example with SNOMED CT coded answer options:

```json
{
  "linkId": "chronic-conditions",
  "type": "choice",
  "repeats": true,
  "code": [{
    "system": "http://loinc.org",
    "code": "75618-9",
    "display": "Do you have any of these conditions?"
  }],
  "text": "Do you have any of these conditions?",
  "answerOption": [
    {
      "valueCoding": {
        "system": "http://snomed.info/sct",
        "code": "73211009",
        "display": "Diabetes mellitus"
      }
    },
    {
      "valueCoding": {
        "system": "http://snomed.info/sct",
        "code": "38341003",
        "display": "Hypertension"
      }
    },
    {
      "valueCoding": {
        "system": "http://snomed.info/sct",
        "code": "195967001",
        "display": "Asthma"
      }
    }
  ]
}
```

### SNOMED CT Semantic Tags

SNOMED CT concepts include semantic tags to clarify their meaning:

- **disorder** - Diseases and conditions (e.g., "Diabetes mellitus (disorder)")
- **finding** - Clinical findings (e.g., "Fever (finding)")
- **procedure** - Clinical procedures (e.g., "Appendectomy (procedure)")
- **body structure** - Anatomical structures (e.g., "Heart structure (body structure)")
- **substance** - Chemical substances (e.g., "Glucose (substance)")
- **organism** - Organisms (e.g., "Virus (organism)")

Use the `--semantic-tag` filter to narrow your search results.

### SNOMED CT System URI

Always use the official SNOMED CT system URI:
```
http://snomed.info/sct
```

### Best Practices

1. **Always search, never guess** - Use `search_snomed.py` for all SNOMED codes
2. **Choose the right granularity** - Use specific codes when appropriate (e.g., "Type 2 diabetes mellitus" vs generic "Diabetes mellitus")
3. **Consider semantic tags** - Filter by semantic tag to find the right concept type
4. **Combine with LOINC** - Use LOINC for the question code and SNOMED for answer options

### Links

- **SNOMED-LOINC Mapping**: For converting between terminologies
- **SNOMED CT Browser**: https://browser.ihtsdotools.org/
- **SNOMED International**: https://www.snomed.org/