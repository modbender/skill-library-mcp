# Progress Tracking System

## File Structure in ~/neet/

### profile.md
```markdown
# Student Profile

## Basic Info
- Name: [Student Name]
- State: [Home State]
- Category: [General/OBC/SC/ST/EWS]
- Board: [CBSE/State Board/Other]
- Exam Date: 2025-05-04

## Targets
- Goal Score: [target]/720
- Goal Rank: [target rank]
- Dream College: [AIIMS Delhi/etc]
- Backup Colleges: [list]
- Preferred State: [for state quota]

## Current Status
- Latest Mock Score: [score]/720
- Estimated Rank: [rank]
- Days Until Exam: [countdown]
- Accuracy Rate: [%]
```

### subjects/{subject}.md
```markdown
# Physics Progress

## Current Status
- Latest Score: 145/180
- Mastery: 75%
- Accuracy: 82%
- Trend: ↑ improving

## Weak Chapters (sorted by ROI)
| Chapter | Mastery | Marks at Stake | Priority |
|---------|---------|----------------|----------|
| Electrostatics | 45% | 16 | ★★★★★ |
| Rotational Motion | 50% | 12 | ★★★★★ |
| Modern Physics | 60% | 14 | ★★★★ |

## Strong Chapters
- Ray Optics: 92%
- Units & Dimensions: 95%

## Error Log (last 10)
| Date | Chapter | Error Type | Fixed? |
|------|---------|------------|--------|
| 02-13 | EMI | Formula confusion | ✓ |
| 02-12 | Mechanics | Silly mistake | ✓ |

## NCERT Completion
- Class 11: 85%
- Class 12: 70%

## Study Hours This Week
- Target: 18h
- Actual: 15h
- Efficiency: 83%
```

### sessions/{date}.md
```markdown
# Study Session: 2025-02-13

## Morning (06:00-12:00)
- Biology: 3h — Human Physiology (Digestion, Respiration)
- Chemistry: 2.5h — Organic reactions practice

## Afternoon (14:00-18:00)
- Physics: 2.5h — Electrostatics problems
- Chemistry: 1.5h — Inorganic p-block revision

## Evening (19:00-23:00)
- Biology: 2h — NCERT reading (Genetics)
- Physics: 1.5h — Mock test analysis
- Revision: 30min — Flashcard review

## Metrics
- Total: 13.5h
- Focus Rating: 8/10
- Energy: Good morning, slight dip post-lunch
- Key Win: Finally understood Lenz's Law application
- Mistakes Made: 3 silly errors in mock
```

### mocks/{date}-{exam_name}.md
```markdown
# Mock Exam: 2025-02-10 Allen Test Series

## Scores
| Subject | Score | Attempted | Accuracy | vs Target |
|---------|-------|-----------|----------|-----------|
| Physics | 140/180 | 42/45 | 83% | -10 |
| Chemistry | 148/180 | 44/45 | 84% | -2 |
| Botany | 156/180 | 43/45 | 90% | +6 |
| Zoology | 160/180 | 44/45 | 91% | +10 |
| **Total** | **604/720** | **173/180** | **87%** | **+4** |

## Rank Estimate
- Expected AIQ Rank: ~12,000
- Government seat chance: Likely (state quota)

## Error Analysis
### Physics
- Q12: Rotational motion — wrong moment of inertia formula
- Q31: EMI — sign error in Lenz's law
- Q42: Modern physics — calculation mistake

### Chemistry
- Q8: Organic — missed resonance effect
- Q23: Physical — log calculation error

## Time Analysis
- Physics: 58 min (target 55) — rushing at end
- Chemistry: 52 min (target 55) — good
- Biology: 85 min (target 90) — efficient

## Action Items
1. Rotational motion — revise moment of inertia formulas today
2. EMI signs — make flashcard for Lenz's law
3. Organic resonance — practice 20 GOC problems
```

### flashcards/
```
flashcards/
├── biology-diagrams.md      # Labeled diagrams for quick revision
├── chemistry-reactions.md   # Named reactions, mechanisms
├── physics-formulas.md      # All formulas by chapter
├── mnemonics.md             # Memory tricks
└── review-schedule.md       # Spaced repetition tracker
```

## Update Triggers

| Event | Action |
|-------|--------|
| Study session ends | Update sessions/{date}.md |
| Mock exam taken | Create mocks/{date}.md, update subjects/* |
| Chapter completed | Update mastery in subject file |
| Weekly | Summarize progress, adjust next week's plan |
| NCERT chapter finished | Update NCERT completion % |

## Metrics to Track

### Daily
- Hours studied per subject
- Questions practiced
- Accuracy rate
- NCERT pages read

### Weekly
- Total study hours vs target
- Mock score trends
- Weak chapters addressed
- Flashcard review completion
- NCERT completion progress

### Monthly
- Mock exam score trajectory
- Rank estimate changes
- College target feasibility
- Burnout indicators
