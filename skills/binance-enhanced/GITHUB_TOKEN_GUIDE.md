# GitHub Token Security Guide

## 🔐 **ВАЖНО: Токен компрометирован!**

Токен `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` был отправлен в открытом виде в чат. 

### 🚨 **Немедленные действия:**

1. **Отзовите токен СЕЙЧАС:**
   ```bash
   # Используйте GitHub API для отзыва
   curl -X DELETE \
     -H "Authorization: token ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
     "https://api.github.com/applications/CLIENT_ID/token" \
     -d '{"access_token":"ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"}'
   ```

2. **Или через веб-интерфейс:**
   - Зайдите на: **https://github.com/settings/tokens**
   - Найдите токен `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - Нажмите **"Delete"**

3. **Создайте новый токен:**
   - **Scopes:** Только `repo` (полный контроль репозиториев)
   - **Expiration:** 90 дней (рекомендуется)
   - **Note:** "OpenClaw Integration - Binance Enhanced"

## 🔧 **Безопасная настройка:**

### **Вариант A: Использовать существующий токен (небезопасно)**
```bash
# НЕ РЕКОМЕНДУЕТСЯ, но если нужно срочно:
./setup-github-secure.sh ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx S7cret
```

### **Вариант B: Создать новый токен и настроить**
```bash
# 1. Создайте новый токен на https://github.com/settings/tokens
# 2. Запустите настройку с новым токеном
./setup-github-secure.sh YOUR_NEW_TOKEN S7cret
```

### **Вариант C: Использовать SSH ключи (рекомендуется)**
```bash
# 1. Создайте SSH ключ
ssh-keygen -t ed25519 -C "openclaw@your-domain.com"

# 2. Добавьте публичный ключ в GitHub
#    https://github.com/settings/ssh/new

# 3. Настройте репозиторий с SSH
git remote set-url origin git@github.com:S7cret/binance-enhanced.git
```

## 🛡️ **Best Practices для токенов:**

### **1. Минимальные permissions:**
```json
{
  "repo": "Full control of private repositories",
  "workflow": "Update GitHub Action workflows"
}
```

### **2. Environment variables:**
```bash
# НИКОГДА не хардкодите токены!
export GITHUB_TOKEN="your-token"
./setup-script.sh

# Или используйте .env файл (в .gitignore!)
echo "GITHUB_TOKEN=your-token" >> .env
source .env
```

### **3. GitHub Secrets:**
```yaml
# В GitHub Actions используйте secrets
- name: Use GitHub Token
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: echo "Token is secure"
```

### **4. Token rotation:**
```bash
# Скрипт для ротации токена
#!/bin/bash
# rotate-token.sh
OLD_TOKEN="$1"
NEW_TOKEN="$2"

# Отозвать старый
curl -X DELETE \
  -H "Authorization: token $OLD_TOKEN" \
  "https://api.github.com/applications/CLIENT_ID/token" \
  -d "{\"access_token\":\"$OLD_TOKEN\"}"

# Обновить remote
git remote set-url origin "https://S7cret:$NEW_TOKEN@github.com/S7cret/binance-enhanced.git"
```

## 🔍 **Проверка безопасности:**

### **1. Проверить активность токена:**
```bash
curl -s -H "Authorization: token YOUR_TOKEN" \
     "https://api.github.com/rate_limit"
```

### **2. Проверить permissions:**
```bash
curl -s -H "Authorization: token YOUR_TOKEN" \
     "https://api.github.com/user" | jq '.permissions'
```

### **3. Аудит логов:**
```bash
# Проверить историю использования
curl -s -H "Authorization: token YOUR_TOKEN" \
     "https://api.github.com/events"
```

## 🚨 **Признаки компрометации:**

1. **Неизвестные commits/pushes** в репозитории
2. **Создание новых веток** без вашего ведома
3. **Изменение settings** репозитория
4. **Неизвестные workflow runs** в Actions

## 🔄 **Процедура при компрометации:**

1. **Немедленно отзовите токен**
2. **Проверьте активность** в репозитории
3. **Восстановите изменения** если нужно
4. **Создайте новый токен** с ограниченными правами
5. **Обновите все интеграции**

## 📞 **Экстренные контакты:**

- **GitHub Support:** https://support.github.com
- **Security Incident:** security@github.com
- **OpenClaw Security:** security@openclaw.ai

## ✅ **Checklist безопасности:**

- [ ] Токен имеет минимальные необходимые permissions
- [ ] Токен имеет expiration date
- [ ] Токен не закоммичен в Git
- [ ] Используются GitHub Secrets для Actions
- [ ] Регулярная ротация токенов (каждые 90 дней)
- [ ] Мониторинг активности токена
- [ ] SSH ключи для доступа к репозиториям

---

**⚠️ ВАЖНО:** Токен `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` должен быть отозван немедленно!

**Рекомендую:** Создать новый токен с ограниченными правами и использовать SSH ключи для долгосрочного доступа.