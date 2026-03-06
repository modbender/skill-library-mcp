# Confidence Assessment Rubric

Use this rubric to score brain dump clarity before generating a contract.

**Threshold**: 95 points minimum to proceed to contract generation.

## Scoring Dimensions

### 1. Problem Clarity (0-20 points)

| Score | Criteria                                                                                    |
| ----- | ------------------------------------------------------------------------------------------- |
| 0-5   | Problem not stated or completely unclear. No idea what we're solving.                       |
| 6-10  | Problem mentioned but vague ("things are slow", "users complain", "it's broken").           |
| 11-15 | Problem clear but missing context: who experiences it, how often, or what impact.           |
| 16-20 | Problem crystal clear: who experiences it, what happens, when it occurs, impact quantified. |

**Questions to ask if low**:
- "What specific problem are you trying to solve?"
- "Who experiences this problem? How often?"
- "What's the cost of not solving this? (time, money, frustration)"
- "Can you describe a specific incident where this was a problem?"

**Examples**:
- Score 5: "The app is bad"
- Score 10: "Users say the app is slow"
- Score 15: "The checkout page loads slowly, causing cart abandonment"
- Score 20: "Checkout page p95 latency is 3.2s, causing 18% cart abandonment, ~$50k/month lost revenue"

---

### 2. Goal Definition (0-20 points)

| Score | Criteria                                                                          |
| ----- | --------------------------------------------------------------------------------- |
| 0-5   | No goals stated. Just a problem or complaint.                                     |
| 6-10  | Vague aspirations ("make it better", "improve UX", "users should like it more").  |
| 11-15 | Goals stated but unmeasurable ("users should be happier", "it should feel fast"). |
| 16-20 | SMART goals with specific metrics ("reduce checkout latency to under 500ms p95"). |

**Questions to ask if low**:
- "What does success look like for this project?"
- "How will you measure whether this worked?"
- "What specific number or metric should change? By how much?"
- "If this project succeeds, what will be different in 3 months?"

---

### 3. Success Criteria (0-20 points)

| Score | Criteria                                                                        |
| ----- | ------------------------------------------------------------------------------- |
| 0-5   | None provided. No way to know when we're done.                                  |
| 6-10  | Subjective criteria only ("looks good", "feels fast", "stakeholder likes it").  |
| 11-15 | Some measurable criteria but incomplete coverage of goals.                      |
| 16-20 | Clear, testable acceptance criteria for ALL stated goals. Pass/fail verifiable. |

**Questions to ask if low**:
- "How will you know when this is done?"
- "What tests would prove this feature works correctly?"
- "What would a QA person check before signing off?"

---

### 4. Scope Boundaries (0-20 points)

| Score | Criteria                                                                                      |
| ----- | --------------------------------------------------------------------------------------------- |
| 0-5   | Unlimited scope. No boundaries stated. Everything could be in scope.                          |
| 6-10  | Some boundaries implied but not explicit. "We're not redesigning everything" type statements. |
| 11-15 | Boundaries stated but gaps exist. Some adjacent features unclear.                             |
| 16-20 | Clear in/out of scope with rationale for exclusions. Future considerations noted.             |

**Questions to ask if low**:
- "What is explicitly NOT part of this project?"
- "Are there related features we should defer to later?"
- "What's the MVP vs. nice-to-have?"
- "If you had to ship in half the time, what would you cut?"

---

### 5. Consistency (0-20 points)

| Score | Criteria                                                           |
| ----- | ------------------------------------------------------------------ |
| 0-5   | Major contradictions in requirements. Impossible to satisfy both.  |
| 6-10  | Some conflicting statements that need resolution.                  |
| 11-15 | Minor inconsistencies that need clarification but aren't blockers. |
| 16-20 | Internally consistent throughout. No contradictions.               |

**Questions to ask if low**:
- "You mentioned [X] but also [Y]. These seem to conflict. Which takes priority?"
- "Earlier you said [A], but now [B]. Can you clarify?"
- "If we can only do one of [X] or [Y], which matters more?"

---

## Confidence Thresholds

| Total Score | Interpretation              | Action                                                                          |
| ----------- | --------------------------- | ------------------------------------------------------------------------------- |
| < 70        | Major gaps in understanding | Ask 5+ questions targeting lowest-scoring dimensions. May need multiple rounds. |
| 70-84       | Moderate gaps               | Ask 3-5 targeted questions. One more round likely sufficient.                   |
| 85-94       | Minor gaps                  | Ask 1-2 specific questions. Almost ready.                                       |
| ≥ 95        | Ready                       | Generate contract. Proceed to phasing and specification.                        |

---

## Question Best Practices

### Do:
- **Be specific**: "What happens when a user tries to bookmark while offline?"
- **Offer options**: "Is offline support A) critical for MVP, B) nice-to-have, or C) future consideration?"
- **Reference context**: "You mentioned 'tags are better than folders.' Should tags be user-created or predefined?"
- **Limit quantity**: 3-5 questions max per round. Don't overwhelm.
- **Prioritize**: Target the lowest-scoring dimension first.

### Don't:
- Ask open-ended questions: "Tell me more" is not useful.
- Ask redundant questions: If they said "mobile app," don't ask "will this be on mobile?"
- Ask leading questions: "You don't want offline mode, right?"
- Ask compound questions: "What's the scope and timeline and who's the user?" is three questions.

---

## Scoring Worksheet

| Dimension        | Score    | Notes |
| ---------------- | -------- | ----- |
| Problem Clarity  | /20      |       |
| Goal Definition  | /20      |       |
| Success Criteria | /20      |       |
| Scope Boundaries | /20      |       |
| Consistency      | /20      |       |
| **TOTAL**        | **/100** |       |

**Lowest dimension**: _________________ (target questions here first)
