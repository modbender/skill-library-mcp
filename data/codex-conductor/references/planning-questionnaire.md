# Planning Questionnaire (Mandatory)

Ask these in order. Do not start implementation until critical answers are provided.

## 0) Coding Agent Selection (Ask First)
1. Which coding agent should run implementation tasks? (`codex` | `claude` | `opencode` | `pi`)
2. What is the fallback coding agent if the primary fails repeatedly?

## A) Outcome and Scope
3. What are we building (one-sentence mission)?
4. Who are the target users?
5. What is in scope for v1?
6. What is explicitly out of scope?
7. What is the deadline (if any)?

## B) User Journeys and Success
8. What are the top 3 user journeys?
9. What must work on day one (must-have features)?
10. What metrics define success (adoption, conversion, latency, reliability)?
11. What does “Definition of Done” mean for this project?

## C) Product and Compliance Constraints
12. Any legal/compliance constraints (privacy, data residency, PCI, HIPAA, etc.)?
13. Any accessibility level target (e.g., WCAG baseline)?
14. Any browser/device/platform constraints?
15. Any third-party integrations required?

## D) Technical Constraints
16. Preferred stack (frontend/backend/database/infra)?
17. Existing repo or greenfield?
18. Required hosting target (Cloudflare, Vercel, AWS, on-prem, etc.)?
19. Required CI/CD platform?
20. Auth requirements (roles, SSO, OAuth providers)?
21. Payments/subscriptions needed?
22. Data model complexity and expected scale?

## E) Quality and Operations
23. Required test levels (unit/integration/e2e/perf/security)?
24. Availability target/SLO?
25. Logging/monitoring/alerting requirements?
26. Rollback expectations?
27. Backup and disaster recovery expectations?

## F) Orchestration Preferences
28. Mode: `autonomous` or `gated`?
29. Should `research_mode` run during planning? (`true/false`)
30. In gated mode, who approves each gate?
31. In autonomous mode, should orchestrator auto-repair failures up to 2 retries? (`true/false`)
32. Preferred progress update frequency?

## G) Acceptance and Sign-off
33. What are the exact acceptance tests for launch?
34. What evidence is required at each gate?
35. Final approver for release?

## Minimum Inputs Required to Start Build
- Primary coding agent choice
- Mission
- Top user journeys
- v1 scope
- Hosting target
- Stack preference (or explicit “recommend one”)
- Mode (`autonomous` or `gated`)
- Definition of Done
- Acceptance tests
