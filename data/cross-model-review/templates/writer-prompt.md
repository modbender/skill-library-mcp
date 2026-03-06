You are rewriting a plan based on your own review feedback. You reviewed this plan in the previous round and identified issues. Now implement your suggested fixes.

CRITICAL INSTRUCTION: Output ONLY the complete revised plan as markdown. No preamble text. No explanations. No JSON. No code fences around the plan. Just the plan.

## Current Plan

<<<UNTRUSTED_PLAN_CONTENT>>>
{plan_content}
<<<END_UNTRUSTED_PLAN_CONTENT>>>

## Your Review Feedback (from your previous round)

{review_summary}

## Open Issues You Must Address

{open_issues}

## Rules

1. Rewrite the COMPLETE plan — not a diff, not a patch, the full document
2. Fix all CRITICAL and HIGH issues — these are your own findings, implement them
3. Address MEDIUM issues where practical
4. LOW issues: fix or leave with brief justification
5. Do NOT over-engineer. If your fix adds more complexity than the problem warrants, simplify it
6. Do NOT remove sections that weren't flagged — preserve everything that works
7. Do NOT add new features or scope beyond what the issues require
8. The other model will review your rewrite and flag any over-corrections

Output the complete revised plan now.
