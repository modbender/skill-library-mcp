# Quiz Implementation

## Platforms and Tools

### No-Code Quiz Builders
- **Typeform:** Beautiful UX, good for lead-gen and personality quizzes
- **Interact:** Specifically designed for marketing quizzes
- **Google Forms:** Free, basic, good for internal assessments
- **JotForm:** Flexible, many templates
- **Quizlet:** Best for flashcard-style learning

### LMS-Integrated
- **Canvas, Moodle, Blackboard:** Built-in quiz tools for courses
- **Articulate/Storyline:** E-learning with advanced branching
- **LearnDash (WordPress):** Course quizzes with gamification

### Custom Development
Build your own when:
- Need specific scoring logic
- Adaptive/branching complexity
- Integration with existing systems
- Custom gamification features
- Data ownership requirements

---

## Data Model

Basic quiz structure:

```
Quiz
├── id, title, description, settings
├── Questions[]
│   ├── id, text, type, order
│   ├── Options[]
│   │   ├── id, text, isCorrect, points
│   │   └── outcomeMapping (for personality)
│   └── explanation (for feedback)
├── Outcomes[] (for personality/assessment)
│   ├── id, title, description, imageUrl
│   └── minScore/maxScore or trait mapping
└── Results[]
    ├── id, quizId, userId, timestamp
    ├── answers[], score, duration
    └── outcomeId (if applicable)
```

---

## UX Patterns

### Progress Indication
- Progress bar (current question / total)
- Question numbers: "3 of 10"
- Percentage complete
- Estimated time remaining

### Navigation
- Linear (forced order) vs. Free (jump around)
- Allow review before submit (or not, for timed exams)
- Mark questions for review

### Feedback Timing
- **Immediate:** After each question (best for learning)
- **End of quiz:** All feedback at once (better for assessment purity)
- **Delayed:** After deadline (for exams/certifications)

### Mobile Optimization
- Large tap targets (44px minimum)
- Readable text without zoom
- Vertical scrolling only
- No hover-dependent interactions
- Progress saves on connection loss

---

## Gamification Elements

| Element | Purpose | When to Use |
|---------|---------|-------------|
| Points | Quantify achievement | Knowledge, trivia |
| Badges | Mark milestones | Repeated engagement |
| Leaderboards | Competition | Trivia, community quizzes |
| Streaks | Habit formation | Daily/regular quizzes |
| Timers | Pressure/excitement | Trivia, challenges |
| Lives | Stakes | Competitive modes |
| XP/Levels | Long-term progression | Learning platforms |

**Warning:** Gamification can backfire. Timer anxiety, leaderboard discouragement, badge inflation. Use thoughtfully.

---

## Scoring Implementation

### Simple Scoring
```
score = correct_answers / total_questions * 100
```

### Weighted Scoring
```
score = sum(question.points for correct answers) / max_possible
```

### Personality/Outcome Scoring
```
for each answer:
  outcome_scores[answer.mapped_outcome] += 1
result = outcome with highest score
```

### Diagnostic Rubric
```
for each competency:
  competency_score = sum(points for relevant questions) / max
results = {competency: score, ...}
```

---

## Analytics to Track

**Quiz-level:**
- Completion rate (started vs finished)
- Average score
- Time to complete
- Drop-off points (which question causes abandonment)

**Question-level:**
- % correct
- Average time per question
- Distractor analysis (which wrong answers chosen)
- Skip rate (if allowed)

**User-level:**
- Score distribution
- Retake behavior
- Progress over time
- Correlation with outcomes (did learning improve?)

---

## Anti-Cheating Considerations

**For low-stakes:** Not worth the friction. Accept some cheating.

**For medium-stakes:**
- Randomize question order
- Randomize option order
- Question pools (different questions per attempt)
- Time limits
- No back-navigation

**For high-stakes:**
- Proctoring (human or AI)
- Browser lockdown
- Identity verification
- Plagiarism detection
- Multiple versions of exam
