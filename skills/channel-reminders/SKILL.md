# Channel Reminders

Навык для создания напоминаний через cron jobs с доставкой в Telegram.

---

## ⚠️ ТРЕБОВАНИЯ (проверь перед использованием)

### 1. Heartbeat должен быть включён

В `~/.openclaw/openclaw.json` проверь:

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "5m",      // ← НЕ должен быть "0m" или отсутствовать
        "target": "last"    // ← Куда отправлять ответы
      }
    }
  }
}
```

Если `heartbeat.every` = "0m" или отсутствует — напоминания НЕ будут работать!

### 2. HEARTBEAT.md должен содержать инструкцию

В `HEARTBEAT.md` main агента **ОБЯЗАТЕЛЬНО** добавь раздел для обработки напоминаний:

```markdown
### Напоминания (systemEvent)

Когда получаешь systemEvent с напоминанием (обычно содержит ⏰, 📅, 💰, 📞, ✅, 🔔, 💊, 🏃 и т.д.) — передай его пользователю в Telegram.

**Пример:**
- Получено: `⏰ НАПОМИНАНИЕ: оплатить интернет`
- Ответ в Telegram: `💰 Напоминаю: пора оплатить интернет!`

Просто доставь напоминание без лишних комментариев.
```

### 3. wakeMode: "now" в cron job

Всегда указывай `"wakeMode": "now"` чтобы heartbeat сработал сразу:

```json
{
  "sessionTarget": "main",
  "wakeMode": "now",    // ← ОБЯЗАТЕЛЬНО для немедленного срабатывания
  "payload": { ... }
}
```

Без этого напоминание будет ждать следующего heartbeat (до 5 минут).

---

## 🧪 ПОСЛЕ УСТАНОВКИ: Тестирование

После установки навыка **обязательно протестируй** все подходы с пользователем:

### Шаг 1: Тест простого напоминания (main агент)
```
Поставь тестовое напоминание через 1 минуту
```

### Шаг 2: Тест через message tool (если есть несколько ботов)
```
Отправь тестовое сообщение через message tool
```

### Шаг 3: Определи рабочий вариант

После тестов **запиши в память** какой подход работает:

**Пример записи в `MEMORY.md` или `memory/YYYY-MM-DD.md`:**
```markdown
## Напоминания

**Рабочий подход:** sessionTarget: "main" + systemEvent + wakeMode: "now"
**Проверено:** 2026-02-14
**Chat ID пользователя:** 7977422300
```

### Шаг 4: Если не работает

Проверь:
1. ✅ Heartbeat включён (`heartbeat.every` ≠ "0m")
2. ✅ HEARTBEAT.md содержит инструкцию для напоминаний
3. ✅ `wakeMode: "now"` указан в cron job
4. ✅ Telegram канал настроен и работает

---

## Быстрый старт

### Для MAIN агента

```json
{
  "name": "Напоминание",
  "schedule": { "kind": "at", "at": "2026-02-14T15:00:00+03:00" },
  "sessionTarget": "main",
  "wakeMode": "now",
  "payload": {
    "kind": "systemEvent",
    "text": "⏰ НАПОМИНАНИЕ: текст напоминания"
  }
}
```

Main агент получит systemEvent → heartbeat сработает → агент ответит в чат.

---

### Для НЕ-main агентов (Semen, Andrey, Hristofor, Discussions)

**Используй схему: main агент + message tool**

```json
{
  "agentId": "main",
  "name": "Напоминание от Semen",
  "schedule": { "kind": "at", "at": "2026-02-14T15:00:00+03:00" },
  "sessionTarget": "main",
  "wakeMode": "now",
  "payload": {
    "kind": "systemEvent",
    "text": "📤 ОТПРАВИТЬ НАПОМИНАНИЕ:\naccountId: semen\ntarget: 7977422300\nmessage: 🤗 текст напоминания"
  }
}
```

**Как это работает:**
1. Cron срабатывает → systemEvent идёт в main session main агента
2. Main агент видит `📤 ОТПРАВИТЬ НАПОМИНАНИЕ:` в HEARTBEAT.md
3. Main агент парсит accountId, target, message
4. Main агент отправляет через `message` tool с указанным accountId
5. Пользователь получает сообщение от бота НЕ-main агента

---

## Необходимые данные

### Chat ID пользователя

**Где взять:**
```bash
curl "https://api.telegram.org/bot<BOT_TOKEN>/getUpdates" | jq '.result[].message.chat.id'
```

**Или из metadata сообщения** — в заголовке Telegram сообщения виден `id:XXXXXXXX`

### AccountId для каждого агента

| Агент | accountId |
|-------|-----------|
| Джон Зойдберг (main) | main |
| Семён | semen |
| Андрей | andrey |
| Христофор | hristofor |
| Discussions | discussions |

---

## Типы расписаний

### Одноразовое (at)

```json
{ "kind": "at", "at": "2026-02-14T15:00:00+03:00" }
```

⚠️ **Всегда указывай таймзону!** Без неё = UTC.

### Повторяющееся (cron)

```json
{ "kind": "cron", "expr": "0 9 * * *", "tz": "Europe/Moscow" }
```

| Выражение | Значение |
|-----------|----------|
| `0 9 * * *` | Каждый день в 9:00 |
| `0 9 * * 1-5` | Будни в 9:00 |
| `0 18 * * 5` | Каждую пятницу в 18:00 |
| `0 */2 * * *` | Каждые 2 часа |

### Интервал (every)

```json
{ "kind": "every", "everyMs": 3600000 }
```

| Интервал | Миллисекунды |
|----------|--------------|
| 5 минут | 300000 |
| 1 час | 3600000 |
| 24 часа | 86400000 |

---

## Примеры

### Main агент: напомнить через 10 минут

```json
{
  "name": "Напоминание через 10 мин",
  "schedule": { "kind": "at", "at": "<текущее время + 10 мин>" },
  "sessionTarget": "main",
  "wakeMode": "now",
  "payload": {
    "kind": "systemEvent",
    "text": "⏰ НАПОМИНАНИЕ: проверить почту"
  }
}
```

### Semen: ежедневное напоминание

```json
{
  "agentId": "main",
  "name": "Утреннее напоминание от Semen",
  "schedule": { "kind": "cron", "expr": "0 9 * * *", "tz": "Europe/Moscow" },
  "sessionTarget": "main",
  "wakeMode": "now",
  "payload": {
    "kind": "systemEvent",
    "text": "📤 ОТПРАВИТЬ НАПОМИНАНИЕ:\naccountId: semen\ntarget: 7977422300\nmessage: 🤗 Доброе утро! Проверь задачи на сегодня."
  }
}
```

### Hristofor: напоминание об оплате

```json
{
  "agentId": "main",
  "name": "Оплата интернета",
  "schedule": { "kind": "at", "at": "2026-02-25T10:00:00+03:00" },
  "sessionTarget": "main",
  "wakeMode": "now",
  "payload": {
    "kind": "systemEvent",
    "text": "📤 ОТПРАВИТЬ НАПОМИНАНИЕ:\naccountId: hristofor\ntarget: 7977422300\nmessage: 💰 Напоминание: оплатить интернет до 28 февраля"
  }
}
```

---

## Управление напоминаниями

### Посмотреть все
```
cron list
```

### Удалить
```
cron remove jobId: "uuid"
```

### Отключить/включить
```
cron update jobId: "uuid" patch: { enabled: false }
cron update jobId: "uuid" patch: { enabled: true }
```

---

## Формат systemEvent для НЕ-main агентов

```
📤 ОТПРАВИТЬ НАПОМИНАНИЕ:
accountId: <accountId бота>
target: <Chat ID пользователя>
message: <текст напоминания с эмодзи>
```

**Эмодзи для разных типов:**
| Эмодзи | Агент |
|--------|-------|
| 🤗 | Semen |
| 🧑💻 | Andrey |
| 💰 | Hristofor |
| 💬 | Discussions |

---

## Настройка HEARTBEAT.md main агента

### Проверка

Перед использованием навыка убедись, что в `HEARTBEAT.md` main агента есть инструкция для обработки `📤 ОТПРАВИТЬ НАПОМИНАНИЕ:`.

**Проверь файл:** `~/.openclaw/workspace-main/HEARTBEAT.md`

**Ищи раздел:**
```markdown
### Напоминания от других агентов (📤 ОТПРАВИТЬ НАПОМИНАНИЕ)
```

### Если раздела нет — добавь:

```markdown
### Напоминания от других агентов (📤 ОТПРАВИТЬ НАПОМИНАНИЕ)

Когда получаешь systemEvent с `📤 ОТПРАВИТЬ НАПОМИНАНИЕ:` — это запрос от НЕ-main агента отправить сообщение через их бота.

**Формат:**
\`\`\`
📤 ОТПРАВИТЬ НАПОМИНАНИЕ:
accountId: semen
target: 7977422300
message: 🤗 текст напоминания
\`\`\`

**Действие:** Используй `message` tool:
\`\`\`json
{
  "action": "send",
  "channel": "telegram",
  "accountId": "<accountId из systemEvent>",
  "target": "<target из systemEvent>",
  "message": "<message из systemEvent>"
}
\`\`\`

Ничего больше не отвечай после отправки (NO_REPLY).
```

### Как это работает

При получении такого systemEvent, main агент:
1. Парсит accountId, target, message из текста
2. Использует `message` tool с этими параметрами
3. Сообщение отправляется от бота с указанным accountId
4. Main агент отвечает NO_REPLY (не дублирует в свой чат)

---

## Почему эта схема работает

1. **Main агент имеет стабильный heartbeat** — systemEvent всегда обрабатывается
2. **Message tool работает** — проверено CLI и tool call
3. **AccountId маршрутизирует** — сообщение идёт от нужного бота
4. **Target указывает получателя** — Chat ID пользователя

---

## Альтернатива: прямая отправка через message tool

Если агент хочет отправить сообщение СЕЙЧАС (не по расписанию):

```json
{
  "action": "send",
  "channel": "telegram",
  "accountId": "semen",
  "target": "7977422300",
  "message": "🤗 Текст сообщения"
}
```

Это работает для любого агента, если он имеет доступ к `message` tool.
