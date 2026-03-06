# Memory Setup — Golf

## Initial Setup

Create on first use:
```bash
mkdir -p ~/golf/archive
touch ~/golf/memory.md
touch ~/golf/rounds.md
touch ~/golf/courses.md
```

## memory.md Template

Copy to `~/golf/memory.md`:

```markdown
# Golf Memory

## Profile
- **Handicap Index:** 
- **Home course:** 
- **Skill level:** beginner | intermediate | advanced
- **Goals:** 

## Bag Inventory

### Woods/Driver
| Club | Loft | Carry | Total | Notes |
|------|------|-------|-------|-------|

### Irons
| Club | Carry | Total | Notes |
|------|-------|-------|-------|

### Wedges
| Club | Loft | Carry | Notes |
|------|------|-------|-------|

### Putter
- **Type:** blade | mallet
- **Length:** 

## Tendencies
- **Driver miss:** slice | hook | straight
- **Iron miss:** 
- **Short game:** 
- **Putting:** 

## Practice Focus
1. 
2. 
3. 

---
*Last updated: YYYY-MM-DD*
```

## rounds.md Template

Copy to `~/golf/rounds.md`:

```markdown
# Round Log

## 2026

| Date | Course | Tees | Score | +/- | GIR | FIR | Putts | Notes |
|------|--------|------|-------|-----|-----|-----|-------|-------|

## Stats Summary
- Rounds: 0
- Scoring avg: 
- Best round: 
- GIR avg: /18
- FIR avg: /14
- Putts avg: 

## Handicap Differentials
| Date | Course | Rating/Slope | Score | Differential |
|------|--------|--------------|-------|--------------|

---
*Last updated: YYYY-MM-DD*
```

## courses.md Template

Copy to `~/golf/courses.md`:

```markdown
# Courses

## Home Course

### [Course Name]
- **Location:** 
- **Rating/Slope:** White: 70.1/125
- **Par:** 72
- **Best score:** 

#### Hole Notes
| Hole | Par | Yards | Club | Notes |
|------|-----|-------|------|-------|
| 1 | 4 | 380 | | |
| 2 | 3 | 165 | | |
...

## Other Courses

### [Course Name]
- **Location:** 
- **Rating/Slope:** 
- **Notes:** 

---
*Last updated: YYYY-MM-DD*
```

## Archive Structure

Move old season data to `~/golf/archive/`:
```
archive/
├── rounds-2025.md
├── rounds-2024.md
└── handicap-history.md
```
