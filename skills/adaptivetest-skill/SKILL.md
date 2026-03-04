---
name: adaptivetest
description: Adaptive testing engine with IRT/CAT, AI question generation, and personalized learning recommendations
version: 1.0.1
author: woodstocksoftware
metadata:
  openclaw:
    requires:
      env:
        - ADAPTIVETEST_API_KEY
      bins:
        - curl
    capabilities:
      - adaptive-testing
      - question-generation
      - learning-recommendations
      - item-calibration
      - student-management
      - results-analytics
    base_url: https://adaptivetest-platform-production.up.railway.app/api
    tags:
      - education
      - assessment
      - irt
      - cat
      - psychometrics
      - ai
---

# AdaptiveTest

Production-grade adaptive testing API. Uses Item Response Theory (IRT 2PL/3PL) with Computerized Adaptive Testing (CAT) to deliver precise ability estimates in fewer questions. Includes AI-powered question generation and personalized learning recommendations.

## When to Use This Skill

Use AdaptiveTest when the user needs to:
- Create or manage assessments and tests
- Run adaptive testing sessions that select questions based on student ability
- Generate assessment questions by topic, difficulty, or academic standard
- Get personalized learning recommendations for students
- Calibrate test items using IRT parameter estimation
- Manage students, classes, and enrollments
- Analyze test results and track student mastery

## Authentication

All requests require the `X-API-Key` header:

```
X-API-Key: ${ADAPTIVETEST_API_KEY}
```

Base URL: `https://adaptivetest-platform-production.up.railway.app/api`

## Core Workflows

### 1. Create and Administer an Adaptive Test

```
POST /tests              -- Create a test (set cat_enabled: true)
POST /tests/{id}/items   -- Add items to the test
POST /tests/{id}/sessions -- Start an adaptive session for a student
GET  /sessions/{id}/next-item -- Get the next CAT-selected item
POST /sessions/{id}/responses -- Submit student response
GET  /sessions/{id}/results   -- Get ability estimate and results
```

The CAT engine selects items using maximum Fisher information. Ability is estimated after each response using IRT 2PL or 3PL models. Sessions terminate when the standard error drops below threshold or max items are reached.

### 2. Generate Questions with AI

```
POST /gen-q -- Generate questions by topic, difficulty, and standard
```

Request body:
```json
{
  "topic": "Quadratic equations",
  "difficulty": "medium",
  "count": 5,
  "standard": "CCSS.MATH.CONTENT.HSA.REI.B.4",
  "format": "multiple_choice"
}
```

Returns QTI 3.0-compatible items with stems, distractors, and rationales. Generation takes ~7 seconds.

### 3. Get Learning Recommendations

```
POST /recs -- Get personalized learning recommendations for a student
```

Request body:
```json
{
  "student_id": "student-uuid",
  "subject": "Mathematics",
  "include_resources": true
}
```

Returns a personalized learning plan based on the student's ability profile and assessment history. Generation takes ~25 seconds.

### 4. Calibrate Test Items

```
POST /tests/{id}/calibrate -- Run IRT calibration on collected response data
```

Requires sufficient response data (minimum 30 responses per item recommended). Returns IRT parameters: difficulty (b), discrimination (a), and guessing (c) for 3PL.

### 5. Manage Students and Classes

```
POST /students           -- Create a student
GET  /students           -- List students
POST /classes            -- Create a class
POST /classes/{id}/enroll -- Enroll students in a class
```

OneRoster 1.2 compatible for SIS integration.

### 6. View Results and Analytics

```
GET /sessions/{id}/results       -- Detailed session results with ability estimate
GET /students/{id}/history       -- Assessment history for a student
GET /tests/{id}/analytics        -- Item-level analytics for a test
```

## Rate Limits

Rate limits depend on your API key tier. Check `X-RateLimit-Remaining` header on each response.

## Error Handling

All errors return JSON with a `detail` field:
```json
{"detail": "Human-readable error message"}
```

Common status codes: 400 (validation), 401 (auth), 403 (limit exceeded), 404 (not found), 429 (rate limited).

## Reference Documentation

For detailed endpoint specifications, request/response shapes, and IRT/CAT concepts, see the `references/` directory:
- `references/api-endpoints.md` -- Full endpoint reference
- `references/adaptive-testing.md` -- IRT and CAT concepts
- `references/calibration.md` -- Item calibration guide
