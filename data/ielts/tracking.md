# Progress Tracking System

## File Structure in ~/ielts/

### profile.md
```markdown
# IELTS Profile

## Basic Info
- Test Type: [Academic/General Training]
- Exam Date: [YYYY-MM-DD]
- Days Remaining: [countdown]

## Targets
- Overall Band: [target]
- Listening: [minimum required]
- Reading: [minimum required]
- Writing: [minimum required]
- Speaking: [minimum required]
- Purpose: [university/immigration/professional]
- Specific Goal: [e.g., "University of Melbourne MSc Data Science" or "Canada Express Entry CLB 9"]

## Current Status
- Last Diagnostic/Mock: [date]
- Estimated Overall: [band]
- Gap to Target: [+/- X bands]
```

### sections/{section}.md
```markdown
# Writing Progress

## Current Status
- Latest Band Estimate: 6.5
- Target: 7.0
- Gap: 0.5 bands

## Criteria Breakdown
| Criterion | Current | Target | Gap |
|-----------|---------|--------|-----|
| Task Achievement | 6.5 | 7.0 | -0.5 |
| Coherence & Cohesion | 6.0 | 7.0 | -1.0 |  ← Priority
| Lexical Resource | 7.0 | 7.0 | 0 |
| Grammatical Range | 6.5 | 7.0 | -0.5 |

## Recurring Issues
- [ ] Overuse of "However" and "Moreover"
- [ ] Weak overview in Task 1
- [ ] Thesis unclear in introduction
- [x] Run-on sentences (improved)

## Practice Log (last 10)
| Date | Task | Band | Notes |
|------|------|------|-------|
| 02-13 | Task 2: Education | 6.5 | CC weak - paragraph links |
| 02-12 | Task 1: Line graph | 7.0 | Good overview |

## Time Analysis
- Task 1 avg completion: 22 min (target: 20)
- Task 2 avg completion: 42 min (target: 40)
```

### sessions/{date}.md
```markdown
# Study Session: 2025-02-13

## Focus Areas
- Writing: Task 1 overview practice (45 min)
- Speaking: Part 2 fluency drill (30 min)
- Vocabulary: Academic collocations (15 min)

## Completed
- ✓ 2 Task 1 graph descriptions with self-assessment
- ✓ 3 Part 2 cue cards (recorded, reviewed)
- ✓ 20 new collocations added to Anki

## Insights
- Part 2: Still using "um" too much in first 30 seconds
- Task 1: Overview improving, need more comparison language

## Tomorrow's Plan
- Listening Section 4 practice (academic lectures)
- Reading: True/False/Not Given drill (20 questions)
```

### mocks/{date}.md
```markdown
# Mock Test: 2025-02-13

## Scores
| Section | Band | vs Last | vs Target |
|---------|------|---------|-----------|
| Listening | 7.0 | +0.5 | 0 |
| Reading | 6.5 | 0 | -0.5 |
| Writing | 6.5 | 0 | -0.5 |
| Speaking | 7.0 | +0.5 | 0 |
| **Overall** | **6.75→7.0** | +0.25 | -0.0 |

## Error Analysis

### Reading
- Q14: True/False/NG — said True, was NG
- Q27-29: Matching headings — lost 2/3 (time pressure)
- Time: Finished with 0 min left (need 5 min buffer)

### Writing
- Task 1: Overview present but generic
- Task 2: Conclusion too short, didn't summarize main points

## Action Items
1. T/F/NG: Review "Not Given" logic — key is *absence* of info
2. Matching headings: Read headings FIRST, then skim paragraphs
3. Task 2 conclusions: Minimum 2 sentences restating position
```

### essays/{date}-{task}.md
```markdown
# Writing Task 2: 2025-02-13

## Prompt
Some people believe that children should spend all their free time with their families. Others say they should be allowed to spend time with friends. Discuss both views and give your opinion.

## My Response
[Full essay text here]

## Assessment
| Criterion | Band | Feedback |
|-----------|------|----------|
| Task Achievement | 6.5 | Position clear but not fully developed in conclusion |
| Coherence & Cohesion | 6.0 | Overuse of "However", weak paragraph openings |
| Lexical Resource | 7.0 | Good range, natural collocations |
| Grammatical Range | 6.5 | Some complex structures, occasional errors |
| **Overall** | **6.5** | |

## Band 7 Rewrite (weak parts)
Original: "However, some people think children should spend time with friends."
Improved: "Proponents of peer interaction, by contrast, argue that friendships cultivate social skills that family settings alone cannot provide."

## Patterns to Fix
- Start paragraphs with topic sentence, not linking word
- Use "by contrast" / "conversely" instead of always "However"
```

## Metrics to Track

### Per Session
- Time spent per section
- Number of practice items completed
- Error patterns identified

### Per Section
- Band trajectory over time (graph data points)
- Time management (completion within limits)
- Criteria breakdown (Writing/Speaking)
- Question type accuracy (Listening/Reading)

### Overall
- Mock test scores over time
- Days to exam vs band gap
- Ready/Not Ready assessment
