# AdaptiveTest API -- Endpoint Reference

> Complete endpoint reference for the AdaptiveTest API. All endpoints require `X-API-Key` header unless noted.

**Base URL:** `https://adaptivetest-platform-production.up.railway.app/api`

---

## Tests

### Create Test
```
POST /tests
```
```json
// Request
{
  "name": "Algebra Readiness Assessment",
  "subject": "Mathematics",
  "description": "Measures algebra readiness for incoming students",
  "max_items": 20,
  "duration_minutes": 45,
  "cat_enabled": true,
  "passing_score": 70.0,
  "irt_model": "3PL"
}

// Response (201)
{
  "id": "uuid",
  "name": "Algebra Readiness Assessment",
  "subject": "Mathematics",
  "description": "Measures algebra readiness for incoming students",
  "max_items": 20,
  "duration_minutes": 45,
  "cat_enabled": true,
  "passing_score": 70.0,
  "irt_model": "3PL",
  "item_count": 0,
  "created_at": "2026-02-24T00:00:00Z"
}
```

### List Tests
```
GET /tests
```
Query params: `page` (default 1), `page_size` (default 50), `subject` (filter)

### Get Test
```
GET /tests/{test_id}
```

### Update Test
```
PATCH /tests/{test_id}
```
Partial update. Only include fields to change.

### Delete Test
```
DELETE /tests/{test_id}
```

---

## Test Items

### Add Item to Test
```
POST /tests/{test_id}/items
```
```json
// Request
{
  "stem": "Solve for x: 2x + 5 = 13",
  "item_type": "multiple_choice",
  "options": [
    {"label": "A", "text": "x = 3", "is_correct": false},
    {"label": "B", "text": "x = 4", "is_correct": true},
    {"label": "C", "text": "x = 5", "is_correct": false},
    {"label": "D", "text": "x = 6", "is_correct": false}
  ],
  "difficulty": 0.5,
  "discrimination": 1.2,
  "guessing": 0.25,
  "standard": "CCSS.MATH.CONTENT.6.EE.B.7",
  "topic": "Linear equations"
}

// Response (201)
{
  "id": "uuid",
  "test_id": "uuid",
  "stem": "Solve for x: 2x + 5 = 13",
  "item_type": "multiple_choice",
  "options": [...],
  "difficulty": 0.5,
  "discrimination": 1.2,
  "guessing": 0.25,
  "standard": "CCSS.MATH.CONTENT.6.EE.B.7",
  "topic": "Linear equations",
  "created_at": "2026-02-24T00:00:00Z"
}
```

### List Items for Test
```
GET /tests/{test_id}/items
```

### Bulk Add Items
```
POST /tests/{test_id}/items/bulk
```
```json
// Request
{
  "items": [
    { "stem": "...", "item_type": "multiple_choice", "options": [...] },
    { "stem": "...", "item_type": "multiple_choice", "options": [...] }
  ]
}
```

---

## Adaptive Sessions

### Start Session
```
POST /tests/{test_id}/sessions
```
```json
// Request
{
  "student_id": "uuid"
}

// Response (201)
{
  "id": "uuid",
  "test_id": "uuid",
  "student_id": "uuid",
  "status": "in_progress",
  "ability_estimate": 0.0,
  "standard_error": 1.0,
  "items_administered": 0,
  "started_at": "2026-02-24T12:00:00Z"
}
```

### Get Next Item (CAT Selection)
```
GET /sessions/{session_id}/next-item
```
```json
// Response (200)
{
  "item_id": "uuid",
  "stem": "Solve for x: 2x + 5 = 13",
  "item_type": "multiple_choice",
  "options": [
    {"label": "A", "text": "x = 3"},
    {"label": "B", "text": "x = 4"},
    {"label": "C", "text": "x = 5"},
    {"label": "D", "text": "x = 6"}
  ],
  "item_number": 1,
  "total_items": 20
}
```

Returns `200` with next item, or `204` if session is complete (stopping rule met).

### Submit Response
```
POST /sessions/{session_id}/responses
```
```json
// Request
{
  "item_id": "uuid",
  "response": "B",
  "response_time_ms": 15000
}

// Response (200)
{
  "correct": true,
  "ability_estimate": 0.45,
  "standard_error": 0.62,
  "items_remaining": 19,
  "session_complete": false
}
```

### Get Session Results
```
GET /sessions/{session_id}/results
```
```json
// Response (200)
{
  "session_id": "uuid",
  "student_id": "uuid",
  "test_id": "uuid",
  "status": "completed",
  "ability_estimate": 1.23,
  "standard_error": 0.31,
  "items_administered": 12,
  "items_correct": 8,
  "percent_correct": 66.7,
  "duration_seconds": 480,
  "mastery_level": "proficient",
  "item_responses": [
    {
      "item_id": "uuid",
      "response": "B",
      "correct": true,
      "response_time_ms": 15000,
      "ability_after": 0.45,
      "information": 1.82
    }
  ],
  "completed_at": "2026-02-24T12:08:00Z"
}
```

---

## AI Question Generation

### Generate Questions
```
POST /gen-q
```
```json
// Request
{
  "topic": "Quadratic equations",
  "difficulty": "medium",
  "count": 5,
  "standard": "CCSS.MATH.CONTENT.HSA.REI.B.4",
  "format": "multiple_choice",
  "grade_level": "9-10",
  "include_rationale": true
}

// Response (200) -- ~7 seconds
{
  "items": [
    {
      "stem": "Which of the following is a solution to x^2 - 5x + 6 = 0?",
      "item_type": "multiple_choice",
      "options": [
        {"label": "A", "text": "x = 1", "is_correct": false},
        {"label": "B", "text": "x = 2", "is_correct": true},
        {"label": "C", "text": "x = 4", "is_correct": false},
        {"label": "D", "text": "x = 6", "is_correct": false}
      ],
      "difficulty": "medium",
      "standard": "CCSS.MATH.CONTENT.HSA.REI.B.4",
      "rationale": "Factor: (x-2)(x-3) = 0, so x = 2 or x = 3. Option B is correct.",
      "distractor_rationales": {
        "A": "Common error: confusing with linear equation",
        "C": "Common error: adding roots instead of factoring",
        "D": "Common error: multiplying coefficients"
      }
    }
  ],
  "generation_time_ms": 6800,
  "model": "claude-haiku"
}
```

**Counts as an AI call** toward monthly AI call limit.

---

## AI Learning Recommendations

### Get Recommendations
```
POST /recs
```
```json
// Request
{
  "student_id": "uuid",
  "subject": "Mathematics",
  "include_resources": true,
  "focus_areas": ["algebra", "geometry"]
}

// Response (200) -- ~25 seconds
{
  "student_id": "uuid",
  "overall_ability": 0.85,
  "mastery_summary": {
    "algebra": {"ability": 1.2, "mastery": "proficient"},
    "geometry": {"ability": 0.3, "mastery": "developing"},
    "statistics": {"ability": 0.9, "mastery": "proficient"}
  },
  "recommendations": [
    {
      "priority": 1,
      "area": "Geometry - Triangle Properties",
      "current_level": "developing",
      "target_level": "proficient",
      "actions": [
        "Review triangle congruence criteria (SSS, SAS, ASA, AAS)",
        "Practice with proof-based problems involving corresponding parts",
        "Work through geometric constructions to build spatial reasoning"
      ],
      "resources": [
        {"title": "Triangle Congruence Review", "type": "practice_set", "url": null}
      ],
      "estimated_sessions": 3
    }
  ],
  "generation_time_ms": 24500,
  "model": "claude-sonnet"
}
```

**Counts as an AI call** toward monthly AI call limit.

---

## Students

### Create Student
```
POST /students
```
```json
// Request
{
  "first_name": "Alex",
  "last_name": "Johnson",
  "email": "alex.johnson@school.edu",
  "grade_level": "10"
}

// Response (201)
{
  "id": "uuid",
  "first_name": "Alex",
  "last_name": "Johnson",
  "email": "alex.johnson@school.edu",
  "grade_level": "10",
  "created_at": "2026-02-24T00:00:00Z"
}
```

### List Students
```
GET /students
```
Query params: `page`, `page_size`, `search` (name/email)

### Get Student
```
GET /students/{student_id}
```

### Get Student Assessment History
```
GET /students/{student_id}/history
```

---

## Classes

### Create Class
```
POST /classes
```
```json
// Request
{
  "name": "Algebra I - Period 3",
  "subject": "Mathematics",
  "grade_level": "9"
}
```

### Enroll Students
```
POST /classes/{class_id}/enroll
```
```json
// Request
{
  "student_ids": ["uuid-1", "uuid-2", "uuid-3"]
}
```

### List Classes
```
GET /classes
```

---

## Item Calibration

### Run Calibration
```
POST /tests/{test_id}/calibrate
```
```json
// Request
{
  "model": "3PL",
  "min_responses": 30
}

// Response (200)
{
  "test_id": "uuid",
  "model": "3PL",
  "total_responses": 450,
  "items_calibrated": 20,
  "items_excluded": 2,
  "results": [
    {
      "item_id": "uuid",
      "difficulty": 0.52,
      "discrimination": 1.35,
      "guessing": 0.22,
      "fit_statistic": 0.98,
      "dif_flags": []
    }
  ],
  "reliability": 0.89,
  "calibrated_at": "2026-02-24T00:00:00Z"
}
```

Requires at least 30 responses per item. Items with fewer responses are excluded. See `references/calibration.md` for IRT calibration concepts.

---

## Error Responses

All errors follow this format:
```json
{
  "detail": "Human-readable error message"
}
```

| Status | Meaning | Example |
|--------|---------|---------|
| 400 | Validation error | `{"detail": "count must be between 1 and 20"}` |
| 401 | Auth failure | `{"detail": "Invalid API key"}` |
| 403 | Limit exceeded | `{"detail": "Monthly API call limit exceeded"}` |
| 404 | Not found | `{"detail": "Test not found"}` |
| 429 | Rate limited | `{"detail": "Rate limit exceeded"}` + `Retry-After` header |
| 500 | Server error | `{"detail": "Internal server error"}` |
