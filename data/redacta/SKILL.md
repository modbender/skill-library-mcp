---
name: redacta
description: Redacta pseudonymises medical documents — replacing patient identifiers (NHS numbers, dates of birth, postcodes, phone numbers, hospital numbers) with labelled tokens so clinical content can be safely processed by AI. Built by PharmaTools.AI.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔒",
        "homepage": "https://pharmatools.ai",
      },
  }
---

# Redacta

Redacta pseudonymises medical documents before AI processing. It detects patient identifiers and replaces them with labelled tokens, preserving clinical meaning while protecting privacy.

## How It Works

When a user shares medical text, scan it for patient identifiers and replace them with pseudonymised tokens. The output should be clinically readable but contain no real patient data.

## What Gets Detected

### Structured Identifiers (regex-based)

Apply these pattern rules automatically:

**NHS Numbers** (UK)
- Format: 3-3-4 digits (e.g. `943 476 5919`) or 10 consecutive digits
- Replace with: `[NHS_NUMBER]`
- Validation: check digit using Modulus 11 algorithm when possible

**Dates of Birth / Dates**
- Formats: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY, YYYY-MM-DD, "3rd February 1985", "Feb 3, 1985"
- Context: dates near keywords like "DOB", "born", "date of birth", "age", "d.o.b"
- Replace with: `[DATE_OF_BIRTH]` (when contextually a DOB) or `[DATE]` (other dates)
- Preserve clinical dates when clearly not patient-identifying (e.g. "appointment on 15 March")

**UK Postcodes**
- Format: A9 9AA, A99 9AA, A9A 9AA, AA9 9AA, AA99 9AA, AA9A 9AA
- Replace with: `[POSTCODE]`

**Phone Numbers**
- UK formats: 07xxx, 01xxx, 02xxx, +44
- US formats: (xxx) xxx-xxxx, xxx-xxx-xxxx, +1
- Replace with: `[PHONE_NUMBER]`

**Email Addresses**
- Standard email pattern
- Replace with: `[EMAIL]`

**Hospital / MRN Numbers**
- Context: numbers near "hospital number", "MRN", "patient ID", "unit number", "case number"
- Replace with: `[HOSPITAL_NUMBER]`

**UK National Insurance Numbers**
- Format: 2 letters + 6 digits + 1 letter (e.g. AB123456C)
- Replace with: `[NI_NUMBER]`

### Contextual Identifiers (agent reasoning)

Use your understanding of clinical documents to detect:

**Patient Names**
- Look for names in: salutations ("Dear Mrs Jones"), headers ("Patient: John Smith"), references in body text
- Distinguish patient names from clinician names — do NOT redact doctor/nurse/consultant names unless explicitly asked
- Replace with: `[PATIENT_NAME]`
- If multiple patients mentioned, use: `[PATIENT_NAME_1]`, `[PATIENT_NAME_2]`

**Patient Addresses**
- Full or partial addresses (house number + street, or referenced near "address", "lives at", "resides")
- Replace with: `[ADDRESS]`
- Postcodes are handled separately above

**Ages**
- Specific ages that could identify when combined with other data: "82-year-old", "aged 47"
- Replace with: `[AGE]`
- Context matters: "children aged 5-12" (general) vs "a 73-year-old woman" (specific patient)

## Output Format

Return two sections:

### 1. Pseudonymised Document
The full document with all identifiers replaced by tokens. Preserve all formatting, paragraph breaks, and clinical content.

### 2. Redaction Report
A summary of what was found and replaced:

```
Redaction Report
================
Items pseudonymised: 7

- [NHS_NUMBER] × 1 (line 3)
- [PATIENT_NAME] × 2 (lines 1, 5)
- [DATE_OF_BIRTH] × 1 (line 2)
- [POSTCODE] × 1 (line 8)
- [PHONE_NUMBER] × 1 (line 9)
- [AGE] × 1 (line 4)

Clinical content preserved: ✓
Clinician names preserved: Dr. Sarah Chen, Mr. James Wright
```

## Rules

1. **Never output the original patient identifiers** in your response — only the pseudonymised version
2. **Preserve all clinical content** — medications, diagnoses, procedures, test results, clinical observations
3. **Preserve clinician names** by default — only redact if the user explicitly asks
4. **Preserve hospital/practice names** by default — these are institutional, not patient data
5. **When uncertain**, err on the side of redacting — false positives are safer than false negatives
6. **Dates**: appointment dates, procedure dates, and follow-up dates should be preserved unless they could identify the patient (e.g. a specific date of birth)
7. **Consistency**: the same identifier should get the same token throughout the document (e.g. every instance of the patient's name becomes `[PATIENT_NAME]`)

## Example

**Input:**
```
Dear Mrs Patricia Hartley,

DOB: 14/03/1952 (age 73)
NHS Number: 943 476 5919
Hospital Number: RXH-2847561

I am writing to inform you of the results of your recent investigations.
Mrs Hartley attended the cardiology outpatient clinic on 10 February 2026
under the care of Dr Sarah Chen.

Address: 14 Oakfield Road, Headingley, Leeds LS6 3PJ
Tel: 0113 278 4532
```

**Output:**
```
Dear [PATIENT_NAME],

DOB: [DATE_OF_BIRTH] (age [AGE])
NHS Number: [NHS_NUMBER]
Hospital Number: [HOSPITAL_NUMBER]

I am writing to inform you of the results of your recent investigations.
[PATIENT_NAME] attended the cardiology outpatient clinic on 10 February 2026
under the care of Dr Sarah Chen.

Address: [ADDRESS], [POSTCODE]
Tel: [PHONE_NUMBER]
```

## What This Skill Does NOT Do

- Store or transmit patient data
- Guarantee 100% detection (always review output)
- Replace formal data protection processes
- Provide legal compliance certification
- Process images or PDFs (text input only in v1)

## Privacy Note

This skill processes text locally within your AI agent session. No patient data is sent to external services. However, the text is processed by the underlying language model — ensure your model provider's data handling meets your organisation's requirements.

---

Built by [PharmaTools.AI](https://pharmatools.ai) — applied AI for pharma and healthcare.
