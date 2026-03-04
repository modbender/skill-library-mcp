# Настройка GitHub Actions для Binance Enhanced

## ✅ **Репозиторий создан:**
- **URL:** https://github.com/s7cret/binance-enhanced
- **Описание:** Enhanced Binance trading skill for OpenClaw
- **Статус:** Код загружен, push protection разрешён

## 🔐 **Настройка Secrets (ОБЯЗАТЕЛЬНО):**

### **1. Перейдите в настройки репозитория:**
```
https://github.com/s7cret/binance-enhanced/settings/secrets/actions
```

### **2. Добавьте следующие Secrets:**

#### **Secret 1: OPENCLAW_API_KEY**
```
Название: OPENCLAW_API_KEY
Значение: (ваш API ключ OpenClaw)
```
**Как получить API ключ:**
```bash
openclaw api-key create --name github-actions --expires 90d
```

#### **Secret 2: GITHUB_TOKEN** (автоматически)
```
Название: GITHUB_TOKEN
Значение: (автоматически, не нужно добавлять вручную)
```
**Примечание:** GitHub автоматически предоставляет `GITHUB_TOKEN` для workflow.

#### **Secret 3: CLAWHUB_API_KEY** (опционально)
```
Название: CLAWHUB_API_KEY  
Значение: (ваш API ключ ClawHub для публикации)
```
**Нужно только если планируете публикацию на ClawHub.**

## 🚀 **Workflow файлы:**

### **1. sync-to-openclaw.yml**
**Что делает:** Автоматически загружает навык в OpenClaw при каждом push в main.
**Триггер:** `push` в ветку `main`
**Действия:**
- Проверяет код
- Создает архив навыка
- Загружает в OpenClaw через API
- Уведомляет об успехе/ошибке

### **2. publish.yml**  
**Что делает:** Публикует навык на ClawHub при создании релиза.
**Триггер:** `release` создание
**Действия:**
- Создает архив
- Загружает на ClawHub
- Обновляет версию

### **3. docs.yml**
**Что делает:** Создает GitHub Pages для документации.
**Триггер:** `push` в main с изменениями в `.md` файлах
**Действия:**
- Собирает документацию
- Публикует на GitHub Pages

## 🧪 **Тестирование интеграции:**

### **Вариант 1: Ручной запуск workflow**
1. Перейдите: https://github.com/s7cret/binance-enhanced/actions
2. Выберите "Sync to OpenClaw"
3. Нажмите "Run workflow"
4. Выберите ветку `main`
5. Нажмите "Run workflow"

### **Вариант 2: Тестовый push**
```bash
cd /home/moltbot1/.openclaw/workspace/binance-enhanced
echo "# Test update $(date)" >> TEST.md
git add TEST.md
git commit -m "Test GitHub Actions integration"
git push origin main
```

### **Вариант 3: Мониторинг выполнения**
- **Actions:** https://github.com/s7cret/binance-enhanced/actions
- **Workflow runs:** Просмотр логов выполнения
- **Уведомления:** Настройте в GitHub Settings → Notifications

## 🔧 **Настройка OpenClaw для приёма webhook:**

### **1. Получите webhook URL:**
```bash
# Если у OpenClaw есть публичный URL
openclaw webhook create --name github --url https://your-instance.com/webhook/github
```

### **2. Настройте GitHub webhook:**
1. https://github.com/s7cret/binance-enhanced/settings/hooks
2. Add webhook
3. **Payload URL:** `https://your-openclaw-instance.com/webhook/github`
4. **Content type:** `application/json`
5. **Secret:** (сгенерируйте случайную строку)
6. **Events:** `Push events`, `Release events`

### **3. Альтернатива: Используйте локальный webhook handler:**
```bash
# Запустите скрипт из репозитория
cd /home/moltbot1/.openclaw/workspace/binance-enhanced
python3 webhook-handler.py
```

## 📊 **Мониторинг:**

### **GitHub Actions статус:**
- ✅ **Success:** Зелёная галочка
- ❌ **Failure:** Красный крестик
- ⏳ **Running:** Жёлтый кружок

### **Логи:**
- Нажмите на workflow run
- Разверните каждый шаг (step)
- Просмотрите logs для debugging

### **Уведомления:**
- Email при успехе/ошибке
- Slack/Discord интеграция (опционально)
- Telegram бот (через OpenClaw)

## 🐛 **Устранение неполадок:**

### **Ошибка: Authentication failed**
```
❌ Authentication failed: Invalid API key
```
**Решение:** Проверьте `OPENCLAW_API_KEY` в Secrets.

### **Ошибка: Permission denied**
```
❌ Permission denied: cannot write to skills directory
```
**Решение:** Убедитесь что OpenClaw имеет права на запись.

### **Ошибка: Workflow not triggered**
```
ℹ️ Workflow не запускается при push
```
**Решение:** Проверьте триггеры в `.github/workflows/*.yml`.

### **Ошибка: Rate limit exceeded**
```
❌ API rate limit exceeded
```
**Решение:** Добавьте паузы между запросами, используйте кэширование.

## 🎯 **Следующие шаги:**

### **1. Настройте Secrets** (СЕЙЧАС)
### **2. Запустите тестовый workflow**
### **3. Проверьте логи выполнения**
### **4. Настройте уведомления**
### **5. Создайте релиз для публикации на ClawHub**

## 🔗 **Полезные ссылки:**
- **Репозиторий:** https://github.com/s7cret/binance-enhanced
- **Actions:** https://github.com/s7cret/binance-enhanced/actions
- **Settings:** https://github.com/s7cret/binance-enhanced/settings
- **Secrets:** https://github.com/s7cret/binance-enhanced/settings/secrets/actions
- **Webhooks:** https://github.com/s7cret/binance-enhanced/settings/hooks

---

**🚀 Готово к автоматизации! Настройте Secrets и тестируйте workflow.**