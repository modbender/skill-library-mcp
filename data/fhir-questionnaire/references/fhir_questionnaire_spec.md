# FHIR Questionnaire Resource Specification (R4)

This reference provides essential information about the FHIR R4 Questionnaire resource structure.

**Source of Truth**: The definitive schema is located at `assets/schema/questionnaire.schema.json`. This document provides a human-readable interpretation of that schema.

## Table of Contents
- Resource Structure
- Root Elements
- Item Elements
- Item Types
- EnableWhen (Conditional Display)
- Answer Options
- Metadata Elements

## Resource Structure

Standard FHIR R4 Questionnaire resource structure:

```json
{
  "resourceType": "Questionnaire",
  "id": "example",
  "url": "http://example.org/fhir/Questionnaire/example",
  "version": "1.0.0",
  "status": "draft",
  "title": "Example Questionnaire",
  "item": [...]
}
```

## Root Elements

| Element | Cardinality | Type | Description |
|---------|------------|------|-------------|
| resourceType | 1..1 | code | Must be "Questionnaire" |
| id | 0..1 | string | Logical id (pattern: ^[A-Za-z0-9\-\.]{1,64}$) |
| url | 0..1 | uri | Canonical identifier (recommended for published) |
| version | 0..1 | string | Business version identifier |
| name | 0..1 | string | Computer-friendly name (no spaces) |
| title | 0..1 | string | Human-friendly name |
| status | 1..1 | code | draft \| active \| retired \| unknown |
| experimental | 0..1 | boolean | For testing purposes only |
| date | 0..1 | dateTime | Date last changed |
| publisher | 0..1 | string | Name of organization |
| description | 0..1 | markdown | Natural language description |
| purpose | 0..1 | markdown | Why this questionnaire is defined |
| code | 0..* | Coding | Concept that represents the overall questionnaire |
| item | 0..* | BackboneElement | Questions and sections |

## Item Elements

Items are the core building blocks of a questionnaire (questions and groups).

| Element | Cardinality | Type | Description |
|---------|------------|------|-------------|
| linkId | 1..1 | string | Unique id for item in questionnaire |
| definition | 0..1 | uri | ElementDefinition - details for the item |
| code | 0..* | Coding | Corresponding concept for this item |
| prefix | 0..1 | string | Display prefix (e.g., "1.", "a)") |
| text | 0..1 | string | Primary text for the item |
| type | 1..1 | code | Type of item (see Item Types below) |
| enableWhen | 0..* | BackboneElement | Conditional display rules |
| enableBehavior | 0..1 | code | all \| any (default: all) |
| required | 0..1 | boolean | Whether item must be answered |
| repeats | 0..1 | boolean | Whether item can repeat |
| readOnly | 0..1 | boolean | Don't allow input |
| maxLength | 0..1 | integer | Max characters for string types |
| answerValueSet | 0..1 | canonical | ValueSet containing permitted answers |
| answerOption | 0..* | BackboneElement | Permitted answers |
| initial | 0..* | BackboneElement | Initial value(s) |
| item | 0..* | BackboneElement | Nested items under this item |

## Item Types

| Type | Description | Answer Format |
|------|-------------|---------------|
| group | Container for items | (no answer) |
| display | Text for display (no answer) | (no answer) |
| boolean | True/False question | answerBoolean |
| decimal | Decimal number | answerDecimal |
| integer | Integer number | answerInteger |
| date | Date (no time) | answerDate |
| dateTime | Date and time | answerDateTime |
| time | Time of day | answerTime |
| string | Short text (< 255 chars) | answerString |
| text | Long text | answerString |
| url | URL/URI | answerString |
| choice | Single selection from list | answerCoding |
| open-choice | Single selection + "other" | answerCoding or answerString |
| attachment | File attachment | answerAttachment |
| reference | Reference to another resource | answerReference |
| quantity | Number with unit | answerQuantity |

## EnableWhen (Conditional Display)

Controls when an item is enabled/displayed based on answers to other questions.

```json
{
  "linkId": "2",
  "type": "string",
  "text": "If yes, please specify",
  "enableWhen": [
    {
      "question": "1",
      "operator": "=",
      "answerBoolean": true
    }
  ],
  "enableBehavior": "all"
}
```

### EnableWhen Elements

| Element | Cardinality | Type | Description |
|---------|------------|------|-------------|
| question | 1..1 | string | linkId of question to depend on |
| operator | 1..1 | code | exists \| = \| != \| > \| < \| >= \| <= |
| answer[x] | 0..1 | * | Answer value to compare against |

### Operators

- `exists`: True if question has any answer
- `=`: Answer equals the specified value
- `!=`: Answer not equal to specified value
- `>`, `<`, `>=`, `<=`: Comparison operators (for numbers, dates)

### EnableBehavior

- `all`: All enableWhen conditions must be true (AND logic)
- `any`: Any enableWhen condition must be true (OR logic)

## Answer Options

For `choice` and `open-choice` items, define permitted answers:

### Using answerOption

```json
{
  "linkId": "gender",
  "type": "choice",
  "text": "Gender",
  "answerOption": [
    {
      "valueCoding": {
        "system": "http://hl7.org/fhir/administrative-gender",
        "code": "male",
        "display": "Male"
      }
    },
    {
      "valueCoding": {
        "system": "http://hl7.org/fhir/administrative-gender",
        "code": "female",
        "display": "Female"
      }
    }
  ]
}
```

### Using answerValueSet

```json
{
  "linkId": "country",
  "type": "choice",
  "text": "Country",
  "answerValueSet": "http://hl7.org/fhir/ValueSet/iso3166-1-3"
}
```

## Metadata Elements

Recommended metadata for published questionnaires:

```json
{
  "resourceType": "Questionnaire",
  "id": "example",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2024-01-01T00:00:00Z",
    "profile": ["http://hl7.org/fhir/StructureDefinition/Questionnaire"]
  },
  "url": "http://example.org/fhir/Questionnaire/example",
  "identifier": [{
    "system": "http://example.org/identifiers",
    "value": "Q12345"
  }],
  "version": "1.0.0",
  "name": "ExampleQuestionnaire",
  "title": "Example Patient Intake Questionnaire",
  "status": "active",
  "experimental": false,
  "date": "2024-01-01",
  "publisher": "Example Healthcare Organization",
  "contact": [{
    "name": "Clinical Informatics Team",
    "telecom": [{
      "system": "email",
      "value": "informatics@example.org"
    }]
  }],
  "description": "Standard patient intake questionnaire",
  "useContext": [{
    "code": {
      "system": "http://terminology.hl7.org/CodeSystem/usage-context-type",
      "code": "focus"
    },
    "valueCodeableConcept": {
      "coding": [{
        "system": "http://snomed.info/sct",
        "code": "408443003",
        "display": "General medical practice"
      }]
    }
  }],
  "jurisdiction": [{
    "coding": [{
      "system": "urn:iso:std:iso:3166",
      "code": "US"
    }]
  }]
}
```

## Common Patterns

### Grouping Items

```json
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
    }
  ]
}
```

### Repeating Items

```json
{
  "linkId": "medications",
  "type": "group",
  "text": "Current Medications",
  "repeats": true,
  "item": [
    {
      "linkId": "med-name",
      "type": "string",
      "text": "Medication Name"
    },
    {
      "linkId": "med-dose",
      "type": "string",
      "text": "Dosage"
    }
  ]
}
```

### Initial Values

```json
{
  "linkId": "country",
  "type": "choice",
  "text": "Country",
  "answerValueSet": "http://hl7.org/fhir/ValueSet/iso3166-1-3",
  "initial": [{
    "valueCoding": {
      "system": "urn:iso:std:iso:3166",
      "code": "US",
      "display": "United States"
    }
  }]
}
```

## Validation Rules

**Note**: The complete structural validation rules are defined in `assets/schema/questionnaire.schema.json`. The following are common validation checks:

1. **linkId uniqueness**: Each linkId must be unique across the entire questionnaire
2. **enableWhen references**: The `question` field must reference a valid linkId
3. **Answer types**: answerOption and answerValueSet should match the item type
4. **Required fields**: resourceType and status are mandatory per FHIR R4
5. **Status constraints**: Active/retired questionnaires should have url and version
6. **Nested groups**: Groups can contain groups, but watch for deep nesting
7. **enableWhen on first item**: Cannot reference questions that appear later
8. **ID pattern**: If present, the id field must match `^[A-Za-z0-9\-\.]{1,64}$`

## Common Coding Systems

| System | URL | Usage |
|--------|-----|-------|
| LOINC | http://loinc.org | Clinical questions and observations |
| SNOMED CT | http://snomed.info/sct | Clinical concepts |
| ICD-10 | http://hl7.org/fhir/sid/icd-10 | Diagnoses |
| RxNorm | http://www.nlm.nih.gov/research/umls/rxnorm | Medications |
| UCUM | http://unitsofmeasure.org | Units of measure |
