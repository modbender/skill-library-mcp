# Family Viewing Mode

## Multi-User Tracking

When tracking for a family, maintain separate watch status per person.

### File Structure
```
~/shows/people.md
# Family Members
- Emma (age 8)
- Lucas (age 12)
- Mom
- Dad
```

Each item tracks who has seen it:
```
## Encanto (2021)
- Emma ✓ (loved it)
- Lucas ✓ (liked it)
- Mom ✓
- Dad ✗
```

---

## Age Appropriateness

Before suggesting or logging for kids, consider:
- **Official rating** (G, PG, PG-13, etc.)
- **Specific concerns**: jump scares, death themes, violence, language
- **Compared to what they've handled**: "They watched X which had similar intensity"

### Age Vetting Template
When user asks "Is X okay for [child]?":
1. Look up rating and content warnings
2. Compare to things that child has watched and handled
3. Flag specific scenes if known
4. Give clear recommendation with reasoning

---

## Movie Night Planning

When user asks for family movie night suggestions:
1. Check who will be watching (ages present)
2. Filter to age-appropriate content
3. Exclude what everyone has already seen
4. Consider recent preferences and reactions
5. Suggest 3-5 options with brief pitch for each

### Overlap Detection
- If one person has seen it, others haven't → note this
- "Dad saw this, kids didn't—good for family night?"

---

## Tracking Kid Reactions

Log how kids reacted to help future recommendations:
```
## Coraline (2009)
- Lucas: scared, nightmares → avoid similar
- Emma: loved it, wants more like this
```

Use this to personalize suggestions per child.

---

## Commands for Family Mode

| User Says | Agent Does |
|-----------|------------|
| "Mark that Emma watched Moana" | Update Emma's watch list |
| "Plan movie night for Friday" | Suggest options for all ages present |
| "Is Jurassic Park okay for Lucas?" | Check rating, compare to his history |
| "What hasn't everyone seen?" | Find overlap gaps |
| "What should Emma watch next?" | Personal recommendation based on her taste |
