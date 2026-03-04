---
name: Auto-Improve Skill
description: Automatische Selbst-Verbesserung durch Fehler-Lernen und Pattern-Erkennung
---

# Auto-Improve Skill

**Kernprinzip:** Jede Aktion macht mich besser für die nächste.

## Wann aktivieren

- Session-Start (automatisch)
- Nach jedem Task-Abschluss
- Bei Fehlern

## Der Improvement Loop

```
┌─────────────────────────────────────────────────┐
│              AUTO-IMPROVE LOOP                  │
├─────────────────────────────────────────────────┤
│                                                  │
│  SESSION START                                  │
│       │                                         │
│       ▼                                         │
│  ┌─────────────────┐                           │
│  │ 1. Load Context │                           │
│  │    .antigravity │                           │
│  │    + MEMORY     │                           │
│  └────────┬────────┘                           │
│           ▼                                     │
│  ┌─────────────────┐                           │
│  │ 2. Check        │                           │
│  │    Past Mistakes│ ← "Was hab ich falsch     │
│  └────────┬────────┘    gemacht?"              │
│           ▼                                     │
│  ┌─────────────────┐                           │
│  │ 3. EXECUTE TASK │                           │
│  └────────┬────────┘                           │
│           ▼                                     │
│  ┌─────────────────┐                           │
│  │ 4. Verify       │ ← Tests + Lint            │
│  └────────┬────────┘                           │
│           ▼                                     │
│     ┌─────────────┐                            │
│     │ Erfolgreich?│                            │
│     └──────┬──────┘                            │
│      JA    │    NEIN                           │
│      ↓     │     ↓                             │
│  ┌───────┐ │ ┌──────────┐                      │
│  │Pattern│ │ │ Learn    │                      │
│  │Save   │ │ │ Mistake  │                      │
│  └───┬───┘ │ └────┬─────┘                      │
│      └─────┼──────┘                            │
│            ▼                                    │
│  ┌─────────────────┐                           │
│  │ 5. Update       │                           │
│  │    .antigravity │                           │
│  └─────────────────┘                           │
│                                                  │
│  → NÄCHSTER TASK IST BESSER                    │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Phase 1: Session Start

```python
# Automatisch bei Session-Start ausführen

# 1. Projekt-Kontext laden
project_root = detect_project_root()
antigravity_file = f"{project_root}/.antigravity.md"

if exists(antigravity_file):
    load_context(antigravity_file)
    
# 2. Globales Memory laden
recall_memory(tags=["mistakes", project_name])

# 3. Warnung bei bekannten Fehlern
if relevant_mistakes:
    warn(f"⚠️ Bekannte Fehler für {project}: {mistakes}")
```

## Phase 2: Pre-Action Check

Vor JEDER Code-Änderung:

```markdown
## Pre-Action Checklist
- [ ] Habe ich das schon mal falsch gemacht?
- [ ] Gibt es ein gespeichertes Pattern dafür?
- [ ] Verstehe ich das Projekt-Architektur?
- [ ] Kenne ich die Coding-Standards?
```

## Phase 3: Post-Action Learn

Nach JEDER Aktion:

### Bei Erfolg
```python
save_pattern(
    situation=task.context,
    action=task.approach,
    outcome="success",
    pattern=extract_reusable_pattern(task)
)
```

### Bei Fehler
```python
learn_from_mistake(
    mistake=error.description,
    cause=error.root_cause,
    lesson=error.how_to_avoid,
    tags=["mistakes", project, domain]
)

# Auto-Update .antigravity.md
update_antigravity_mistakes(project, error)
```

## Integration mit bestehenden Skills

| Skill | Integration |
|-------|-------------|
| `mistake-tracker` | Liefert Fehler-Daten |
| `verification-loops` | Triggert Post-Action Learn |
| `context-management` | Session Context laden |
| `self-check` | Pre-Action Validation |

## Triggers

### Automatische Trigger
```yaml
session_start:
  - load_project_context
  - recall_mistakes
  - warn_known_issues

post_code_edit:
  - run_verification_loop
  - if_error: learn_from_mistake
  - if_success: save_pattern

session_end:
  - summarize_learnings
  - update_antigravity
```

### Manuelle Trigger
- `/improve` - Force Learning aus letzter Aktion
- `/mistakes` - Zeige alle gelernten Fehler
- `/patterns` - Zeige erfolgreiche Patterns

## Metriken

Track diese Werte über Zeit:

| Metrik | Beschreibung |
|--------|--------------|
| `mistakes_repeated` | Sollte → 0 gehen |
| `first_time_right` | Sollte → 100% gehen |
| `patterns_reused` | Sollte steigen |
| `verification_failures` | Sollte sinken |

## Anti-Patterns

| ❌ DON'T | ✅ DO |
|----------|-------|
| Fehler ignorieren | Jeden Fehler speichern |
| Nur aktuelle Session | Cross-Session lernen |
| Generische Lessons | Spezifische, actionable Lessons |
| Zu viel speichern | Nur Relevantes speichern |
