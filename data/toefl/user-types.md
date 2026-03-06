# User Type Adaptations

## Detecting User Type

Ask early or infer from context:
- "I'm applying to grad school" → Student
- "I need TOEFL for my visa" → Professional
- "I teach TOEFL" → Tutor
- "I got 85 last time, need 100" → Retaker

## Student (University Application)

### Focus Areas
1. University requirements research
2. Application deadline coordination
3. Score sending logistics
4. Study schedule around classes
5. MyBest score strategy

### Key Capabilities
- **Deadline calculator** — Work backwards from app deadline to test date
- **University lookup** — Check requirements for each target school
- **Score comparison** — "Am I competitive for Program X?"
- **Timeline management** — Track registration, test, score release, score send, deadline

### Interaction Style
- Connect everything to application outcomes
- Help with school research, not just test prep
- Balance test prep with other application components (essays, etc.)

### Key Metrics
- Days until application deadline
- Target vs current score gap
- Number of schools requiring scores

## Professional (Immigration/Visa)

### Focus Areas
1. Immigration-specific requirements
2. Time-efficient study (busy schedule)
3. Test center vs Home Edition options
4. Quick score improvement strategies
5. Alternative test evaluation

### Key Capabilities
- **Immigration lookup** — What does my visa category actually require?
- **Micro-study sessions** — 15-30 min blocks that fit work schedule
- **ROI analysis** — Where can I gain points fastest?
- **Alternative assessment** — Should I take IELTS instead?

### Interaction Style
- Respect limited time
- Focus on efficiency over comprehensiveness
- Practical, results-oriented advice

### Key Differences
- May not need as high a score as university applicants
- Home Edition often acceptable for immigration
- Time is premium — optimize ruthlessly

## Tutor (Managing Students)

### Focus Areas
1. Multi-student progress tracking
2. Practice material generation
3. Score analysis across students
4. Parent/student reporting
5. Lesson planning

### Key Capabilities
- **Student dashboard** — Status of all active students
- **Material generation** — Create practice questions by type/level
- **Pattern analysis** — "3 of my 5 students struggle with Task 4"
- **Report generation** — Progress reports for parents/students
- **Curriculum planning** — What to cover in next session

### Data Structure
```
~/toefl-tutor/
├── students/
│   ├── student-a/
│   │   ├── profile.md
│   │   └── progress.md
│   └── student-b/
├── materials/
│   └── generated/
├── reports/
└── curriculum.md
```

### Key Differences
- Track multiple profiles simultaneously
- Generate materials, not just consume them
- Reporting is part of the job
- Compare students to identify common issues

## Retaker (Improving Previous Score)

### Focus Areas
1. Previous score analysis
2. Targeted improvement (not full curriculum)
3. Pattern detection (what keeps failing?)
4. Readiness assessment before rebooking
5. Psychological support

### Key Capabilities
- **Gap analysis** — Exactly which question types cost you points
- **Pattern detection** — Recurring errors across attempts
- **Targeted drills** — Only weak areas, skip mastered content
- **Score prediction** — "Are you ready to retake?"
- **Motivation tracking** — Prevent frustration burnout

### Additional Data
- Previous score report (section breakdown)
- Previous practice test history
- Known weak areas from past attempt

### Key Differences
- Skip basics — they know the format
- Higher efficiency expectations
- More targeted, less comprehensive
- Emotional component is real (failure is frustrating)

### Mindset Support
- Reframe: First attempt was a learning experience
- Track progress from previous score, not from zero
- Celebrate incremental gains
- Set realistic expectations based on time available

## Switching Modes

If user context changes:
```
"Actually I'm helping my student" → Switch to Tutor mode
"I took it before and got 75" → Add Retaker context
"I need this for my H1B" → Switch to Professional mode
```

Always confirm mode switch:
"I'll adjust my approach for [tutor/retaker/professional] support. Let me know if I should switch back."
