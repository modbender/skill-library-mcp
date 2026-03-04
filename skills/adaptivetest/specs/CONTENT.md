# AdaptiveTest Skill -- Content Spec

> **All copy, taglines, and text content. Landing page and ClawHub listing reference this for exact wording.**

---

## ClawHub Listing

**Name:** AdaptiveTest
**Slug:** `adaptivetest`
**Version:** 1.0.0
**Category:** Education / Assessment
**Tags:** `adaptive-testing`, `irt`, `cat`, `education`, `assessment`, `ai-questions`, `learning-recommendations`, `psychometrics`

**Short Description (140 chars):**
> Adaptive testing engine with IRT/CAT, AI question generation, and personalized learning recommendations.

**Long Description:**
> Production-grade adaptive testing for education and training. Uses Item Response Theory (IRT 2PL/3PL) with Computerized Adaptive Testing (CAT) to deliver precise ability estimates in fewer questions. Includes AI-powered question generation by topic and standard, plus personalized learning recommendation plans. Battle-tested: 3,000+ tests administered, 94.8% audit score.

---

## Landing Page Copy

### Hero Section

**Label:** For Developers
**Headline:** Add Adaptive Testing to Any Application
**Subtitle:** Production-grade IRT/CAT engine, AI question generation, and personalized learning recommendations. One API key, six capabilities.
**Primary CTA:** Start Free Trial
**Secondary CTA:** View Documentation

### Capabilities Section

**Section Headline:** What You Can Build
**Section Subtitle:** Six production-ready capabilities through a single API.

| # | Title | Description | Icon |
|---|-------|-------------|------|
| 1 | Adaptive Testing | IRT 2PL/3PL engine with CAT item selection. Precise ability estimates in 40-60% fewer questions than fixed-form tests. | `Brain` |
| 2 | AI Question Generation | Generate assessment items by topic, difficulty, and academic standard. Claude-powered with QTI 3.0 export. | `Sparkles` |
| 3 | Learning Recommendations | Personalized learning plans based on student ability profiles. AI-generated with actionable next steps. | `GraduationCap` |
| 4 | Item Calibration | Estimate IRT parameters from response data. Classical Test Theory pre-screening, DIF analysis, model fit statistics. | `BarChart3` |
| 5 | Student & Class Management | CRUD for students, classes, and enrollments. OneRoster 1.2 compatible for SIS integration. | `Users` |
| 6 | Results & Analytics | Real-time ability estimates, mastery tracking, item-level analytics, and assessment history. | `LineChart` |

### Code Example Section

**Headline:** Simple to Integrate
**Subtitle:** Start an adaptive test session in three API calls.

```python
import httpx

BASE = "https://adaptivetest-platform-production.up.railway.app/api"
HEADERS = {"X-API-Key": "at_live_your_key_here"}

# 1. Create a test
test = httpx.post(f"{BASE}/tests", headers=HEADERS, json={
    "name": "Algebra Readiness",
    "subject": "Mathematics",
    "max_items": 20,
    "cat_enabled": True
}).json()

# 2. Start an adaptive session
session = httpx.post(
    f"{BASE}/tests/{test['id']}/sessions",
    headers=HEADERS,
    json={"student_id": "student-123"}
).json()

# 3. Get the first item (CAT-selected)
item = httpx.get(
    f"{BASE}/sessions/{session['id']}/next-item",
    headers=HEADERS
).json()
```

### How It Works Section

**Headline:** From ClawHub to Production in Minutes

| Step | Title | Description |
|------|-------|-------------|
| 1 | Sign Up | Create a free account and get your API key instantly. 7-day trial with 100 API calls. |
| 2 | Install the Skill | Add the AdaptiveTest skill to your OpenClaw workspace. Your agent learns the full API. |
| 3 | Configure | Set your `ADAPTIVETEST_API_KEY` environment variable. The skill handles auth automatically. |
| 4 | Build | Your agent can now create tests, generate questions, run adaptive sessions, and analyze results. |

### Pricing Section

**Headline:** Simple, Predictable Pricing
**Subtitle:** Start free. Scale when you're ready.

| | Free Trial | Pro | Enterprise |
|---|---|---|---|
| **Price** | $0 | $49/mo | Custom |
| **Duration** | 7 days | Monthly or annual | Custom |
| **API calls/mo** | 100 | 10,000 | Unlimited |
| **AI calls/mo** | 10 | 1,000 | Unlimited |
| **API keys** | 1 | 5 | Unlimited |
| **Rate limit** | 10 req/min | 60 req/min | Custom |
| **Support** | Docs only | Email | Dedicated |
| **Annual price** | -- | $490/yr (2 months free) | Custom |
| **CTA** | Start Free Trial | Subscribe | Contact Us |

### FAQ Section

**Headline:** Frequently Asked Questions

| Question | Answer |
|----------|--------|
| What is adaptive testing? | Adaptive testing uses Item Response Theory (IRT) to select questions based on a student's estimated ability. Each question is chosen to maximize information, resulting in precise measurements with 40-60% fewer items than traditional fixed-form tests. |
| What AI models power the question generation? | Question generation uses Claude Haiku for fast, cost-effective item creation. Learning recommendations use Claude Sonnet for deeper pedagogical analysis. Both are accessed through the AdaptiveTest API -- you don't need your own Anthropic API key. |
| Is AdaptiveTest FERPA-aligned? | Yes. AdaptiveTest is designed with FERPA alignment in mind. Student data is encrypted at rest and in transit, access is scoped to API keys, and no student PII is shared with third parties. |
| Can I use the API without OpenClaw? | Yes. The API works with any HTTP client. The OpenClaw skill adds AI-assisted workflow orchestration, but the REST API is fully usable standalone. |
| What happens when my trial ends? | Your API key stops working after 7 days or 100 API calls, whichever comes first. No automatic charges. Subscribe to Pro to continue. |
| Do you support LTI integration? | The AdaptiveTest platform supports LTI 1.3 for direct LMS integration. LTI endpoints are available on Pro and Enterprise tiers. Contact us for LTI setup guidance. |

### Bottom CTA Section

**Headline:** Ready to Build?
**Subtitle:** Get your API key and start building adaptive assessments in minutes.
**Primary CTA:** Start Free Trial
**Secondary CTA:** Read the Docs

---

## API Overview

**Base URL:** `https://adaptivetest-platform-production.up.railway.app/api`
**Auth:** `X-API-Key: at_live_<key>` header on all requests
**Content-Type:** `application/json`
**Response format:** JSON with consistent error shape:
```json
{
  "detail": "Human-readable error message"
}
```

**HTTP status codes:**
- `200` -- Success
- `201` -- Created
- `400` -- Validation error
- `401` -- Missing or invalid API key
- `403` -- Tier limit exceeded (include `X-RateLimit-*` headers)
- `404` -- Resource not found
- `429` -- Rate limit exceeded
- `500` -- Internal server error

**Rate limit headers (all responses):**
- `X-RateLimit-Limit` -- requests per minute for this key's tier
- `X-RateLimit-Remaining` -- requests remaining in current window
- `X-RateLimit-Reset` -- UTC epoch seconds when window resets

---

## Content Rules

- **Tone:** Developer-first. Technical and direct in API docs. Professional and capability-focused on landing page.
- **FERPA:** Always "FERPA-aligned", never "FERPA compliant"
- **SOC 2:** No claims
- **Brand:** "AdaptiveTest" one word, capital A and T
- **Pricing:** Free Trial (7 days), Pro ($49/mo), Enterprise (custom)
- **Quality claims:** "3,000+ tests administered", "94.8% audit score" -- use these exact numbers
- **Avoid:** "revolutionary", "cutting-edge", "state-of-the-art", "best-in-class"
- **Prefer:** "production-grade", "battle-tested", "precise", "efficient"
