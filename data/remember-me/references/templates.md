# Templates

## Daily memory entry

```markdown
- [HH:MM TZ] Tag: <FACT|PREFERENCE|GOAL|HYPOTHESIS>
  Signal: <what happened>
  Memory: <what to remember>
  Confidence: <high|medium|low>  # required for HYPOTHESIS
  Impact-Score: <1|2|3>
  Outcome/TODO: <next action>
```

## Long-term memory entry

```markdown
## Preferences / behavior
- <durable preference>

## Assumptions (Hypotheses)
- <inference> (confidence: <high|medium|low>, status: <untested|validated|rejected>)

## Active priorities
- <current focus>

## Boundaries
- <explicit do/don't>
```

## Explicit remember request

```markdown
- [HH:MM TZ] User explicitly asked to remember: <content>
  Scope: <project/personal/workflow>
  Retention: <temporary/long-term>
```

## Demotion (stale long-term memory)

```markdown
- [HH:MM TZ] Demoted from MEMORY.md: <entry>
  Reason: <contradicted|abandoned|stale>
  Status: stale
```

## Hypothesis discard

```markdown
- [HH:MM TZ] Discarded hypothesis: <hypothesis>
  Reason: <not validated after 5 sessions|contradicted>
```
