# Behavior Tracking Patterns

## Logging Incidents

Every incident entry should capture:
- **What happened** — Specific description
- **When** — Date, time, context (alone? after meal? visitors?)
- **Where** — Location in home
- **Potential trigger** — If identifiable

### Example Log Entries

```json
{"date":"2024-01-15T14:30","type":"incident","pet":"Luna","desc":"Peed on couch","context":"Left alone 5 hours","tags":["potty","indoor","alone"]}
{"date":"2024-01-16T08:00","type":"incident","pet":"Luna","desc":"Knocked plant off shelf","context":"Morning zoomies","tags":["destruction","zoomies"]}
{"date":"2024-01-17T19:00","type":"incident","pet":"Max","desc":"Growled at delivery person","context":"Doorbell rang","tags":["aggression","strangers","door"]}
```

---

## Common Patterns to Track

### Dogs
| Behavior | Track | Pattern Questions |
|----------|-------|-------------------|
| Indoor accidents | Time, location, duration alone | Always same spot? Correlated with time alone? |
| Destructive chewing | What item, when, context | When alone? After insufficient exercise? |
| Barking | Trigger, duration, response | Specific triggers? Attention-seeking? |
| Leash reactivity | What triggered, intensity | Dogs? People? Bikes? Distance threshold? |

### Cats
| Behavior | Track | Pattern Questions |
|----------|-------|-------------------|
| Litter box issues | Location used, when, box status | Box clean? New litter brand? Stress event? |
| Scratching furniture | What item, time, before/after | Near window? Territory marking? Boredom? |
| Aggression | Target, context, warning signs | Petting-induced? Redirected? Play aggression? |
| Excessive vocalization | Time, trigger, response | Night? Hunger? Attention? Senior cat? |

---

## Spotting Patterns

When generating reports, look for:

1. **Time patterns** — Same time of day? Day of week?
2. **Context patterns** — After specific events? When alone? After visitors?
3. **Location patterns** — Same spot? Specific room?
4. **Frequency trends** — Increasing? Decreasing? Stable?
5. **Correlation with changes** — New food? New schedule? New family member?

---

## Progress Indicators

Positive signs:
- Decreasing incident frequency
- Longer gaps between incidents
- Reduced intensity
- Better response to redirection

Concerning signs:
- Increasing frequency
- New types of incidents
- Escalating intensity
- Regression after progress

---

## When to Recommend Professional Help

Log suggests escalation needed when:
- Aggression toward people or animals
- Sudden behavior changes (rule out medical)
- Self-harm or extreme anxiety
- No improvement despite consistent approach
- Behavior beyond normal species range

Note: Agent logs and tracks, does not diagnose. Recommend vet or certified behaviorist for serious concerns.
