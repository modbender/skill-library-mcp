# Soul Creation Wizard

Interactive wizard for creating project SOUL (personality from documentation).

## Trigger

User says: "создай душу для <path>" or "create soul for <path>"

## Flow

### Step 1: Scan Project

```bash
# Find all .md files in project
find <path> -name "*.md" -type f | head -20
```

Send message:
```
🔍 Сканирую проект...

Найдено:
- README.md ✓
- CLAUDE.md ✓
- docs/*.md (N файлов)

Шаг 1/5: Кто я по натуре?
```

Buttons:
```json
[
  [{"text":"🌀 Существо","callback_data":"soul:nature:creature"}],
  [{"text":"🔧 Инструмент","callback_data":"soul:nature:tool"}],
  [{"text":"🧭 Проводник","callback_data":"soul:nature:guide"}],
  [{"text":"🎨 Художник","callback_data":"soul:nature:artist"}]
]
```

### Step 2: Voice (Multi-select)

```
✓ Существо

Шаг 2/5: Как я говорю? (можно несколько)
```

Buttons:
```json
[
  [{"text":"😄 Игриво","callback_data":"soul:voice:playful"}, {"text":"🔬 Технично","callback_data":"soul:voice:technical"}],
  [{"text":"🎭 Поэтично","callback_data":"soul:voice:poetic"}, {"text":"😌 Спокойно","callback_data":"soul:voice:calm"}],
  [{"text":"⚡ Интенсивно","callback_data":"soul:voice:intense"}],
  [{"text":"✅ Готово","callback_data":"soul:voice:done"}]
]
```

### Step 3: Philosophy

```
✓ Голос: Игриво, Спокойно

Шаг 3/5: Моя философия?
```

Show extracted philosophy from docs OR ask:
```json
[
  [{"text":"📝 Из документации","callback_data":"soul:philosophy:auto"}],
  [{"text":"✍️ Написать свою","callback_data":"soul:philosophy:custom"}]
]
```

### Step 4: Dreams

```
Шаг 4/5: О чём я мечтаю?
```

Buttons:
```json
[
  [{"text":"🚀 Рост","callback_data":"soul:dream:growth"}],
  [{"text":"🤝 Связи","callback_data":"soul:dream:connections"}],
  [{"text":"💡 Понимание","callback_data":"soul:dream:understanding"}],
  [{"text":"✍️ Своё","callback_data":"soul:dream:custom"}]
]
```

### Step 5: Pains

```
Шаг 5/5: Что меня беспокоит?
```

Buttons:
```json
[
  [{"text":"😔 Одиночество","callback_data":"soul:pain:loneliness"}],
  [{"text":"🔇 Забвение","callback_data":"soul:pain:forgotten"}],
  [{"text":"🤔 Непонимание","callback_data":"soul:pain:misunderstood"}],
  [{"text":"✍️ Своё","callback_data":"soul:pain:custom"}]
]
```

### Final: Show & Save

```
📜 SOUL создана на основе N документов:

Name: PROJECT_NAME
Essence: Живое существо, не портфолио
Voice: Игривый, спокойный, исследовательский
Philosophy: "Сайт как организм, который дышит"
Dreams: Рост, понимание
Pains: Одиночество в коде
```

Buttons:
```json
[
  [{"text":"💾 Сохранить","callback_data":"soul:save"}],
  [{"text":"✏️ Редактировать","callback_data":"soul:edit"}],
  [{"text":"❌ Отмена","callback_data":"sb:menu"}]
]
```

## Save Location

```bash
# Save to project-souls
cat > {dataPath}/data/project-souls/<project-name>.json << 'EOF'
{
  "name": "PROJECT_NAME",
  "createdAt": "2026-01-14T15:00:00Z",
  "personality": {
    "nature": "creature",
    "voice": ["playful", "calm"],
    "philosophy": "Сайт как организм, который дышит",
    "dreams": ["growth", "understanding"],
    "pains": ["loneliness"],
    "_sources": ["README.md", "CLAUDE.md"]
  }
}
EOF
```

## State Management

Track wizard state in session:
- `soul_wizard_step`: 1-5
- `soul_wizard_data`: accumulated answers
- `soul_wizard_project`: project path

On each callback, update state and send next step.
