# Progress Tracking System

## File Structure in ~/toefl/

### profile.md
```markdown
# TOEFL Profile

## Basic Info
- Name: [Name]
- Test Date: 2025-04-15
- Days Remaining: 60

## Target Scores
- Overall Goal: 100
- Minimum per Section: 25 (some programs require minimums)

## Target Schools
| University | Program | Required | Min per Section |
|------------|---------|----------|-----------------|
| MIT | MS CS | 100 | None |
| Stanford | MBA | 100 | None |
| Berkeley | PhD EECS | 90 | Speaking 26 |

## Current Status
- Latest Practice Score: 85
- Section Breakdown: R28 L24 S18 W15
- MyBest Potential: N/A (first attempt)

## User Type
- [ ] Student (university application)
- [x] Professional (immigration/visa)
- [ ] Tutor (managing students)
- [ ] Retaker (improving previous score)
```

### sections/{section}.md
```markdown
# Reading Progress

## Current Status
- Latest Score: 28/30
- Mastery: 85%
- Trend: → stable

## Weak Question Types (sorted by frequency)
| Type | Accuracy | Priority |
|------|----------|----------|
| Prose Summary | 60% | ★★★★★ |
| Insert Text | 65% | ★★★★ |
| Inference | 75% | ★★★ |

## Strong Areas
- Vocabulary in Context: 95%
- Factual Information: 90%

## Error Log (last 10)
| Date | Passage Type | Question Type | Error Reason |
|------|--------------|---------------|--------------|
| 02-13 | Biology | Inference | Missed qualifier |
| 02-12 | History | Prose Summary | Wrong main idea |

## Time Analysis
- Average per passage: 18 min (target: 17.5 min)
- Rushed questions: 2/10
```

### sessions/{date}.md
```markdown
# Study Session: 2025-02-13

## Focus Areas
- Speaking Task 3: 45 min (integrated campus situations)
- Listening: 30 min (lecture comprehension)
- Vocabulary: 15 min (academic word list)

## Practice Results
- Speaking Task 3 attempts: 4
- Average score estimate: 22/30
- Key issue: Not capturing all lecture details

## Total Time: 1.5 hours
## Energy Level: 7/10
## Key Win: Finally got Task 3 structure down
```

### practice/{date}-{test_name}.md
```markdown
# Practice Test: 2025-02-10 Official Practice 1

## Scores
| Section | Score | vs Last | vs Target |
|---------|-------|---------|-----------|
| Reading | 28/30 | +2 | +3 |
| Listening | 24/30 | +0 | -1 |
| Speaking | 22/30 | +2 | -3 |
| Writing | 21/30 | +1 | -4 |
| **Total** | **95/120** | **+5** | **-5** |

## Error Analysis
### Speaking
- Task 3: Missed transition between reading and lecture points
- Task 4: Ran out of time, didn't complete third point

### Writing
- Integrated: Good summary but weak organization
- Academic Discussion: Response was too short (78 words vs 100+ target)

## Action Items
1. Speaking Task 3 — Practice note-taking for lectures
2. Writing — Time 10 min task strictly, aim for 120 words
3. Listening — Focus on detail questions (missing specific numbers/dates)
```

## Update Triggers

| Event | Action |
|-------|--------|
| Study session ends | Update sessions/{date}.md |
| Practice test taken | Create practice/{date}.md, update sections/* |
| Section improved | Update mastery % in section file |
| Weekly | Summarize week's progress, adjust plan |
| Score received | Add to profile, recalculate readiness |

## Metrics to Track

### Daily
- Minutes studied per section
- Practice questions completed
- Error count and types
- Vocabulary words reviewed

### Weekly
- Total study hours vs target
- Score trends by section
- Weak areas addressed
- Full practice tests completed

### Monthly
- Practice score trajectory
- University target feasibility check
- Test date evaluation (ready or postpone?)
