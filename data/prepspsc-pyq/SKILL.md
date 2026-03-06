---
name: prepspsc-pyq
description: 'Use when the user asks about Indian competitive exam preparation, Sikkim PSC (SPSC) questions, previous year questions (PYQ), mock test generation, exam pattern practice, or needs reference questions for AI-powered question generation. Invoke for SPSC exam prep, PYQ search, mock tests, subject-wise practice, or studying for government job exams in India.'
triggers:
  - SPSC exam
  - Sikkim PSC
  - previous year questions
  - PYQ
  - mock test
  - exam preparation
  - Indian competitive exam
  - government job exam
  - SPSC mock test
  - exam practice
  - question bank
license: MIT License
metadata:
  author: PrepSPSC
  version: 1.0.0
  website: https://prepspsc.com
---

# PrepSPSC PYQ API

Search 7,400+ real previous year questions from Sikkim PSC (SPSC) exams and generate mock tests across 64 exam patterns. Returns MCQ questions with options, correct answers, explanations, topics, cognitive levels, and difficulty metadata.

## Quick Reference

| Detail | Value |
|--------|-------|
| Base URL | `https://qqqditxzghqzodvauxth.supabase.co/functions/v1/pyq-api` |
| Auth | `Authorization: Bearer sk_live_YOUR_KEY` |
| Questions | 7,442 across 27 subjects |
| Exam Patterns | 64 (Civil Services, Police, Medical, Engineering, Education, IT, and more) |
| Get API Key | [prepspsc.com/developers](https://prepspsc.com/developers) |

## Authentication

All requests require a Bearer token in the `Authorization` header. API keys start with `sk_live_`.

### Check Existing Setup First

Before guiding the user through setup, check if the API key is already available:

```bash
if [ -n "$PREPSPSC_API_KEY" ]; then
  echo "Configured"
else
  echo "No API key found. Get one at https://prepspsc.com/developers"
fi
```

If no key is found, direct the user to https://prepspsc.com/developers to generate a free API key.

### Making Requests

```bash
curl -X POST "https://qqqditxzghqzodvauxth.supabase.co/functions/v1/pyq-api" \
  -H "Authorization: Bearer $PREPSPSC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "fundamental rights", "subject": "Indian Polity", "limit": 5}'
```

---

## Endpoints

### 1. List Available Subjects

**`GET /pyq-api`** — Returns all subjects with question counts. Call this first to see what's available.

```bash
curl "https://qqqditxzghqzodvauxth.supabase.co/functions/v1/pyq-api" \
  -H "Authorization: Bearer $PREPSPSC_API_KEY"
```

**Response:**
```json
{
  "subjects": [
    { "subject": "Indian Polity", "count": 842 },
    { "subject": "History", "count": 756 },
    { "subject": "General Knowledge", "count": 698 }
  ],
  "total_questions": 7442
}
```

Available subjects: General English, General Knowledge, Indian Polity, History, Geography, Science, Environment, Indian Economy, Arithmetic and Logical Reasoning, Agriculture, Botany, Zoology, Nepali Literature, Current Affairs, and more (27 total).

---

### 2. Search Questions (Semantic Search)

**`POST /pyq-api`** — Search PYQs using natural language. Uses vector similarity + keyword hybrid matching.

```bash
curl -X POST "https://qqqditxzghqzodvauxth.supabase.co/functions/v1/pyq-api" \
  -H "Authorization: Bearer $PREPSPSC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Fundamental Rights Article 21",
    "subject": "Indian Polity",
    "limit": 5,
    "threshold": 0.3
  }'
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | Natural language search (min 3 chars) |
| `subject` | string | Yes | Subject to search within |
| `limit` | integer | No | Max results, 1-20 (default: 5) |
| `threshold` | number | No | Min similarity 0-1 (default: 0.3, lower = more results) |
| `year_min` | integer | No | Exclude time-sensitive questions older than this year |
| `exclude_ids` | string[] | No | Question UUIDs to exclude (for pagination) |

**Response:**
```json
{
  "questions": [
    {
      "id": "uuid",
      "question": "Which Article of the Indian Constitution guarantees the Right to Life?",
      "options": [
        { "id": "a", "text": "Article 14" },
        { "id": "b", "text": "Article 19" },
        { "id": "c", "text": "Article 21" },
        { "id": "d", "text": "Article 32" }
      ],
      "correct_option_id": "c",
      "explanation": "Article 21 states that no person shall be deprived of his life or personal liberty...",
      "subject": "Indian Polity",
      "topics": ["Fundamental Rights", "Article 21", "Right to Life"],
      "difficulty": "easy",
      "cognitive_level": "remember",
      "is_time_sensitive": false,
      "high_yield": true,
      "similarity": 0.89
    }
  ],
  "count": 5
}
```

---

### 3. Generate Mock Test

**`POST /pyq-api/mock-test`** — Generate a complete mock test following real SPSC exam patterns with difficulty balancing.

```bash
curl -X POST "https://qqqditxzghqzodvauxth.supabase.co/functions/v1/pyq-api/mock-test" \
  -H "Authorization: Bearer $PREPSPSC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "pattern": "undersecretary-prelims",
    "difficulty_mix": { "easy": 30, "medium": 50, "hard": 20 }
  }'
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `pattern` | string | Yes | Exam pattern ID (64 available, see below) |
| `difficulty_mix` | object | No | Custom difficulty % (default: 30/50/20) |
| `year_min` | integer | No | Exclude stale current affairs |
| `exclude_ids` | string[] | No | Skip questions from previous tests |

**Response includes:** test metadata (name, total questions, duration, marking scheme) + sections with difficulty-balanced questions.

#### Available Exam Patterns (64 Total)

**Core / General:** `undersecretary-prelims`, `general-prelims`, `spsc-mains-gs1`, `spsc-mains-gs2`, `quick-practice-30`

**Civil Services:** `sscs-prelims`, `combined-mains-gs3`, `combined-mains-english`

**Police / Law:** `si-police-prelims`, `si-police-mains`, `si-excise`, `sub-jailer`

**Fire Service:** `sub-fire-officer`

**Engineering:** `junior-engineer-prelims`, `assistant-engineer-civil`, `assistant-engineer-electrical`, `assistant-engineer-mechanical`, `assistant-engineer-agriculture`

**Medical / Health:** `gdmo`, `veterinary-officer`, `dental-surgeon`, `specialist-sr-grade`, `staff-nurse`, `paramedical`, `health-educator`, `mphw`, `drug-inspector`, `food-safety-officer`, `pharmacist-ayush`, `yoga-instructor-ayush`, `scientific-officer-ayush`, `tutor-clinical-instructor`

**Administrative:** `ldc-prelims`, `accounts-clerk`, `stenographer`, `cooperative-inspector`, `statistical-inspector`, `revenue-inspector`, `revenue-surveyor`, `commercial-tax-inspector`

**Forestry / Fisheries:** `forest-ranger-prelims`, `fisheries-officer`, `assistant-director-fisheries`, `livestock-assistant`

**Education:** `lecturer-diet`, `iti-instructor`, `principal-iti`, `assistant-professor-sheda`

**Other Specialized:** `assistant-town-planner`, `assistant-architect`, `assistant-geologist`, `digital-analyst`, `assistant-programmer`, `assistant-director-it`, `lab-assistant`, `field-assistant`, `ado-wdo-hdo`, `senior-information-assistant`, `sub-editor`, `inspector-legal-metrology`, `photographer`, `script-writer`, `feed-mill-operator`, `printing-stationery`

Use `GET /pyq-api/patterns` to get full details with subject distribution, duration, and marking scheme for each pattern.

---

### 4. List Exam Patterns

**`GET /pyq-api/patterns`** — Returns all 64 exam patterns with subject distribution, question counts, duration, and marking scheme.

```bash
curl "https://qqqditxzghqzodvauxth.supabase.co/functions/v1/pyq-api/patterns" \
  -H "Authorization: Bearer $PREPSPSC_API_KEY"
```

---

### 5. Record Progress

**`POST /pyq-api/progress`** — Record a user's answer to a question.

```bash
curl -X POST "https://qqqditxzghqzodvauxth.supabase.co/functions/v1/pyq-api/progress" \
  -H "Authorization: Bearer $PREPSPSC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "external_user_id": "user123",
    "question_id": "uuid-here",
    "selected_option": "c",
    "is_correct": true,
    "time_spent_seconds": 45
  }'
```

### 6. Get User Progress

**`GET /pyq-api/progress?user_id=user123`** — Retrieve a user's complete answer history.

```bash
curl "https://qqqditxzghqzodvauxth.supabase.co/functions/v1/pyq-api/progress?user_id=user123" \
  -H "Authorization: Bearer $PREPSPSC_API_KEY"
```

---

### 7. Performance Analytics

**`GET /pyq-api/analytics?user_id=user123`** — Get accuracy by subject, difficulty breakdown, and recent activity.

```bash
curl "https://qqqditxzghqzodvauxth.supabase.co/functions/v1/pyq-api/analytics?user_id=user123" \
  -H "Authorization: Bearer $PREPSPSC_API_KEY"
```

---

### 8. Leaderboard

**`GET /pyq-api/leaderboard`** — Rankings by correct answers and accuracy.

```bash
curl "https://qqqditxzghqzodvauxth.supabase.co/functions/v1/pyq-api/leaderboard?limit=20&time_range=all_time" \
  -H "Authorization: Bearer $PREPSPSC_API_KEY"
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | Max entries (1-100) |
| `time_range` | string | `all_time` | `week`, `month`, or `all_time` |

---

### 9. Bookmarks

**Add bookmark:**
```bash
curl -X POST "https://qqqditxzghqzodvauxth.supabase.co/functions/v1/pyq-api/bookmarks" \
  -H "Authorization: Bearer $PREPSPSC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"external_user_id": "user123", "question_id": "uuid-here", "note": "Review later"}'
```

**List bookmarks:**
```bash
curl "https://qqqditxzghqzodvauxth.supabase.co/functions/v1/pyq-api/bookmarks?user_id=user123" \
  -H "Authorization: Bearer $PREPSPSC_API_KEY"
```

**Remove bookmark:**
```bash
curl -X DELETE "https://qqqditxzghqzodvauxth.supabase.co/functions/v1/pyq-api/bookmarks" \
  -H "Authorization: Bearer $PREPSPSC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"external_user_id": "user123", "question_id": "uuid-here"}'
```

---

## Common Workflows

### Quick Practice Session
1. `GET /pyq-api` — Check available subjects
2. `POST /pyq-api/mock-test` with `"pattern": "quick-practice-30"` — Get a 30-question test
3. Present questions to user one at a time
4. `POST /pyq-api/progress` — Record each answer
5. `GET /pyq-api/analytics?user_id=xxx` — Show performance summary

### Subject-Specific Study
1. `POST /pyq-api` — Search for questions on a specific topic (e.g., `"query": "Fundamental Rights"`, `"subject": "Indian Polity"`)
2. Present questions as flashcards or quiz
3. Track progress with `POST /pyq-api/progress`

### Full Mock Exam
1. `GET /pyq-api/patterns` — Show available exam patterns
2. User picks a pattern (e.g., `undersecretary-prelims`)
3. `POST /pyq-api/mock-test` — Generate the test
4. Time the user (duration from response metadata)
5. Record all answers via `POST /pyq-api/progress`
6. Show analytics via `GET /pyq-api/analytics`

### AI Question Generation Reference
1. `POST /pyq-api` — Fetch real PYQs as few-shot examples
2. Analyze returned `topics`, `cognitive_level`, `difficulty`
3. Use as reference to generate new questions matching real exam standards

---

## Error Handling

| HTTP Status | Error Code | Meaning |
|-------------|-----------|---------|
| 400 | `INVALID_QUERY` | Query too short or missing required fields |
| 401 | `INVALID_API_KEY` | API key missing, invalid, or revoked |
| 404 | `INVALID_PATTERN` | Unknown exam pattern ID |
| 429 | `RATE_LIMITED` | Too many requests (free: 10/min, paid: 60/min) |
| 500 | `INTERNAL_ERROR` | Server error |

---

## Rate Limits

| Tier | Requests/min | Requests/month |
|------|-------------|----------------|
| Free | 10 | 1,000 |
| Paid | 60 | 50,000 |
| Enterprise | 500 | Unlimited |

Get your free API key at **https://prepspsc.com/developers**
