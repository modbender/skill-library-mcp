# FHIR Questionnaire Examples

Complete examples of various questionnaire types and patterns.

## Table of Contents
- Simple Patient Intake
- PHQ-2 Depression Screening (Standardized)
- Conditional Logic Example
- Repeating Groups Example
- Choice Questions with ValueSets
- Complex Medical History

## Simple Patient Intake

A basic patient intake questionnaire with demographics and contact information.

```json
{
  "resourceType": "Questionnaire",
  "id": "patient-intake-simple",
  "url": "http://example.org/fhir/Questionnaire/patient-intake-simple",
  "version": "1.0.0",
  "name": "SimplePatientIntake",
  "title": "Simple Patient Intake Form",
  "status": "active",
  "date": "2024-01-01",
  "publisher": "Example Healthcare",
  "description": "Basic patient intake questionnaire for new patients",
  "item": [
    {
      "linkId": "demographics",
      "type": "group",
      "text": "Demographics",
      "item": [
        {
          "linkId": "name",
          "type": "string",
          "text": "Full Name",
          "required": true
        },
        {
          "linkId": "dob",
          "type": "date",
          "text": "Date of Birth",
          "required": true
        },
        {
          "linkId": "gender",
          "type": "choice",
          "text": "Gender",
          "answerValueSet": "http://hl7.org/fhir/ValueSet/administrative-gender",
          "required": true
        }
      ]
    },
    {
      "linkId": "contact",
      "type": "group",
      "text": "Contact Information",
      "item": [
        {
          "linkId": "phone",
          "type": "string",
          "text": "Phone Number",
          "required": true
        },
        {
          "linkId": "email",
          "type": "string",
          "text": "Email Address"
        },
        {
          "linkId": "address",
          "type": "text",
          "text": "Home Address",
          "required": true
        }
      ]
    }
  ]
}
```

## PHQ-2 Depression Screening

Standardized questionnaire using LOINC codes (shortened version of PHQ-9).

```json
{
  "resourceType": "Questionnaire",
  "id": "phq-2",
  "url": "http://example.org/fhir/Questionnaire/phq-2",
  "version": "1.0.0",
  "name": "PHQ2",
  "title": "Patient Health Questionnaire-2 (PHQ-2)",
  "status": "active",
  "code": [{
    "system": "http://loinc.org",
    "code": "69737-5",
    "display": "PHQ-2 quick depression assessment panel"
  }],
  "item": [
    {
      "linkId": "phq2-instructions",
      "type": "display",
      "text": "Over the last 2 weeks, how often have you been bothered by any of the following problems?"
    },
    {
      "linkId": "phq2-1",
      "prefix": "1.",
      "type": "choice",
      "text": "Little interest or pleasure in doing things",
      "required": true,
      "code": [{
        "system": "http://loinc.org",
        "code": "44250-9"
      }],
      "answerOption": [
        {
          "valueCoding": {
            "system": "http://loinc.org",
            "code": "LA6568-5",
            "display": "Not at all"
          }
        },
        {
          "valueCoding": {
            "system": "http://loinc.org",
            "code": "LA6569-3",
            "display": "Several days"
          }
        },
        {
          "valueCoding": {
            "system": "http://loinc.org",
            "code": "LA6570-1",
            "display": "More than half the days"
          }
        },
        {
          "valueCoding": {
            "system": "http://loinc.org",
            "code": "LA6571-9",
            "display": "Nearly every day"
          }
        }
      ]
    },
    {
      "linkId": "phq2-2",
      "prefix": "2.",
      "type": "choice",
      "text": "Feeling down, depressed, or hopeless",
      "required": true,
      "code": [{
        "system": "http://loinc.org",
        "code": "44255-8"
      }],
      "answerOption": [
        {
          "valueCoding": {
            "system": "http://loinc.org",
            "code": "LA6568-5",
            "display": "Not at all"
          }
        },
        {
          "valueCoding": {
            "system": "http://loinc.org",
            "code": "LA6569-3",
            "display": "Several days"
          }
        },
        {
          "valueCoding": {
            "system": "http://loinc.org",
            "code": "LA6570-1",
            "display": "More than half the days"
          }
        },
        {
          "valueCoding": {
            "system": "http://loinc.org",
            "code": "LA6571-9",
            "display": "Nearly every day"
          }
        }
      ]
    }
  ]
}
```

## Conditional Logic Example

Questionnaire demonstrating enableWhen conditions.

```json
{
  "resourceType": "Questionnaire",
  "id": "conditional-example",
  "url": "http://example.org/fhir/Questionnaire/conditional-example",
  "version": "1.0.0",
  "name": "ConditionalExample",
  "title": "Conditional Logic Example",
  "status": "draft",
  "item": [
    {
      "linkId": "has-symptoms",
      "type": "boolean",
      "text": "Have you experienced any symptoms in the past week?",
      "required": true
    },
    {
      "linkId": "symptom-details",
      "type": "group",
      "text": "Symptom Details",
      "enableWhen": [{
        "question": "has-symptoms",
        "operator": "=",
        "answerBoolean": true
      }],
      "item": [
        {
          "linkId": "symptom-type",
          "type": "choice",
          "text": "What type of symptoms?",
          "answerOption": [
            {"valueCoding": {"code": "fever", "display": "Fever"}},
            {"valueCoding": {"code": "cough", "display": "Cough"}},
            {"valueCoding": {"code": "fatigue", "display": "Fatigue"}},
            {"valueCoding": {"code": "other", "display": "Other"}}
          ]
        },
        {
          "linkId": "other-symptom",
          "type": "string",
          "text": "Please describe other symptoms",
          "enableWhen": [{
            "question": "symptom-type",
            "operator": "=",
            "answerCoding": {
              "code": "other"
            }
          }]
        },
        {
          "linkId": "symptom-severity",
          "type": "choice",
          "text": "How would you rate the severity?",
          "answerOption": [
            {"valueCoding": {"code": "mild", "display": "Mild"}},
            {"valueCoding": {"code": "moderate", "display": "Moderate"}},
            {"valueCoding": {"code": "severe", "display": "Severe"}}
          ]
        }
      ]
    },
    {
      "linkId": "seek-treatment",
      "type": "boolean",
      "text": "Have you sought medical treatment for severe symptoms?",
      "enableWhen": [
        {
          "question": "has-symptoms",
          "operator": "=",
          "answerBoolean": true
        },
        {
          "question": "symptom-severity",
          "operator": "=",
          "answerCoding": {
            "code": "severe"
          }
        }
      ],
      "enableBehavior": "all"
    }
  ]
}
```

## Repeating Groups Example

Questionnaire with repeating medication entries.

```json
{
  "resourceType": "Questionnaire",
  "id": "medications",
  "url": "http://example.org/fhir/Questionnaire/medications",
  "version": "1.0.0",
  "name": "MedicationList",
  "title": "Current Medications",
  "status": "active",
  "item": [
    {
      "linkId": "instructions",
      "type": "display",
      "text": "Please list all medications you are currently taking, including over-the-counter medications and supplements."
    },
    {
      "linkId": "has-medications",
      "type": "boolean",
      "text": "Are you currently taking any medications?",
      "required": true
    },
    {
      "linkId": "medication",
      "type": "group",
      "text": "Medication",
      "repeats": true,
      "enableWhen": [{
        "question": "has-medications",
        "operator": "=",
        "answerBoolean": true
      }],
      "item": [
        {
          "linkId": "medication.name",
          "type": "string",
          "text": "Medication Name",
          "required": true
        },
        {
          "linkId": "medication.dosage",
          "type": "string",
          "text": "Dosage (e.g., 10mg)",
          "required": true
        },
        {
          "linkId": "medication.frequency",
          "type": "choice",
          "text": "How often do you take it?",
          "answerOption": [
            {"valueCoding": {"code": "daily", "display": "Daily"}},
            {"valueCoding": {"code": "twice-daily", "display": "Twice Daily"}},
            {"valueCoding": {"code": "weekly", "display": "Weekly"}},
            {"valueCoding": {"code": "as-needed", "display": "As Needed"}}
          ]
        },
        {
          "linkId": "medication.reason",
          "type": "string",
          "text": "Reason for taking (optional)"
        }
      ]
    }
  ]
}
```

## Choice Questions with ValueSets

Examples using various answer patterns.

```json
{
  "resourceType": "Questionnaire",
  "id": "choice-examples",
  "url": "http://example.org/fhir/Questionnaire/choice-examples",
  "version": "1.0.0",
  "name": "ChoiceExamples",
  "title": "Choice Question Examples",
  "status": "draft",
  "item": [
    {
      "linkId": "gender",
      "type": "choice",
      "text": "Gender (using ValueSet reference)",
      "answerValueSet": "http://hl7.org/fhir/ValueSet/administrative-gender"
    },
    {
      "linkId": "yes-no",
      "type": "choice",
      "text": "Simple Yes/No (inline options)",
      "answerOption": [
        {
          "valueCoding": {
            "system": "http://terminology.hl7.org/CodeSystem/v2-0136",
            "code": "Y",
            "display": "Yes"
          }
        },
        {
          "valueCoding": {
            "system": "http://terminology.hl7.org/CodeSystem/v2-0136",
            "code": "N",
            "display": "No"
          }
        }
      ]
    },
    {
      "linkId": "pain-scale",
      "type": "choice",
      "text": "Pain level (0-10)",
      "answerOption": [
        {"valueInteger": 0},
        {"valueInteger": 1},
        {"valueInteger": 2},
        {"valueInteger": 3},
        {"valueInteger": 4},
        {"valueInteger": 5},
        {"valueInteger": 6},
        {"valueInteger": 7},
        {"valueInteger": 8},
        {"valueInteger": 9},
        {"valueInteger": 10}
      ]
    },
    {
      "linkId": "education",
      "type": "choice",
      "text": "Highest level of education",
      "answerOption": [
        {"valueCoding": {"code": "less-hs", "display": "Less than high school"}},
        {"valueCoding": {"code": "hs", "display": "High school graduate"}},
        {"valueCoding": {"code": "some-college", "display": "Some college"}},
        {"valueCoding": {"code": "bachelors", "display": "Bachelor's degree"}},
        {"valueCoding": {"code": "graduate", "display": "Graduate degree"}}
      ]
    },
    {
      "linkId": "languages",
      "type": "open-choice",
      "text": "Languages spoken (can specify other)",
      "repeats": true,
      "answerOption": [
        {"valueCoding": {"code": "en", "display": "English"}},
        {"valueCoding": {"code": "es", "display": "Spanish"}},
        {"valueCoding": {"code": "fr", "display": "French"}},
        {"valueCoding": {"code": "de", "display": "German"}},
        {"valueCoding": {"code": "zh", "display": "Chinese"}}
      ]
    }
  ]
}
```

## Complex Medical History

Comprehensive medical history with multiple sections.

```json
{
  "resourceType": "Questionnaire",
  "id": "medical-history",
  "url": "http://example.org/fhir/Questionnaire/medical-history",
  "version": "1.0.0",
  "name": "MedicalHistory",
  "title": "Comprehensive Medical History",
  "status": "active",
  "date": "2024-01-01",
  "publisher": "Example Healthcare",
  "item": [
    {
      "linkId": "chronic-conditions",
      "type": "group",
      "text": "Chronic Conditions",
      "item": [
        {
          "linkId": "has-chronic",
          "type": "boolean",
          "text": "Do you have any chronic medical conditions?",
          "required": true
        },
        {
          "linkId": "chronic-list",
          "type": "open-choice",
          "text": "Select all that apply",
          "repeats": true,
          "enableWhen": [{
            "question": "has-chronic",
            "operator": "=",
            "answerBoolean": true
          }],
          "answerOption": [
            {"valueCoding": {"system": "http://snomed.info/sct", "code": "44054006", "display": "Diabetes"}},
            {"valueCoding": {"system": "http://snomed.info/sct", "code": "38341003", "display": "Hypertension"}},
            {"valueCoding": {"system": "http://snomed.info/sct", "code": "195967001", "display": "Asthma"}},
            {"valueCoding": {"system": "http://snomed.info/sct", "code": "49601007", "display": "Cardiovascular disease"}}
          ]
        }
      ]
    },
    {
      "linkId": "allergies",
      "type": "group",
      "text": "Allergies",
      "code": [{
        "system": "http://loinc.org",
        "code": "48765-2",
        "display": "Allergies"
      }],
      "item": [
        {
          "linkId": "has-allergies",
          "type": "boolean",
          "text": "Do you have any known allergies?",
          "required": true
        },
        {
          "linkId": "allergy",
          "type": "group",
          "text": "Allergy",
          "repeats": true,
          "enableWhen": [{
            "question": "has-allergies",
            "operator": "=",
            "answerBoolean": true
          }],
          "item": [
            {
              "linkId": "allergy.substance",
              "type": "string",
              "text": "Allergen (e.g., peanuts, penicillin)"
            },
            {
              "linkId": "allergy.reaction",
              "type": "string",
              "text": "Reaction (e.g., rash, anaphylaxis)"
            },
            {
              "linkId": "allergy.severity",
              "type": "choice",
              "text": "Severity",
              "answerOption": [
                {"valueCoding": {"code": "mild", "display": "Mild"}},
                {"valueCoding": {"code": "moderate", "display": "Moderate"}},
                {"valueCoding": {"code": "severe", "display": "Severe"}}
              ]
            }
          ]
        }
      ]
    },
    {
      "linkId": "surgeries",
      "type": "group",
      "text": "Surgical History",
      "item": [
        {
          "linkId": "has-surgeries",
          "type": "boolean",
          "text": "Have you had any surgeries?",
          "required": true
        },
        {
          "linkId": "surgery",
          "type": "group",
          "text": "Surgery",
          "repeats": true,
          "enableWhen": [{
            "question": "has-surgeries",
            "operator": "=",
            "answerBoolean": true
          }],
          "item": [
            {
              "linkId": "surgery.type",
              "type": "string",
              "text": "Type of surgery"
            },
            {
              "linkId": "surgery.date",
              "type": "date",
              "text": "Approximate date"
            }
          ]
        }
      ]
    },
    {
      "linkId": "family-history",
      "type": "group",
      "text": "Family History",
      "item": [
        {
          "linkId": "family-conditions",
          "type": "open-choice",
          "text": "Has anyone in your immediate family had any of the following?",
          "repeats": true,
          "answerOption": [
            {"valueCoding": {"code": "heart-disease", "display": "Heart Disease"}},
            {"valueCoding": {"code": "cancer", "display": "Cancer"}},
            {"valueCoding": {"code": "diabetes", "display": "Diabetes"}},
            {"valueCoding": {"code": "mental-health", "display": "Mental Health Conditions"}}
          ]
        }
      ]
    },
    {
      "linkId": "social-history",
      "type": "group",
      "text": "Social History",
      "item": [
        {
          "linkId": "tobacco",
          "type": "choice",
          "text": "Tobacco use",
          "code": [{
            "system": "http://loinc.org",
            "code": "72166-2",
            "display": "Tobacco smoking status"
          }],
          "answerOption": [
            {"valueCoding": {"code": "never", "display": "Never smoked"}},
            {"valueCoding": {"code": "former", "display": "Former smoker"}},
            {"valueCoding": {"code": "current", "display": "Current smoker"}}
          ]
        },
        {
          "linkId": "alcohol",
          "type": "choice",
          "text": "Alcohol consumption",
          "answerOption": [
            {"valueCoding": {"code": "none", "display": "None"}},
            {"valueCoding": {"code": "occasional", "display": "Occasional (1-2 drinks/week)"}},
            {"valueCoding": {"code": "moderate", "display": "Moderate (3-7 drinks/week)"}},
            {"valueCoding": {"code": "heavy", "display": "Heavy (8+ drinks/week)"}}
          ]
        }
      ]
    }
  ]
}
```

## Usage Tips

### When to Use Each Pattern

1. **Simple Patient Intake**: Basic data collection with minimal logic
2. **PHQ-2**: Standardized clinical instruments with LOINC codes
3. **Conditional Logic**: Dynamic forms that adapt based on answers
4. **Repeating Groups**: Variable number of similar items (medications, allergies)
5. **Choice Questions**: Multiple selection patterns and answer formats
6. **Complex Medical History**: Comprehensive forms with multiple sections

### Adapting Examples

To adapt these examples:
1. Copy the relevant structure
2. Update linkId values to match your naming convention
3. Modify question text for your use case
4. Add appropriate codes (LOINC, SNOMED CT)
5. Adjust required/optional fields
6. Update ValueSets to match your terminology
7. Validate using the validation script

### Testing Approach

For each example:
1. Save as a .json file
2. Run validation: `python scripts/validate_questionnaire.py example.json`
3. Test in a FHIR server or rendering tool
4. Collect user feedback
5. Iterate and refine
