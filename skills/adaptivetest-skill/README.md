# AdaptiveTest Skill

ClawHub skill that wraps the AdaptiveTest API for adaptive testing. Provides IRT/CAT-based assessment, AI question generation, and personalized learning recommendations.

**ClawHub ID:** `k97dcrpcd7p520ds5g09px6b0181sfq1`
**Status:** Published v1.0.0
**Homepage:** [adaptivetest.io/developers](https://adaptivetest.io/developers)

## What It Does

This skill enables Claude and other AI assistants to interact with the AdaptiveTest platform API. It supports six core capabilities:

- **Adaptive Testing** -- Create and administer tests using Item Response Theory (IRT 2PL/3PL) with Computerized Adaptive Testing (CAT) for precise ability estimation in fewer questions
- **AI Question Generation** -- Generate assessment items by topic, difficulty, and academic standard (~7s per call, QTI 3.0 compatible)
- **Learning Recommendations** -- Get personalized learning plans based on student ability profiles and assessment history (~25s per call)
- **Item Calibration** -- Estimate IRT parameters (difficulty, discrimination, guessing) from collected response data
- **Student and Class Management** -- CRUD for students, classes, and enrollments (OneRoster 1.2 compatible)
- **Results and Analytics** -- Real-time ability estimates, assessment history, and item-level analytics

## Pricing

| Plan | Price | API Calls/mo | AI Calls/mo | Rate Limit |
|------|-------|-------------|------------|------------|
| Free Trial | $0 (7 days) | 100 | 10 | 10/min |
| Pro | $49/mo | 10,000 | 1,000 | 60/min |
| Enterprise | Custom | Unlimited | Unlimited | Custom |

Annual Pro plan available at $490/yr (2 months free).

Purchase at [adaptivetest.io/developers](https://adaptivetest.io/developers) or contact jim@woodstocksoftware.com for Enterprise.

## Authentication

All API requests require an `X-API-Key` header. Keys are provisioned automatically after purchase via Stripe checkout.

```
X-API-Key: at_live_...
```

Set the `ADAPTIVETEST_API_KEY` environment variable for the skill to use.

## Repo Structure

This is a skill distribution repo. It contains no application code.

```
adaptivetest-skill/
  SKILL.md              Skill definition published to ClawHub
  clawhub.json          ClawHub manifest (metadata, tags, pricing URL)
  CHANGELOG.md          Version history
  references/
    api-endpoints.md    Full API endpoint reference
    adaptive-testing.md IRT and CAT concepts
    calibration.md      Item calibration guide
  screenshots/
    hero.png            Landing page hero section
    code-example.png    Code integration example
    pricing.png         Pricing cards
```

Implementation specs (data models, Stripe integration, design system) live in the private [`adaptivetest-specs`](https://github.com/woodstocksoftware/adaptivetest-specs) repo.

## Cross-Repo Dependencies

| Repo | Role | Status |
|------|------|--------|
| [`adaptivetest-specs`](https://github.com/woodstocksoftware/adaptivetest-specs) (private) | Implementation specs | Active |
| `adaptivetest-platform` | API key management module (`src/apikeys/`) | Merged (PR #24) |
| `adaptivetest-marketing` | `/developers` landing page | Merged (PR #4) |

## License

Proprietary. The skill definition and API reference docs are published to ClawHub under their terms of service.

## Contact

Jim Williams -- jim@woodstocksoftware.com
Woodstock Software LLC -- [woodstocksoftware.com](https://woodstocksoftware.com)
