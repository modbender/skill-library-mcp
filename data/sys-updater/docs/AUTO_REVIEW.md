# Auto-Review System for sys-updater

Автоматическая система ревью обновлений пакетов для npm и brew в sys-updater.

## Обзор

Система автоматически проверяет доступные обновления пакетов npm и brew перед их установкой, используя:
- Данные из npm registry и Homebrew API
- GitHub Issues для выявления критических проблем
- Changelog analysis для обнаружения breaking changes
- Правила semver для определения уровня риска

## Архитектура

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   pkg_maint.py  │────▶│   auto_review   │────▶│  retry_logic    │
│   (check mode)  │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   npm_tracked.json      auto_review.log         npm_tracked.json
   brew_tracked.json     (decisions audit)      brew_tracked.json
```

## Файлы

- `scripts/auto_review.py` — основной модуль ревью
- `scripts/retry_logic.py` — логика повторных попыток обновления
- `state/apt/npm_tracked.json` — состояние npm пакетов
- `state/apt/brew_tracked.json` — состояние brew пакетов
- `logs/auto_review.log` — лог решений (retention 30 дней)

## Расширенная структура tracked.json

```json
{
  "items": {
    "package-name": {
      "firstSeenAt": "2024-01-01T00:00:00Z",
      "reviewedAt": null,
      "planned": false,
      "blocked": false,
      "note": null,
      "currentVersion": "1.2.3",
      "latestVersion": "1.2.4",
      "manager": "npm",
      "type": "package",
      
      // Новые поля для auto-review:
      "releaseDate": "2024-01-01T00:00:00Z",
      "autoReviewAt": "2024-01-03T00:00:00Z",
      "reviewedBy": "auto",
      "reviewResult": "ok",
      "failedAttempts": 0,
      "lastAttemptAt": null
    }
  }
}
```

### Описание полей

| Поле | Тип | Описание |
|------|-----|----------|
| `releaseDate` | string (ISO) | Дата релиза версии из npm/brew API |
| `autoReviewAt` | string (ISO) | Время выполнения auto-review |
| `reviewedBy` | "auto" \| "manual" \| null | Кто принял решение |
| `reviewResult` | "ok" \| "blocked" \| "pending" \| null | Результат ревью |
| `failedAttempts` | int | Счётчик неудачных попыток обновления |
| `lastAttemptAt` | string (ISO) \| null | Время последней попытки |

## Критерии принятия решений

### Версии patch (x.y.Z)

**Автоматически OK**, если:
- Прошло ≥2 дня с релиза
- Changelog не содержит danger keywords

### Версии minor (x.Y.z)

**Требуется проверка:**
- Прошло ≥2 дня с релиза
- Нет critical/blocking issues в GitHub за последние 3 дня
- Changelog не содержит danger keywords

### Версии major (X.y.z)

**Всегда BLOCKED** — требует ручного ревью

### Danger Keywords

При обнаружении в changelog/issue title:
- `breaking` / `breaking change`
- `regression`
- `rollback`
- `critical`
- `security vulnerability`
- `deprecat` (deprecated, deprecation)
- `removed`
- `dropped support`
- `incompatible`

### Blocking Issue Labels

Issues с метками:
- `bug`
- `critical`
- `security`
- `regression`
- `blocking`
- `crash`
- `data loss`

### Логика retry

- Максимум 3 попытки обновления
- Минимум 1 день между попытками
- После 3 неудачных попыток — auto-block
- Счётчик сбрасывается при успешном обновлении

## Rate Limiting

### GitHub API

- Неаутентифицированный доступ: 60 запросов/час
- Минимум 1 секунда между запросами
- При достижении лимита — логируется warning, пакеты помечаются как pending

### npm Registry

- Ограничения не документированы
- Используем стандартные HTTP timeout (30s)

### Homebrew API

- Ограничения не документированы
- Используем стандартные HTTP timeout (30s)

## Использование

### Автоматический запуск

Auto-review выполняется автоматически в `run_6am()` после `pkg_maint.py`:

```
run_6am()
  ├── pkg_maint.py check
  ├── pkg_maint.py upgrade
  ├── retry_logic.process_retries()
  └── auto_review.run_auto_review()
```

### Ручной запуск

```bash
# Полный auto-review
python3 scripts/apt_maint.py auto-review

# Сухой прогон (без сохранения)
python3 scripts/apt_maint.py auto-review --dry-run

# Подробный вывод
python3 scripts/apt_maint.py auto-review --verbose
```

### Независимый запуск модулей

```bash
# Только auto-review
python3 scripts/auto_review.py --verbose

# Только retry logic
python3 scripts/retry_logic.py --verbose
```

## Пример лога (auto_review.log)

```
2024-01-15T06:05:23Z [INFO] === AUTO-REVIEW START ===
2024-01-15T06:05:24Z [INFO] Starting auto-review: 3 npm, 2 brew packages
2024-01-15T06:05:25Z [INFO] [OK] npm/axios: Patch version with no danger indicators
2024-01-15T06:05:26Z [INFO] [BLOCKED] npm/express: Major version update (4.x → 5.x) requires manual review
2024-01-15T06:05:27Z [INFO] [BLOCKED] brew/node: Changelog contains danger keywords: breaking, incompatible
2024-01-15T06:05:28Z [INFO] [OK] npm/lodash: Minor version, no critical issues found
2024-01-15T06:05:28Z [INFO] Auto-review complete: 5 reviewed, 2 approved, 2 blocked
2024-01-15T06:05:28Z [INFO] === AUTO-REVIEW END ===
```

## Тестирование

```bash
# Запуск всех тестов
cd /home/moltuser/clawd/sys-updater
python3 tests/test_auto_review.py

# С подробным выводом
python3 tests/test_auto_review.py -v
```

## Безопасность

1. **Нет автоматических обновлений major версий** — всегда требуется ручное ревью
2. **Grace period 2 дня** — время для community на нахождение проблем
3. **GitHub issues monitoring** — проверка на critical bugs
4. **Changelog scanning** — поиск breaking changes
5. **Failed attempt tracking** — автоматический блок после 3 неудач

## Отладка

### Проверка отдельного пакета

```python
import sys
sys.path.insert(0, '/home/moltuser/clawd/sys-updater/scripts')
from auto_review import check_npm_package, auto_review_package, PackageMeta

# Проверить npm пакет
result = check_npm_package("express", "5.0.0")
print(result)

# Полное ревью
meta = PackageMeta(
    name="express",
    current_version="4.18.0",
    latest_version="5.0.0",
    manager="npm"
)
result, reason = auto_review_package(meta)
print(result, reason)
```

### Просмотр логов

```bash
# Последние решения
tail -50 logs/auto_review.log

# Решения по конкретному пакету
grep "express" logs/auto_review.log

# Только blocked
grep "BLOCKED" logs/auto_review.log
```

## Интеграция с существующей системой

Система полностью совместима с существующими механизмами:

- `planned` — пакет помечается для обновления при `reviewResult: "ok"`
- `blocked` — пакет блокируется при `reviewResult: "blocked"`
- `pkg_maint.py upgrade` — обновляет только `planned=True`
- Ручное ревью через `reviewedBy: "manual"` — auto-review пропускает такие пакеты

## TODO / Roadmap

- [ ] Поддержка кастомных реестров npm
- [ ] Кэширование GitHub API ответов
- [ ] Интеграция с security advisories (npm audit, GitHub Security Advisories)
- [ ] Webhook notifications для blocked пакетов
- [ ] ML-based risk scoring
