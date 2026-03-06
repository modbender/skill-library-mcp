# Scoring Rubric Template

Use this template to create a project-specific scoring rubric. Customize the modifiers based on the onboarding interview answers.

## Base Score: 50 (neutral, well-implemented PR)

## Positive Modifiers

| Signal | Points | Notes |
|--------|--------|-------|
| Fixes a security vulnerability | +20 | Highest priority for most projects |
| Bug fix with test coverage | +10 | Reliable fix with proof |
| Improves core functionality | +10 | Directly advances the project mission |
| Performance improvement (measured) | +8 | Must include benchmarks or evidence |
| Improves onboarding/UX | +8 | Lowers barrier to adoption |
| Adds/improves key integration | +7 | Extends project reach |
| Documentation improvement | +5 | Helps users and contributors |
| Has tests | +5 | Quality signal |
| Small, focused diff | +5 | Under 200 lines changed, under 5 files |
| Addresses an open issue | +3 | Community-responsive |

## Negative Modifiers

| Signal | Points | Notes |
|--------|--------|-------|
| Spam or promotional content | -30 | Auto-reject |
| Introduces unwanted dependency | -25 | Customize: what counts as unwanted? |
| Violates core principle | -20 | Customize: what are the principles? |
| Large diff with no tests | -15 | Over 500 lines, zero test coverage |
| AI slop / low-quality generated code | -15 | Low effort, copy-paste errors |
| Adds unnecessary abstraction | -12 | Over-engineering |
| Breaks API without migration path | -12 | Must handle gracefully |
| Duplicate of existing PR | -10 | Wastes maintainer time |
| Unrelated scope / feature creep | -10 | Not what the project needs |
| Misleading description | -8 | Description does not match the code |
| No description or context | -5 | Hard to evaluate |
| PR template unfilled | -5 | Low-effort signal |

## Score Interpretation

| Score | Action |
|-------|--------|
| 80-100 | Strong align. Prioritize review. |
| 50-79 | Reasonable. Standard review queue. |
| 35-49 | Weak align. Close or request major changes. |
| 0-34 | Misaligned. Close with explanation. |

## Customization Guide

After the onboarding interview, customize this rubric by:

1. **Adding project-specific positive modifiers** for areas where you want help
2. **Adding project-specific negative modifiers** for anti-patterns in your project
3. **Adjusting point values** based on your priorities (security-first projects might bump security to +25)
4. **Adding file-path heuristics** (e.g., changes to `src/auth/*` get +5 security bonus)
5. **Defining "unwanted dependencies"** and "core principles" concretely
